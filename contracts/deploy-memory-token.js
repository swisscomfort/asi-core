const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying Memory Token to Polygon Mumbai...");

  // Mumbai USDC address (Testnet)
  const USDC_MUMBAI = "0x326C977E6efc84E512bB9C30f76E30c160eD06FB"; // Mumbai USDC

  // DAO Treasury address (kann später geändert werden)
  const DAO_TREASURY = "0x742d35Cc6636C0532925a3b8Ad21Bb93C7C9cdeb"; // Beispiel-Adresse

  // Initial Owner (Deployer)
  const [deployer] = await ethers.getSigners();

  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Contract deployen
  const MemoryToken = await ethers.getContractFactory("MemoryToken");
  const memoryToken = await MemoryToken.deploy(
    USDC_MUMBAI,
    DAO_TREASURY,
    deployer.address
  );

  await memoryToken.deployed();

  console.log("Memory Token deployed to:", memoryToken.address);
  console.log("USDC Token address:", USDC_MUMBAI);
  console.log("DAO Treasury address:", DAO_TREASURY);
  console.log("Initial Owner:", deployer.address);

  // Verify contract parameters
  console.log("\n=== Contract Verification ===");
  console.log("Token Name:", await memoryToken.name());
  console.log("Token Symbol:", await memoryToken.symbol());
  console.log(
    "Max Supply:",
    ethers.utils.formatEther(await memoryToken.MAX_SUPPLY())
  );
  console.log(
    "DAO Allocation:",
    ethers.utils.formatEther(await memoryToken.DAO_ALLOCATION())
  );
  console.log(
    "User Allocation:",
    ethers.utils.formatEther(await memoryToken.USER_ALLOCATION())
  );
  console.log(
    "Dev Allocation:",
    ethers.utils.formatEther(await memoryToken.DEV_ALLOCATION())
  );

  // Check initial DAO treasury balance
  const daoBalance = await memoryToken.balanceOf(DAO_TREASURY);
  console.log("DAO Treasury Balance:", ethers.utils.formatEther(daoBalance));

  console.log("\n=== Deployment Complete ===");
  console.log("Contract Address:", memoryToken.address);
  console.log("Add this to your .env file:");
  console.log(`MEMORY_TOKEN_ADDRESS=${memoryToken.address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
