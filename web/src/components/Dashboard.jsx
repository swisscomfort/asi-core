import React, { useState, useEffect } from "react";
import {
  ChartBarIcon,
  TrendingUpIcon,
  UsersIcon,
  SparklesIcon,
  CalendarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import PersonalInsights from "./PersonalInsights.jsx";

const Dashboard = () => {
  const [personalStats, setPersonalStats] = useState({});
  const [collectiveStats, setCollectiveStats] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Load personal states
      const personalResponse = await fetch("/api/states?days=7");
      if (personalResponse.ok) {
        const personalData = await personalResponse.json();
        setPersonalStats(personalData);
      }

      // Load collective data
      const collectiveResponse = await fetch("/api/states/aggregate");
      if (collectiveResponse.ok) {
        const collectiveData = await collectiveResponse.json();
        setCollectiveStats(collectiveData);
      }

      // Load recommendations
      const recommendationResponse = await fetch("/api/recommendations");
      if (recommendationResponse.ok) {
        const recommendationData = await recommendationResponse.json();
        setRecommendations(recommendationData);
      }

      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();

    // Refresh every 5 minutes
    const interval = setInterval(loadDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getPersonalStreaks = () => {
    const streaks = [];
    Object.entries(personalStats).forEach(([key, data]) => {
      if (data.streak > 0) {
        streaks.push({
          activity: formatActivityLabel(key),
          streak: data.streak,
          lastActivity: data.last_activity,
        });
      }
    });
    return streaks.sort((a, b) => b.streak - a.streak);
  };

  const formatActivityLabel = (key) => {
    const labels = {
      walked: "Spaziergang",
      focused: "Fokussiert",
      slept_well: "Gut geschlafen",
      meditated: "Meditation",
      productive_morning: "Produktiver Morgen",
      exercised: "Sport",
      read: "Gelesen",
      journaled: "Tagebuch",
      socialized: "Sozial",
      creative_work: "Kreativ",
    };
    return labels[key] || key;
  };

  const getSuccessRate = (key) => {
    const data = collectiveStats[key];
    return data ? data.success_rate : 0;
  };

  const getTrendIcon = (rate) => {
    if (rate >= 70) return <ArrowUpIcon className="w-4 h-4 text-green-600" />;
    if (rate >= 50) return <ArrowUpIcon className="w-4 h-4 text-yellow-600" />;
    return <ArrowDownIcon className="w-4 h-4 text-red-600" />;
  };

  const refreshData = () => {
    setRefreshTrigger((prev) => prev + 1);
    loadDashboardData();
  };

  if (isLoading && Object.keys(personalStats).length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Lade Dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ASI Dashboard</h1>
            <p className="text-gray-600">
              Persönliche Entwicklung und kollektive Erkenntnisse
            </p>
          </div>
          <button
            onClick={refreshData}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <ArrowUpIcon className="w-4 h-4 mr-2" />
            Aktualisieren
          </button>
        </div>

        {/* Personal Streaks Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <TrendingUpIcon className="w-6 h-6 text-green-600 mr-2" />
            Persönliche Streaks
          </h2>
          {getPersonalStreaks().length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {getPersonalStreaks().map((streak, i) => (
                <div
                  key={i}
                  className="bg-green-50 border border-green-200 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-green-800">
                        {streak.activity}
                      </h3>
                      <p className="text-sm text-green-600">
                        {streak.streak} {streak.streak === 1 ? "Tag" : "Tage"}{" "}
                        in Folge
                      </p>
                    </div>
                    <div className="text-2xl font-bold text-green-600">
                      {streak.streak}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <TrendingUpIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Noch keine aktiven Streaks</p>
              <p className="text-sm">
                Erstelle eine Reflexion mit Aktivitäten, um zu beginnen!
              </p>
            </div>
          )}
        </div>

        {/* Collective Success Rates */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <UsersIcon className="w-6 h-6 text-blue-600 mr-2" />
            Kollektive Erfolgsquoten
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(collectiveStats).map(([key, data]) => (
              <div
                key={key}
                className="bg-blue-50 border border-blue-200 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-blue-800">
                    {formatActivityLabel(key)}
                  </h3>
                  {getTrendIcon(data.success_rate)}
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-blue-600">Erfolgsquote:</span>
                    <span className="font-medium text-blue-800">
                      {Math.round(data.success_rate)}%
                    </span>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${data.success_rate}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-blue-600">
                    {data.total_entries} Einträge insgesamt
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Proactive Recommendations */}
        {recommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <SparklesIcon className="w-6 h-6 text-indigo-600 mr-2" />
              Proaktive Empfehlungen
            </h2>
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="bg-indigo-50 border border-indigo-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-indigo-800 font-medium">
                        {rec.message}
                      </p>
                      {rec.actions && rec.actions.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {rec.actions.map((action, j) => (
                            <span
                              key={j}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-indigo-100 text-indigo-700"
                            >
                              {formatActivityLabel(action)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="ml-4 text-right">
                      <div className="text-xs text-indigo-600">
                        {rec.type === "time_based" && (
                          <ClockIcon className="w-4 h-4 inline mr-1" />
                        )}
                        {rec.type === "pattern_based" && (
                          <ChartBarIcon className="w-4 h-4 inline mr-1" />
                        )}
                        {Math.round((rec.confidence || 0) * 100)}% Vertrauen
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Personal Insights Component */}
        <PersonalInsights refreshTrigger={refreshTrigger} />

        {/* Footer with last updated */}
        {lastUpdated && (
          <div className="text-center text-sm text-gray-500">
            <CalendarIcon className="w-4 h-4 inline mr-1" />
            Zuletzt aktualisiert: {lastUpdated.toLocaleString("de-DE")}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
