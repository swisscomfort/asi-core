// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "./CreditLedger.sol";
import "./ReputationSBT.sol";

/**
 * @title TicketRegistry
 * @dev Core contract for Oryn decentralized ticket system
 * @notice Manages ticket lifecycle: open → claimed → submitted → approved → rewarded
 * @dev Based on ASI TaskRegistry but adapted for Oryn's credit-based system
 */
contract TicketRegistry is ReentrancyGuard, AccessControl, Pausable {
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");
    bytes32 public constant MAINTAINER_ROLE = keccak256("MAINTAINER_ROLE");
    bytes32 public constant TICKET_CREATOR_ROLE = keccak256("TICKET_CREATOR_ROLE");
    
    enum TicketState { Open, Claimed, Submitted, Approved, Rewarded, Disputed, Expired }
    
    struct Ticket {
        bytes32 ticketSheetCID;      // IPFS hash of YAML ticket definition
        string title;                // Human-readable ticket title
        string category;             // e.g., "security", "ui", "docs", "translation"
        uint8 difficulty;            // 1-5 difficulty scale
        uint256 creditReward;        // Non-tradeable credits to award
        uint8 reputationWeight;      // 1-10 reputation impact
        TicketState state;           // Current ticket state
        address claimedBy;           // Who claimed the ticket
        uint256 claimDeadline;       // When claim expires (auto-reopen)
        uint256 submitDeadline;      // When submission is due
        bytes32 evidenceCID;         // IPFS hash of submission evidence
        bytes32 verifierReportCID;   // IPFS hash of verifier report
        uint256 createdAt;           // Creation timestamp
        uint256 claimedAt;           // Claim timestamp
        uint256 submittedAt;         // Submission timestamp
        uint256 approvedAt;          // Approval timestamp
        address approvedBy;          // Verifier who approved
        
        // Oryn-specific fields
        string[] skillTags;          // Required skills for this ticket
        bool requiresOneHuman;       // Requires One-Human attestation
        uint256 estimatedHours;      // Estimated work hours (for fair rewards)
    }
    
    // ticketId => Ticket
    mapping(bytes32 => Ticket) public tickets;
    
    // Track ticket IDs for enumeration and filtering
    bytes32[] public ticketIds;
    mapping(bytes32 => uint256) public ticketIdToIndex;
    
    // Category and difficulty filtering
    mapping(string => bytes32[]) public ticketsByCategory;
    mapping(uint8 => bytes32[]) public ticketsByDifficulty;
    mapping(address => bytes32[]) public ticketsByUser;
    
    // User statistics for reputation calculation
    mapping(address => uint256) public userCompletedTickets;
    mapping(address => uint256) public userClaimedTickets;
    mapping(address => uint256) public userTotalCreditsEarned;
    mapping(address => uint256) public userTotalReputationEarned;
    mapping(address => uint256) public userLastActivityTimestamp;
    
    // Configuration
    uint256 public defaultClaimTimeout = 7 days;    // Shorter than tasks
    uint256 public defaultSubmitTimeout = 14 days;  // Community-friendly
    uint256 public disputeTimeout = 3 days;         // Quick dispute resolution
    
    // External contracts
    CreditLedger public creditLedger;
    ReputationSBT public reputationSBT;
    
    // Events
    event TicketCreated(
        bytes32 indexed ticketId,
        string title,
        string category,
        uint8 difficulty,
        uint256 creditReward,
        bytes32 ticketSheetCID
    );
    
    event TicketClaimed(
        bytes32 indexed ticketId,
        address indexed claimer,
        uint256 claimDeadline,
        uint256 submitDeadline
    );
    
    event TicketSubmitted(
        bytes32 indexed ticketId,
        address indexed claimer,
        bytes32 evidenceCID,
        uint256 submittedAt
    );
    
    event TicketApproved(
        bytes32 indexed ticketId,
        address indexed verifier,
        address indexed contributor,
        bytes32 verifierReportCID,
        uint256 creditReward,
        uint8 reputationGained
    );
    
    event TicketRewarded(
        bytes32 indexed ticketId,
        address indexed recipient,
        uint256 credits,
        uint8 reputation
    );
    
    event TicketDisputed(
        bytes32 indexed ticketId,
        address indexed disputer,
        string reason
    );
    
    event TicketReopened(
        bytes32 indexed ticketId,
        string reason
    );
    
    event TicketExpired(
        bytes32 indexed ticketId,
        address indexed previousClaimer
    );
    
    constructor(
        address _creditLedger,
        address _reputationSBT
    ) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MAINTAINER_ROLE, msg.sender);
        _grantRole(VERIFIER_ROLE, msg.sender);
        _grantRole(TICKET_CREATOR_ROLE, msg.sender);
        
        creditLedger = CreditLedger(_creditLedger);
        reputationSBT = ReputationSBT(_reputationSBT);
    }
    
    /**
     * @dev Create a new ticket (can be called by authorized ticket creators)
     * @param ticketId Unique identifier for the ticket
     * @param title Human-readable ticket title
     * @param category Ticket category (e.g., "security", "ui", "docs")
     * @param difficulty Difficulty scale 1-5
     * @param creditReward Credits to award on completion
     * @param reputationWeight Reputation impact 1-10
     * @param ticketSheetCID IPFS CID of the ticket YAML definition
     * @param skillTags Required skills for this ticket
     * @param estimatedHours Estimated work hours
     * @param requiresOneHuman Whether One-Human attestation is required
     */
    function createTicket(
        string calldata ticketId,
        string calldata title,
        string calldata category,
        uint8 difficulty,
        uint256 creditReward,
        uint8 reputationWeight,
        bytes32 ticketSheetCID,
        string[] calldata skillTags,
        uint256 estimatedHours,
        bool requiresOneHuman
    ) external onlyRole(TICKET_CREATOR_ROLE) whenNotPaused {
        bytes32 id = keccak256(abi.encodePacked(ticketId));
        
        require(tickets[id].createdAt == 0, "Ticket already exists");
        require(bytes(title).length > 0, "Title cannot be empty");
        require(bytes(category).length > 0, "Category cannot be empty");
        require(difficulty >= 1 && difficulty <= 5, "Difficulty must be 1-5");
        require(creditReward > 0, "Credit reward must be > 0");
        require(reputationWeight >= 1 && reputationWeight <= 10, "Reputation weight must be 1-10");
        require(ticketSheetCID != bytes32(0), "Invalid ticket sheet CID");
        require(estimatedHours > 0, "Estimated hours must be > 0");
        
        tickets[id] = Ticket({
            ticketSheetCID: ticketSheetCID,
            title: title,
            category: category,
            difficulty: difficulty,
            creditReward: creditReward,
            reputationWeight: reputationWeight,
            state: TicketState.Open,
            claimedBy: address(0),
            claimDeadline: 0,
            submitDeadline: 0,
            evidenceCID: bytes32(0),
            verifierReportCID: bytes32(0),
            createdAt: block.timestamp,
            claimedAt: 0,
            submittedAt: 0,
            approvedAt: 0,
            approvedBy: address(0),
            skillTags: skillTags,
            requiresOneHuman: requiresOneHuman,
            estimatedHours: estimatedHours
        });
        
        // Add to enumeration and category indexing
        ticketIdToIndex[id] = ticketIds.length;
        ticketIds.push(id);
        ticketsByCategory[category].push(id);
        ticketsByDifficulty[difficulty].push(id);
        
        emit TicketCreated(
            id,
            title,
            category,
            difficulty,
            creditReward,
            ticketSheetCID
        );
    }
    
    /**
     * @dev Claim a ticket for work
     * @param ticketId ID of the ticket to claim
     */
    function claimTicket(bytes32 ticketId) external whenNotPaused nonReentrant {
        Ticket storage ticket = tickets[ticketId];
        
        require(ticket.createdAt > 0, "Ticket does not exist");
        require(ticket.state == TicketState.Open, "Ticket not available");
        require(ticket.claimedBy == address(0), "Ticket already claimed");
        
        // Check One-Human requirement if needed
        if (ticket.requiresOneHuman) {
            require(reputationSBT.hasOneHumanAttestation(msg.sender), "One-Human attestation required");
        }
        
        // Update ticket state
        ticket.state = TicketState.Claimed;
        ticket.claimedBy = msg.sender;
        ticket.claimedAt = block.timestamp;
        ticket.claimDeadline = block.timestamp + defaultClaimTimeout;
        ticket.submitDeadline = block.timestamp + defaultSubmitTimeout;
        
        // Update user statistics
        userClaimedTickets[msg.sender]++;
        userLastActivityTimestamp[msg.sender] = block.timestamp;
        ticketsByUser[msg.sender].push(ticketId);
        
        emit TicketClaimed(
            ticketId,
            msg.sender,
            ticket.claimDeadline,
            ticket.submitDeadline
        );
    }
    
    /**
     * @dev Submit evidence for a claimed ticket
     * @param ticketId ID of the ticket
     * @param evidenceCID IPFS CID of the submission evidence
     */
    function submitTicket(
        bytes32 ticketId,
        bytes32 evidenceCID
    ) external whenNotPaused nonReentrant {
        Ticket storage ticket = tickets[ticketId];
        
        require(ticket.createdAt > 0, "Ticket does not exist");
        require(ticket.state == TicketState.Claimed, "Ticket not claimed");
        require(ticket.claimedBy == msg.sender, "Not the claimer");
        require(block.timestamp <= ticket.submitDeadline, "Submission deadline passed");
        require(evidenceCID != bytes32(0), "Invalid evidence CID");
        
        // Update ticket state
        ticket.state = TicketState.Submitted;
        ticket.evidenceCID = evidenceCID;
        ticket.submittedAt = block.timestamp;
        
        // Update user activity
        userLastActivityTimestamp[msg.sender] = block.timestamp;
        
        emit TicketSubmitted(
            ticketId,
            msg.sender,
            evidenceCID,
            block.timestamp
        );
    }
    
    /**
     * @dev Approve a submitted ticket (called by verifier service)
     * @param ticketId ID of the ticket
     * @param verifierReportCID IPFS CID of the verifier report
     */
    function approveTicket(
        bytes32 ticketId,
        bytes32 verifierReportCID
    ) external onlyRole(VERIFIER_ROLE) whenNotPaused nonReentrant {
        Ticket storage ticket = tickets[ticketId];
        
        require(ticket.createdAt > 0, "Ticket does not exist");
        require(ticket.state == TicketState.Submitted, "Ticket not submitted");
        require(verifierReportCID != bytes32(0), "Invalid verifier report CID");
        
        // Update ticket state
        ticket.state = TicketState.Approved;
        ticket.verifierReportCID = verifierReportCID;
        ticket.approvedAt = block.timestamp;
        ticket.approvedBy = msg.sender;
        
        emit TicketApproved(
            ticketId,
            msg.sender,
            ticket.claimedBy,
            verifierReportCID,
            ticket.creditReward,
            ticket.reputationWeight
        );
        
        // Automatically reward the contributor
        _rewardContributor(ticketId);
    }
    
    /**
     * @dev Internal function to reward the contributor
     * @param ticketId ID of the approved ticket
     */
    function _rewardContributor(bytes32 ticketId) internal {
        Ticket storage ticket = tickets[ticketId];
        address contributor = ticket.claimedBy;
        
        require(ticket.state == TicketState.Approved, "Ticket not approved");
        require(contributor != address(0), "No contributor");
        
        // Update ticket state
        ticket.state = TicketState.Rewarded;
        
        // Award credits
        creditLedger.mintCredits(contributor, ticket.creditReward);
        
        // Award reputation
        reputationSBT.addReputation(
            contributor,
            ticket.reputationWeight,
            ticket.category,
            ticket.difficulty
        );
        
        // Update user statistics
        userCompletedTickets[contributor]++;
        userTotalCreditsEarned[contributor] += ticket.creditReward;
        userTotalReputationEarned[contributor] += ticket.reputationWeight;
        userLastActivityTimestamp[contributor] = block.timestamp;
        
        emit TicketRewarded(
            ticketId,
            contributor,
            ticket.creditReward,
            ticket.reputationWeight
        );
    }
    
    /**
     * @dev Reopen an expired ticket
     * @param ticketId ID of the ticket to reopen
     */
    function reopenExpiredTicket(bytes32 ticketId) external whenNotPaused {
        Ticket storage ticket = tickets[ticketId];
        
        require(ticket.createdAt > 0, "Ticket does not exist");
        require(ticket.state == TicketState.Claimed, "Ticket not claimed");
        require(block.timestamp > ticket.claimDeadline, "Claim not expired");
        
        // Reset ticket state
        ticket.state = TicketState.Open;
        ticket.claimedBy = address(0);
        ticket.claimDeadline = 0;
        ticket.submitDeadline = 0;
        ticket.claimedAt = 0;
        
        emit TicketExpired(ticketId, ticket.claimedBy);
        emit TicketReopened(ticketId, "Claim expired");
    }
    
    /**
     * @dev Get tickets by category
     * @param category Category to filter by
     * @return Array of ticket IDs in the category
     */
    function getTicketsByCategory(string calldata category) external view returns (bytes32[] memory) {
        return ticketsByCategory[category];
    }
    
    /**
     * @dev Get tickets by difficulty
     * @param difficulty Difficulty level to filter by
     * @return Array of ticket IDs with the difficulty
     */
    function getTicketsByDifficulty(uint8 difficulty) external view returns (bytes32[] memory) {
        return ticketsByDifficulty[difficulty];
    }
    
    /**
     * @dev Get tickets by user
     * @param user User address to filter by
     * @return Array of ticket IDs claimed by the user
     */
    function getTicketsByUser(address user) external view returns (bytes32[] memory) {
        return ticketsByUser[user];
    }
    
    /**
     * @dev Get all ticket IDs
     * @return Array of all ticket IDs
     */
    function getAllTicketIds() external view returns (bytes32[] memory) {
        return ticketIds;
    }
    
    /**
     * @dev Get ticket count
     * @return Total number of tickets
     */
    function getTicketCount() external view returns (uint256) {
        return ticketIds.length;
    }
    
    /**
     * @dev Get user statistics
     * @param user User address
     * @return completed Number of completed tickets
     * @return claimed Number of claimed tickets  
     * @return totalCredits Total credits earned
     * @return totalReputation Total reputation earned
     * @return lastActivity Last activity timestamp
     */
    function getUserStats(address user) external view returns (
        uint256 completed,
        uint256 claimed,
        uint256 totalCredits,
        uint256 totalReputation,
        uint256 lastActivity
    ) {
        return (
            userCompletedTickets[user],
            userClaimedTickets[user],
            userTotalCreditsEarned[user],
            userTotalReputationEarned[user],
            userLastActivityTimestamp[user]
        );
    }
    
    /**
     * @dev Emergency functions for maintainers
     */
    function setClaimTimeout(uint256 _timeout) external onlyRole(MAINTAINER_ROLE) {
        defaultClaimTimeout = _timeout;
    }
    
    function setSubmitTimeout(uint256 _timeout) external onlyRole(MAINTAINER_ROLE) {
        defaultSubmitTimeout = _timeout;
    }
    
    function setDisputeTimeout(uint256 _timeout) external onlyRole(MAINTAINER_ROLE) {
        disputeTimeout = _timeout;
    }
    
    function pause() external onlyRole(MAINTAINER_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(MAINTAINER_ROLE) {
        _unpause();
    }
}