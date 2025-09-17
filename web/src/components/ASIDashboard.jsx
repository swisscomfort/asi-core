import { useState, useEffect } from 'react';
import WalletConnect from './wallet/WalletConnect';
import WalletInfo from './wallet/WalletInfo';
import TaskRegistry from './TaskRegistry';
import IPFSManager from './IPFSManager';

export default function ASIDashboard({ className = "" }) {
  const [activeTab, setActiveTab] = useState('tasks');
  const [account, setAccount] = useState(null);
  const [chainId, setChainId] = useState(null);

  const handleWalletConnect = (newAccount, newChainId) => {
    setAccount(newAccount);
    setChainId(newChainId);
  };

  const handleWalletDisconnect = () => {
    setAccount(null);
    setChainId(null);
  };

  const tabs = [
    { id: 'tasks', label: 'Task Registry', icon: '📋' },
    { id: 'wallet', label: 'Wallet', icon: '💳' },
    { id: 'storage', label: 'IPFS Storage', icon: '📁' },
    { id: 'stats', label: 'Statistics', icon: '📊' }
  ];

  return (
    <div className={`bg-white border border-gray-200 rounded-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">ASI Core Dashboard</h1>
            <p className="text-purple-100 text-sm">
              Decentralized Task Registry & Contributor Platform
            </p>
          </div>
          
          {/* Quick Stats */}
          <div className="text-right">
            <div className="text-sm opacity-90">
              {account ? `Connected: ${account.slice(0, 8)}...` : 'Not Connected'}
            </div>
            <div className="text-xs opacity-75">
              {chainId ? `Chain ID: ${chainId}` : 'No Network'}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'tasks' && (
          <div>
            {!account ? (
              <div className="text-center py-8">
                <div className="mb-6">
                  <div className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🔗</span>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Connect Wallet to Access Tasks
                </h3>
                <p className="text-gray-600 mb-6">
                  Connect your Web3 wallet to view and claim available tasks
                </p>
                <div className="max-w-md mx-auto">
                  <WalletConnect
                    onConnect={handleWalletConnect}
                    onDisconnect={handleWalletDisconnect}
                  />
                </div>
              </div>
            ) : (
              <TaskRegistry
                account={account}
                chainId={chainId}
                className="border-0 bg-transparent"
              />
            )}
          </div>
        )}

        {activeTab === 'wallet' && (
          <div className="space-y-6">
            <WalletConnect
              onConnect={handleWalletConnect}
              onDisconnect={handleWalletDisconnect}
            />
            
            {account && (
              <WalletInfo
                account={account}
                chainId={chainId}
              />
            )}
          </div>
        )}

        {activeTab === 'storage' && (
          <IPFSManager className="border-0 bg-transparent" />
        )}

        {activeTab === 'stats' && (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Statistics Coming Soon
            </h3>
            <p className="text-gray-600 text-sm">
              Detailed analytics and contributor statistics will be available here
            </p>
            
            {/* Placeholder stats */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">13</div>
                <div className="text-sm text-blue-800">Total Tasks</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">34,500</div>
                <div className="text-sm text-green-800">Total Bounties (ASI)</div>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">0</div>
                <div className="text-sm text-purple-800">Active Contributors</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>🌐 Decentralized</span>
            <span>🔒 Secure</span>
            <span>💰 Rewarded</span>
          </div>
          <div>
            <a
              href="https://github.com/swisscomfort/asi-core"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800"
            >
              GitHub →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}