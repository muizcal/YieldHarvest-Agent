// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "./interfaces/IYieldSource.sol";
import "./SessionKeyManager.sol";
import "./DecisionLogger.sol";

/**
 * @title YieldVaultManager
 * @notice Core vault contract managing autonomous yield farming operations
 * @dev Integrates with SessionKeyManager for non-custodial control
 */
contract YieldVaultManager is Ownable, ReentrancyGuard, Pausable {
    
    // ============ State Variables ============
    
    SessionKeyManager public sessionKeyManager;
    DecisionLogger public decisionLogger;
    
    // Protocol whitelist
    mapping(address => bool) public whitelistedProtocols;
    mapping(address => uint256) public protocolAllocations; // in basis points (10000 = 100%)
    
    // Position tracking
    struct Position {
        address protocol;
        address token;
        uint256 amount;
        uint256 entryTimestamp;
        uint256 entryAPY;
        uint256 lastCompoundTimestamp;
    }
    
    Position[] public positions;
    mapping(address => uint256) public protocolTVL;
    
    // Configuration
    uint256 public maxAllocationPerProtocol = 2000; // 20%
    uint256 public minAPY = 500; // 5% in basis points
    uint256 public maxRiskScore = 7; // 0-10 scale
    uint256 public compoundInterval = 4 hours;
    uint256 public rebalanceThreshold = 200; // 2% APY difference
    
    // Performance tracking
    uint256 public totalDeposited;
    uint256 public totalWithdrawn;
    uint256 public totalYieldEarned;
    uint256 public totalGasSpent;
    
    // Emergency
    address public emergencyWithdrawAddress;
    
    // ============ Events ============
    
    event ProtocolWhitelisted(address indexed protocol, bool status);
    event PositionOpened(
        uint256 indexed positionId,
        address indexed protocol,
        address token,
        uint256 amount,
        uint256 apy
    );
    event PositionClosed(
        uint256 indexed positionId,
        address indexed protocol,
        uint256 amount,
        uint256 profit
    );
    event Compounded(
        uint256 indexed positionId,
        uint256 rewardAmount,
        uint256 newTotalAmount
    );
    event Rebalanced(
        uint256 fromPositionId,
        uint256 toPositionId,
        uint256 amount,
        string reason
    );
    event EmergencyWithdraw(address indexed to, uint256 amount);
    event ConfigUpdated(string param, uint256 value);
    
    // ============ Errors ============
    
    error ProtocolNotWhitelisted();
    error AllocationExceeded();
    error InsufficientAPY();
    error RiskScoreTooHigh();
    error UnauthorizedSessionKey();
    error CompoundTooSoon();
    error InvalidPosition();
    error ZeroAmount();
    
    // ============ Constructor ============
    
    constructor(
        address _sessionKeyManager,
        address _decisionLogger,
        address _emergencyAddress
    ) Ownable(msg.sender) {
        sessionKeyManager = SessionKeyManager(_sessionKeyManager);
        decisionLogger = DecisionLogger(_decisionLogger);
        emergencyWithdrawAddress = _emergencyAddress;
    }
    
    // ============ Modifiers ============
    
    modifier onlyAuthorized() {
    if (msg.sender != owner() && !sessionKeyManager.isValidSessionKey(msg.sender)) {
        revert UnauthorizedSessionKey();
    }
    _;
}
    
    // ============ Core Functions ============
    
    /**
     * @notice Open a new yield farming position
     */
    function openPosition(
        address protocol,
        address token,
        uint256 amount,
        uint256 apy,
        uint256 riskScore,
        string calldata reason
    ) public onlyAuthorized nonReentrant whenNotPaused returns (uint256) {
        if (amount == 0) revert ZeroAmount();
        if (!whitelistedProtocols[protocol]) revert ProtocolNotWhitelisted();
        if (apy < minAPY) revert InsufficientAPY();
        if (riskScore > maxRiskScore) revert RiskScoreTooHigh();
        
        // Check allocation limits
        uint256 totalTVL = address(this).balance;
        if (totalTVL > 0) {
            uint256 newProtocolTVL = protocolTVL[protocol] + amount;
            if (newProtocolTVL * 10000 / totalTVL > maxAllocationPerProtocol) {
                revert AllocationExceeded();
            }
        }
        
        // Log decision
        decisionLogger.logDecision(
            msg.sender,
            "OPEN_POSITION",
            protocol,
            amount,
            apy,
            reason
        );
        
        // Create position
        uint256 positionId = positions.length;
        positions.push(Position({
            protocol: protocol,
            token: token,
            amount: amount,
            entryTimestamp: block.timestamp,
            entryAPY: apy,
            lastCompoundTimestamp: block.timestamp
        }));
        
        protocolTVL[protocol] += amount;
        totalDeposited += amount;
        
        // Interact with protocol
        IYieldSource(protocol).deposit{value: amount}(token);
        
        emit PositionOpened(positionId, protocol, token, amount, apy);
        
        return positionId;
    }
    
    /**
     * @notice Close an existing position
     */
    function closePosition(
        uint256 positionId,
        string calldata reason
    ) public onlyAuthorized nonReentrant whenNotPaused returns (uint256) {
        if (positionId >= positions.length) revert InvalidPosition();
        
        Position storage position = positions[positionId];
        if (position.amount == 0) revert InvalidPosition();
        
        // Log decision
        decisionLogger.logDecision(
            msg.sender,
            "CLOSE_POSITION",
            position.protocol,
            position.amount,
            position.entryAPY,
            reason
        );
        
        // Withdraw from protocol
        uint256 withdrawn = IYieldSource(position.protocol).withdraw(
            position.token,
            position.amount
        );
        
        uint256 profit = withdrawn > position.amount ? withdrawn - position.amount : 0;
        
        protocolTVL[position.protocol] -= position.amount;
        totalWithdrawn += withdrawn;
        totalYieldEarned += profit;
        
        // Mark as closed
        position.amount = 0;
        
        emit PositionClosed(positionId, position.protocol, withdrawn, profit);
        
        return withdrawn;
    }
    
    /**
     * @notice Compound rewards for a position
     */
    function compound(
        uint256 positionId
    ) external onlyAuthorized nonReentrant whenNotPaused returns (uint256) {
        if (positionId >= positions.length) revert InvalidPosition();
        
        Position storage position = positions[positionId];
        if (position.amount == 0) revert InvalidPosition();
        
        // Check compound interval
        if (block.timestamp < position.lastCompoundTimestamp + compoundInterval) {
            revert CompoundTooSoon();
        }
        
        // Harvest rewards
        uint256 rewards = IYieldSource(position.protocol).harvest(position.token);
        
        if (rewards > 0) {
            // Reinvest rewards
            IYieldSource(position.protocol).deposit{value: rewards}(position.token);
            
            position.amount += rewards;
            position.lastCompoundTimestamp = block.timestamp;
            protocolTVL[position.protocol] += rewards;
            totalYieldEarned += rewards;
            
            emit Compounded(positionId, rewards, position.amount);
        }
        
        return rewards;
    }
    
    /**
     * @notice Rebalance from one position to another
     */
    function rebalance(
        uint256 fromPositionId,
        address toProtocol,
        address toToken,
        uint256 toAPY,
        uint256 riskScore,
        string calldata reason
    ) external onlyAuthorized nonReentrant whenNotPaused returns (uint256) {
        // Close old position
        uint256 amount = closePosition(fromPositionId, reason);
        
        // Open new position
        uint256 newPositionId = openPosition(
            toProtocol,
            toToken,
            amount,
            toAPY,
            riskScore,
            reason
        );
        
        emit Rebalanced(fromPositionId, newPositionId, amount, reason);
        
        return newPositionId;
    }
    
    // ============ Admin Functions ============
    
    function whitelistProtocol(address protocol, bool status) external onlyOwner {
        whitelistedProtocols[protocol] = status;
        emit ProtocolWhitelisted(protocol, status);
    }
    
    function updateConfig(
        uint256 _maxAllocationPerProtocol,
        uint256 _minAPY,
        uint256 _maxRiskScore,
        uint256 _compoundInterval,
        uint256 _rebalanceThreshold
    ) external onlyOwner {
        maxAllocationPerProtocol = _maxAllocationPerProtocol;
        minAPY = _minAPY;
        maxRiskScore = _maxRiskScore;
        compoundInterval = _compoundInterval;
        rebalanceThreshold = _rebalanceThreshold;
        
        emit ConfigUpdated("maxAllocationPerProtocol", _maxAllocationPerProtocol);
        emit ConfigUpdated("minAPY", _minAPY);
        emit ConfigUpdated("maxRiskScore", _maxRiskScore);
        emit ConfigUpdated("compoundInterval", _compoundInterval);
        emit ConfigUpdated("rebalanceThreshold", _rebalanceThreshold);
    }
    
    function pause() external onlyOwner {
        _pause();
    }
    
    function unpause() external onlyOwner {
        _unpause();
    }
    
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        (bool success, ) = emergencyWithdrawAddress.call{value: balance}("");
        require(success, "Transfer failed");
        emit EmergencyWithdraw(emergencyWithdrawAddress, balance);
    }
    
    // ============ View Functions ============
    
    function getPosition(uint256 positionId) external view returns (Position memory) {
        return positions[positionId];
    }
    
    function getPositionCount() external view returns (uint256) {
        return positions.length;
    }
    
    function getTotalTVL() external view returns (uint256) {
        return address(this).balance;
    }
    
    function getPerformanceMetrics() external view returns (
        uint256 deposited,
        uint256 withdrawn,
        uint256 yieldEarned,
        uint256 gasSpent,
        uint256 netProfit
    ) {
        deposited = totalDeposited;
        withdrawn = totalWithdrawn;
        yieldEarned = totalYieldEarned;
        gasSpent = totalGasSpent;
        netProfit = yieldEarned > gasSpent ? yieldEarned - gasSpent : 0;
    }
    
    // ============ Receive ETH ============
    
    receive() external payable {}
}
