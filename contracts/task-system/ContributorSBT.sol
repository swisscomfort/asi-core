// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ContributorSBT (Soulbound Token)
 * @dev Non-transferable achievement tokens for ASI Core contributors
 * @notice Tracks reputation and achievements for task completion
 */
contract ContributorSBT is ERC721, AccessControl, Pausable {
    using Counters for Counters.Counter;
    using Strings for uint256;
    
    bytes32 public constant TASK_REGISTRY_ROLE = keccak256("TASK_REGISTRY_ROLE");
    bytes32 public constant MILESTONE_ROLE = keccak256("MILESTONE_ROLE");
    
    enum BadgeType {
        TaskCompletion,     // Individual task completed
        MilestoneAchievement, // Milestone completed
        QualityBonus,       // Exceptional quality work
        EarlyContributor,   // Among first X contributors
        Mentor,             // Helped onboard others
        SecurityAuditor,    // Security review contributions
        Innovation          // Novel contributions/improvements
    }
    
    struct Badge {
        BadgeType badgeType;
        string taskOrMilestoneId;   // Related task/milestone
        uint256 issuedAt;           // Timestamp
        bytes32 evidenceCID;        // IPFS CID of evidence/proof
        uint256 value;              // Optional numeric value (bounty amount, etc.)
        string metadata;            // Additional JSON metadata
    }
    
    // Token counter
    Counters.Counter private _tokenIdCounter;
    
    // tokenId => Badge details
    mapping(uint256 => Badge) public badges;
    
    // user => BadgeType => count
    mapping(address => mapping(BadgeType => uint256)) public userBadgeCounts;
    
    // user => total badges
    mapping(address => uint256) public userTotalBadges;
    
    // user => tokenIds owned
    mapping(address => uint256[]) public userTokens;
    mapping(uint256 => uint256) public tokenToUserIndex;
    
    // Badge type statistics
    mapping(BadgeType => uint256) public totalBadgesByType;
    
    // Base URI for metadata
    string private _baseTokenURI;
    
    // Events
    event BadgeMinted(
        address indexed recipient,
        uint256 indexed tokenId,
        BadgeType indexed badgeType,
        string taskOrMilestoneId,
        uint256 value
    );
    
    event BadgeRevoked(
        address indexed holder,
        uint256 indexed tokenId,
        string reason
    );
    
    constructor(
        string memory name,
        string memory symbol,
        string memory baseURI
    ) ERC721(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(TASK_REGISTRY_ROLE, msg.sender);
        _grantRole(MILESTONE_ROLE, msg.sender);
        
        _baseTokenURI = baseURI;
        
        // Start token IDs at 1
        _tokenIdCounter.increment();
    }
    
    /**
     * @dev Mint task completion badge
     * @param recipient Address receiving the badge
     * @param taskId Task that was completed
     * @param evidenceCID IPFS CID of task evidence
     * @param bountyAmount Bounty amount earned
     */
    function mintTaskCompletion(
        address recipient,
        string calldata taskId,
        bytes32 evidenceCID,
        uint256 bountyAmount
    ) external onlyRole(TASK_REGISTRY_ROLE) whenNotPaused {
        _mintBadge(
            recipient,
            BadgeType.TaskCompletion,
            taskId,
            evidenceCID,
            bountyAmount,
            ""
        );
    }
    
    /**
     * @dev Mint milestone achievement badge
     * @param recipient Address receiving the badge
     * @param milestoneId Milestone that was completed
     * @param manifestCID IPFS CID of milestone manifest
     */
    function mintMilestoneAchievement(
        address recipient,
        string calldata milestoneId,
        bytes32 manifestCID
    ) external onlyRole(MILESTONE_ROLE) whenNotPaused {
        _mintBadge(
            recipient,
            BadgeType.MilestoneAchievement,
            milestoneId,
            manifestCID,
            0,
            ""
        );
    }
    
    /**
     * @dev Mint special achievement badge
     * @param recipient Address receiving the badge
     * @param badgeType Type of special badge
     * @param identifier Related identifier (task, milestone, etc.)
     * @param evidenceCID Supporting evidence
     * @param value Optional numeric value
     * @param metadata Additional JSON metadata
     */
    function mintSpecialBadge(
        address recipient,
        BadgeType badgeType,
        string calldata identifier,
        bytes32 evidenceCID,
        uint256 value,
        string calldata metadata
    ) external onlyRole(DEFAULT_ADMIN_ROLE) whenNotPaused {
        require(badgeType != BadgeType.TaskCompletion, "Use mintTaskCompletion");
        require(badgeType != BadgeType.MilestoneAchievement, "Use mintMilestoneAchievement");
        
        _mintBadge(recipient, badgeType, identifier, evidenceCID, value, metadata);
    }
    
    /**
     * @dev Internal badge minting logic
     */
    function _mintBadge(
        address recipient,
        BadgeType badgeType,
        string calldata identifier,
        bytes32 evidenceCID,
        uint256 value,
        string calldata metadata
    ) internal {
        require(recipient != address(0), "Invalid recipient");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        // Create badge
        badges[tokenId] = Badge({
            badgeType: badgeType,
            taskOrMilestoneId: identifier,
            issuedAt: block.timestamp,
            evidenceCID: evidenceCID,
            value: value,
            metadata: metadata
        });
        
        // Update user statistics
        userBadgeCounts[recipient][badgeType]++;
        userTotalBadges[recipient]++;
        totalBadgesByType[badgeType]++;
        
        // Add to user's token list
        userTokens[recipient].push(tokenId);
        tokenToUserIndex[tokenId] = userTokens[recipient].length - 1;
        
        // Mint the token
        _safeMint(recipient, tokenId);
        
        emit BadgeMinted(recipient, tokenId, badgeType, identifier, value);
    }
    
    /**
     * @dev Get user's badges by type
     * @param user User address
     * @param badgeType Type of badge to query
     * @return count Number of badges of this type
     */
    function getUserBadgeCount(address user, BadgeType badgeType) 
        external 
        view 
        returns (uint256) 
    {
        return userBadgeCounts[user][badgeType];
    }
    
    /**
     * @dev Get user's total reputation score
     * @param user User address
     * @return score Calculated reputation score
     */
    function getUserReputationScore(address user) external view returns (uint256) {
        uint256 score = 0;
        
        // Different badge types have different weights
        score += userBadgeCounts[user][BadgeType.TaskCompletion] * 10;
        score += userBadgeCounts[user][BadgeType.MilestoneAchievement] * 50;
        score += userBadgeCounts[user][BadgeType.QualityBonus] * 25;
        score += userBadgeCounts[user][BadgeType.EarlyContributor] * 100;
        score += userBadgeCounts[user][BadgeType.Mentor] * 75;
        score += userBadgeCounts[user][BadgeType.SecurityAuditor] * 150;
        score += userBadgeCounts[user][BadgeType.Innovation] * 200;
        
        return score;
    }
    
    /**
     * @dev Get user's token IDs
     * @param user User address
     * @return tokenIds Array of token IDs owned by user
     */
    function getUserTokens(address user) external view returns (uint256[] memory) {
        return userTokens[user];
    }
    
    /**
     * @dev Get badge details
     * @param tokenId Token ID to query
     */
    function getBadge(uint256 tokenId) external view returns (
        BadgeType badgeType,
        string memory taskOrMilestoneId,
        uint256 issuedAt,
        bytes32 evidenceCID,
        uint256 value,
        string memory metadata
    ) {
        require(_exists(tokenId), "Badge does not exist");
        
        Badge storage badge = badges[tokenId];
        return (
            badge.badgeType,
            badge.taskOrMilestoneId,
            badge.issuedAt,
            badge.evidenceCID,
            badge.value,
            badge.metadata
        );
    }
    
    /**
     * @dev Get platform statistics
     */
    function getPlatformStats() external view returns (
        uint256 totalBadges,
        uint256 totalHolders,
        uint256[7] memory badgeCountsByType
    ) {
        totalBadges = _tokenIdCounter.current() - 1; // Subtract 1 because we start at 1
        
        // Note: totalHolders would need to be tracked separately for efficiency
        totalHolders = 0; // Placeholder
        
        for (uint i = 0; i < 7; i++) {
            badgeCountsByType[i] = totalBadgesByType[BadgeType(i)];
        }
    }
    
    /**
     * @dev Revoke a badge (emergency only)
     * @param tokenId Token ID to revoke
     * @param reason Reason for revocation
     */
    function revokeBadge(
        uint256 tokenId,
        string calldata reason
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_exists(tokenId), "Badge does not exist");
        
        address holder = ownerOf(tokenId);
        Badge storage badge = badges[tokenId];
        
        // Update statistics
        userBadgeCounts[holder][badge.badgeType]--;
        userTotalBadges[holder]--;
        totalBadgesByType[badge.badgeType]--;
        
        // Remove from user's token list
        uint256[] storage userTokenList = userTokens[holder];
        uint256 index = tokenToUserIndex[tokenId];
        uint256 lastIndex = userTokenList.length - 1;
        
        if (index != lastIndex) {
            uint256 lastTokenId = userTokenList[lastIndex];
            userTokenList[index] = lastTokenId;
            tokenToUserIndex[lastTokenId] = index;
        }
        
        userTokenList.pop();
        delete tokenToUserIndex[tokenId];
        
        // Burn the token
        _burn(tokenId);
        delete badges[tokenId];
        
        emit BadgeRevoked(holder, tokenId, reason);
    }
    
    /**
     * @dev Override to prevent transfers (Soulbound)
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
        
        // Allow minting (from == address(0)) and burning (to == address(0))
        // Prevent all other transfers
        require(
            from == address(0) || to == address(0),
            "Soulbound: token transfer is not allowed"
        );
    }
    
    /**
     * @dev Override to prevent approvals (Soulbound)
     */
    function approve(address, uint256) public pure override {
        revert("Soulbound: approve is not allowed");
    }
    
    /**
     * @dev Override to prevent approvals (Soulbound)
     */
    function setApprovalForAll(address, bool) public pure override {
        revert("Soulbound: setApprovalForAll is not allowed");
    }
    
    /**
     * @dev Override token URI to include badge type in metadata
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "Badge does not exist");
        
        Badge storage badge = badges[tokenId];
        
        return string(abi.encodePacked(
            _baseTokenURI,
            tokenId.toString(),
            "?type=",
            uint256(badge.badgeType).toString(),
            "&task=",
            badge.taskOrMilestoneId
        ));
    }
    
    /**
     * @dev Update base URI
     */
    function updateBaseURI(string calldata newBaseURI) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        _baseTokenURI = newBaseURI;
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
     * @dev See {IERC165-supportsInterface}.
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}