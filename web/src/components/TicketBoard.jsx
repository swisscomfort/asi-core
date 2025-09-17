import React, { useState, useEffect } from 'react';
import { useTicketContract } from '../hooks/useTicketContract';
import { useWallet } from '../hooks/useWallet';
import TicketCard from './TicketCard';
import TicketFilters from './TicketFilters';
import ClaimTicketModal from './ClaimTicketModal';
import { mockTickets } from '../data/mockTickets';

const TicketBoard = () => {
  const [tickets, setTickets] = useState([]);
  const [filteredTickets, setFilteredTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: 'all',
    difficulty: 'all',
    status: 'open',
    search: ''
  });

  const { wallet, connectWallet, isConnected } = useWallet();
  const { 
    claimTicket, 
    submitTicket, 
    getTickets, 
    getUserStats,
    loading: contractLoading 
  } = useTicketContract();

  useEffect(() => {
    loadTickets();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [tickets, filters]);

  const loadTickets = async () => {
    try {
      setLoading(true);
      
      // In production: load from smart contract
      // const contractTickets = await getTickets();
      
      // For MVP: use mock data
      const allTickets = mockTickets;
      
      setTickets(allTickets);
    } catch (error) {
      console.error('Error loading tickets:', error);
      // Fallback to mock data
      setTickets(mockTickets);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...tickets];

    // Category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(ticket => ticket.category === filters.category);
    }

    // Difficulty filter
    if (filters.difficulty !== 'all') {
      filtered = filtered.filter(ticket => ticket.difficulty === parseInt(filters.difficulty));
    }

    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(ticket => ticket.status === filters.status);
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(ticket => 
        ticket.title.toLowerCase().includes(searchLower) ||
        ticket.description.toLowerCase().includes(searchLower) ||
        ticket.skillTags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    setFilteredTickets(filtered);
  };

  const handleTicketClaim = async (ticketId) => {
    if (!isConnected) {
      await connectWallet();
      return;
    }

    try {
      const ticket = tickets.find(t => t.id === ticketId);
      setSelectedTicket(ticket);
      setIsClaimModalOpen(true);
    } catch (error) {
      console.error('Error claiming ticket:', error);
    }
  };

  const handleClaimConfirm = async () => {
    if (!selectedTicket) return;

    try {
      // In production: call smart contract
      // await claimTicket(selectedTicket.id);
      
      // For MVP: update local state
      setTickets(prev => prev.map(ticket => 
        ticket.id === selectedTicket.id 
          ? { ...ticket, status: 'claimed', claimedBy: wallet?.address }
          : ticket
      ));

      setIsClaimModalOpen(false);
      setSelectedTicket(null);
    } catch (error) {
      console.error('Error claiming ticket:', error);
    }
  };

  const getStatsData = () => {
    const stats = {
      total: tickets.length,
      open: tickets.filter(t => t.status === 'open').length,
      claimed: tickets.filter(t => t.status === 'claimed').length,
      completed: tickets.filter(t => t.status === 'approved').length,
    };

    return stats;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-lg">Loading tickets...</span>
      </div>
    );
  }

  const stats = getStatsData();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🎫 Oryn Ticket Board
              </h1>
              <div className="ml-4 flex items-center space-x-4 text-sm text-gray-600">
                <span className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                  {stats.open} Open
                </span>
                <span className="flex items-center">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
                  {stats.claimed} Claimed
                </span>
                <span className="flex items-center">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>
                  {stats.completed} Completed
                </span>
              </div>
            </div>
            
            {/* Wallet Connection */}
            <div className="flex items-center space-x-4">
              {isConnected ? (
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>{wallet?.address?.slice(0, 6)}...{wallet?.address?.slice(-4)}</span>
                </div>
              ) : (
                <button
                  onClick={connectWallet}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Connect Wallet
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6">
          <TicketFilters
            filters={filters}
            onFiltersChange={setFilters}
            totalTickets={tickets.length}
            filteredCount={filteredTickets.length}
          />
        </div>

        {/* Tickets Grid */}
        {filteredTickets.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No tickets found
            </h3>
            <p className="text-gray-600">
              Try adjusting your filters or check back later for new tickets.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTickets.map((ticket) => (
              <TicketCard
                key={ticket.id}
                ticket={ticket}
                onClaim={handleTicketClaim}
                isConnected={isConnected}
                userAddress={wallet?.address}
              />
            ))}
          </div>
        )}

        {/* Load More Button */}
        {filteredTickets.length > 0 && filteredTickets.length < tickets.length && (
          <div className="text-center mt-8">
            <button
              onClick={loadTickets}
              disabled={loading}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Loading...' : 'Load More Tickets'}
            </button>
          </div>
        )}
      </div>

      {/* Claim Modal */}
      <ClaimTicketModal
        isOpen={isClaimModalOpen}
        onClose={() => setIsClaimModalOpen(false)}
        ticket={selectedTicket}
        onConfirm={handleClaimConfirm}
        loading={contractLoading}
      />
    </div>
  );
};

export default TicketBoard;