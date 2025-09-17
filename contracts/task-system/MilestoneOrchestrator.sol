// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

interface ITaskRegistry {
    enum TaskStatus { Open, Claimed, Submitted, Approved, Paid, Disputed }
    
    function getTask(string calldata taskId) external view returns (
        bytes32 taskSheetCID,
        address bountyToken,
        uint256 bountyAmount,
        TaskStatus status,
        address claimer,
        address payoutVault,
        uint256 claimDeadline,
        uint256 submitDeadline,
        bytes32 evidenceCID,
        bytes32 verifierReportCID,
        uint256 createdAt,
        uint256 claimedAt,
        uint256 submittedAt,
        uint256 approvedAt
    );
}

/**
 * @title MilestoneOrchestrator
 * @dev Manages milestone dependencies and unlocks new task waves
 * @notice Coordinates task completion to enable systematic progression
 */
contract MilestoneOrchestrator is AccessControl, Pausable {
    bytes32 public constant MAINTAINER_ROLE = keccak256("MAINTAINER_ROLE");
    
    struct Milestone {
        string name;                    // Human readable name
        string description;             // Description of milestone goals
        string[] requiredTasks;         // Tasks that must be completed
        string[] unlockedTasks;         // Tasks unlocked when milestone completes
        bool isActive;                  // Can tasks be claimed?
        bool isCompleted;               // All required tasks completed?
        uint256 createdAt;              // Creation timestamp
        uint256 completedAt;            // Completion timestamp
        bytes32 manifestCID;            // IPFS CID of release manifest
    }
    
    // milestoneId => Milestone
    mapping(uint256 => Milestone) public milestones;
    
    // Track milestone count
    uint256 public milestoneCount;
    
    // Task Registry reference
    ITaskRegistry public taskRegistry;
    
    // Track which milestone each task belongs to
    mapping(string => uint256) public taskToMilestone;
    
    // Track active milestones
    mapping(uint256 => bool) public activeMilestones;
    
    // Events
    event MilestoneCreated(
        uint256 indexed milestoneId,
        string name,
        string[] requiredTasks,
        string[] unlockedTasks
    );
    
    event MilestoneActivated(
        uint256 indexed milestoneId,
        string name,
        uint256 activatedAt
    );
    
    event MilestoneCompleted(
        uint256 indexed milestoneId,
        string name,
        uint256 completedAt,
        bytes32 manifestCID
    );
    
    event TasksUnlocked(
        uint256 indexed milestoneId,
        string[] unlockedTasks,
        uint256 unlockedAt
    );
    
    constructor(address _taskRegistry) {
        require(_taskRegistry != address(0), "Invalid task registry");
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MAINTAINER_ROLE, msg.sender);
        
        taskRegistry = ITaskRegistry(_taskRegistry);
    }
    
    /**
     * @dev Create a new milestone
     * @param name Human readable milestone name
     * @param description Milestone description
     * @param requiredTasks Tasks that must complete for this milestone
     * @param unlockedTasks Tasks that get unlocked when this completes
     */
    function createMilestone(
        string calldata name,
        string calldata description,
        string[] calldata requiredTasks,
        string[] calldata unlockedTasks
    ) external onlyRole(MAINTAINER_ROLE) whenNotPaused {
        require(bytes(name).length > 0, "Name cannot be empty");
        require(requiredTasks.length > 0, "Must have required tasks");
        
        uint256 milestoneId = milestoneCount++;
        
        milestones[milestoneId] = Milestone({
            name: name,
            description: description,
            requiredTasks: requiredTasks,
            unlockedTasks: unlockedTasks,
            isActive: false,
            isCompleted: false,
            createdAt: block.timestamp,
            completedAt: 0,
            manifestCID: bytes32(0)
        });
        
        // Map tasks to this milestone
        for (uint i = 0; i < requiredTasks.length; i++) {
            taskToMilestone[requiredTasks[i]] = milestoneId;
        }
        
        emit MilestoneCreated(milestoneId, name, requiredTasks, unlockedTasks);
    }
    
    /**
     * @dev Activate a milestone (allows tasks to be claimed)
     * @param milestoneId The milestone to activate
     */
    function activateMilestone(uint256 milestoneId) 
        external 
        onlyRole(MAINTAINER_ROLE) 
        whenNotPaused 
    {
        require(milestoneId < milestoneCount, "Milestone does not exist");
        require(!milestones[milestoneId].isActive, "Already active");
        require(!milestones[milestoneId].isCompleted, "Already completed");
        
        milestones[milestoneId].isActive = true;
        activeMilestones[milestoneId] = true;
        
        emit MilestoneActivated(
            milestoneId, 
            milestones[milestoneId].name, 
            block.timestamp
        );
    }
    
    /**
     * @dev Check if milestone is complete and unlock next tasks
     * @param milestoneId The milestone to check
     */
    function checkAndCompleteMilestone(uint256 milestoneId) 
        external 
        whenNotPaused 
    {
        require(milestoneId < milestoneCount, "Milestone does not exist");
        require(milestones[milestoneId].isActive, "Milestone not active");
        require(!milestones[milestoneId].isCompleted, "Already completed");
        
        Milestone storage milestone = milestones[milestoneId];
        
        // Check if all required tasks are completed
        bool allCompleted = true;
        for (uint i = 0; i < milestone.requiredTasks.length; i++) {
            try taskRegistry.getTask(milestone.requiredTasks[i]) returns (
                bytes32, address, uint256, ITaskRegistry.TaskStatus status,
                address, address, uint256, uint256, bytes32, bytes32,
                uint256, uint256, uint256, uint256
            ) {
                if (status != ITaskRegistry.TaskStatus.Paid) {
                    allCompleted = false;
                    break;
                }
            } catch {
                allCompleted = false;
                break;
            }
        }
        
        require(allCompleted, "Not all required tasks completed");
        
        // Complete milestone
        milestone.isCompleted = true;
        milestone.completedAt = block.timestamp;
        activeMilestones[milestoneId] = false;
        
        emit MilestoneCompleted(
            milestoneId,
            milestone.name,
            block.timestamp,
            milestone.manifestCID
        );
        
        // Unlock next tasks if any
        if (milestone.unlockedTasks.length > 0) {
            emit TasksUnlocked(
                milestoneId,
                milestone.unlockedTasks,
                block.timestamp
            );
        }
    }
    
    /**
     * @dev Set release manifest for completed milestone
     * @param milestoneId The milestone ID
     * @param manifestCID IPFS CID of release manifest
     */
    function setMilestoneManifest(
        uint256 milestoneId,
        bytes32 manifestCID
    ) external onlyRole(MAINTAINER_ROLE) {
        require(milestoneId < milestoneCount, "Milestone does not exist");
        require(milestones[milestoneId].isCompleted, "Milestone not completed");
        require(manifestCID != bytes32(0), "Invalid manifest CID");
        
        milestones[milestoneId].manifestCID = manifestCID;
    }
    
    /**
     * @dev Get milestone details
     */
    function getMilestone(uint256 milestoneId) 
        external 
        view 
        returns (
            string memory name,
            string memory description,
            string[] memory requiredTasks,
            string[] memory unlockedTasks,
            bool isActive,
            bool isCompleted,
            uint256 createdAt,
            uint256 completedAt,
            bytes32 manifestCID
        ) 
    {
        require(milestoneId < milestoneCount, "Milestone does not exist");
        
        Milestone storage milestone = milestones[milestoneId];
        return (
            milestone.name,
            milestone.description,
            milestone.requiredTasks,
            milestone.unlockedTasks,
            milestone.isActive,
            milestone.isCompleted,
            milestone.createdAt,
            milestone.completedAt,
            milestone.manifestCID
        );
    }
    
    /**
     * @dev Get milestone progress
     * @param milestoneId The milestone ID
     * @return completedTasks Number of completed tasks
     * @return totalTasks Total number of required tasks
     * @return completionPercentage Percentage complete (0-100)
     */
    function getMilestoneProgress(uint256 milestoneId) 
        external 
        view 
        returns (
            uint256 completedTasks,
            uint256 totalTasks,
            uint256 completionPercentage
        ) 
    {
        require(milestoneId < milestoneCount, "Milestone does not exist");
        
        Milestone storage milestone = milestones[milestoneId];
        totalTasks = milestone.requiredTasks.length;
        completedTasks = 0;
        
        for (uint i = 0; i < totalTasks; i++) {
            try taskRegistry.getTask(milestone.requiredTasks[i]) returns (
                bytes32, address, uint256, ITaskRegistry.TaskStatus status,
                address, address, uint256, uint256, bytes32, bytes32,
                uint256, uint256, uint256, uint256
            ) {
                if (status == ITaskRegistry.TaskStatus.Paid) {
                    completedTasks++;
                }
            } catch {
                // Task doesn't exist, don't count it
            }
        }
        
        completionPercentage = totalTasks > 0 ? (completedTasks * 100) / totalTasks : 0;
    }
    
    /**
     * @dev Check if a task can be claimed (milestone is active)
     * @param taskId The task ID to check
     * @return True if task can be claimed
     */
    function canClaimTask(string calldata taskId) external view returns (bool) {
        uint256 milestoneId = taskToMilestone[taskId];
        return activeMilestones[milestoneId];
    }
    
    /**
     * @dev Get all active milestones
     * @return activeIds Array of active milestone IDs
     */
    function getActiveMilestones() external view returns (uint256[] memory) {
        uint256[] memory activeIds = new uint256[](milestoneCount);
        uint256 activeCount = 0;
        
        for (uint256 i = 0; i < milestoneCount; i++) {
            if (activeMilestones[i]) {
                activeIds[activeCount] = i;
                activeCount++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](activeCount);
        for (uint256 i = 0; i < activeCount; i++) {
            result[i] = activeIds[i];
        }
        
        return result;
    }
    
    /**
     * @dev Update task registry address
     * @param newRegistry New task registry address
     */
    function updateTaskRegistry(address newRegistry) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        require(newRegistry != address(0), "Invalid registry address");
        taskRegistry = ITaskRegistry(newRegistry);
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