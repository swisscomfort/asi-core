import React from 'react';

const TicketFilters = ({ filters, onFiltersChange, totalTickets, filteredCount }) => {
  const updateFilter = (key, value) => {
    onFiltersChange(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    onFiltersChange({
      category: 'all',
      difficulty: 'all', 
      status: 'open',
      search: ''
    });
  };

  const categories = [
    { value: 'all', label: 'All Categories', icon: '📋' },
    { value: 'security', label: 'Security', icon: '🛡️' },
    { value: 'ui', label: 'UI/UX', icon: '🎨' },
    { value: 'docs', label: 'Documentation', icon: '📚' },
    { value: 'translation', label: 'Translation', icon: '🌐' },
    { value: 'testing', label: 'Testing', icon: '🧪' },
    { value: 'infrastructure', label: 'Infrastructure', icon: '⚙️' }
  ];

  const difficulties = [
    { value: 'all', label: 'All Levels' },
    { value: '1', label: 'Level 1 (Beginner)' },
    { value: '2', label: 'Level 2 (Intermediate)' },
    { value: '3', label: 'Level 3 (Advanced)' },
    { value: '4', label: 'Level 4 (Expert)' },
    { value: '5', label: 'Level 5 (Master)' }
  ];

  const statuses = [
    { value: 'all', label: 'All Status' },
    { value: 'open', label: 'Open' },
    { value: 'claimed', label: 'Claimed' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'approved', label: 'Approved' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Search Bar */}
      <div className="mb-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className="text-gray-400">🔍</span>
          </div>
          <input
            type="text"
            placeholder="Search tickets by title, description, or skills..."
            value={filters.search}
            onChange={(e) => updateFilter('search', e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
      </div>

      {/* Filter Controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => updateFilter('category', e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {categories.map((category) => (
              <option key={category.value} value={category.value}>
                {category.icon} {category.label}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Difficulty
          </label>
          <select
            value={filters.difficulty}
            onChange={(e) => updateFilter('difficulty', e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {difficulties.map((difficulty) => (
              <option key={difficulty.value} value={difficulty.value}>
                {difficulty.label}
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
            value={filters.status}
            onChange={(e) => updateFilter('status', e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            {statuses.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Clear Filters Button */}
        <div className="flex items-end">
          <button
            onClick={clearFilters}
            className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:border-gray-500 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Results Counter */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Showing {filteredCount} of {totalTickets} tickets
        </span>
        
        {/* Active Filters Display */}
        <div className="flex items-center space-x-2">
          {filters.category !== 'all' && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
              {categories.find(c => c.value === filters.category)?.label}
              <button 
                onClick={() => updateFilter('category', 'all')}
                className="ml-1 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          )}
          
          {filters.difficulty !== 'all' && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800">
              Level {filters.difficulty}
              <button 
                onClick={() => updateFilter('difficulty', 'all')}
                className="ml-1 text-green-600 hover:text-green-800"
              >
                ×
              </button>
            </span>
          )}
          
          {filters.status !== 'open' && filters.status !== 'all' && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-yellow-100 text-yellow-800">
              {filters.status}
              <button 
                onClick={() => updateFilter('status', 'open')}
                className="ml-1 text-yellow-600 hover:text-yellow-800"
              >
                ×
              </button>
            </span>
          )}
          
          {filters.search && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
              "{filters.search}"
              <button 
                onClick={() => updateFilter('search', '')}
                className="ml-1 text-purple-600 hover:text-purple-800"
              >
                ×
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketFilters;