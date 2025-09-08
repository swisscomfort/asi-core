import { ethers } from "ethers";

class ChainInterface {
  constructor() {
    this.contractAddress = null;
    this.contract = null;
    this.provider = null;
    this.signer = null;
    this.wallet = null;
    this.isInitialized = false;

    // Polygon Mumbai testnet configuration
    this.networkConfig = {
      chainId: 80001,
      name: "Polygon Mumbai",
      rpcUrl: "https://rpc-mumbai.maticvigil.com/",
      blockExplorer: "https://mumbai.polygonscan.com/",
    };

    // Smart contract ABI for state logging
    this.contractABI = [
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
      {
        anonymous: false,
        inputs: [
          {
            indexed: true,
            internalType: "address",
            name: "user",
            type: "address",
          },
          {
            indexed: false,
            internalType: "string",
            name: "key",
            type: "string",
          },
          {
            indexed: false,
            internalType: "uint256",
            name: "value",
            type: "uint256",
          },
          {
            indexed: false,
            internalType: "string",
            name: "cid",
            type: "string",
          },
          {
            indexed: false,
            internalType: "uint256",
            name: "timestamp",
            type: "uint256",
          },
        ],
        name: "StateLogged",
        type: "event",
      },
    ];
  }

  async initialize(seedPhrase = null) {
    try {
      // Initialize provider
      this.provider = new ethers.JsonRpcProvider(this.networkConfig.rpcUrl);

      // Create or restore wallet
      if (seedPhrase) {
        this.wallet = ethers.Wallet.fromPhrase(seedPhrase);
      } else {
        // Check if we have a stored wallet
        const storedWallet = localStorage.getItem("asi_wallet_encrypted");
        if (storedWallet) {
          const password = await this.getWalletPassword();
          this.wallet = await ethers.Wallet.fromEncryptedJson(
            storedWallet,
            password
          );
        } else {
          // Generate new wallet
          this.wallet = ethers.Wallet.createRandom();
          await this.storeWallet();
        }
      }

      this.signer = this.wallet.connect(this.provider);

      // Initialize contract (would need to be deployed first)
      this.contractAddress = this.getContractAddress();
      if (this.contractAddress) {
        this.contract = new ethers.Contract(
          this.contractAddress,
          this.contractABI,
          this.signer
        );
      }

      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error("Failed to initialize ChainInterface:", error);
      return false;
    }
  }

  async storeWallet() {
    const password = await this.generateWalletPassword();
    const encryptedWallet = await this.wallet.encrypt(password);
    localStorage.setItem("asi_wallet_encrypted", encryptedWallet);
    localStorage.setItem("asi_wallet_address", this.wallet.address);
  }

  async generateWalletPassword() {
    // Generate a deterministic password based on browser fingerprint
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    ctx.textBaseline = "top";
    ctx.font = "14px Arial";
    ctx.fillText("ASI Fingerprint", 2, 2);

    const fingerprint =
      canvas.toDataURL() +
      navigator.userAgent +
      navigator.language +
      screen.width +
      screen.height;

    const encoder = new TextEncoder();
    const data = encoder.encode(fingerprint);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    return hashHex;
  }

  async getWalletPassword() {
    return await this.generateWalletPassword();
  }

  getContractAddress() {
    // In production, this would be the deployed contract address
    // For now, return null to indicate contract needs deployment
    return localStorage.getItem("asi_contract_address") || null;
  }

  async logState(key, value, cid = "") {
    if (!this.isInitialized || !this.contract) {
      throw new Error(
        "ChainInterface not initialized or contract not deployed"
      );
    }

    try {
      // Check if we have enough gas
      const gasPrice = await this.provider.getFeeData();
      const balance = await this.provider.getBalance(this.wallet.address);

      if (balance === 0n) {
        throw new Error(
          "Insufficient balance for transaction. Please fund your wallet."
        );
      }

      // Estimate gas
      const estimatedGas = await this.contract.logState.estimateGas(
        key,
        value,
        cid
      );

      // Send transaction
      const tx = await this.contract.logState(key, value, cid, {
        gasLimit: (estimatedGas * 120n) / 100n, // Add 20% buffer
        gasPrice: gasPrice.gasPrice,
      });

      const receipt = await tx.wait();

      return {
        success: true,
        transactionHash: receipt.hash,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString(),
        effectiveGasPrice: receipt.effectiveGasPrice.toString(),
      };
    } catch (error) {
      console.error("Failed to log state to blockchain:", error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  async getGlobalStats(stateKey) {
    if (!this.isInitialized || !this.contract) {
      return { totalEntries: 0, positiveCount: 0, uniqueUsers: 0 };
    }

    try {
      const [totalEntries, positiveCount, uniqueUsers] =
        await this.contract.getGlobalStats(stateKey);

      return {
        totalEntries: Number(totalEntries),
        positiveCount: Number(positiveCount),
        uniqueUsers: Number(uniqueUsers),
        positiveRate:
          Number(totalEntries) > 0
            ? Number(positiveCount) / Number(totalEntries)
            : 0,
      };
    } catch (error) {
      console.error("Failed to fetch global stats:", error);
      return {
        totalEntries: 0,
        positiveCount: 0,
        uniqueUsers: 0,
        positiveRate: 0,
      };
    }
  }

  async getUserStateHistory(stateKey, userAddress = null) {
    if (!this.isInitialized || !this.contract) {
      return [];
    }

    try {
      const address = userAddress || this.wallet.address;
      const history = await this.contract.getUserStateHistory(
        address,
        stateKey
      );

      return history.map((entry) => ({
        key: entry.key,
        value: Number(entry.value),
        cid: entry.cid,
        timestamp: Number(entry.timestamp) * 1000, // Convert to milliseconds
      }));
    } catch (error) {
      console.error("Failed to fetch user state history:", error);
      return [];
    }
  }

  async getWalletInfo() {
    if (!this.wallet) {
      return null;
    }

    try {
      const balance = await this.provider.getBalance(this.wallet.address);
      const nonce = await this.provider.getTransactionCount(
        this.wallet.address
      );

      return {
        address: this.wallet.address,
        balance: ethers.formatEther(balance),
        nonce: nonce,
        network: this.networkConfig.name,
        chainId: this.networkConfig.chainId,
      };
    } catch (error) {
      console.error("Failed to get wallet info:", error);
      return null;
    }
  }

  async generateCollectiveInsights(stateKeys) {
    const insights = [];

    for (const stateKey of stateKeys) {
      try {
        const stats = await this.getGlobalStats(stateKey);

        if (stats.totalEntries > 10) {
          // Only show insights with sufficient data
          insights.push({
            type: "collective_pattern",
            message: `${Math.round(
              stats.positiveRate * 100
            )}% der Nutzer berichten von positiven Ergebnissen mit "${stateKey}".`,
            confidence: Math.min(stats.totalEntries / 100, 1.0),
            stateKey: stateKey,
            sampleSize: stats.totalEntries,
            uniqueUsers: stats.uniqueUsers,
          });

          if (stats.positiveRate > 0.8) {
            insights.push({
              type: "recommendation",
              message: `"${stateKey}" zeigt sehr positive Ergebnisse. Möchtest du es heute versuchen?`,
              confidence: Math.min(stats.totalEntries / 50, 1.0),
              stateKey: stateKey,
            });
          }
        }
      } catch (error) {
        console.error(`Failed to generate insights for ${stateKey}:`, error);
      }
    }

    return insights.sort((a, b) => b.confidence - a.confidence);
  }

  async deployContract() {
    // This would be used to deploy the smart contract
    // Implementation depends on having the contract bytecode
    throw new Error(
      "Contract deployment not implemented. Use existing deployed contract."
    );
  }

  async fundWallet() {
    // In a real application, this would provide instructions for funding
    const walletInfo = await this.getWalletInfo();

    return {
      message: "Please fund your wallet to interact with the blockchain.",
      address: walletInfo?.address,
      network: this.networkConfig.name,
      explorerUrl: `${this.networkConfig.blockExplorer}/address/${walletInfo?.address}`,
      instructions: [
        "1. Visit a Polygon Mumbai faucet (e.g., https://faucet.polygon.technology/)",
        "2. Enter your wallet address",
        "3. Request test MATIC tokens",
        "4. Wait for the transaction to confirm",
      ],
    };
  }

  async switchToPolygon() {
    if (!window.ethereum) {
      throw new Error("MetaMask not detected");
    }

    try {
      await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: "0x13881" }], // Polygon Mumbai
      });
    } catch (switchError) {
      // Chain not added to MetaMask
      if (switchError.code === 4902) {
        await window.ethereum.request({
          method: "wallet_addEthereumChain",
          params: [
            {
              chainId: "0x13881",
              chainName: "Polygon Mumbai",
              nativeCurrency: {
                name: "MATIC",
                symbol: "MATIC",
                decimals: 18,
              },
              rpcUrls: ["https://rpc-mumbai.maticvigil.com/"],
              blockExplorerUrls: ["https://mumbai.polygonscan.com/"],
            },
          ],
        });
      }
    }
  }

  async verifyChainConnection() {
    if (!this.provider) return false;

    try {
      const network = await this.provider.getNetwork();
      return Number(network.chainId) === this.networkConfig.chainId;
    } catch (error) {
      console.error("Failed to verify chain connection:", error);
      return false;
    }
  }

  getExplorerUrl(txHash) {
    return `${this.networkConfig.blockExplorer}/tx/${txHash}`;
  }

  async estimateTransactionCost(stateKey, value, cid = "") {
    if (!this.contract) {
      return { gasLimit: 0, gasPrice: 0, totalCost: "0" };
    }

    try {
      const gasLimit = await this.contract.logState.estimateGas(
        stateKey,
        value,
        cid
      );
      const gasPrice = await this.provider.getFeeData();
      const totalCost = gasLimit * gasPrice.gasPrice;

      return {
        gasLimit: gasLimit.toString(),
        gasPrice: gasPrice.gasPrice.toString(),
        totalCost: ethers.formatEther(totalCost),
      };
    } catch (error) {
      console.error("Failed to estimate transaction cost:", error);
      return { gasLimit: 0, gasPrice: 0, totalCost: "0" };
    }
  }
}

export default ChainInterface;
