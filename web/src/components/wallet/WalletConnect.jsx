import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

export default function WalletConnect({ onConnect, onDisconnect, className = "" }) {
  const [account, setAccount] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [chainId, setChainId] = useState(null);

  // Supported networks for ASI Core
  const SUPPORTED_NETWORKS = {
    80001: {
      name: 'Polygon Mumbai',
      rpcUrl: 'https://rpc.ankr.com/polygon_mumbai',
      blockExplorer: 'https://mumbai.polygonscan.com',
      nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 }
    },
    137: {
      name: 'Polygon Mainnet',
      rpcUrl: 'https://rpc.ankr.com/polygon',
      blockExplorer: 'https://polygonscan.com',
      nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 }
    }
  };

  // Check if wallet is already connected on component mount
  useEffect(() => {
    checkConnection();
    
    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
    }
    
    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, []);

  const checkConnection = async () => {
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          const chainId = await window.ethereum.request({ method: 'eth_chainId' });
          setChainId(parseInt(chainId, 16));
          onConnect?.(accounts[0], parseInt(chainId, 16));
        }
      } catch (error) {
        console.error('Error checking connection:', error);
      }
    }
  };

  const handleAccountsChanged = (accounts) => {
    if (accounts.length === 0) {
      disconnect();
    } else {
      setAccount(accounts[0]);
      onConnect?.(accounts[0], chainId);
    }
  };

  const handleChainChanged = (chainIdHex) => {
    const newChainId = parseInt(chainIdHex, 16);
    setChainId(newChainId);
    
    if (!SUPPORTED_NETWORKS[newChainId]) {
      setError(`Unsupported network. Please switch to Polygon Mumbai or Mainnet.`);
    } else {
      setError(null);
    }
  };

  const connectWallet = async () => {
    if (!window.ethereum) {
      setError('MetaMask or compatible wallet not found. Please install a Web3 wallet.');
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });

      if (accounts.length > 0) {
        const account = accounts[0];
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        const numericChainId = parseInt(chainId, 16);

        setAccount(account);
        setChainId(numericChainId);

        // Check if we're on a supported network
        if (!SUPPORTED_NETWORKS[numericChainId]) {
          // Try to switch to Polygon Mumbai (testnet)
          await switchNetwork(80001);
        }

        onConnect?.(account, numericChainId);
      }
    } catch (error) {
      console.error('Connection error:', error);
      if (error.code === 4001) {
        setError('Connection rejected by user');
      } else {
        setError(`Connection failed: ${error.message}`);
      }
    } finally {
      setIsConnecting(false);
    }
  };

  const switchNetwork = async (targetChainId) => {
    if (!window.ethereum) return;

    const network = SUPPORTED_NETWORKS[targetChainId];
    if (!network) return;

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }]
      });
    } catch (switchError) {
      // If network doesn't exist, add it
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: `0x${targetChainId.toString(16)}`,
              chainName: network.name,
              nativeCurrency: network.nativeCurrency,
              rpcUrls: [network.rpcUrl],
              blockExplorerUrls: [network.blockExplorer]
            }]
          });
        } catch (addError) {
          setError(`Failed to add network: ${addError.message}`);
        }
      } else {
        setError(`Failed to switch network: ${switchError.message}`);
      }
    }
  };

  const disconnect = () => {
    setAccount(null);
    setChainId(null);
    setError(null);
    onDisconnect?.();
  };

  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getCurrentNetwork = () => {
    return SUPPORTED_NETWORKS[chainId] || { name: 'Unknown Network' };
  };

  if (account) {
    return (
      <div className={`bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg p-4 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <div>
              <div className="font-semibold">{formatAddress(account)}</div>
              <div className="text-sm opacity-90">{getCurrentNetwork().name}</div>
            </div>
          </div>
          <button
            onClick={disconnect}
            className="px-3 py-1 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-md text-sm transition-all"
          >
            Disconnect
          </button>
        </div>
        
        {error && (
          <div className="mt-2 p-2 bg-red-500 bg-opacity-30 rounded text-sm">
            ⚠️ {error}
          </div>
        )}
        
        {chainId && !SUPPORTED_NETWORKS[chainId] && (
          <div className="mt-2 flex items-center justify-between p-2 bg-yellow-500 bg-opacity-30 rounded text-sm">
            <span>⚠️ Switch to supported network</span>
            <button
              onClick={() => switchNetwork(80001)}
              className="px-2 py-1 bg-white bg-opacity-20 hover:bg-opacity-30 rounded text-xs"
            >
              Switch to Mumbai
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center ${className}`}>
      <div className="mb-4">
        <div className="w-16 h-16 mx-auto bg-gradient-to-r from-purple-500 to-blue-600 rounded-full flex items-center justify-center">
          <span className="text-2xl">🔗</span>
        </div>
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        Connect Your Wallet
      </h3>
      
      <p className="text-gray-600 mb-4 text-sm">
        Connect your Web3 wallet to participate in ASI Core tasks and earn rewards
      </p>
      
      <button
        onClick={connectWallet}
        disabled={isConnecting}
        className={`px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium transition-all ${
          isConnecting 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:from-purple-700 hover:to-blue-700 transform hover:scale-105'
        }`}
      >
        {isConnecting ? (
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Connecting...</span>
          </div>
        ) : (
          'Connect Wallet'
        )}
      </button>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="mt-4 text-xs text-gray-500">
        Supports MetaMask, WalletConnect, and other Web3 wallets
      </div>
    </div>
  );
}
