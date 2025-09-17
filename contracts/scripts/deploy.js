const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying ASI-Core Smart Contracts...");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📍 Deploying contracts with account:", deployer.address);

  // Check balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "MATIC");

  if (balance === 0n) {
    throw new Error("Insufficient balance. Get Mumbai MATIC from https://faucet.polygon.technology/");
  }

  // Deploy ASI State Tracker
  console.log("\n📄 Deploying ASI State Tracker...");
  const ASIStateTracker = await ethers.getContractFactory("ASIStateTracker");
  const asiStateTracker = await ASIStateTracker.deploy();
  await asiStateTracker.waitForDeployment();
  
  const asiAddress = await asiStateTracker.getAddress();
  console.log("✅ ASI State Tracker deployed to:", asiAddress);

  // Deploy Memory Token
  console.log("\n🪙 Deploying Memory Token...");
  const MemoryToken = await ethers.getContractFactory("MemoryToken");
  const memoryToken = await MemoryToken.deploy(
    "ASI Memory Token",
    "ASIMEM",
    ethers.parseEther("1000000") // 1M initial supply
  );
  await memoryToken.waitForDeployment();
  
  const tokenAddress = await memoryToken.getAddress();
  console.log("✅ Memory Token deployed to:", tokenAddress);

  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log("\n📊 Network Info:");
  console.log("   Chain ID:", network.chainId);
  console.log("   Network Name:", network.name);

  // Save deployment info
  const deploymentInfo = {
    network: {
      name: network.name,
      chainId: Number(network.chainId)
    },
    contracts: {
      ASIStateTracker: {
        address: asiAddress,
        deployer: deployer.address,
        deploymentTransaction: asiStateTracker.deploymentTransaction()?.hash
      },
      MemoryToken: {
        address: tokenAddress,
        deployer: deployer.address,
        deploymentTransaction: memoryToken.deploymentTransaction()?.hash
      }
    },
    deployedAt: new Date().toISOString(),
    deployer: deployer.address
  };

  // Save to JSON file
  const outputPath = path.join(__dirname, "..", "deployed_addresses.json");
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("\n💾 Deployment info saved to:", outputPath);

  // Generate ABI files
  const asiArtifact = await ethers.getContractFactory("ASIStateTracker");
  const tokenArtifact = await ethers.getContractFactory("MemoryToken");

  const asiABI = {
    contractName: "ASIStateTracker",
    abi: asiArtifact.interface.formatJson(),
    bytecode: asiArtifact.bytecode,
    deployedBytecode: asiArtifact.deployedBytecode,
    address: asiAddress,
    network: network.name
  };

  const tokenABI = {
    contractName: "MemoryToken", 
    abi: tokenArtifact.interface.formatJson(),
    bytecode: tokenArtifact.bytecode,
    deployedBytecode: tokenArtifact.deployedBytecode,
    address: tokenAddress,
    network: network.name
  };

  fs.writeFileSync(
    path.join(__dirname, "..", "ASI.json"),
    JSON.stringify(asiABI, null, 2)
  );

  fs.writeFileSync(
    path.join(__dirname, "..", "MemoryToken.json"),
    JSON.stringify(tokenABI, null, 2)
  );

  console.log("✅ ABI files generated");

  // Verification commands
  console.log("\n🔍 Verification Commands:");
  console.log(`npx hardhat verify --network ${network.name} ${asiAddress}`);
  console.log(`npx hardhat verify --network ${network.name} ${tokenAddress} "ASI Memory Token" "ASIMEM" "${ethers.parseEther("1000000")}"`);

  // Update config files
  console.log("\n⚙️ Updating configuration files...");
  
  // Update ../config/secrets.json
  const secretsPath = path.join(__dirname, "..", "..", "config", "secrets.json");
  if (fs.existsSync(secretsPath)) {
    const secrets = JSON.parse(fs.readFileSync(secretsPath, "utf8"));
    secrets.blockchain = secrets.blockchain || {};
    secrets.blockchain.contract_address = asiAddress;
    secrets.tokens = secrets.tokens || {};
    secrets.tokens.memory_token_address = tokenAddress;
    
    fs.writeFileSync(secretsPath, JSON.stringify(secrets, null, 2));
    console.log("✅ Updated config/secrets.json");
  }

  // Update ../web/.env
  const webEnvPath = path.join(__dirname, "..", "..", "web", ".env");
  if (fs.existsSync(webEnvPath)) {
    let envContent = fs.readFileSync(webEnvPath, "utf8");
    
    // Update contract addresses
    envContent = envContent.replace(
      /VITE_ASI_CONTRACT_ADDRESS=.*/,
      `VITE_ASI_CONTRACT_ADDRESS=${asiAddress}`
    );
    envContent = envContent.replace(
      /VITE_MEMORY_TOKEN_ADDRESS=.*/,
      `VITE_MEMORY_TOKEN_ADDRESS=${tokenAddress}`
    );
    
    fs.writeFileSync(webEnvPath, envContent);
    console.log("✅ Updated web/.env");
  }

  console.log("\n🎉 Deployment completed successfully!");
  console.log("📋 Summary:");
  console.log("   ASI State Tracker:", asiAddress);
  console.log("   Memory Token:", tokenAddress);
  console.log("   Network:", network.name);
  console.log("   Deployer:", deployer.address);
  console.log("\n🔗 Polygon Mumbai Explorer:");
  console.log(`   ASI: https://mumbai.polygonscan.com/address/${asiAddress}`);
  console.log(`   Token: https://mumbai.polygonscan.com/address/${tokenAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });