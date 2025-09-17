// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title RewardVault
 * @dev Secure token storage and payout management for ASI Core task system
 * @notice Only TaskRegistry can trigger payouts, ensuring controlled fund distribution
 */
contract RewardVault is AccessControl, ReentrancyGuard, Pausable {
    bytes32 public constant TASK_REGISTRY_ROLE = keccak256("TASK_REGISTRY_ROLE");
    bytes32 public constant TREASURER_ROLE = keccak256("TREASURER_ROLE");
    
    // Track balances per token
    mapping(address => uint256) public tokenBalances;
    
    // Track total payouts per user per token
    mapping(address => mapping(address => uint256)) public userPayouts;
    
    // Track total payouts per token
    mapping(address => uint256) public totalPayouts;
    
    // Emergency withdrawal settings
    uint256 public emergencyWithdrawDelay = 7 days;
    mapping(address => uint256) public emergencyWithdrawRequests;
    
    // Events
    event Deposit(
        address indexed token,
        address indexed depositor,
        uint256 amount,
        uint256 newBalance
    );
    
    event Payout(
        address indexed token,
        address indexed recipient,
        uint256 amount,
        address indexed triggeredBy
    );
    
    event EmergencyWithdrawRequested(
        address indexed token,
        address indexed requester,
        uint256 amount,
        uint256 availableAt
    );
    
    event EmergencyWithdraw(
        address indexed token,
        address indexed recipient,
        uint256 amount
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(TREASURER_ROLE, msg.sender);
    }
    
    /**
     * @dev Deposit tokens to fund bounties
     * @param token ERC20 token address
     * @param amount Amount to deposit
     */
    function deposit(
        address token,
        uint256 amount
    ) external whenNotPaused nonReentrant {
        require(token != address(0), "Invalid token address");
        require(amount > 0, "Amount must be > 0");
        
        IERC20(token).transferFrom(msg.sender, address(this), amount);
        
        tokenBalances[token] += amount;
        
        emit Deposit(token, msg.sender, amount, tokenBalances[token]);
    }
    
    /**
     * @dev Process payout for completed task (TaskRegistry only)
     * @param token ERC20 token address
     * @param recipient Address to receive payment
     * @param amount Amount to pay
     */
    function payout(
        address token,
        address recipient,
        uint256 amount
    ) external onlyRole(TASK_REGISTRY_ROLE) whenNotPaused nonReentrant {
        require(token != address(0), "Invalid token address");
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Amount must be > 0");
        require(tokenBalances[token] >= amount, "Insufficient vault balance");
        
        // Update balances
        tokenBalances[token] -= amount;
        userPayouts[recipient][token] += amount;
        totalPayouts[token] += amount;
        
        // Transfer tokens
        IERC20(token).transfer(recipient, amount);
        
        emit Payout(token, recipient, amount, msg.sender);
    }
    
    /**
     * @dev Get available balance for a token
     * @param token ERC20 token address
     * @return Available balance
     */
    function getBalance(address token) external view returns (uint256) {
        return tokenBalances[token];
    }
    
    /**
     * @dev Get total amount paid to a user for a specific token
     * @param user User address
     * @param token Token address
     * @return Total amount paid
     */
    function getUserPayouts(address user, address token) 
        external 
        view 
        returns (uint256) 
    {
        return userPayouts[user][token];
    }
    
    /**
     * @dev Get total payouts for a token
     * @param token Token address
     * @return Total amount paid out
     */
    function getTotalPayouts(address token) external view returns (uint256) {
        return totalPayouts[token];
    }
    
    /**
     * @dev Check if payout is possible
     * @param token Token address
     * @param amount Amount to check
     * @return True if payout is possible
     */
    function canPayout(address token, uint256 amount) 
        external 
        view 
        returns (bool) 
    {
        return tokenBalances[token] >= amount;
    }
    
    /**
     * @dev Request emergency withdrawal (Treasurer only)
     * @param token Token address
     * @param amount Amount to withdraw
     */
    function requestEmergencyWithdraw(
        address token,
        uint256 amount
    ) external onlyRole(TREASURER_ROLE) {
        require(token != address(0), "Invalid token address");
        require(amount > 0, "Amount must be > 0");
        require(tokenBalances[token] >= amount, "Insufficient balance");
        
        uint256 availableAt = block.timestamp + emergencyWithdrawDelay;
        emergencyWithdrawRequests[token] = availableAt;
        
        emit EmergencyWithdrawRequested(token, msg.sender, amount, availableAt);
    }
    
    /**
     * @dev Execute emergency withdrawal after delay
     * @param token Token address
     * @param amount Amount to withdraw
     * @param recipient Recipient address
     */
    function emergencyWithdraw(
        address token,
        uint256 amount,
        address recipient
    ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
        require(token != address(0), "Invalid token address");
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Amount must be > 0");
        require(tokenBalances[token] >= amount, "Insufficient balance");
        require(emergencyWithdrawRequests[token] != 0, "No withdrawal request");
        require(
            block.timestamp >= emergencyWithdrawRequests[token],
            "Withdrawal delay not met"
        );
        
        // Reset request
        emergencyWithdrawRequests[token] = 0;
        
        // Update balance
        tokenBalances[token] -= amount;
        
        // Transfer
        IERC20(token).transfer(recipient, amount);
        
        emit EmergencyWithdraw(token, recipient, amount);
    }
    
    /**
     * @dev Cancel emergency withdrawal request
     * @param token Token address
     */
    function cancelEmergencyWithdraw(address token) 
        external 
        onlyRole(TREASURER_ROLE) 
    {
        emergencyWithdrawRequests[token] = 0;
    }
    
    /**
     * @dev Update emergency withdrawal delay
     * @param newDelay New delay in seconds
     */
    function updateEmergencyDelay(uint256 newDelay) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        require(newDelay >= 1 days, "Delay must be at least 1 day");
        require(newDelay <= 30 days, "Delay cannot exceed 30 days");
        
        emergencyWithdrawDelay = newDelay;
    }
    
    /**
     * @dev Get contract statistics
     */
    function getStats() external view returns (
        uint256 totalTokensManaged,
        uint256 totalUniqueRecipients
    ) {
        // Note: This is a simplified version
        // In production, you'd want to track these values more efficiently
        return (0, 0); // Placeholder implementation
    }
    
    /**
     * @dev Emergency pause
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Recover accidentally sent tokens (not managed tokens)
     * @param token Token address
     * @param recipient Recipient address
     */
    function recoverToken(
        address token,
        address recipient
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(token != address(0), "Invalid token address");
        require(recipient != address(0), "Invalid recipient");
        
        uint256 contractBalance = IERC20(token).balanceOf(address(this));
        uint256 managedBalance = tokenBalances[token];
        
        require(contractBalance > managedBalance, "No recoverable tokens");
        
        uint256 recoverableAmount = contractBalance - managedBalance;
        IERC20(token).transfer(recipient, recoverableAmount);
    }
}