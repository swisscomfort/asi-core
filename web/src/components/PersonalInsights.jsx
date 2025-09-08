import React, { useState, useEffect } from "react";
import {
  SparklesIcon,
  TrendingUpIcon,
  CalendarIcon,
  ClockIcon,
  HeartIcon,
  RefreshIcon,
} from "@heroicons/react/24/outline";
import HybridModel from "../../src/modules/hybrid-model/index.js";

const PersonalInsights = ({ refreshTrigger = 0 }) => {
  const [insights, setInsights] = useState([]);
  const [streaks, setStreaks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const hybridModel = new HybridModel();

  const loadInsights = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await hybridModel.initialize();

      // Load personal insights
      const personalInsights =
        await hybridModel.insightEngine.getPersonalInsights();

      // Load state streaks
      const stateStreaks = await getStateStreaks();

      setInsights(personalInsights);
      setStreaks(stateStreaks);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Failed to load insights:", err);
      setError("Erkenntnisse konnten nicht geladen werden");
    } finally {
      setIsLoading(false);
    }
  };

  const getStateStreaks = async () => {
    const states = [
      "walked",
      "focused",
      "slept_well",
      "meditated",
      "productive_morning",
    ];
    const streakPromises = states.map(async (state) => {
      const history = await hybridModel.stateTracker.getStateHistory(state, 14);
      const streak = hybridModel.stateTracker.calculateStreak(history);

      return {
        state,
        streak,
        lastActivity:
          history.length > 0
            ? new Date(history[history.length - 1].timestamp)
            : null,
      };
    });

    return Promise.all(streakPromises);
  };

  useEffect(() => {
    loadInsights();
  }, [refreshTrigger]);

  const getInsightIcon = (type) => {
    switch (type) {
      case "streak":
        return <TrendingUpIcon className="w-5 h-5 text-green-600" />;
      case "mood_improvement":
        return <HeartIcon className="w-5 h-5 text-pink-600" />;
      case "time_pattern":
        return <ClockIcon className="w-5 h-5 text-blue-600" />;
      default:
        return <SparklesIcon className="w-5 h-5 text-indigo-600" />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case "streak":
        return "border-green-200 bg-green-50";
      case "mood_improvement":
        return "border-pink-200 bg-pink-50";
      case "time_pattern":
        return "border-blue-200 bg-blue-50";
      default:
        return "border-indigo-200 bg-indigo-50";
    }
  };

  const formatStateLabel = (state) => {
    const labels = {
      walked: "Spaziergang",
      focused: "Fokussiert",
      slept_well: "Gut geschlafen",
      meditated: "Meditation",
      productive_morning: "Produktiver Morgen",
    };
    return labels[state] || state;
  };

  if (isLoading) {
    return (
      <div className="insights-container bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center">
          <RefreshIcon className="w-6 h-6 animate-spin text-indigo-600 mr-3" />
          <span className="text-gray-600">Lade Erkenntnisse...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="insights-container bg-white rounded-lg shadow-md p-6">
        <div className="text-center text-red-600">
          <p>{error}</p>
          <button
            onClick={loadInsights}
            className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
          >
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="insights-container space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <SparklesIcon className="w-6 h-6 text-indigo-600 mr-2" />
          Persönliche Erkenntnisse
        </h3>
        <button
          onClick={loadInsights}
          className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center"
        >
          <RefreshIcon className="w-4 h-4 mr-1" />
          Aktualisieren
        </button>
      </div>

      {/* Streaks Section */}
      {streaks.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <h4 className="text-md font-medium text-gray-800 mb-3 flex items-center">
            <TrendingUpIcon className="w-5 h-5 text-green-600 mr-2" />
            Aktuelle Streaks
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {streaks
              .filter((s) => s.streak > 0)
              .sort((a, b) => b.streak - a.streak)
              .map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between bg-green-50 border border-green-200 rounded-md p-3"
                >
                  <div>
                    <p className="text-sm font-medium text-green-800">
                      {formatStateLabel(item.state)}
                    </p>
                    <p className="text-xs text-green-600">
                      {item.streak} {item.streak === 1 ? "Tag" : "Tage"}
                    </p>
                  </div>
                  <div className="text-green-600 font-bold text-lg">
                    {item.streak}
                  </div>
                </div>
              ))}
          </div>
          {streaks.filter((s) => s.streak > 0).length === 0 && (
            <p className="text-gray-500 text-sm italic">
              Noch keine aktiven Streaks. Beginne mit einer Aktivität!
            </p>
          )}
        </div>
      )}

      {/* Insights Cards */}
      {insights.length > 0 ? (
        <div className="space-y-3">
          {insights.map((insight, i) => (
            <div
              key={insight.id || i}
              className={`insight-card border rounded-lg p-4 ${getInsightColor(
                insight.type
              )}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  {getInsightIcon(insight.type)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">
                    {insight.message || insight.text}
                  </p>
                  {insight.source && (
                    <small className="text-xs text-gray-500 mt-1 block">
                      Quelle: {insight.source}
                    </small>
                  )}
                  {insight.confidence && (
                    <div className="mt-2">
                      <div className="flex items-center">
                        <span className="text-xs text-gray-600 mr-2">
                          Vertrauen:
                        </span>
                        <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-indigo-600 h-1.5 rounded-full"
                            style={{ width: `${insight.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600 ml-2">
                          {Math.round(insight.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <SparklesIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Noch keine Erkenntnisse verfügbar.</p>
          <p className="text-sm text-gray-400 mt-1">
            Erstelle ein paar Reflexionen und füge Aktivitäten hinzu, um
            personalisierte Erkenntnisse zu erhalten.
          </p>
        </div>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="text-center">
          <p className="text-xs text-gray-400">
            Zuletzt aktualisiert: {lastUpdated.toLocaleTimeString("de-DE")}
          </p>
        </div>
      )}
    </div>
  );
};

export default PersonalInsights;
