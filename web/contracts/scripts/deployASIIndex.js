const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying ASIIndex Contract...");

  // Get the contract factory
  const ASIIndex = await ethers.getContractFactory("ASIIndex");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);

  // Check balance
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH");

  // Deploy the contract
  console.log("⏳ Deploying contract...");
  const asiIndex = await ASIIndex.deploy();

  // Wait for deployment
  await asiIndex.waitForDeployment();

  const contractAddress = await asiIndex.getAddress();
  console.log("✅ ASIIndex deployed to:", contractAddress);

  // Save deployment info
  const deploymentInfo = {
    contractAddress: contractAddress,
    deployer: deployer.address,
    network: network.name,
    deploymentTime: new Date().toISOString(),
    blockNumber: await ethers.provider.getBlockNumber(),
    transactionHash: asiIndex.deploymentTransaction().hash,
  };

  // Save to JSON file
  const deploymentsDir = path.join(__dirname, "../deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deploymentFile = path.join(
    deploymentsDir,
    `ASIIndex-${network.name}.json`
  );
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log("📄 Deployment info saved to:", deploymentFile);

  // Save ABI
  const artifacts = await hre.artifacts.readArtifact("ASIIndex");
  const abiFile = path.join(deploymentsDir, "ASIIndex-ABI.json");
  fs.writeFileSync(abiFile, JSON.stringify(artifacts.abi, null, 2));
  console.log("📋 ABI saved to:", abiFile);

  // Verify deployment by calling a view function
  try {
    const totalEntries = await asiIndex.getTotalEntries();
    console.log(
      "🔍 Contract verification - Total entries:",
      totalEntries.toString()
    );

    // Test event emission by registering a dummy entry
    console.log("🧪 Testing contract with dummy entry...");
    const dummyTx = await asiIndex.registerEntry(
      "QmTestCID123456789", // dummy CID
      ["test", "deployment"], // tags
      ethers.toUtf8Bytes("dummy_embedding_data"), // embedding
      Math.floor(Date.now() / 1000) // timestamp
    );

    const receipt = await dummyTx.wait();
    console.log("✅ Test transaction confirmed in block:", receipt.blockNumber);

    // Get the entry back
    const entry = await asiIndex.getEntry(1);
    console.log("📖 Test entry CID:", entry.cid);
    console.log("🏷️  Test entry tags:", entry.tags);
  } catch (error) {
    console.error("❌ Contract verification failed:", error.message);
  }

  console.log("\n🎉 Deployment Summary:");
  console.log("==================");
  console.log("Contract Address:", contractAddress);
  console.log("Network:", network.name);
  console.log("Deployer:", deployer.address);
  console.log("Transaction Hash:", asiIndex.deploymentTransaction().hash);
  console.log("Deployment File:", deploymentFile);
  console.log("ABI File:", abiFile);

  // Instructions for integration
  console.log("\n📝 Integration Instructions:");
  console.log("============================");
  console.log("1. Copy the contract address to your Python .env file:");
  console.log(`   ASI_CONTRACT_ADDRESS=${contractAddress}`);
  console.log("2. Set the network RPC URL in your .env file");
  console.log("3. Set your private key in your .env file");
  console.log("4. Use the ABI file for Python Web3 integration");

  return {
    contract: asiIndex,
    address: contractAddress,
    deploymentInfo: deploymentInfo,
  };
}

// Error handling
main()
  .then((result) => {
    console.log("\n✅ Deployment completed successfully!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  });
