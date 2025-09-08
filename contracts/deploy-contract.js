const { ethers } = require("ethers");
const fs = require("fs");

/**
 * Deploy ASI State Tracker Contract to Polygon Mumbai Testnet
 *
 * Usage:
 * 1. Fund your wallet with Mumbai MATIC from https://faucet.polygon.technology/
 * 2. Set PRIVATE_KEY environment variable
 * 3. Run: node deploy-contract.js
 */

async function deployContract() {
  console.log("🚀 Deploying ASI State Tracker Contract...");

  // Configuration
  const NETWORK_CONFIG = {
    name: "Polygon Mumbai",
    rpcUrl: "https://rpc-mumbai.maticvigil.com/",
    chainId: 80001,
    blockExplorer: "https://mumbai.polygonscan.com/",
  };

  // Check environment
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error("❌ Please set PRIVATE_KEY environment variable");
    process.exit(1);
  }

  try {
    // Setup provider and wallet
    const provider = new ethers.JsonRpcProvider(NETWORK_CONFIG.rpcUrl);
    const wallet = new ethers.Wallet(privateKey, provider);

    console.log(`📍 Deploying from: ${wallet.address}`);

    // Check balance
    const balance = await provider.getBalance(wallet.address);
    console.log(`💰 Wallet balance: ${ethers.formatEther(balance)} MATIC`);

    if (balance === 0n) {
      console.error(
        "❌ Insufficient balance. Please fund your wallet at https://faucet.polygon.technology/"
      );
      process.exit(1);
    }

    // Read contract source (you'll need to compile this separately)
    const contractSource = fs.readFileSync(
      "./contracts/ASIStateTracker.sol",
      "utf8"
    );

    // For this example, we'll use pre-compiled bytecode
    // In production, use hardhat or truffle for compilation
    const contractBytecode = "0x608060405234801561001057600080fd5b50..."; // Compile the contract to get actual bytecode
    const contractABI = [
      {
        inputs: [
          { internalType: "string", name: "key", type: "string" },
          { internalType: "uint256", name: "value", type: "uint256" },
          { internalType: "string", name: "cid", type: "string" },
        ],
        name: "logState",
        outputs: [],
        stateMutability: "nonpayable",
        type: "function",
      },
      {
        inputs: [
          { internalType: "address", name: "user", type: "address" },
          { internalType: "string", name: "key", type: "string" },
        ],
        name: "getUserStateHistory",
        outputs: [
          {
            components: [
              { internalType: "string", name: "key", type: "string" },
              { internalType: "uint256", name: "value", type: "uint256" },
              { internalType: "string", name: "cid", type: "string" },
              { internalType: "uint256", name: "timestamp", type: "uint256" },
            ],
            internalType: "struct ASIStateTracker.StateEntry[]",
            name: "",
            type: "tuple[]",
          },
        ],
        stateMutability: "view",
        type: "function",
      },
      {
        inputs: [{ internalType: "string", name: "key", type: "string" }],
        name: "getGlobalStats",
        outputs: [
          { internalType: "uint256", name: "totalEntries", type: "uint256" },
          { internalType: "uint256", name: "positiveCount", type: "uint256" },
          { internalType: "uint256", name: "uniqueUsers", type: "uint256" },
        ],
        stateMutability: "view",
        type: "function",
      },
    ];

    // Get gas price
    const feeData = await provider.getFeeData();
    console.log(
      `⛽ Gas price: ${ethers.formatUnits(feeData.gasPrice, "gwei")} gwei`
    );

    // Create contract factory
    const contractFactory = new ethers.ContractFactory(
      contractABI,
      contractBytecode,
      wallet
    );

    // Estimate deployment gas
    const deployTx = await contractFactory.getDeployTransaction();
    const gasEstimate = await provider.estimateGas(deployTx);
    const deploymentCost = gasEstimate * feeData.gasPrice;

    console.log(`📊 Estimated gas: ${gasEstimate.toString()}`);
    console.log(
      `💸 Estimated cost: ${ethers.formatEther(deploymentCost)} MATIC`
    );

    // Deploy contract
    console.log("📤 Deploying contract...");
    const contract = await contractFactory.deploy({
      gasLimit: (gasEstimate * 120n) / 100n, // Add 20% buffer
      gasPrice: feeData.gasPrice,
    });

    console.log(
      `⏳ Transaction sent: ${contract.deploymentTransaction().hash}`
    );
    console.log("⏳ Waiting for confirmation...");

    // Wait for deployment
    await contract.waitForDeployment();
    const contractAddress = await contract.getAddress();

    console.log("✅ Contract deployed successfully!");
    console.log(`📍 Contract address: ${contractAddress}`);
    console.log(
      `🔗 View on explorer: ${NETWORK_CONFIG.blockExplorer}/address/${contractAddress}`
    );

    // Test contract
    console.log("🧪 Testing contract...");

    const contractInfo = await contract.getContractInfo();
    console.log(`📋 Contract version: ${contractInfo[0]}`);
    console.log(`📋 Contract description: ${contractInfo[1]}`);

    // Save deployment info
    const deploymentInfo = {
      contractAddress: contractAddress,
      network: NETWORK_CONFIG.name,
      chainId: NETWORK_CONFIG.chainId,
      deployer: wallet.address,
      deploymentHash: contract.deploymentTransaction().hash,
      blockExplorer: `${NETWORK_CONFIG.blockExplorer}/address/${contractAddress}`,
      deployedAt: new Date().toISOString(),
      abi: contractABI,
    };

    fs.writeFileSync(
      "./deployment.json",
      JSON.stringify(deploymentInfo, null, 2)
    );
    console.log("💾 Deployment info saved to deployment.json");

    // Update config file for frontend
    const configPath = "./config/secrets.json";
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      config.POLYGON_CONTRACT_ADDRESS = contractAddress;
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
      console.log("🔧 Updated config/secrets.json with contract address");
    }

    console.log("\n🎉 Deployment completed successfully!");
    console.log("\nNext steps:");
    console.log("1. Update your frontend to use the new contract address");
    console.log("2. Test the contract with small transactions");
    console.log("3. Monitor on PolygonScan for any issues");
  } catch (error) {
    console.error("❌ Deployment failed:", error);

    if (error.message.includes("insufficient funds")) {
      console.log(
        "\n💡 Solution: Fund your wallet at https://faucet.polygon.technology/"
      );
    } else if (error.message.includes("nonce")) {
      console.log("\n💡 Solution: Wait a moment and try again (nonce issue)");
    } else if (error.message.includes("gas")) {
      console.log(
        "\n💡 Solution: Increase gas limit or wait for lower gas prices"
      );
    }

    process.exit(1);
  }
}

// Alternative: Deploy using a simple factory pattern if compilation is not available
async function deploySimpleContract() {
  console.log("🚀 Deploying Simple State Logger...");

  // Simple contract that just logs states without complex storage
  const simpleContractBytecode = "0x608060405234801561001057600080fd5b50..."; // Minimal bytecode
  const simpleABI = [
    {
      inputs: [
        { internalType: "string", name: "key", type: "string" },
        { internalType: "uint256", name: "value", type: "uint256" },
      ],
      name: "logState",
      outputs: [],
      stateMutability: "nonpayable",
      type: "function",
    },
    {
      anonymous: false,
      inputs: [
        {
          indexed: true,
          internalType: "address",
          name: "user",
          type: "address",
        },
        { indexed: false, internalType: "string", name: "key", type: "string" },
        {
          indexed: false,
          internalType: "uint256",
          name: "value",
          type: "uint256",
        },
      ],
      name: "StateLogged",
      type: "event",
    },
  ];

  // This would be a much simpler deployment for MVP
  console.log(
    "💡 For MVP, consider using event-only logging to reduce complexity"
  );
}

// Run deployment
if (require.main === module) {
  deployContract().catch(console.error);
}

module.exports = { deployContract, deploySimpleContract };
