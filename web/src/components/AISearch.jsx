import React, { useState, useCallback } from "react";
import { MagnifyingGlassIcon, SparklesIcon } from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";

const AISearch = ({ onSearchResults }) => {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  const performSemanticSearch = useCallback(
    async (searchQuery) => {
      if (!searchQuery.trim()) return;

      setIsSearching(true);

      try {
        console.log(`🔎 Starte Suche nach: "${searchQuery}"`);
        const results = await AIApiService.semanticSearch(searchQuery, {
          limit: 20,
          minSimilarity: 0.6,
        });

        console.log(`📋 Ergebnisse für "${searchQuery}":`, results);
        const searchResults = results.results || [];
        onSearchResults(searchResults);

        // Zur Suchhistorie hinzufügen
        setSearchHistory((prev) => [
          { query: searchQuery, timestamp: new Date() },
          ...prev.slice(0, 4), // Nur die letzten 5 Suchen speichern
        ]);

        console.log(
          `✅ Suche abgeschlossen: ${searchResults.length} Ergebnisse gefunden`
        );
      } catch (error) {
        console.error("❌ Fehler bei der semantischen Suche:", error);
        // Zeige eine Benutzerfreundliche Fehlermeldung
        alert(
          `Suche fehlgeschlagen: ${error.message}\n\nStelle sicher, dass das Backend unter http://localhost:8000 läuft.`
        );
        onSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    },
    [onSearchResults]
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    performSemanticSearch(query);
  };

  const handleHistoryClick = (historicalQuery) => {
    setQuery(historicalQuery);
    performSemanticSearch(historicalQuery);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex items-center mb-4">
        <SparklesIcon className="h-6 w-6 text-indigo-600 mr-2" />
        <h2 className="text-lg font-semibold text-gray-800">
          KI-gestützte Suche
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Suche in deinen Reflexionen... (z.B. 'Momente der Freude' oder 'berufliche Herausforderungen')"
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={isSearching}
          />
        </div>

        <button
          type="submit"
          disabled={!query.trim() || isSearching}
          className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-medium py-3 rounded-lg transition-colors"
        >
          {isSearching ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Suche läuft...
            </div>
          ) : (
            "Semantisch suchen"
          )}
        </button>
      </form>

      {/* Suchhistorie */}
      {searchHistory.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">
            Letzte Suchen:
          </h3>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((item, index) => (
              <button
                key={index}
                onClick={() => handleHistoryClick(item.query)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors"
              >
                {item.query}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AISearch;
