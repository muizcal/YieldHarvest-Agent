// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IYieldSource
 * @notice Interface for yield-generating protocols (PancakeSwap, Venus, Thena)
 */
interface IYieldSource {
    /**
     * @notice Deposit tokens into the yield source
     * @param token Token to deposit
     */
    function deposit(address token) external payable;
    
    /**
     * @notice Withdraw tokens from the yield source
     * @param token Token to withdraw
     * @param amount Amount to withdraw
     * @return Amount withdrawn
     */
    function withdraw(address token, uint256 amount) external returns (uint256);
    
    /**
     * @notice Harvest rewards
     * @param token Token to harvest rewards for
     * @return Amount of rewards harvested
     */
    function harvest(address token) external returns (uint256);
    
    /**
     * @notice Get pending rewards
     * @param token Token to check rewards for
     * @param account Account to check
     * @return Amount of pending rewards
     */
    function pendingRewards(address token, address account) external view returns (uint256);
    
    /**
     * @notice Get current APY
     * @param token Token to check APY for
     * @return APY in basis points (10000 = 100%)
     */
    function getAPY(address token) external view returns (uint256);
    
    /**
     * @notice Get total value locked in this source
     * @return TVL in wei
     */
    function getTVL() external view returns (uint256);
}
