import React, { useState, useEffect } from "react";
import {
  CurrencyDollarIcon,
  TrophyIcon,
  GiftIcon,
  ShareIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

const TokenDashboard = ({ userAddress, reflectionCount = 0 }) => {
  const [tokenBalance, setTokenBalance] = useState(0);
  const [contractStats, setContractStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [claimLoading, setClaimLoading] = useState(false);
  const [recentRewards, setRecentRewards] = useState([]);

  // Fetch token balance and stats
  useEffect(() => {
    if (userAddress) {
      fetchTokenData();
    }
  }, [userAddress]);

  const fetchTokenData = async () => {
    try {
      setLoading(true);

      // Fetch balance
      const balanceResponse = await fetch(`/api/token/balance/${userAddress}`);
      const balanceData = await balanceResponse.json();

      if (!balanceData.error) {
        setTokenBalance(balanceData.balance || 0);
      }

      // Fetch contract stats
      const statsResponse = await fetch("/api/token/stats");
      const statsData = await statsResponse.json();

      if (!statsData.error) {
        setContractStats(statsData);
      }
    } catch (error) {
      console.error("Error fetching token data:", error);
    } finally {
      setLoading(false);
    }
  };

  const claimReward = async (activityType) => {
    if (!userAddress) return;

    try {
      setClaimLoading(true);

      const response = await fetch("/api/token/claim", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_address: userAddress,
          activity_type: activityType,
        }),
      });

      const result = await response.json();

      if (!result.error) {
        // Update balance
        await fetchTokenData();

        // Add to recent rewards
        setRecentRewards((prev) => [
          {
            type: activityType,
            amount: result.amount,
            timestamp: new Date().toISOString(),
            tx_hash: result.tx_hash,
          },
          ...prev.slice(0, 4), // Keep only last 5
        ]);

        // Show success notification
        alert(`🎉 ${result.amount} $MEM erfolgreich erhalten!`);
      } else {
        alert(`Fehler beim Belohnung einlösen: ${result.error}`);
      }
    } catch (error) {
      console.error("Error claiming reward:", error);
      alert("Netzwerkfehler beim Belohnung einlösen");
    } finally {
      setClaimLoading(false);
    }
  };

  const getClaimableRewards = () => {
    const rewards = [];

    // Milestone rewards based on reflection count
    if (reflectionCount >= 10 && reflectionCount % 10 === 0) {
      rewards.push({
        type: "milestone_10_reflections",
        amount: 10,
        description: "10 Reflexionen erreicht!",
      });
    }

    if (reflectionCount >= 50 && reflectionCount % 50 === 0) {
      rewards.push({
        type: "milestone_50_reflections",
        amount: 50,
        description: "50 Reflexionen erreicht!",
      });
    }

    if (reflectionCount >= 100 && reflectionCount % 100 === 0) {
      rewards.push({
        type: "milestone_100_reflections",
        amount: 100,
        description: "100 Reflexionen erreicht!",
      });
    }

    return rewards;
  };

  if (loading) {
    return (
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
    );
  }

  const claimableRewards = getClaimableRewards();

  return (
    <div className="space-y-6">
      {/* Token Balance Card */}
      <div className="bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-2">Dein $MEM Balance</h3>
            <div className="text-3xl font-bold">
              {tokenBalance.toLocaleString()} $MEM
            </div>
          </div>
          <CurrencyDollarIcon className="h-12 w-12 opacity-80" />
        </div>

        {contractStats && (
          <div className="mt-4 pt-4 border-t border-white/20">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="opacity-80">Gesamtumlauf</div>
                <div className="font-medium">
                  {(
                    contractStats.total_supply - contractStats.total_burned
                  ).toLocaleString()}
                </div>
              </div>
              <div>
                <div className="opacity-80">Verbrannt</div>
                <div className="font-medium">
                  {contractStats.total_burned.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Claimable Rewards */}
      {claimableRewards.length > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
          <div className="flex">
            <GiftIcon className="h-6 w-6 text-yellow-400" />
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">
                Belohnungen verfügbar!
              </h4>
              <div className="mt-2 space-y-2">
                {claimableRewards.map((reward, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div>
                      <div className="text-sm text-yellow-700">
                        {reward.description}
                      </div>
                      <div className="text-xs text-yellow-600">
                        +{reward.amount} $MEM
                      </div>
                    </div>
                    <button
                      onClick={() => claimReward(reward.type)}
                      disabled={claimLoading}
                      className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm font-medium disabled:opacity-50"
                    >
                      {claimLoading ? "Wird bearbeitet..." : "Einlösen"}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Earning Opportunities */}
      <div className="bg-white rounded-lg shadow p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center">
          <TrophyIcon className="h-5 w-5 mr-2 text-orange-500" />
          Verdienungsmöglichkeiten
        </h4>

        <div className="grid gap-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium">Reflexion speichern</div>
              <div className="text-sm text-gray-600">
                Pro gespeicherter Reflexion
              </div>
            </div>
            <div className="text-green-600 font-semibold">+1 $MEM</div>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium">Muster erkennen</div>
              <div className="text-sm text-gray-600">
                Wenn KI ein Muster entdeckt
              </div>
            </div>
            <div className="text-green-600 font-semibold">+5 $MEM</div>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium">Anonyme Musterfreigabe</div>
              <div className="text-sm text-gray-600">Muster anonym teilen</div>
            </div>
            <div className="text-green-600 font-semibold">+10 $MEM</div>
          </div>
        </div>
      </div>

      {/* Recent Rewards */}
      {recentRewards.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h4 className="text-lg font-semibold mb-4">Letzte Belohnungen</h4>
          <div className="space-y-3">
            {recentRewards.map((reward, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-green-50 rounded-lg"
              >
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                  <div>
                    <div className="font-medium">+{reward.amount} $MEM</div>
                    <div className="text-sm text-gray-600">
                      {reward.type.replace(/_/g, " ")}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(reward.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                {reward.tx_hash && (
                  <a
                    href={`https://mumbai.polygonscan.com/tx/${reward.tx_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700 text-xs"
                  >
                    Transaktion anzeigen
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Share Anonymously Option */}
      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start">
          <ShareIcon className="h-6 w-6 text-blue-500 mt-1" />
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-800">
              Verdiene mehr durch anonymes Teilen
            </h4>
            <p className="text-sm text-blue-600 mt-1">
              Teile deine Reflexionsmuster anonymisiert mit der Community und
              erhalte 10 $MEM pro freigegebenes Muster. Deine Identität bleibt
              dabei vollständig geschützt.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TokenDashboard;
