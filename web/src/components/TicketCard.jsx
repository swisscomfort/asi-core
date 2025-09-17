import React from 'react';

const TicketCard = ({ ticket, onClaim, isConnected, userAddress }) => {
  const getDifficultyColor = (difficulty) => {
    const colors = {
      1: 'bg-green-100 text-green-800',
      2: 'bg-blue-100 text-blue-800', 
      3: 'bg-yellow-100 text-yellow-800',
      4: 'bg-orange-100 text-orange-800',
      5: 'bg-red-100 text-red-800'
    };
    return colors[difficulty] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      security: '🛡️',
      ui: '🎨',
      docs: '📚',
      translation: '🌐',
      testing: '🧪',
      infrastructure: '⚙️'
    };
    return icons[category] || '📋';
  };

  const getStatusBadge = (status) => {
    const styles = {
      open: 'bg-green-100 text-green-800',
      claimed: 'bg-yellow-100 text-yellow-800',
      submitted: 'bg-blue-100 text-blue-800',
      approved: 'bg-purple-100 text-purple-800',
      disputed: 'bg-red-100 text-red-800'
    };

    const labels = {
      open: 'Open',
      claimed: 'Claimed',
      submitted: 'Submitted',
      approved: 'Approved',
      disputed: 'Disputed'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  const canClaim = () => {
    if (ticket.status !== 'open') return false;
    if (!isConnected) return true; // Show button to prompt connection
    if (ticket.requiresOneHuman && !ticket.userHasOneHuman) return false;
    return true;
  };

  const getClaimButtonText = () => {
    if (!isConnected) return 'Connect Wallet to Claim';
    if (ticket.status === 'claimed' && ticket.claimedBy === userAddress) return 'You claimed this';
    if (ticket.status === 'claimed') return 'Already Claimed';
    if (ticket.status !== 'open') return 'Not Available';
    if (ticket.requiresOneHuman && !ticket.userHasOneHuman) return 'One-Human Required';
    return 'Claim Ticket';
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      {/* Card Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getCategoryIcon(ticket.category)}</span>
            <span className="text-sm font-medium text-gray-600 capitalize">
              {ticket.category}
            </span>
          </div>
          {getStatusBadge(ticket.status)}
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {ticket.title}
        </h3>
        
        <p className="text-sm text-gray-600 line-clamp-3 mb-3">
          {ticket.description}
        </p>
      </div>

      {/* Card Body */}
      <div className="p-4">
        {/* Rewards & Difficulty */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <span className="text-lg">💎</span>
              <span className="text-sm font-medium text-gray-900">
                {ticket.creditReward} Credits
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-lg">⭐</span>
              <span className="text-sm font-medium text-gray-900">
                +{ticket.reputationWeight} Rep
              </span>
            </div>
          </div>
          
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(ticket.difficulty)}`}>
            Level {ticket.difficulty}
          </span>
        </div>

        {/* Skills Tags */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {ticket.skillTags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
              >
                {tag}
              </span>
            ))}
            {ticket.skillTags.length > 3 && (
              <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                +{ticket.skillTags.length - 3} more
              </span>
            )}
          </div>
        </div>

        {/* Estimated Time */}
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span className="mr-1">⏱️</span>
          <span>~{ticket.estimatedHours}h estimated</span>
        </div>

        {/* One-Human Requirement */}
        {ticket.requiresOneHuman && (
          <div className="flex items-center text-sm text-blue-600 mb-4">
            <span className="mr-1">🔐</span>
            <span>One-Human verification required</span>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={() => canClaim() && onClaim(ticket.id)}
          disabled={!canClaim() || (ticket.status === 'claimed' && ticket.claimedBy !== userAddress)}
          className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            canClaim() && ticket.status === 'open'
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : ticket.status === 'claimed' && ticket.claimedBy === userAddress
              ? 'bg-green-100 text-green-800 cursor-default'
              : 'bg-gray-100 text-gray-500 cursor-not-allowed'
          }`}
        >
          {getClaimButtonText()}
        </button>

        {/* Additional Info for Claimed Tickets */}
        {ticket.status === 'claimed' && ticket.claimedBy && (
          <div className="mt-2 text-xs text-gray-500 text-center">
            {ticket.claimedBy === userAddress 
              ? `Claimed by you • Deadline: ${new Date(ticket.submitDeadline).toLocaleDateString()}`
              : `Claimed by ${ticket.claimedBy.slice(0, 6)}...${ticket.claimedBy.slice(-4)}`
            }
          </div>
        )}
      </div>
    </div>
  );
};

export default TicketCard;