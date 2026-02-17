// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SessionKeyManager
 * @notice Manages session keys with spending limits and expiry for non-custodial agent control
 * @dev Allows AI agent to operate autonomously within predefined limits
 */
contract SessionKeyManager is Ownable {
    
    // ============ State Variables ============
    
    struct SessionKey {
        address key;
        uint256 spendingLimit; // in wei
        uint256 spentAmount;
        uint256 expiryTimestamp;
        bool isActive;
        string purpose;
    }
    
    mapping(address => SessionKey) public sessionKeys;
    address[] public activeKeys;
    
    uint256 public defaultSpendingLimit = 0.1 ether;
    uint256 public defaultExpiry = 24 hours;
    uint256 public maxConcurrentKeys = 5;
    
    // ============ Events ============
    
    event SessionKeyCreated(
        address indexed key,
        uint256 spendingLimit,
        uint256 expiryTimestamp,
        string purpose
    );
    event SessionKeyRevoked(address indexed key, string reason);
    event SessionKeyUsed(address indexed key, uint256 amount, uint256 remaining);
    event SpendingLimitUpdated(address indexed key, uint256 newLimit);
    event ExpiryExtended(address indexed key, uint256 newExpiry);
    
    // ============ Errors ============
    
    error KeyAlreadyExists();
    error KeyNotFound();
    error KeyExpired();
    error KeyInactive();
    error SpendingLimitExceeded();
    error MaxKeysReached();
    error InvalidAmount();
    error InvalidExpiry();
    
    // ============ Constructor ============
    
    constructor() Ownable(msg.sender) {}
    
    // ============ Core Functions ============
    
    /**
     * @notice Create a new session key with spending limits
     * @param key Address of the session key
     * @param spendingLimit Maximum amount key can spend (0 = use default)
     * @param duration How long key is valid (0 = use default)
     * @param purpose Description of key purpose
     */
    function createSessionKey(
        address key,
        uint256 spendingLimit,
        uint256 duration,
        string calldata purpose
    ) external onlyOwner {
        if (sessionKeys[key].key != address(0)) revert KeyAlreadyExists();
        if (activeKeys.length >= maxConcurrentKeys) revert MaxKeysReached();
        
        uint256 limit = spendingLimit == 0 ? defaultSpendingLimit : spendingLimit;
        uint256 expiry = block.timestamp + (duration == 0 ? defaultExpiry : duration);
        
        sessionKeys[key] = SessionKey({
            key: key,
            spendingLimit: limit,
            spentAmount: 0,
            expiryTimestamp: expiry,
            isActive: true,
            purpose: purpose
        });
        
        activeKeys.push(key);
        
        emit SessionKeyCreated(key, limit, expiry, purpose);
    }
    
    /**
     * @notice Revoke a session key
     * @param key Address of session key to revoke
     * @param reason Reason for revocation
     */
    function revokeSessionKey(address key, string calldata reason) external onlyOwner {
        if (sessionKeys[key].key == address(0)) revert KeyNotFound();
        
        sessionKeys[key].isActive = false;
        
        // Remove from active keys array
        for (uint256 i = 0; i < activeKeys.length; i++) {
            if (activeKeys[i] == key) {
                activeKeys[i] = activeKeys[activeKeys.length - 1];
                activeKeys.pop();
                break;
            }
        }
        
        emit SessionKeyRevoked(key, reason);
    }
    
    /**
     * @notice Record spending by a session key
     * @param key Session key address
     * @param amount Amount being spent
     */
    function recordSpending(address key, uint256 amount) external {
        SessionKey storage sessionKey = sessionKeys[key];
        
        if (sessionKey.key == address(0)) revert KeyNotFound();
        if (!sessionKey.isActive) revert KeyInactive();
        if (block.timestamp > sessionKey.expiryTimestamp) revert KeyExpired();
        if (sessionKey.spentAmount + amount > sessionKey.spendingLimit) {
            revert SpendingLimitExceeded();
        }
        
        sessionKey.spentAmount += amount;
        
        uint256 remaining = sessionKey.spendingLimit - sessionKey.spentAmount;
        emit SessionKeyUsed(key, amount, remaining);
    }
    
    /**
     * @notice Check if session key is valid and can spend
     * @param key Session key address
     */
    function isValidSessionKey(address key) external view returns (bool) {
        SessionKey storage sessionKey = sessionKeys[key];
        
        if (sessionKey.key == address(0)) return false;
        if (!sessionKey.isActive) return false;
        if (block.timestamp > sessionKey.expiryTimestamp) return false;
        
        return true;
    }
    
    /**
     * @notice Check if session key can spend specific amount
     * @param key Session key address
     * @param amount Amount to check
     */
    function canSpend(address key, uint256 amount) external view returns (bool) {
        SessionKey storage sessionKey = sessionKeys[key];
        
        if (sessionKey.key == address(0)) return false;
        if (!sessionKey.isActive) return false;
        if (block.timestamp > sessionKey.expiryTimestamp) return false;
        if (sessionKey.spentAmount + amount > sessionKey.spendingLimit) return false;
        
        return true;
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Update spending limit for a session key
     * @param key Session key address
     * @param newLimit New spending limit
     */
    function updateSpendingLimit(address key, uint256 newLimit) external onlyOwner {
        if (sessionKeys[key].key == address(0)) revert KeyNotFound();
        if (newLimit == 0) revert InvalidAmount();
        
        sessionKeys[key].spendingLimit = newLimit;
        emit SpendingLimitUpdated(key, newLimit);
    }
    
    /**
     * @notice Extend expiry of a session key
     * @param key Session key address
     * @param additionalTime Additional time to add
     */
    function extendExpiry(address key, uint256 additionalTime) external onlyOwner {
        if (sessionKeys[key].key == address(0)) revert KeyNotFound();
        if (additionalTime == 0) revert InvalidExpiry();
        
        uint256 newExpiry = sessionKeys[key].expiryTimestamp + additionalTime;
        sessionKeys[key].expiryTimestamp = newExpiry;
        
        emit ExpiryExtended(key, newExpiry);
    }
    
    /**
     * @notice Update default settings
     */
    function updateDefaults(
        uint256 _defaultSpendingLimit,
        uint256 _defaultExpiry,
        uint256 _maxConcurrentKeys
    ) external onlyOwner {
        defaultSpendingLimit = _defaultSpendingLimit;
        defaultExpiry = _defaultExpiry;
        maxConcurrentKeys = _maxConcurrentKeys;
    }
    
    // ============ View Functions ============
    
    function getSessionKey(address key) external view returns (SessionKey memory) {
        return sessionKeys[key];
    }
    
    function getActiveKeys() external view returns (address[] memory) {
        return activeKeys;
    }
    
    function getRemainingSpending(address key) external view returns (uint256) {
        SessionKey storage sessionKey = sessionKeys[key];
        if (sessionKey.key == address(0)) return 0;
        
        return sessionKey.spendingLimit - sessionKey.spentAmount;
    }
    
    function getTimeRemaining(address key) external view returns (uint256) {
        SessionKey storage sessionKey = sessionKeys[key];
        if (sessionKey.key == address(0)) return 0;
        if (block.timestamp >= sessionKey.expiryTimestamp) return 0;
        
        return sessionKey.expiryTimestamp - block.timestamp;
    }
}
