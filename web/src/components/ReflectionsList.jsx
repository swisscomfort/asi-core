import React, { useState, useEffect } from "react";
import {
  DocumentTextIcon,
  CalendarIcon,
  TagIcon,
  HeartIcon,
  ChatBubbleLeftIcon,
} from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";
import { localStorage } from "../services/localStorage";

const ReflectionsList = ({ searchResults, onReflectionSelect }) => {
  const [reflections, setReflections] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedReflection, setSelectedReflection] = useState(null);

  useEffect(() => {
    if (searchResults && searchResults.length > 0) {
      setReflections(searchResults);
    } else {
      loadRecentReflections();
    }
  }, [searchResults]);

  const loadRecentReflections = async () => {
    setIsLoading(true);

    try {
      // Try to load from local storage first
      const localReflections = await localStorageService.getAllReflections();

      if (localReflections && localReflections.length > 0) {
        // Sort by timestamp, newest first
        const sortedLocal = localReflections
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 20);
        setReflections(sortedLocal);
      } else {
        // Fallback to API if no local data
        const data = await AIApiService.loadRecentReflections(20);
        setReflections(data.reflections || []);
      }
    } catch (error) {
      console.error("Fehler beim Laden der Reflexionen:", error);
      // Try local storage as fallback
      try {
        const localReflections = await localStorageService.getAllReflections();
        setReflections(localReflections || []);
      } catch (localError) {
        console.error("Auch lokaler Speicher fehlgeschlagen:", localError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "😊";
      case "negative":
        return "😔";
      case "neutral":
        return "😐";
      default:
        return "💭";
    }
  };

  const handleReflectionClick = (reflection) => {
    setSelectedReflection(reflection);
    if (onReflectionSelect) {
      onReflectionSelect(reflection);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
          <span className="ml-3 text-gray-600">
            Reflexionen werden geladen...
          </span>
        </div>
      </div>
    );
  }

  if (reflections.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="text-center py-8">
          <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Keine Reflexionen gefunden
          </h3>
          <p className="text-gray-600">
            {searchResults
              ? "Versuche eine andere Suchanfrage."
              : "Erstelle deine erste Reflexion, um zu beginnen."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">
            {searchResults ? "Suchergebnisse" : "Deine Reflexionen"}
          </h2>
          <span className="text-sm text-gray-500">
            {reflections.length}{" "}
            {reflections.length === 1 ? "Eintrag" : "Einträge"}
          </span>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {reflections.map((reflection, index) => (
          <div
            key={reflection.hash || index}
            onClick={() => handleReflectionClick(reflection)}
            className={`p-6 hover:bg-gray-50 cursor-pointer transition-colors ${
              selectedReflection?.hash === reflection.hash
                ? "bg-indigo-50 border-l-4 border-indigo-500"
                : ""
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                {/* Header mit Datum und Sentiment */}
                <div className="flex items-center mb-3">
                  <CalendarIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-500">
                    {formatDate(reflection.timestamp)}
                  </span>
                  {reflection.sentiment && (
                    <span className="ml-3 text-lg">
                      {getSentimentIcon(reflection.sentiment)}
                    </span>
                  )}
                  {reflection.similarity_score && (
                    <span className="ml-auto text-xs text-indigo-600 bg-indigo-100 px-2 py-1 rounded-full">
                      {Math.round(reflection.similarity_score * 100)}%
                      Ähnlichkeit
                    </span>
                  )}
                </div>

                {/* Inhalt */}
                <div className="mb-3">
                  <p className="text-gray-800 text-sm leading-relaxed">
                    {reflection.content_preview || reflection.content}
                  </p>
                </div>

                {/* Tags */}
                {reflection.tags && reflection.tags.length > 0 && (
                  <div className="flex items-center mb-2">
                    <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <div className="flex flex-wrap gap-1">
                      {reflection.tags.slice(0, 5).map((tag, tagIndex) => (
                        <span
                          key={tagIndex}
                          className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                      {reflection.tags.length > 5 && (
                        <span className="text-xs text-gray-400">
                          +{reflection.tags.length - 5} weitere
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Matching Themes (bei Suchergebnissen) */}
                {reflection.matching_themes &&
                  reflection.matching_themes.length > 0 && (
                    <div className="flex items-center">
                      <ChatBubbleLeftIcon className="h-4 w-4 text-green-500 mr-2" />
                      <span className="text-xs text-green-600">
                        Passende Themen: {reflection.matching_themes.join(", ")}
                      </span>
                    </div>
                  )}
              </div>

              {/* Privacy Level */}
              <div className="ml-4 flex-shrink-0">
                {reflection.shared ? (
                  <div className="flex items-center text-xs text-blue-600">
                    <HeartIcon className="h-4 w-4 mr-1" />
                    Geteilt
                  </div>
                ) : (
                  <div className="flex items-center text-xs text-gray-500">
                    <span className="w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
                    Privat
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReflectionsList;
