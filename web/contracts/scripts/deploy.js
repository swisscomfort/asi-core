const { ethers } = require("hardhat");

async function main() {
  const MemoryIndex = await ethers.getContractFactory("MemoryIndex");
  const memoryIndex = await MemoryIndex.deploy();

  await memoryIndex.deployed();

  console.log("MemoryIndex deployed to:", memoryIndex.address);
  console.log(
    "Update MEMORY_INDEX_ADDRESS in aiApiService.js to:",
    memoryIndex.address
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
