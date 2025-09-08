// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MemoryToken is ERC20, Ownable, ReentrancyGuard {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 Milliarde Token
    
    // Token-Verteilung
    uint256 public constant USER_ALLOCATION = 400_000_000 * 10**18; // 40%
    uint256 public constant DEV_ALLOCATION = 300_000_000 * 10**18;  // 30%
    uint256 public constant DAO_ALLOCATION = 300_000_000 * 10**18;  // 30%
    
    // Tracking der Verteilung
    uint256 public userTokensMinted = 0;
    uint256 public devTokensMinted = 0;
    uint256 public daoTokensMinted = 0;
    
    // USDC Contract für Buyback
    IERC20 public usdcToken;
    
    // Buyback-Parameter
    uint256 public burnPercentage = 50; // 50% der gekauften Token werden verbrannt
    uint256 public totalBurned = 0;
    
    // Governance
    address public daoTreasury;
    
    // Events
    event TokensBurned(uint256 amount);
    event BuybackExecuted(uint256 usdcAmount, uint256 tokensBought, uint256 tokensBurned);
    event UserReward(address indexed user, uint256 amount, string reason);
    event DevReward(address indexed dev, uint256 amount, string reason);
    
    constructor(
        address _usdcToken,
        address _daoTreasury,
        address _initialOwner
    ) ERC20("Memory Token", "MEM") {
        usdcToken = IERC20(_usdcToken);
        daoTreasury = _daoTreasury;
        _transferOwnership(_initialOwner);
        
        // Initial DAO-Mint
        _mint(daoTreasury, DAO_ALLOCATION);
        daoTokensMinted = DAO_ALLOCATION;
    }
    
    /**
     * @dev Belohne Nutzer für Aktivitäten
     */
    function rewardUser(
        address user, 
        uint256 amount, 
        string memory reason
    ) external onlyOwner {
        require(user != address(0), "Invalid user address");
        require(userTokensMinted + amount <= USER_ALLOCATION, "User allocation exceeded");
        
        _mint(user, amount);
        userTokensMinted += amount;
        
        emit UserReward(user, amount, reason);
    }
    
    /**
     * @dev Belohne Entwickler für Contributions
     */
    function rewardDeveloper(
        address developer, 
        uint256 amount, 
        string memory reason
    ) external onlyOwner {
        require(developer != address(0), "Invalid developer address");
        require(devTokensMinted + amount <= DEV_ALLOCATION, "Dev allocation exceeded");
        
        _mint(developer, amount);
        devTokensMinted += amount;
        
        emit DevReward(developer, amount, reason);
    }
    
    /**
     * @dev Buyback und Burn-Mechanismus
     */
    function executeBuyback(uint256 usdcAmount) external onlyOwner nonReentrant {
        require(usdcAmount > 0, "USDC amount must be greater than 0");
        
        // USDC vom Owner transferieren
        require(
            usdcToken.transferFrom(msg.sender, address(this), usdcAmount),
            "USDC transfer failed"
        );
        
        // Berechne Token-Menge basierend auf aktuellem Preis
        // Vereinfachte Preisberechnung: 1 USDC = 1000 MEM (kann angepasst werden)
        uint256 tokensToAcquire = usdcAmount * 1000;
        
        // 50% der Token werden verbrannt
        uint256 tokensToBurn = (tokensToAcquire * burnPercentage) / 100;
        uint256 tokensToTreasury = tokensToAcquire - tokensToBurn;
        
        // Mint Token für den Burn und Treasury
        if (tokensToBurn > 0) {
            _mint(address(this), tokensToBurn);
            _burn(address(this), tokensToBurn);
            totalBurned += tokensToBurn;
        }
        
        if (tokensToTreasury > 0) {
            _mint(daoTreasury, tokensToTreasury);
        }
        
        emit BuybackExecuted(usdcAmount, tokensToAcquire, tokensToBurn);
        emit TokensBurned(tokensToBurn);
    }
    
    /**
     * @dev Token verbrennen (öffentlich verfügbar)
     */
    function burn(uint256 amount) public {
        _burn(msg.sender, amount);
        totalBurned += amount;
        emit TokensBurned(amount);
    }
    
    /**
     * @dev Burn-Prozentsatz ändern (nur Owner)
     */
    function setBurnPercentage(uint256 _burnPercentage) external onlyOwner {
        require(_burnPercentage <= 100, "Burn percentage cannot exceed 100");
        burnPercentage = _burnPercentage;
    }
    
    /**
     * @dev DAO Treasury Adresse ändern
     */
    function setDaoTreasury(address _daoTreasury) external onlyOwner {
        require(_daoTreasury != address(0), "Invalid DAO treasury address");
        daoTreasury = _daoTreasury;
    }
    
    /**
     * @dev USDC Token Adresse ändern
     */
    function setUsdcToken(address _usdcToken) external onlyOwner {
        require(_usdcToken != address(0), "Invalid USDC token address");
        usdcToken = IERC20(_usdcToken);
    }
    
    /**
     * @dev Verfügbare Token in jeder Kategorie anzeigen
     */
    function getAvailableTokens() external view returns (
        uint256 userAvailable,
        uint256 devAvailable,
        uint256 totalSupplyRemaining
    ) {
        userAvailable = USER_ALLOCATION - userTokensMinted;
        devAvailable = DEV_ALLOCATION - devTokensMinted;
        totalSupplyRemaining = MAX_SUPPLY - totalSupply();
    }
    
    /**
     * @dev Emergency USDC withdrawal (nur für Owner)
     */
    function emergencyWithdrawUSDC() external onlyOwner {
        uint256 balance = usdcToken.balanceOf(address(this));
        if (balance > 0) {
            require(usdcToken.transfer(owner(), balance), "USDC transfer failed");
        }
    }
}
