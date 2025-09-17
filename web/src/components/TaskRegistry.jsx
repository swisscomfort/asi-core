import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

export default function TaskRegistry({ account, chainId, className = "" }) {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedMilestone, setSelectedMilestone] = useState('all');
  const [filter, setFilter] = useState('all'); // 'all', 'open', 'claimed', 'mine'
  const [myTasks, setMyTasks] = useState([]);

  // Mock task data (in production, this comes from smart contract)
  const mockTasks = [
    {
      id: 'M0-T001',
      title: 'Org Setup + CI + Security Foundation',
      description: 'Set up GitHub org, CI pipelines, and security policies',
      bounty: { amount: 1500, token: 'ASI' },
      status: 'Open',
      milestone: 'M0',
      claimer: null,
      difficulty: 'Medium',
      estimatedHours: 8,
      tags: ['DevOps', 'Security', 'CI/CD'],
      dependencies: [],
      deadline: '2025-10-15'
    },
    {
      id: 'M0-T002', 
      title: 'Local Crypto Library (AES+HKDF+Tests)',
      description: 'Implement local cryptography library with test vectors',
      bounty: { amount: 2000, token: 'ASI' },
      status: 'Open',
      milestone: 'M0',
      claimer: null,
      difficulty: 'Hard',
      estimatedHours: 12,
      tags: ['Cryptography', 'TypeScript', 'Testing'],
      dependencies: ['M0-T001'],
      deadline: '2025-10-20'
    },
    {
      id: 'M1-T001',
      title: 'PWA Skeleton (Chat+Storage Views)',
      description: 'Create Progressive Web App skeleton with chat and storage interfaces',
      bounty: { amount: 3000, token: 'ASI' },
      status: 'Claimed',
      milestone: 'M1',
      claimer: account, // User has claimed this task
      difficulty: 'Medium',
      estimatedHours: 16,
      tags: ['React', 'PWA', 'UI/UX'],
      dependencies: ['M0-T001', 'M0-T002'],
      deadline: '2025-10-25'
    },
    {
      id: 'M1-T002',
      title: 'Wallet Login (Passkeys + DID Support)', 
      description: 'Implement Web3 wallet login with optional passkeys and DID',
      bounty: { amount: 2800, token: 'ASI' },
      status: 'Open',
      milestone: 'M1',
      claimer: null,
      difficulty: 'Hard',
      estimatedHours: 14,
      tags: ['Web3', 'Authentication', 'DID'],
      dependencies: ['M1-T001'],
      deadline: '2025-11-01'
    },
    {
      id: 'M2-T001',
      title: 'TaskRegistry Smart Contract Deployment',
      description: 'Deploy and verify TaskRegistry contract on testnet/mainnet',
      bounty: { amount: 3000, token: 'ASI' },
      status: 'Open',
      milestone: 'M2',
      claimer: null,
      difficulty: 'Hard',
      estimatedHours: 10,
      tags: ['Solidity', 'Deployment', 'Web3'],
      dependencies: ['M1-T001', 'M1-T002'],
      deadline: '2025-11-05'
    }
  ];

  useEffect(() => {
    loadTasks();
  }, [account, chainId]);

  const loadTasks = async () => {
    setIsLoading(true);
    try {
      // In production: fetch from smart contract
      // For now: use mock data
      setTasks(mockTasks);
      
      // Filter tasks claimed by current user
      const userTasks = mockTasks.filter(task => 
        task.claimer && task.claimer.toLowerCase() === account?.toLowerCase()
      );
      setMyTasks(userTasks);
      
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const claimTask = async (taskId) => {
    if (!account) {
      alert('Please connect your wallet first');
      return;
    }

    try {
      // In production: call smart contract
      console.log('Claiming task:', taskId);
      
      // Mock: update local state
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId 
            ? { ...task, status: 'Claimed', claimer: account }
            : task
        )
      );
      
      alert(`Task ${taskId} claimed successfully!`);
      
    } catch (error) {
      console.error('Error claiming task:', error);
      alert('Failed to claim task. Please try again.');
    }
  };

  const getFilteredTasks = () => {
    let filtered = tasks;

    // Filter by milestone
    if (selectedMilestone !== 'all') {
      filtered = filtered.filter(task => task.milestone === selectedMilestone);
    }

    // Filter by status/ownership
    switch (filter) {
      case 'open':
        filtered = filtered.filter(task => task.status === 'Open');
        break;
      case 'claimed':
        filtered = filtered.filter(task => task.status === 'Claimed');
        break;
      case 'mine':
        filtered = filtered.filter(task => 
          task.claimer && task.claimer.toLowerCase() === account?.toLowerCase()
        );
        break;
      default:
        // Show all
        break;
    }

    return filtered;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Open': return 'bg-green-100 text-green-800 border-green-200';
      case 'Claimed': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Submitted': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Approved': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Paid': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-700';
      case 'Medium': return 'bg-yellow-100 text-yellow-700';
      case 'Hard': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const milestones = ['all', 'M0', 'M1', 'M2'];
  const filteredTasks = getFilteredTasks();

  return (
    <div className={`bg-white border border-gray-200 rounded-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Task Registry</h2>
            <p className="text-gray-600 text-sm">
              Claim tasks, contribute to ASI Core, and earn rewards
            </p>
          </div>
          <button
            onClick={loadTasks}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? '🔄' : '↻'} Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4">
          {/* Milestone Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Milestone
            </label>
            <select
              value={selectedMilestone}
              onChange={(e) => setSelectedMilestone(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              {milestones.map(milestone => (
                <option key={milestone} value={milestone}>
                  {milestone === 'all' ? 'All Milestones' : milestone}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">All Tasks</option>
              <option value="open">Open Tasks</option>
              <option value="claimed">Claimed Tasks</option>
              <option value="mine">My Tasks</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{tasks.filter(t => t.status === 'Open').length}</div>
            <div className="text-sm text-gray-600">Open Tasks</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-600">{myTasks.length}</div>
            <div className="text-sm text-gray-600">My Tasks</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              {tasks.reduce((sum, task) => sum + task.bounty.amount, 0)}
            </div>
            <div className="text-sm text-gray-600">Total Bounties</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">
              {myTasks.reduce((sum, task) => sum + task.bounty.amount, 0)}
            </div>
            <div className="text-sm text-gray-600">My Earnings</div>
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="p-6">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📋</div>
            <div className="text-gray-600">No tasks match your filters</div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredTasks.map(task => (
              <div key={task.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                {/* Task Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h3 className="font-semibold text-gray-900">{task.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(task.status)}`}>
                        {task.status}
                      </span>
                    </div>
                    <p className="text-gray-600 text-sm">{task.description}</p>
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-lg font-bold text-purple-600">
                      {task.bounty.amount} {task.bounty.token}
                    </div>
                    <div className="text-xs text-gray-500">Bounty</div>
                  </div>
                </div>

                {/* Task Details */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                  <span className="flex items-center">
                    🏷️ {task.id}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(task.difficulty)}`}>
                    {task.difficulty}
                  </span>
                  <span>⏱️ ~{task.estimatedHours}h</span>
                  <span>📅 Due: {new Date(task.deadline).toLocaleDateString()}</span>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {task.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Dependencies */}
                {task.dependencies.length > 0 && (
                  <div className="mb-3 text-sm">
                    <span className="text-gray-600">Requires: </span>
                    <span className="text-blue-600">{task.dependencies.join(', ')}</span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    {task.claimer && (
                      <span>Claimed by: {task.claimer === account ? 'You' : `${task.claimer.slice(0, 8)}...`}</span>
                    )}
                  </div>
                  
                  {account && task.status === 'Open' && (
                    <button
                      onClick={() => claimTask(task.id)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      🎯 Claim Task
                    </button>
                  )}
                  
                  {task.claimer === account && task.status === 'Claimed' && (
                    <div className="flex space-x-2">
                      <button className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-sm hover:bg-blue-200">
                        📤 Submit Evidence
                      </button>
                      <button className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm hover:bg-gray-200">
                        📋 View Details
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}