// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TaskRegistry
 * @dev Core contract for ASI Core distributed task system
 * @notice Manages task lifecycle: create → claim → submit → approve → payout
 */
contract TaskRegistry is ReentrancyGuard, AccessControl, Pausable {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant MAINTAINER_ROLE = keccak256("MAINTAINER_ROLE");
    
    enum TaskStatus { Open, Claimed, Submitted, Approved, Paid, Disputed }
    
    struct Task {
        bytes32 taskSheetCID;        // IPFS hash of YAML task sheet
        address bountyToken;         // ERC20 token for payment
        uint256 bountyAmount;        // Amount to pay on completion
        TaskStatus status;           // Current task status
        address claimer;             // Who claimed the task
        address payoutVault;         // Contract that holds the funds
        uint256 claimDeadline;       // When claim expires
        uint256 submitDeadline;      // When submission is due
        bytes32 evidenceCID;         // IPFS hash of submission evidence
        bytes32 verifierReportCID;   // IPFS hash of verifier report
        uint256 createdAt;           // Creation timestamp
        uint256 claimedAt;           // Claim timestamp
        uint256 submittedAt;         // Submission timestamp
        uint256 approvedAt;          // Approval timestamp
    }
    
    // taskId => Task
    mapping(bytes32 => Task) public tasks;
    
    // Track task IDs for enumeration
    bytes32[] public taskIds;
    mapping(bytes32 => uint256) public taskIdToIndex;
    
    // User statistics
    mapping(address => uint256) public userCompletedTasks;
    mapping(address => uint256) public userClaimedTasks;
    mapping(address => uint256) public userTotalEarnings;
    
    // Configuration
    uint256 public defaultClaimTimeout = 14 days;
    uint256 public defaultSubmitTimeout = 30 days;
    uint256 public minimumClaimCollateral = 0; // Wei amount
    
    // Events
    event TaskCreated(
        bytes32 indexed taskId,
        bytes32 taskSheetCID,
        address bountyToken,
        uint256 bountyAmount,
        address payoutVault
    );
    
    event TaskClaimed(
        bytes32 indexed taskId,
        address indexed claimer,
        uint256 claimDeadline,
        uint256 submitDeadline
    );
    
    event TaskSubmitted(
        bytes32 indexed taskId,
        address indexed claimer,
        bytes32 evidenceCID,
        uint256 submittedAt
    );
    
    event TaskApproved(
        bytes32 indexed taskId,
        address indexed verifier,
        bytes32 verifierReportCID,
        uint256 approvedAt
    );
    
    event TaskPaid(
        bytes32 indexed taskId,
        address indexed recipient,
        address token,
        uint256 amount
    );
    
    event TaskDisputed(
        bytes32 indexed taskId,
        address indexed disputer,
        string reason
    );
    
    event TaskReopened(
        bytes32 indexed taskId,
        string reason
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MAINTAINER_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
    }
    
    /**
     * @dev Create a new task
     * @param taskId Unique identifier for the task
     * @param taskSheetCID IPFS CID of the task YAML sheet
     * @param bountyToken ERC20 token address for payment
     * @param bountyAmount Amount to pay on completion
     * @param payoutVault Contract address that will handle payouts
     */
    function createTask(
        string calldata taskId,
        bytes32 taskSheetCID,
        address bountyToken,
        uint256 bountyAmount,
        address payoutVault
    ) external onlyRole(MAINTAINER_ROLE) whenNotPaused {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        
        require(tasks[id].createdAt == 0, "Task already exists");
        require(taskSheetCID != bytes32(0), "Invalid task sheet CID");
        require(bountyToken != address(0), "Invalid token address");
        require(bountyAmount > 0, "Bounty must be > 0");
        require(payoutVault != address(0), "Invalid vault address");
        
        tasks[id] = Task({
            taskSheetCID: taskSheetCID,
            bountyToken: bountyToken,
            bountyAmount: bountyAmount,
            status: TaskStatus.Open,
            claimer: address(0),
            payoutVault: payoutVault,
            claimDeadline: 0,
            submitDeadline: 0,
            evidenceCID: bytes32(0),
            verifierReportCID: bytes32(0),
            createdAt: block.timestamp,
            claimedAt: 0,
            submittedAt: 0,
            approvedAt: 0
        });
        
        // Add to enumeration
        taskIdToIndex[id] = taskIds.length;
        taskIds.push(id);
        
        emit TaskCreated(id, taskSheetCID, bountyToken, bountyAmount, payoutVault);
    }
    
    /**
     * @dev Claim a task for completion
     * @param taskId The task to claim
     */
    function claimTask(string calldata taskId) 
        external 
        payable 
        whenNotPaused 
        nonReentrant 
    {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.createdAt > 0, "Task does not exist");
        require(task.status == TaskStatus.Open, "Task not available");
        require(msg.value >= minimumClaimCollateral, "Insufficient collateral");
        
        task.status = TaskStatus.Claimed;
        task.claimer = msg.sender;
        task.claimedAt = block.timestamp;
        task.claimDeadline = block.timestamp + defaultClaimTimeout;
        task.submitDeadline = block.timestamp + defaultSubmitTimeout;
        
        userClaimedTasks[msg.sender]++;
        
        emit TaskClaimed(id, msg.sender, task.claimDeadline, task.submitDeadline);
    }
    
    /**
     * @dev Submit evidence for a claimed task
     * @param taskId The task ID
     * @param evidenceCID IPFS CID of submission evidence
     */
    function submitTask(
        string calldata taskId,
        bytes32 evidenceCID
    ) external whenNotPaused {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.claimer == msg.sender, "Not the claimer");
        require(task.status == TaskStatus.Claimed, "Task not in claimed state");
        require(block.timestamp <= task.submitDeadline, "Submission deadline passed");
        require(evidenceCID != bytes32(0), "Invalid evidence CID");
        
        task.status = TaskStatus.Submitted;
        task.evidenceCID = evidenceCID;
        task.submittedAt = block.timestamp;
        
        // Return collateral
        if (minimumClaimCollateral > 0) {
            (bool success, ) = payable(msg.sender).call{value: minimumClaimCollateral}("");
            require(success, "Collateral return failed");
        }
        
        emit TaskSubmitted(id, msg.sender, evidenceCID, block.timestamp);
    }
    
    /**
     * @dev Approve a submitted task (verifier only)
     * @param taskId The task ID
     * @param verifierReportCID IPFS CID of verification report
     */
    function approveTask(
        string calldata taskId,
        bytes32 verifierReportCID
    ) external onlyRole(VERIFIER_ROLE) whenNotPaused {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.status == TaskStatus.Submitted, "Task not submitted");
        require(verifierReportCID != bytes32(0), "Invalid report CID");
        
        task.status = TaskStatus.Approved;
        task.verifierReportCID = verifierReportCID;
        task.approvedAt = block.timestamp;
        
        emit TaskApproved(id, msg.sender, verifierReportCID, block.timestamp);
    }
    
    /**
     * @dev Process payout for approved task
     * @param taskId The task ID
     */
    function payout(string calldata taskId) 
        external 
        whenNotPaused 
        nonReentrant 
    {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.status == TaskStatus.Approved, "Task not approved");
        require(task.claimer != address(0), "No claimer");
        
        task.status = TaskStatus.Paid;
        
        // Update statistics
        userCompletedTasks[task.claimer]++;
        userTotalEarnings[task.claimer] += task.bountyAmount;
        
        // Call vault for payout
        (bool success, ) = task.payoutVault.call(
            abi.encodeWithSignature(
                "payout(address,address,uint256)",
                task.bountyToken,
                task.claimer,
                task.bountyAmount
            )
        );
        require(success, "Payout failed");
        
        emit TaskPaid(id, task.claimer, task.bountyToken, task.bountyAmount);
    }
    
    /**
     * @dev Dispute a task decision
     * @param taskId The task ID
     * @param reason Dispute reason
     */
    function disputeTask(
        string calldata taskId,
        string calldata reason
    ) external whenNotPaused {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(
            task.claimer == msg.sender || hasRole(VERIFIER_ROLE, msg.sender),
            "Not authorized to dispute"
        );
        require(
            task.status == TaskStatus.Submitted || task.status == TaskStatus.Approved,
            "Cannot dispute in current state"
        );
        
        task.status = TaskStatus.Disputed;
        
        emit TaskDisputed(id, msg.sender, reason);
    }
    
    /**
     * @dev Reopen a task (admin only)
     * @param taskId The task ID
     * @param reason Reason for reopening
     */
    function reopenTask(
        string calldata taskId,
        string calldata reason
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.createdAt > 0, "Task does not exist");
        
        // Reset task to open state
        task.status = TaskStatus.Open;
        task.claimer = address(0);
        task.claimDeadline = 0;
        task.submitDeadline = 0;
        task.evidenceCID = bytes32(0);
        task.verifierReportCID = bytes32(0);
        task.claimedAt = 0;
        task.submittedAt = 0;
        task.approvedAt = 0;
        
        emit TaskReopened(id, reason);
    }
    
    /**
     * @dev Get task by string ID
     */
    function getTask(string calldata taskId) 
        external 
        view 
        returns (Task memory) 
    {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        return tasks[id];
    }
    
    /**
     * @dev Get total number of tasks
     */
    function getTotalTasks() external view returns (uint256) {
        return taskIds.length;
    }
    
    /**
     * @dev Get task ID by index
     */
    function getTaskIdByIndex(uint256 index) external view returns (bytes32) {
        require(index < taskIds.length, "Index out of bounds");
        return taskIds[index];
    }
    
    /**
     * @dev Cleanup expired claims
     * @param taskId The task ID to check
     */
    function cleanupExpiredClaim(string calldata taskId) external {
        bytes32 id = keccak256(abi.encodePacked(taskId));
        Task storage task = tasks[id];
        
        require(task.status == TaskStatus.Claimed, "Task not claimed");
        require(block.timestamp > task.claimDeadline, "Claim not expired");
        
        // Reset to open
        task.status = TaskStatus.Open;
        task.claimer = address(0);
        task.claimDeadline = 0;
        task.submitDeadline = 0;
        task.claimedAt = 0;
        
        // Keep collateral as penalty
        
        emit TaskReopened(id, "Claim timeout");
    }
    
    /**
     * @dev Update configuration (admin only)
     */
    function updateConfig(
        uint256 _claimTimeout,
        uint256 _submitTimeout,
        uint256 _minCollateral
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        defaultClaimTimeout = _claimTimeout;
        defaultSubmitTimeout = _submitTimeout;
        minimumClaimCollateral = _minCollateral;
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
}