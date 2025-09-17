import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

export default function WalletInfo({ account, chainId, className = "" }) {
  const [balance, setBalance] = useState('0');
  const [asiBalance, setAsiBalance] = useState('0');
  const [sbtCount, setSbtCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // ASI Token contract address (will be updated after deployment)
  const ASI_TOKEN_ADDRESS = '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0'; // Mock address
  const SBT_CONTRACT_ADDRESS = '0x'; // ContributorSBT contract address

  const NETWORK_INFO = {
    80001: {
      name: 'Polygon Mumbai',
      symbol: 'MATIC',
      explorer: 'https://mumbai.polygonscan.com'
    },
    137: {
      name: 'Polygon Mainnet', 
      symbol: 'MATIC',
      explorer: 'https://polygonscan.com'
    }
  };

  useEffect(() => {
    if (account && window.ethereum) {
      fetchBalances();
    }
  }, [account, chainId]);

  const fetchBalances = async () => {
    if (!account || !window.ethereum) return;
    
    setIsLoading(true);
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      
      // Get native token balance (MATIC)
      const nativeBalance = await provider.getBalance(account);
      setBalance(ethers.formatEther(nativeBalance));

      // Get ASI token balance (if contract exists)
      try {
        const asiContract = new ethers.Contract(
          ASI_TOKEN_ADDRESS,
          ['function balanceOf(address) view returns (uint256)'],
          provider
        );
        const asiTokenBalance = await asiContract.balanceOf(account);
        setAsiBalance(ethers.formatEther(asiTokenBalance));
      } catch (error) {
        // ASI contract not deployed yet
        setAsiBalance('0');
      }

      // Get SBT count (reputation badges)
      try {
        if (SBT_CONTRACT_ADDRESS && SBT_CONTRACT_ADDRESS !== '0x') {
          const sbtContract = new ethers.Contract(
            SBT_CONTRACT_ADDRESS,
            ['function balanceOf(address) view returns (uint256)'],
            provider
          );
          const sbtBalance = await sbtContract.balanceOf(account);
          setSbtCount(Number(sbtBalance));
        }
      } catch (error) {
        // SBT contract not deployed yet
        setSbtCount(0);
      }

    } catch (error) {
      console.error('Error fetching balances:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatBalance = (balance, decimals = 4) => {
    const num = parseFloat(balance);
    if (num === 0) return '0';
    if (num < 0.0001) return '< 0.0001';
    return num.toFixed(decimals);
  };

  const getNetworkInfo = () => {
    return NETWORK_INFO[chainId] || { name: 'Unknown', symbol: 'ETH', explorer: '#' };
  };

  const openInExplorer = () => {
    const network = getNetworkInfo();
    if (network.explorer !== '#') {
      window.open(`${network.explorer}/address/${account}`, '_blank');
    }
  };

  if (!account) {
    return null;
  }

  const network = getNetworkInfo();

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Wallet Info</h3>
        <button
          onClick={openInExplorer}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View on Explorer →
        </button>
      </div>

      {/* Account Address */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-1">Address</div>
        <div className="font-mono text-sm bg-gray-50 p-2 rounded border">
          {account}
        </div>
      </div>

      {/* Network Info */}
      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-1">Network</div>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${chainId ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm font-medium">{network.name}</span>
        </div>
      </div>

      {/* Balances */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Native Token Balance */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="text-sm text-blue-600 font-medium">{network.symbol} Balance</div>
          <div className="text-lg font-bold text-blue-900">
            {isLoading ? (
              <div className="w-16 h-6 bg-blue-200 rounded animate-pulse"></div>
            ) : (
              `${formatBalance(balance)} ${network.symbol}`
            )}
          </div>
        </div>

        {/* ASI Token Balance */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
          <div className="text-sm text-purple-600 font-medium">ASI Tokens</div>
          <div className="text-lg font-bold text-purple-900">
            {isLoading ? (
              <div className="w-16 h-6 bg-purple-200 rounded animate-pulse"></div>
            ) : (
              `${formatBalance(asiBalance)} ASI`
            )}
          </div>
          <div className="text-xs text-purple-600 mt-1">Task Rewards</div>
        </div>

        {/* SBT Count */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="text-sm text-green-600 font-medium">Reputation</div>
          <div className="text-lg font-bold text-green-900">
            {isLoading ? (
              <div className="w-16 h-6 bg-green-200 rounded animate-pulse"></div>
            ) : (
              `${sbtCount} SBTs`
            )}
          </div>
          <div className="text-xs text-green-600 mt-1">Completed Tasks</div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="mt-4 flex justify-center">
        <button
          onClick={fetchBalances}
          disabled={isLoading}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            isLoading
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
              <span>Refreshing...</span>
            </div>
          ) : (
            '🔄 Refresh Balances'
          )}
        </button>
      </div>

      {/* Contract Addresses (for debugging) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <div>ASI Token: {ASI_TOKEN_ADDRESS}</div>
            <div>SBT Contract: {SBT_CONTRACT_ADDRESS || 'Not deployed'}</div>
          </div>
        </div>
      )}
    </div>
  );
}
