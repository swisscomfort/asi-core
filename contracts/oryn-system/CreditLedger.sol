// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title CreditLedger
 * @dev Non-tradeable credit system for Oryn ecosystem
 * @notice Credits are earned through ticket completion and can only be spent on platform services
 * @dev Implements non-transferable token-like functionality without being an actual token
 */
contract CreditLedger is AccessControl, ReentrancyGuard, Pausable {
    bytes32 public constant CREDIT_MINTER_ROLE = keccak256("CREDIT_MINTER_ROLE");
    bytes32 public constant CREDIT_BURNER_ROLE = keccak256("CREDIT_BURNER_ROLE");
    bytes32 public constant SERVICE_PROVIDER_ROLE = keccak256("SERVICE_PROVIDER_ROLE");
    bytes32 public constant MAINTAINER_ROLE = keccak256("MAINTAINER_ROLE");
    
    // User credit balances
    mapping(address => uint256) private _balances;
    
    // Spending categories and their costs
    mapping(string => uint256) public serviceCosts;
    
    // User spending history by category
    mapping(address => mapping(string => uint256)) public userSpending;
    mapping(address => uint256) public totalUserSpending;
    
    // Global statistics
    uint256 public totalCreditsIssued;
    uint256 public totalCreditsSpent;
    uint256 public totalCreditsCirculating;
    
    // Credit earning history
    struct CreditTransaction {
        uint256 amount;
        string reason;
        uint256 timestamp;
        address from; // For spending transactions
        string category; // For spending transactions
    }
    
    mapping(address => CreditTransaction[]) public creditHistory;
    mapping(address => uint256) public totalCreditsEarned;
    
    // Service spending limits (anti-abuse)
    mapping(string => uint256) public dailySpendingLimits;
    mapping(address => mapping(string => mapping(uint256 => uint256))) public dailySpending; // user => service => day => amount
    
    // Events
    event CreditsIssued(
        address indexed recipient,
        uint256 amount,
        string reason,
        uint256 timestamp
    );
    
    event CreditsSpent(
        address indexed spender,
        string indexed service,
        uint256 amount,
        address indexed serviceProvider,
        uint256 timestamp
    );
    
    event ServiceCostUpdated(
        string indexed service,
        uint256 oldCost,
        uint256 newCost
    );
    
    event SpendingLimitUpdated(
        string indexed service,
        uint256 oldLimit,
        uint256 newLimit
    );
    
    event CreditsExpired(
        address indexed user,
        uint256 amount,
        string reason
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MAINTAINER_ROLE, msg.sender);
        _grantRole(CREDIT_MINTER_ROLE, msg.sender);
        _grantRole(CREDIT_BURNER_ROLE, msg.sender);
        
        // Initialize default service costs (in credits)
        serviceCosts["extra_storage_1gb"] = 10;           // 1GB extra storage for 1 month
        serviceCosts["translation_document"] = 5;         // Translate 1 document
        serviceCosts["ai_summary_long"] = 3;             // AI summary of long text
        serviceCosts["priority_support"] = 20;           // Priority community support
        serviceCosts["custom_domain"] = 50;              // Custom domain for 1 year
        serviceCosts["advanced_analytics"] = 15;         // Advanced usage analytics
        serviceCosts["backup_service"] = 25;             // Premium backup service
        
        // Initialize daily spending limits to prevent abuse
        dailySpendingLimits["translation_document"] = 50;
        dailySpendingLimits["ai_summary_long"] = 30;
        dailySpendingLimits["priority_support"] = 100;
    }
    
    /**
     * @dev Issue credits to a user (called by authorized minters like TicketRegistry)
     * @param recipient Address to receive credits
     * @param amount Amount of credits to issue
     * @param reason Reason for issuing credits (e.g., "ticket_completed")
     */
    function mintCredits(
        address recipient,
        uint256 amount,
        string calldata reason
    ) external onlyRole(CREDIT_MINTER_ROLE) whenNotPaused {
        require(recipient != address(0), "Cannot mint to zero address");
        require(amount > 0, "Amount must be > 0");
        require(bytes(reason).length > 0, "Reason cannot be empty");
        
        _balances[recipient] += amount;
        totalCreditsIssued += amount;
        totalCreditsCirculating += amount;
        totalCreditsEarned[recipient] += amount;
        
        // Record in credit history
        creditHistory[recipient].push(CreditTransaction({
            amount: amount,
            reason: reason,
            timestamp: block.timestamp,
            from: address(0),
            category: ""
        }));
        
        emit CreditsIssued(recipient, amount, reason, block.timestamp);
    }
    
    /**
     * @dev Overloaded mintCredits for compatibility with TicketRegistry
     * @param recipient Address to receive credits
     * @param amount Amount of credits to issue
     */
    function mintCredits(
        address recipient,
        uint256 amount
    ) external onlyRole(CREDIT_MINTER_ROLE) whenNotPaused {
        mintCredits(recipient, amount, "ticket_completed");
    }
    
    /**
     * @dev Spend credits on a service
     * @param service Service identifier (e.g., "extra_storage_1gb")
     * @param serviceProvider Address providing the service
     * @return success Whether the spending was successful
     */
    function spendCredits(
        string calldata service,
        address serviceProvider
    ) external whenNotPaused nonReentrant returns (bool success) {
        uint256 cost = serviceCosts[service];
        require(cost > 0, "Service not available");
        require(_balances[msg.sender] >= cost, "Insufficient credits");
        require(serviceProvider != address(0), "Invalid service provider");
        
        // Check daily spending limits if applicable
        uint256 today = block.timestamp / 1 days;
        if (dailySpendingLimits[service] > 0) {
            require(
                dailySpending[msg.sender][service][today] + cost <= dailySpendingLimits[service],
                "Daily spending limit exceeded"
            );
            dailySpending[msg.sender][service][today] += cost;
        }
        
        // Deduct credits
        _balances[msg.sender] -= cost;
        totalCreditsSpent += cost;
        totalCreditsCirculating -= cost;
        
        // Update spending statistics
        userSpending[msg.sender][service] += cost;
        totalUserSpending[msg.sender] += cost;
        
        // Record spending in credit history
        creditHistory[msg.sender].push(CreditTransaction({
            amount: cost,
            reason: service,
            timestamp: block.timestamp,
            from: serviceProvider,
            category: service
        }));
        
        emit CreditsSpent(msg.sender, service, cost, serviceProvider, block.timestamp);
        
        return true;
    }
    
    /**
     * @dev Spend credits with custom amount (for flexible services)
     * @param service Service identifier
     * @param amount Custom amount to spend
     * @param serviceProvider Address providing the service
     * @return success Whether the spending was successful
     */
    function spendCreditsCustom(
        string calldata service,
        uint256 amount,
        address serviceProvider
    ) external onlyRole(SERVICE_PROVIDER_ROLE) whenNotPaused nonReentrant returns (bool success) {
        require(amount > 0, "Amount must be > 0");
        require(_balances[msg.sender] >= amount, "Insufficient credits");
        require(serviceProvider != address(0), "Invalid service provider");
        
        // Deduct credits
        _balances[msg.sender] -= amount;
        totalCreditsSpent += amount;
        totalCreditsCirculating -= amount;
        
        // Update spending statistics
        userSpending[msg.sender][service] += amount;
        totalUserSpending[msg.sender] += amount;
        
        // Record spending in credit history
        creditHistory[msg.sender].push(CreditTransaction({
            amount: amount,
            reason: service,
            timestamp: block.timestamp,
            from: serviceProvider,
            category: service
        }));
        
        emit CreditsSpent(msg.sender, service, amount, serviceProvider, block.timestamp);
        
        return true;
    }
    
    /**
     * @dev Get credit balance of an address
     * @param account Address to check
     * @return balance Credit balance
     */
    function balanceOf(address account) external view returns (uint256 balance) {
        return _balances[account];
    }
    
    /**
     * @dev Get cost of a service
     * @param service Service identifier
     * @return cost Cost in credits
     */
    function getServiceCost(string calldata service) external view returns (uint256 cost) {
        return serviceCosts[service];
    }
    
    /**
     * @dev Get user's spending in a specific category
     * @param user User address
     * @param service Service category
     * @return spent Amount spent in the category
     */
    function getUserSpending(address user, string calldata service) external view returns (uint256 spent) {
        return userSpending[user][service];
    }
    
    /**
     * @dev Get user's total spending
     * @param user User address
     * @return totalSpent Total amount spent by user
     */
    function getUserTotalSpending(address user) external view returns (uint256 totalSpent) {
        return totalUserSpending[user];
    }
    
    /**
     * @dev Get user's credit history
     * @param user User address
     * @return transactions Array of credit transactions
     */
    function getCreditHistory(address user) external view returns (CreditTransaction[] memory transactions) {
        return creditHistory[user];
    }
    
    /**
     * @dev Get user's credit history count
     * @param user User address
     * @return count Number of transactions
     */
    function getCreditHistoryCount(address user) external view returns (uint256 count) {
        return creditHistory[user].length;
    }
    
    /**
     * @dev Get global credit statistics
     * @return issued Total credits issued
     * @return spent Total credits spent
     * @return circulating Total credits currently circulating
     */
    function getGlobalStats() external view returns (
        uint256 issued,
        uint256 spent,
        uint256 circulating
    ) {
        return (totalCreditsIssued, totalCreditsSpent, totalCreditsCirculating);
    }
    
    /**
     * @dev Check if user can afford a service
     * @param user User address
     * @param service Service identifier
     * @return canAfford Whether user can afford the service
     * @return cost Cost of the service
     * @return userBalance User's current balance
     */
    function canAffordService(address user, string calldata service) external view returns (
        bool canAfford,
        uint256 cost,
        uint256 userBalance
    ) {
        cost = serviceCosts[service];
        userBalance = _balances[user];
        canAfford = userBalance >= cost && cost > 0;
        
        // Check daily limits if applicable
        if (canAfford && dailySpendingLimits[service] > 0) {
            uint256 today = block.timestamp / 1 days;
            uint256 todaySpent = dailySpending[user][service][today];
            canAfford = todaySpent + cost <= dailySpendingLimits[service];
        }
        
        return (canAfford, cost, userBalance);
    }
    
    // =============================================================================
    // ADMIN FUNCTIONS
    // =============================================================================
    
    /**
     * @dev Update service cost (admin only)
     * @param service Service identifier
     * @param newCost New cost in credits
     */
    function updateServiceCost(
        string calldata service,
        uint256 newCost
    ) external onlyRole(MAINTAINER_ROLE) {
        uint256 oldCost = serviceCosts[service];
        serviceCosts[service] = newCost;
        
        emit ServiceCostUpdated(service, oldCost, newCost);
    }
    
    /**
     * @dev Update daily spending limit (admin only)
     * @param service Service identifier
     * @param newLimit New daily limit
     */
    function updateSpendingLimit(
        string calldata service,
        uint256 newLimit
    ) external onlyRole(MAINTAINER_ROLE) {
        uint256 oldLimit = dailySpendingLimits[service];
        dailySpendingLimits[service] = newLimit;
        
        emit SpendingLimitUpdated(service, oldLimit, newLimit);
    }
    
    /**
     * @dev Emergency credit burn (for abuse cases)
     * @param user User address
     * @param amount Amount to burn
     * @param reason Reason for burning
     */
    function burnCredits(
        address user,
        uint256 amount,
        string calldata reason
    ) external onlyRole(CREDIT_BURNER_ROLE) {
        require(_balances[user] >= amount, "Insufficient balance to burn");
        
        _balances[user] -= amount;
        totalCreditsCirculating -= amount;
        
        emit CreditsExpired(user, amount, reason);
    }
    
    /**
     * @dev Add a new service
     * @param service Service identifier
     * @param cost Cost in credits
     * @param dailyLimit Daily spending limit (0 for no limit)
     */
    function addService(
        string calldata service,
        uint256 cost,
        uint256 dailyLimit
    ) external onlyRole(MAINTAINER_ROLE) {
        require(cost > 0, "Cost must be > 0");
        require(serviceCosts[service] == 0, "Service already exists");
        
        serviceCosts[service] = cost;
        if (dailyLimit > 0) {
            dailySpendingLimits[service] = dailyLimit;
        }
        
        emit ServiceCostUpdated(service, 0, cost);
        if (dailyLimit > 0) {
            emit SpendingLimitUpdated(service, 0, dailyLimit);
        }
    }
    
    /**
     * @dev Remove a service
     * @param service Service identifier
     */
    function removeService(string calldata service) external onlyRole(MAINTAINER_ROLE) {
        require(serviceCosts[service] > 0, "Service does not exist");
        
        uint256 oldCost = serviceCosts[service];
        uint256 oldLimit = dailySpendingLimits[service];
        
        delete serviceCosts[service];
        delete dailySpendingLimits[service];
        
        emit ServiceCostUpdated(service, oldCost, 0);
        if (oldLimit > 0) {
            emit SpendingLimitUpdated(service, oldLimit, 0);
        }
    }
    
    /**
     * @dev Emergency functions
     */
    function pause() external onlyRole(MAINTAINER_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(MAINTAINER_ROLE) {
        _unpause();
    }
    
    // =============================================================================
    // NON-TRANSFERABLE ENFORCEMENT
    // =============================================================================
    
    /**
     * @dev These functions are intentionally not implemented to prevent transfers
     * Credits are bound to the earning address and cannot be transferred
     */
    
    // function transfer(address to, uint256 amount) external pure returns (bool) {
    //     revert("Credits are non-transferable");
    // }
    
    // function transferFrom(address from, address to, uint256 amount) external pure returns (bool) {
    //     revert("Credits are non-transferable");
    // }
    
    // function approve(address spender, uint256 amount) external pure returns (bool) {
    //     revert("Credits are non-transferable");
    // }
}