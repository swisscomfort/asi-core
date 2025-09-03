import React, { useState, useEffect } from "react";
import {
  ChartBarIcon,
  LightBulbIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";

const AIInsights = ({ currentReflection }) => {
  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [patterns, setPatterns] = useState([]);

  useEffect(() => {
    if (currentReflection) {
      generateInsights(currentReflection);
    }
  }, [currentReflection]);

  const generateInsights = async (reflection) => {
    setIsLoading(true);

    try {
      // Parallele API-Aufrufe für bessere Performance
      const [patternsData, insightsData] = await Promise.all([
        AIApiService.recognizePatterns(reflection),
        AIApiService.generateInsights(reflection),
      ]);

      setPatterns(patternsData.patterns || []);
      setInsights(insightsData);
    } catch (error) {
      console.error("Fehler beim Generieren der KI-Insights:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50";
      case "negative":
        return "text-red-600 bg-red-50";
      case "neutral":
        return "text-gray-600 bg-gray-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          <span className="ml-3 text-gray-600">
            KI analysiert deine Reflexion...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KI-Insights */}
      {insights && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center mb-4">
            <LightBulbIcon className="h-6 w-6 text-amber-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-800">KI-Insights</h2>
          </div>

          <div className="space-y-4">
            {/* Sentiment-Analyse */}
            {insights.sentiment && (
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <span className="text-sm font-medium text-gray-700">
                  Stimmung:
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${getSentimentColor(
                    insights.sentiment.label
                  )}`}
                >
                  {insights.sentiment.label === "positive"
                    ? "😊 Positiv"
                    : insights.sentiment.label === "negative"
                    ? "😔 Negativ"
                    : "😐 Neutral"}{" "}
                  ({Math.round(insights.sentiment.confidence * 100)}%)
                </span>
              </div>
            )}

            {/* Themen-Extraktion */}
            {insights.themes && insights.themes.length > 0 && (
              <div className="p-3 rounded-lg border">
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  Erkannte Themen:
                </h3>
                <div className="flex flex-wrap gap-2">
                  {insights.themes.map((theme, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full"
                    >
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Empfehlungen */}
            {insights.recommendations &&
              insights.recommendations.length > 0 && (
                <div className="p-3 rounded-lg border">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    💡 Empfehlungen:
                  </h3>
                  <ul className="space-y-1">
                    {insights.recommendations.map((rec, index) => (
                      <li
                        key={index}
                        className="text-sm text-gray-600 flex items-start"
                      >
                        <span className="text-indigo-500 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
          </div>
        </div>
      )}

      {/* Erkannte Muster */}
      {patterns.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center mb-4">
            <ChartBarIcon className="h-6 w-6 text-blue-500 mr-2" />
            <h2 className="text-lg font-semibold text-gray-800">
              Erkannte Muster
            </h2>
          </div>

          <div className="space-y-4">
            {patterns.map((pattern, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-800">{pattern.name}</h3>
                  <div className="flex items-center text-sm text-gray-500">
                    <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    {Math.round(pattern.confidence * 100)}% Wahrscheinlichkeit
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-3">
                  {pattern.description}
                </p>

                {pattern.frequency && (
                  <div className="flex items-center text-xs text-gray-500">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    Häufigkeit: {pattern.frequency}
                  </div>
                )}

                {pattern.related_entries &&
                  pattern.related_entries.length > 0 && (
                    <div className="mt-3">
                      <span className="text-xs text-gray-500">
                        Ähnliche Reflexionen: {pattern.related_entries.length}
                      </span>
                    </div>
                  )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIInsights;
