import React from 'react';

const ClaimTicketModal = ({ isOpen, onClose, ticket, onConfirm, loading }) => {
  if (!isOpen || !ticket) return null;

  const getDifficultyColor = (difficulty) => {
    const colors = {
      1: 'text-green-600',
      2: 'text-blue-600', 
      3: 'text-yellow-600',
      4: 'text-orange-600',
      5: 'text-red-600'
    };
    return colors[difficulty] || 'text-gray-600';
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        ></div>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div>
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
              <span className="text-2xl">🎫</span>
            </div>
            
            <div className="mt-3 text-center sm:mt-5">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Claim Ticket
              </h3>
              
              <div className="mt-4 text-left">
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {ticket.title}
                  </h4>
                  
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center justify-between">
                      <span>Category:</span>
                      <span className="font-medium capitalize">{ticket.category}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Difficulty:</span>
                      <span className={`font-medium ${getDifficultyColor(ticket.difficulty)}`}>
                        Level {ticket.difficulty}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Reward:</span>
                      <span className="font-medium">
                        💎 {ticket.creditReward} Credits + ⭐ {ticket.reputationWeight} Rep
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span>Estimated Time:</span>
                      <span className="font-medium">~{ticket.estimatedHours} hours</span>
                    </div>
                  </div>
                </div>

                {/* Required Skills */}
                <div className="mb-4">
                  <h5 className="text-sm font-medium text-gray-900 mb-2">Required Skills:</h5>
                  <div className="flex flex-wrap gap-1">
                    {ticket.skillTags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Requirements */}
                {ticket.requiresOneHuman && (
                  <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center">
                      <span className="text-yellow-600 mr-2">🔐</span>
                      <span className="text-sm text-yellow-800">
                        This ticket requires One-Human verification
                      </span>
                    </div>
                  </div>
                )}

                {/* Deadlines */}
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <h5 className="text-sm font-medium text-blue-900 mb-1">Important Deadlines:</h5>
                  <div className="text-sm text-blue-800">
                    <div>• Claim expires after 7 days if no progress</div>
                    <div>• Submission deadline: 14 days from claim</div>
                    <div>• Unclaimed tickets return to open status</div>
                  </div>
                </div>

                <div className="text-sm text-gray-600">
                  <p className="mb-2">
                    <strong>By claiming this ticket, you agree to:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Complete the work within the estimated timeframe</li>
                    <li>Follow the Definition of Done requirements</li>
                    <li>Submit quality evidence for verification</li>
                    <li>Participate in the review process if needed</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button
              type="button"
              disabled={loading}
              onClick={onConfirm}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Claiming...
                </>
              ) : (
                'Claim Ticket'
              )}
            </button>
            
            <button
              type="button"
              onClick={onClose}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:col-start-1 sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClaimTicketModal;