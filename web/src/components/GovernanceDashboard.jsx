import React, { useState, useEffect } from "react";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  UserGroupIcon,
  DocumentTextIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";

const GovernanceDashboard = ({ userAddress, tokenBalance }) => {
  const [proposals, setProposals] = useState([]);
  const [userVotes, setUserVotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState({});

  // Mock proposals data (in production, fetch from Snapshot.org API)
  const mockProposals = [
    {
      id: "proposal-1",
      title: "Erhöhung der Reflexions-Belohnungen",
      description:
        "Vorschlag zur Erhöhung der $MEM-Belohnungen für Reflexionen von 1 auf 2 Token",
      author: "0x742d35Cc6636C0532925a3b8Ad21Bb93C7C9cdeb",
      startTime: new Date("2025-09-01T00:00:00Z"),
      endTime: new Date("2025-09-15T23:59:59Z"),
      status: "active",
      choices: ["Ja", "Nein", "Enthaltung"],
      votes: {
        Ja: 1250000,
        Nein: 450000,
        Enthaltung: 100000,
      },
      totalVotes: 1800000,
      quorum: 1000000,
      type: "single-choice",
    },
    {
      id: "proposal-2",
      title: "Neue Kategorien für Muster-Erkennung",
      description:
        "Einführung neuer Kategorien für die automatische Mustererkennung: Gesundheit, Produktivität, Beziehungen",
      author: "0x1234567890123456789012345678901234567890",
      startTime: new Date("2025-08-15T00:00:00Z"),
      endTime: new Date("2025-08-30T23:59:59Z"),
      status: "closed",
      choices: [
        "Alle Kategorien",
        "Nur Gesundheit",
        "Nur Produktivität",
        "Ablehnen",
      ],
      votes: {
        "Alle Kategorien": 2100000,
        "Nur Gesundheit": 300000,
        "Nur Produktivität": 150000,
        Ablehnen: 200000,
      },
      totalVotes: 2750000,
      quorum: 1000000,
      type: "single-choice",
      result: "Alle Kategorien",
    },
    {
      id: "proposal-3",
      title: "Entwickler-Funding Program Q4 2025",
      description:
        "Verteilung von 1M $MEM Token für Entwickler-Incentives im Q4 2025",
      author: "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
      startTime: new Date("2025-09-10T00:00:00Z"),
      endTime: new Date("2025-09-24T23:59:59Z"),
      status: "upcoming",
      choices: ["Zustimmen", "Ablehnen", "Betrag reduzieren"],
      votes: {},
      totalVotes: 0,
      quorum: 1500000,
      type: "single-choice",
    },
  ];

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setProposals(mockProposals);

      // Mock user votes
      setUserVotes({
        "proposal-2": "Alle Kategorien",
      });

      setLoading(false);
    }, 1000);
  }, []);

  const canVote = (proposal) => {
    return (
      proposal.status === "active" &&
      tokenBalance > 0 &&
      !userVotes[proposal.id] &&
      new Date() <= proposal.endTime
    );
  };

  const handleVote = async (proposalId, choice) => {
    if (!userAddress || voting[proposalId]) return;

    setVoting((prev) => ({ ...prev, [proposalId]: true }));

    try {
      // In production, this would interact with Snapshot.org or on-chain voting
      // For now, we'll simulate the vote
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Update local state
      setUserVotes((prev) => ({ ...prev, [proposalId]: choice }));

      // Update proposal votes (mock)
      setProposals((prev) =>
        prev.map((proposal) => {
          if (proposal.id === proposalId) {
            return {
              ...proposal,
              votes: {
                ...proposal.votes,
                [choice]: (proposal.votes[choice] || 0) + tokenBalance,
              },
              totalVotes: proposal.totalVotes + tokenBalance,
            };
          }
          return proposal;
        })
      );

      alert(`✅ Stimme für "${choice}" erfolgreich abgegeben!`);
    } catch (error) {
      console.error("Voting error:", error);
      alert("❌ Fehler beim Abstimmen. Bitte versuche es erneut.");
    } finally {
      setVoting((prev) => ({ ...prev, [proposalId]: false }));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "text-green-600 bg-green-100";
      case "closed":
        return "text-gray-600 bg-gray-100";
      case "upcoming":
        return "text-blue-600 bg-blue-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "active":
        return "Aktiv";
      case "closed":
        return "Beendet";
      case "upcoming":
        return "Bevorstehend";
      default:
        return status;
    }
  };

  const calculatePercentage = (votes, total) => {
    if (total === 0) return 0;
    return Math.round((votes / total) * 100);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Governance Dashboard
            </h2>
            <p className="text-gray-600 mt-1">
              Stimme über die Zukunft des ASI-Projekts ab
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600">Deine Stimmkraft</div>
            <div className="text-2xl font-bold text-purple-600">
              {tokenBalance.toLocaleString()} $MEM
            </div>
          </div>
        </div>
      </div>

      {/* Voting Power Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start">
          <UserGroupIcon className="h-6 w-6 text-purple-500 mt-1" />
          <div className="ml-3">
            <h4 className="text-sm font-medium text-purple-800">
              Wie funktioniert das Abstimmen?
            </h4>
            <p className="text-sm text-purple-700 mt-1">
              Deine Stimmkraft entspricht deinem $MEM Token-Guthaben. Jeder
              Token gibt dir eine Stimme. Die Abstimmungen werden über
              Snapshot.org durchgeführt.
            </p>
          </div>
        </div>
      </div>

      {/* Proposals */}
      <div className="space-y-4">
        {proposals.map((proposal) => (
          <div key={proposal.id} className="bg-white rounded-lg shadow p-6">
            {/* Proposal Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {proposal.title}
                  </h3>
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      proposal.status
                    )}`}
                  >
                    {getStatusText(proposal.status)}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-2">
                  {proposal.description}
                </p>
                <div className="flex items-center text-xs text-gray-500 space-x-4">
                  <span>Von: {proposal.author.substring(0, 8)}...</span>
                  <span className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {proposal.endTime.toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Voting Results */}
            {proposal.totalVotes > 0 && (
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Ergebnisse
                  </span>
                  <span className="text-sm text-gray-500">
                    {proposal.totalVotes.toLocaleString()} Stimmen
                  </span>
                </div>

                <div className="space-y-2">
                  {proposal.choices.map((choice) => {
                    const votes = proposal.votes[choice] || 0;
                    const percentage = calculatePercentage(
                      votes,
                      proposal.totalVotes
                    );
                    const isWinner = proposal.result === choice;

                    return (
                      <div key={choice} className="relative">
                        <div className="flex justify-between items-center mb-1">
                          <span
                            className={`text-sm ${
                              isWinner
                                ? "font-semibold text-green-700"
                                : "text-gray-700"
                            }`}
                          >
                            {choice} {isWinner && "🏆"}
                          </span>
                          <span className="text-sm text-gray-500">
                            {percentage}% ({votes.toLocaleString()})
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              isWinner ? "bg-green-500" : "bg-blue-500"
                            }`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Quorum Status */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">
                      Quorum ({proposal.quorum.toLocaleString()} $MEM)
                    </span>
                    <span
                      className={`font-medium ${
                        proposal.totalVotes >= proposal.quorum
                          ? "text-green-600"
                          : "text-red-600"
                      }`}
                    >
                      {proposal.totalVotes >= proposal.quorum ? (
                        <span className="flex items-center">
                          <CheckCircleIcon className="h-4 w-4 mr-1" />
                          Erreicht
                        </span>
                      ) : (
                        <span className="flex items-center">
                          <XCircleIcon className="h-4 w-4 mr-1" />
                          Nicht erreicht
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* User Vote Status */}
            {userVotes[proposal.id] ? (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                  <span className="ml-2 text-sm text-green-800">
                    Du hast für "{userVotes[proposal.id]}" gestimmt
                  </span>
                </div>
              </div>
            ) : (
              canVote(proposal) && (
                <div className="border-t border-gray-200 pt-4">
                  <div className="mb-3">
                    <span className="text-sm font-medium text-gray-700">
                      Deine Stimme:
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {proposal.choices.map((choice) => (
                      <button
                        key={choice}
                        onClick={() => handleVote(proposal.id, choice)}
                        disabled={voting[proposal.id]}
                        className="bg-blue-50 hover:bg-blue-100 text-blue-700 px-4 py-2 rounded-lg border border-blue-200 text-sm font-medium disabled:opacity-50 transition"
                      >
                        {voting[proposal.id] ? "Wird abgestimmt..." : choice}
                      </button>
                    ))}
                  </div>
                </div>
              )
            )}

            {/* Cannot Vote Reasons */}
            {!canVote(proposal) && !userVotes[proposal.id] && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <div className="flex items-center text-sm text-gray-600">
                  <XCircleIcon className="h-4 w-4 mr-2" />
                  {proposal.status !== "active"
                    ? "Abstimmung nicht aktiv"
                    : tokenBalance === 0
                    ? "Keine $MEM Token zum Abstimmen"
                    : new Date() > proposal.endTime
                    ? "Abstimmung beendet"
                    : "Abstimmung nicht verfügbar"}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Create Proposal Info */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start">
          <DocumentTextIcon className="h-6 w-6 text-yellow-500 mt-1" />
          <div className="ml-3">
            <h4 className="text-sm font-medium text-yellow-800">
              Eigenen Vorschlag erstellen
            </h4>
            <p className="text-sm text-yellow-700 mt-1">
              Besitzt du mindestens 100,000 $MEM Token? Dann kannst du eigene
              Governance-Vorschläge erstellen. Kontaktiere das Team über Discord
              oder GitHub.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernanceDashboard;
