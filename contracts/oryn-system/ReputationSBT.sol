// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ReputationSBT
 * @dev Soulbound Token (SBT) implementation for Oryn reputation system
 * @notice Non-transferable reputation tokens that track user contributions and expertise
 * @dev Implements reputation decay, One-Human attestation, and category-based reputation
 */
contract ReputationSBT is AccessControl, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    bytes32 public constant REPUTATION_MINTER_ROLE = keccak256("REPUTATION_MINTER_ROLE");
    bytes32 public constant ATTESTOR_ROLE = keccak256("ATTESTOR_ROLE");
    bytes32 public constant MAINTAINER_ROLE = keccak256("MAINTAINER_ROLE");
    
    Counters.Counter private _tokenIds;
    
    // Core reputation structure
    struct ReputationProfile {
        uint256 totalReputation;        // Total reputation points earned
        uint256 lastActivityTimestamp;  // Last time reputation was earned
        uint256 decayStartTimestamp;    // When decay calculation starts
        mapping(string => uint256) categoryReputation; // Reputation by category
        mapping(string => uint256) categoryLastActivity; // Last activity per category
        bool hasOneHumanAttestation;   // One-Human verification status
        uint256 oneHumanTimestamp;     // When One-Human was verified
        address attestedBy;            // Who provided One-Human attestation
        string[] categories;           // List of categories user has reputation in
    }
    
    // Reputation breakdown by contribution type
    struct ContributionStats {
        uint256 ticketsCompleted;      // Number of tickets completed
        uint256 securityContributions; // Security-related contributions
        uint256 uiContributions;      // UI/UX contributions
        uint256 docsContributions;    // Documentation contributions
        uint256 translationContributions; // Translation contributions
        uint256 mentorshipActions;    // Mentoring other contributors
        uint256 qualityScore;         // Average quality of contributions (0-100)
        uint256 averageDifficulty;    // Average difficulty of completed tickets
    }
    
    // Maps address to reputation profile
    mapping(address => ReputationProfile) private _profiles;
    mapping(address => ContributionStats) public contributionStats;
    
    // Reputation decay configuration
    uint256 public constant DECAY_START_PERIOD = 180 days; // 6 months
    uint256 public constant FULL_DECAY_PERIOD = 365 days;  // 1 year for full decay
    uint256 public constant MIN_REPUTATION_RETAINED = 10;  // Minimum % retained after full decay
    
    // One-Human attestation configuration
    mapping(address => bool) public authorizedAttestors;
    uint256 public constant ONE_HUMAN_VALIDITY_PERIOD = 365 days; // 1 year validity
    
    // Category weights (how much each category contributes to overall reputation)
    mapping(string => uint256) public categoryWeights;
    
    // Global statistics
    uint256 public totalProfiles;
    uint256 public totalReputationIssued;
    uint256 public totalOneHumanAttestations;
    
    // Events
    event ReputationAdded(
        address indexed user,
        uint256 amount,
        string category,
        uint8 difficulty,
        uint256 newTotal
    );
    
    event ReputationDecayed(
        address indexed user,
        uint256 amountDecayed,
        string category,
        uint256 newTotal
    );
    
    event OneHumanAttested(
        address indexed user,
        address indexed attestor,
        uint256 timestamp
    );
    
    event OneHumanRevoked(
        address indexed user,
        address indexed revokedBy,
        string reason
    );
    
    event CategoryWeightUpdated(
        string category,
        uint256 oldWeight,
        uint256 newWeight
    );
    
    event QualityScoreUpdated(
        address indexed user,
        uint256 oldScore,
        uint256 newScore
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MAINTAINER_ROLE, msg.sender);
        _grantRole(REPUTATION_MINTER_ROLE, msg.sender);
        _grantRole(ATTESTOR_ROLE, msg.sender);
        
        // Initialize category weights (1-100 scale)
        categoryWeights["security"] = 100;      // Highest weight
        categoryWeights["ui"] = 80;             // High weight
        categoryWeights["docs"] = 70;           // Good weight
        categoryWeights["translation"] = 60;    // Medium weight
        categoryWeights["testing"] = 75;        // Good weight
        categoryWeights["mentorship"] = 90;     // High weight
        categoryWeights["governance"] = 85;     // High weight
        categoryWeights["infrastructure"] = 95; // Very high weight
    }
    
    /**
     * @dev Add reputation to a user (called by TicketRegistry)
     * @param user Address to add reputation to
     * @param amount Base reputation amount
     * @param category Contribution category
     * @param difficulty Difficulty level (1-5) for multiplier
     */
    function addReputation(
        address user,
        uint256 amount,
        string calldata category,
        uint8 difficulty
    ) external onlyRole(REPUTATION_MINTER_ROLE) whenNotPaused {
        require(user != address(0), "Cannot add reputation to zero address");
        require(amount > 0, "Amount must be > 0");
        require(difficulty >= 1 && difficulty <= 5, "Difficulty must be 1-5");
        require(bytes(category).length > 0, "Category cannot be empty");
        
        ReputationProfile storage profile = _profiles[user];
        
        // Calculate reputation with difficulty multiplier and category weight
        uint256 categoryWeight = categoryWeights[category];
        if (categoryWeight == 0) categoryWeight = 50; // Default weight
        
        uint256 difficultyMultiplier = 50 + (difficulty * 10); // 60-100% multiplier
        uint256 finalAmount = (amount * difficultyMultiplier * categoryWeight) / 10000;
        
        // Initialize profile if first time
        if (profile.totalReputation == 0) {
            totalProfiles++;
            profile.decayStartTimestamp = block.timestamp;
        }
        
        // Add to total and category reputation
        profile.totalReputation += finalAmount;
        profile.categoryReputation[category] += finalAmount;
        profile.lastActivityTimestamp = block.timestamp;
        profile.categoryLastActivity[category] = block.timestamp;
        
        // Add category to list if not exists
        bool categoryExists = false;
        for (uint i = 0; i < profile.categories.length; i++) {
            if (keccak256(bytes(profile.categories[i])) == keccak256(bytes(category))) {
                categoryExists = true;
                break;
            }
        }
        if (!categoryExists) {
            profile.categories.push(category);
        }
        
        // Update contribution stats
        ContributionStats storage stats = contributionStats[user];
        stats.ticketsCompleted++;
        stats.averageDifficulty = ((stats.averageDifficulty * (stats.ticketsCompleted - 1)) + difficulty) / stats.ticketsCompleted;
        
        // Update category-specific stats
        if (keccak256(bytes(category)) == keccak256(bytes("security"))) {
            stats.securityContributions++;
        } else if (keccak256(bytes(category)) == keccak256(bytes("ui"))) {
            stats.uiContributions++;
        } else if (keccak256(bytes(category)) == keccak256(bytes("docs"))) {
            stats.docsContributions++;
        } else if (keccak256(bytes(category)) == keccak256(bytes("translation"))) {
            stats.translationContributions++;
        }
        
        totalReputationIssued += finalAmount;
        
        emit ReputationAdded(user, finalAmount, category, difficulty, profile.totalReputation);
    }
    
    /**
     * @dev Provide One-Human attestation for a user
     * @param user Address to attest
     */
    function attestOneHuman(address user) external onlyRole(ATTESTOR_ROLE) whenNotPaused {
        require(user != address(0), "Cannot attest zero address");
        require(user != msg.sender, "Cannot self-attest");
        require(authorizedAttestors[msg.sender], "Not authorized attestor");
        
        ReputationProfile storage profile = _profiles[user];
        require(!profile.hasOneHumanAttestation || 
                block.timestamp > profile.oneHumanTimestamp + ONE_HUMAN_VALIDITY_PERIOD, 
                "Already has valid One-Human attestation");
        
        profile.hasOneHumanAttestation = true;
        profile.oneHumanTimestamp = block.timestamp;
        profile.attestedBy = msg.sender;
        
        totalOneHumanAttestations++;
        
        emit OneHumanAttested(user, msg.sender, block.timestamp);
    }
    
    /**
     * @dev Revoke One-Human attestation (for abuse cases)
     * @param user Address to revoke attestation from
     * @param reason Reason for revocation
     */
    function revokeOneHuman(
        address user,
        string calldata reason
    ) external onlyRole(ATTESTOR_ROLE) {
        require(user != address(0), "Cannot revoke from zero address");
        require(_profiles[user].hasOneHumanAttestation, "No attestation to revoke");
        
        _profiles[user].hasOneHumanAttestation = false;
        _profiles[user].oneHumanTimestamp = 0;
        _profiles[user].attestedBy = address(0);
        
        totalOneHumanAttestations--;
        
        emit OneHumanRevoked(user, msg.sender, reason);
    }
    
    /**
     * @dev Calculate current reputation with decay
     * @param user Address to calculate for
     * @return currentReputation Reputation after decay calculation
     */
    function getCurrentReputation(address user) public view returns (uint256 currentReputation) {
        ReputationProfile storage profile = _profiles[user];
        
        if (profile.totalReputation == 0) {
            return 0;
        }
        
        uint256 timeSinceLastActivity = block.timestamp - profile.lastActivityTimestamp;
        
        // No decay if activity within 6 months
        if (timeSinceLastActivity <= DECAY_START_PERIOD) {
            return profile.totalReputation;
        }
        
        // Calculate decay
        uint256 decayTime = timeSinceLastActivity - DECAY_START_PERIOD;
        
        if (decayTime >= FULL_DECAY_PERIOD) {
            // Maximum decay: retain only minimum percentage
            return (profile.totalReputation * MIN_REPUTATION_RETAINED) / 100;
        }
        
        // Gradual decay: linear decay over the decay period
        uint256 decayPercentage = (decayTime * (100 - MIN_REPUTATION_RETAINED)) / FULL_DECAY_PERIOD;
        uint256 retainedPercentage = 100 - decayPercentage;
        
        return (profile.totalReputation * retainedPercentage) / 100;
    }
    
    /**
     * @dev Get reputation in a specific category with decay
     * @param user Address to check
     * @param category Category to check
     * @return categoryReputation Reputation in the category after decay
     */
    function getCategoryReputation(address user, string calldata category) public view returns (uint256 categoryReputation) {
        ReputationProfile storage profile = _profiles[user];
        uint256 baseCategoryReputation = profile.categoryReputation[category];
        
        if (baseCategoryReputation == 0) {
            return 0;
        }
        
        uint256 timeSinceLastActivity = block.timestamp - profile.categoryLastActivity[category];
        
        // No decay if activity within 6 months
        if (timeSinceLastActivity <= DECAY_START_PERIOD) {
            return baseCategoryReputation;
        }
        
        // Calculate category-specific decay
        uint256 decayTime = timeSinceLastActivity - DECAY_START_PERIOD;
        
        if (decayTime >= FULL_DECAY_PERIOD) {
            return (baseCategoryReputation * MIN_REPUTATION_RETAINED) / 100;
        }
        
        uint256 decayPercentage = (decayTime * (100 - MIN_REPUTATION_RETAINED)) / FULL_DECAY_PERIOD;
        uint256 retainedPercentage = 100 - decayPercentage;
        
        return (baseCategoryReputation * retainedPercentage) / 100;
    }
    
    /**
     * @dev Check if user has valid One-Human attestation
     * @param user Address to check
     * @return hasValid Whether user has valid attestation
     */
    function hasOneHumanAttestation(address user) external view returns (bool hasValid) {
        ReputationProfile storage profile = _profiles[user];
        
        if (!profile.hasOneHumanAttestation) {
            return false;
        }
        
        // Check if attestation is still valid (within validity period)
        return block.timestamp <= profile.oneHumanTimestamp + ONE_HUMAN_VALIDITY_PERIOD;
    }
    
    /**
     * @dev Get user's reputation profile
     * @param user Address to check
     * @return totalRep Total reputation (with decay)
     * @param rawTotalRep Raw total reputation (without decay)
     * @param lastActivity Last activity timestamp
     * @return categories Array of categories user has reputation in
     */
    function getReputationProfile(address user) external view returns (
        uint256 totalRep,
        uint256 rawTotalRep,
        uint256 lastActivity,
        string[] memory categories
    ) {
        ReputationProfile storage profile = _profiles[user];
        return (
            getCurrentReputation(user),
            profile.totalReputation,
            profile.lastActivityTimestamp,
            profile.categories
        );
    }
    
    /**
     * @dev Get user's contribution statistics
     * @param user Address to check
     * @return stats ContributionStats struct
     */
    function getContributionStats(address user) external view returns (ContributionStats memory stats) {
        return contributionStats[user];
    }
    
    /**
     * @dev Get One-Human attestation info
     * @param user Address to check
     * @return hasAttestation Whether user has attestation
     * @return timestamp When attestation was made
     * @return attestor Who provided the attestation
     * @return isValid Whether attestation is still valid
     */
    function getOneHumanInfo(address user) external view returns (
        bool hasAttestation,
        uint256 timestamp,
        address attestor,
        bool isValid
    ) {
        ReputationProfile storage profile = _profiles[user];
        return (
            profile.hasOneHumanAttestation,
            profile.oneHumanTimestamp,
            profile.attestedBy,
            this.hasOneHumanAttestation(user)
        );
    }
    
    /**
     * @dev Update quality score for a user (based on external evaluation)
     * @param user Address to update
     * @param qualityScore New quality score (0-100)
     */
    function updateQualityScore(
        address user,
        uint256 qualityScore
    ) external onlyRole(REPUTATION_MINTER_ROLE) {
        require(qualityScore <= 100, "Quality score must be <= 100");
        
        uint256 oldScore = contributionStats[user].qualityScore;
        contributionStats[user].qualityScore = qualityScore;
        
        emit QualityScoreUpdated(user, oldScore, qualityScore);
    }
    
    /**
     * @dev Add mentorship action
     * @param mentor Address of the mentor
     * @param amount Reputation amount for mentorship
     */
    function addMentorshipReputation(
        address mentor,
        uint256 amount
    ) external onlyRole(REPUTATION_MINTER_ROLE) {
        contributionStats[mentor].mentorshipActions++;
        addReputation(mentor, amount, "mentorship", 3); // Medium difficulty default
    }
    
    // =============================================================================
    // ADMIN FUNCTIONS
    // =============================================================================
    
    /**
     * @dev Add authorized attestor
     * @param attestor Address to authorize
     */
    function addAuthorizedAttestor(address attestor) external onlyRole(MAINTAINER_ROLE) {
        require(attestor != address(0), "Cannot authorize zero address");
        authorizedAttestors[attestor] = true;
        _grantRole(ATTESTOR_ROLE, attestor);
    }
    
    /**
     * @dev Remove authorized attestor
     * @param attestor Address to revoke authorization
     */
    function removeAuthorizedAttestor(address attestor) external onlyRole(MAINTAINER_ROLE) {
        authorizedAttestors[attestor] = false;
        _revokeRole(ATTESTOR_ROLE, attestor);
    }
    
    /**
     * @dev Update category weight
     * @param category Category name
     * @param weight New weight (1-100)
     */
    function updateCategoryWeight(
        string calldata category,
        uint256 weight
    ) external onlyRole(MAINTAINER_ROLE) {
        require(weight > 0 && weight <= 100, "Weight must be 1-100");
        
        uint256 oldWeight = categoryWeights[category];
        categoryWeights[category] = weight;
        
        emit CategoryWeightUpdated(category, oldWeight, weight);
    }
    
    /**
     * @dev Emergency reputation adjustment (for abuse cases)
     * @param user User address
     * @param newAmount New total reputation amount
     * @param reason Reason for adjustment
     */
    function emergencyAdjustReputation(
        address user,
        uint256 newAmount,
        string calldata reason
    ) external onlyRole(MAINTAINER_ROLE) {
        require(bytes(reason).length > 0, "Reason required");
        
        ReputationProfile storage profile = _profiles[user];
        uint256 oldAmount = profile.totalReputation;
        profile.totalReputation = newAmount;
        
        // Adjust global stats
        if (newAmount > oldAmount) {
            totalReputationIssued += (newAmount - oldAmount);
        } else {
            totalReputationIssued -= (oldAmount - newAmount);
        }
        
        emit ReputationAdded(user, newAmount, "emergency_adjustment", 1, newAmount);
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
    // SOULBOUND TOKEN ENFORCEMENT
    // =============================================================================
    
    /**
     * @dev Reputation tokens are soulbound and cannot be transferred
     * These functions are intentionally not implemented or revert
     */
    
    // Standard ERC721-like interface that always reverts
    function transferFrom(address, address, uint256) external pure {
        revert("Reputation is soulbound and non-transferable");
    }
    
    function safeTransferFrom(address, address, uint256) external pure {
        revert("Reputation is soulbound and non-transferable");
    }
    
    function safeTransferFrom(address, address, uint256, bytes memory) external pure {
        revert("Reputation is soulbound and non-transferable");
    }
    
    function approve(address, uint256) external pure {
        revert("Reputation is soulbound and non-transferable");
    }
    
    function setApprovalForAll(address, bool) external pure {
        revert("Reputation is soulbound and non-transferable");
    }
}