// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title DecisionLogger
 * @notice Logs all AI agent decisions onchain for transparency and auditability
 * @dev Every agent action is recorded with reasoning and context
 */
contract DecisionLogger is Ownable {
    
    // ============ State Variables ============
    
    struct Decision {
        uint256 id;
        uint256 timestamp;
        address executor;
        string action;
        address targetProtocol;
        uint256 amount;
        uint256 apy;
        string reason;
        bytes32 contextHash;
    }
    
    Decision[] public decisions;
    mapping(address => uint256[]) public executorDecisions;
    mapping(string => uint256[]) public actionDecisions;
    
    uint256 public totalDecisions;
    
    // ============ Events ============
    
    event DecisionLogged(
        uint256 indexed id,
        address indexed executor,
        string action,
        address targetProtocol,
        uint256 amount,
        uint256 apy,
        string reason
    );
    
    event PerformanceSnapshot(
        uint256 indexed timestamp,
        uint256 totalTVL,
        uint256 totalYield,
        uint256 averageAPY,
        uint256 activePositions
    );
    
    // ============ Constructor ============
    
    constructor() Ownable(msg.sender) {}
    
    // ============ Core Functions ============
    
    /**
     * @notice Log an agent decision
     * @param executor Address making the decision (session key)
     * @param action Type of action (OPEN_POSITION, CLOSE_POSITION, COMPOUND, REBALANCE)
     * @param targetProtocol Protocol being interacted with
     * @param amount Amount involved in the decision
     * @param apy APY associated with the decision
     * @param reason AI reasoning behind the decision
     */
    function logDecision(
        address executor,
        string calldata action,
        address targetProtocol,
        uint256 amount,
        uint256 apy,
        string calldata reason
    ) external onlyOwner returns (uint256) {
        uint256 decisionId = totalDecisions;
        
        // Create context hash for additional data
        bytes32 contextHash = keccak256(abi.encodePacked(
            executor,
            action,
            targetProtocol,
            amount,
            apy,
            block.timestamp
        ));
        
        Decision memory decision = Decision({
            id: decisionId,
            timestamp: block.timestamp,
            executor: executor,
            action: action,
            targetProtocol: targetProtocol,
            amount: amount,
            apy: apy,
            reason: reason,
            contextHash: contextHash
        });
        
        decisions.push(decision);
        executorDecisions[executor].push(decisionId);
        actionDecisions[action].push(decisionId);
        totalDecisions++;
        
        emit DecisionLogged(
            decisionId,
            executor,
            action,
            targetProtocol,
            amount,
            apy,
            reason
        );
        
        return decisionId;
    }
    
    /**
     * @notice Log a performance snapshot
     * @param totalTVL Total value locked
     * @param totalYield Total yield earned
     * @param averageAPY Average APY across positions
     * @param activePositions Number of active positions
     */
    function logPerformanceSnapshot(
        uint256 totalTVL,
        uint256 totalYield,
        uint256 averageAPY,
        uint256 activePositions
    ) external onlyOwner {
        emit PerformanceSnapshot(
            block.timestamp,
            totalTVL,
            totalYield,
            averageAPY,
            activePositions
        );
    }
    
    // ============ View Functions ============
    
    /**
     * @notice Get a specific decision
     */
    function getDecision(uint256 decisionId) external view returns (Decision memory) {
        require(decisionId < totalDecisions, "Invalid decision ID");
        return decisions[decisionId];
    }
    
    /**
     * @notice Get recent decisions (last N)
     */
    function getRecentDecisions(uint256 count) external view returns (Decision[] memory) {
        uint256 returnCount = count > totalDecisions ? totalDecisions : count;
        Decision[] memory recentDecisions = new Decision[](returnCount);
        
        uint256 startIndex = totalDecisions - returnCount;
        for (uint256 i = 0; i < returnCount; i++) {
            recentDecisions[i] = decisions[startIndex + i];
        }
        
        return recentDecisions;
    }
    
    /**
     * @notice Get decisions by executor
     */
    function getDecisionsByExecutor(
        address executor,
        uint256 offset,
        uint256 limit
    ) external view returns (Decision[] memory) {
        uint256[] memory decisionIds = executorDecisions[executor];
        uint256 returnCount = limit;
        
        if (offset >= decisionIds.length) {
            return new Decision[](0);
        }
        
        if (offset + limit > decisionIds.length) {
            returnCount = decisionIds.length - offset;
        }
        
        Decision[] memory result = new Decision[](returnCount);
        for (uint256 i = 0; i < returnCount; i++) {
            result[i] = decisions[decisionIds[offset + i]];
        }
        
        return result;
    }
    
    /**
     * @notice Get decisions by action type
     */
    function getDecisionsByAction(
        string calldata action,
        uint256 offset,
        uint256 limit
    ) external view returns (Decision[] memory) {
        uint256[] memory decisionIds = actionDecisions[action];
        uint256 returnCount = limit;
        
        if (offset >= decisionIds.length) {
            return new Decision[](0);
        }
        
        if (offset + limit > decisionIds.length) {
            returnCount = decisionIds.length - offset;
        }
        
        Decision[] memory result = new Decision[](returnCount);
        for (uint256 i = 0; i < returnCount; i++) {
            result[i] = decisions[decisionIds[offset + i]];
        }
        
        return result;
    }
    
    /**
     * @notice Get decisions in a time range
     */
    function getDecisionsByTimeRange(
        uint256 startTime,
        uint256 endTime
    ) external view returns (Decision[] memory) {
        // Count matching decisions first
        uint256 count = 0;
        for (uint256 i = 0; i < totalDecisions; i++) {
            if (decisions[i].timestamp >= startTime && decisions[i].timestamp <= endTime) {
                count++;
            }
        }
        
        // Build result array
        Decision[] memory result = new Decision[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < totalDecisions; i++) {
            if (decisions[i].timestamp >= startTime && decisions[i].timestamp <= endTime) {
                result[index] = decisions[i];
                index++;
            }
        }
        
        return result;
    }
    
    /**
     * @notice Get total decisions count
     */
    function getTotalDecisions() external view returns (uint256) {
        return totalDecisions;
    }
    
    /**
     * @notice Get decision count by executor
     */
    function getExecutorDecisionCount(address executor) external view returns (uint256) {
        return executorDecisions[executor].length;
    }
    
    /**
     * @notice Get decision count by action
     */
    function getActionDecisionCount(string calldata action) external view returns (uint256) {
        return actionDecisions[action].length;
    }
}
