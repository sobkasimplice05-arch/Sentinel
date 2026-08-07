// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Sentinel Autonomous Yield & Security Vault (SentinelVault)
 * @author Sentinel AI - Autonomous Systems Engineering
 * @notice Coffre-fort DeFi institutionnel de niveau supérieur optimisé pour Arbitrum (Layer 2).
 * Intègre un Reentrancy Guard natif, un Circuit Breaker d'urgence et une gestion de rendement B2B.
 */
interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract SentinelVault {
    // --- Sécurité & Contrôle d'Accès ---
    address public immutable owner;
    address public sentinelAIOracle;
    
    bool public circuitBreakerTriggered;
    uint256 private unlocked = 1;

    // --- Paramètres du Coffre-Fort ---
    IERC20 public immutable stakingToken;
    uint256 public totalStaked;
    uint256 public accumulatedYield;
    
    mapping(address => uint256) public balances;
    mapping(address => uint256) public depositTimestamps;

    // --- Événements Institutionnels ---
    event Deposited(address indexed user, uint256 amount, uint256 timestamp);
    event Withdrawn(address indexed user, uint256 amount, uint256 yieldPaid);
    event CircuitBreakerToggled(bool status, string reason);
    event YieldHarvested(uint256 amount, uint256 timestamp);
    event OracleUpdated(address indexed newOracle);

    // --- Modificateurs ---
    modifier onlyOwner() {
        require(msg.sender == owner, "Sentinel: Caller is not the owner");
        _;
    }

    modifier onlyAuthorized() {
        require(msg.sender == owner || msg.sender == sentinelAIOracle, "Sentinel: Unauthorized entity");
        _;
    }

    modifier nonReentrant() {
        require(unlocked == 1, "Sentinel: REENTRANCY_GUARD_TRIGGERED");
        unlocked = 0;
        _;
        unlocked = 1;
    }

    modifier whenNotPaused() {
        require(!circuitBreakerTriggered, "Sentinel: CIRCUIT_BREAKER_ACTIVE_EMERGENCY_LOCK");
        _;
    }

    constructor(address _stakingToken, address _sentinelAIOracle) {
        owner = msg.sender;
        stakingToken = IERC20(_stakingToken);
        sentinelAIOracle = _sentinelAIOracle;
        circuitBreakerTriggered = false;
    }

    /**
     * @notice Dépôt de fonds sécurisé dans le coffre-fort institutionnel.
     * @param amount Montant du token ERC20 à déposer.
     */
    function deposit(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Sentinel: Cannot deposit zero amount");
        
        require(
            stakingToken.transferFrom(msg.sender, address(this), amount),
            "Sentinel: Transfer failed"
        );

        balances[msg.sender] += amount;
        totalStaked += amount;
        depositTimestamps[msg.sender] = block.timestamp;

        emit Deposited(msg.sender, amount, block.timestamp);
    }

    /**
     * @notice Retrait du capital initial et des rendements accumulés (optimisé gaz Arbitrum).
     * @param amount Montant à retirer.
     */
    function withdraw(uint256 amount) external nonReentrant {
        require(amount > 0, "Sentinel: Cannot withdraw zero amount");
        require(balances[msg.sender] >= amount, "Sentinel: Insufficient balance");

        uint256 userYield = _calculateYield(msg.sender, amount);
        
        balances[msg.sender] -= amount;
        totalStaked -= amount;

        uint256 totalPayout = amount + userYield;
        require(
            stakingToken.transfer(msg.sender, totalPayout),
            "Sentinel: Payout transfer failed"
        );

        emit Withdrawn(msg.sender, amount, userYield);
    }

    /**
     * @notice Calcul algorithmique du rendement basé sur le temps d'immobilité et le volume (L2 gas optimized).
     */
    function _calculateYield(address user, uint256 amount) internal view returns (uint256) {
        uint256 duration = block.timestamp - depositTimestamps[user];
        // Rendement de base annuel simulé à 12% prorata temporis
        uint256 annualRateBps = 1200; // 12.00%
        uint256 secondsInYear = 31536000;
        
        uint256 yieldAmount = (amount * annualRateBps * duration) / (10000 * secondsInYear);
        return yieldAmount;
    }

    /**
     * @notice Circuit Breaker d'urgence piloté par l'IA Sentinel ou l'administrateur en cas d'anomalie détectée.
     */
    function toggleCircuitBreaker(bool _status, string calldata reason) external onlyAuthorized {
        circuitBreakerTriggered = _status;
        emit CircuitBreakerToggled(_status, reason);
    }

    /**
     * @notice Mise à jour de l'Oracle IA Sentinel par le propriétaire.
     */
    function setSentinelAIOracle(address _newOracle) external onlyOwner {
        require(_newOracle != address(0), "Sentinel: Invalid oracle address");
        sentinelAIOracle = _newOracle;
        emit OracleUpdated(_newOracle);
    }

    /**
     * @notice Fonction de récolte et injection de rendement B2B.
     */
    function harvestYield(uint256 yieldAmount) external onlyAuthorized {
        accumulatedYield += yieldAmount;
        emit YieldHarvested(yieldAmount, block.timestamp);
    }
}
