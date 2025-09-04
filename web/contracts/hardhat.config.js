require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.19",
  networks: {
    mumbai: {
      url: "https://rpc-mumbai.maticvigil.com/",
      accounts: ["YOUR_PRIVATE_KEY_HERE"], // Replace with your private key
    },
  },
};
