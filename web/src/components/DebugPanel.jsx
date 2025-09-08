import React, { useState, useEffect } from "react";
import StorachaStatus from "./StorachaStatus";

const DebugPanel = () => {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [frontendStatus] = useState("running");
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    checkBackendStatus();
    // Überprüfe den Backend-Status alle 10 Sekunden
    const interval = setInterval(checkBackendStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      const apiUrl =
        process.env.NODE_ENV === "production"
          ? "https://swisscomfort.github.io/asi-core"
          : "http://localhost:8000";

      const response = await fetch(`${apiUrl}/api/health`, {
        method: "GET",
        timeout: 5000,
      });
      if (response.ok) {
        const data = await response.json();
        console.log("🏥 Backend Health Check:", data);
        setBackendStatus("connected");
      } else {
        console.error("🚨 Backend Health Check failed:", response.status);
        setBackendStatus("error");
      }
    } catch (error) {
      console.log("❌ Backend nicht erreichbar:", error);
      setBackendStatus("disconnected");
    }
  };

  const testSearch = async () => {
    try {
      console.log("🧪 Teste Suchfunktion...");
      const apiUrl =
        process.env.NODE_ENV === "production"
          ? "https://swisscomfort.github.io/asi-core"
          : "http://localhost:8000";

      const url = new URL(`${apiUrl}/api/search`);
      url.searchParams.append("q", "test");
      url.searchParams.append("limit", "5");

      const response = await fetch(url);
      const data = await response.json();
      console.log("✅ Suchtest erfolgreich:", data);
      alert(
        `Suchtest erfolgreich! ${
          data.results?.length || 0
        } Ergebnisse gefunden.`
      );
    } catch (error) {
      console.error("❌ Suchtest fehlgeschlagen:", error);
      alert(`Suchtest fehlgeschlagen: ${error.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "running":
      case "connected":
        return "text-green-500";
      case "checking":
        return "text-yellow-500";
      case "disconnected":
      case "error":
        return "text-red-500";
      default:
        return "text-gray-500";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "running":
        return "✅ Läuft";
      case "connected":
        return "✅ Verbunden";
      case "checking":
        return "🔄 Prüfe...";
      case "disconnected":
        return "❌ Nicht erreichbar";
      case "error":
        return "❌ Fehler";
      default:
        return "❓ Unbekannt";
    }
  };

  if (process.env.NODE_ENV === "production") {
    return null; // Debug-Panel nur in Entwicklungsumgebung anzeigen
  }

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white rounded-lg shadow-lg z-50 max-w-sm">
      {/* Kompakter Status */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="font-semibold">🐛 Debug Status</div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs text-gray-300 hover:text-white"
          >
            {showDetails ? "Weniger" : "Mehr"}
          </button>
        </div>

        <div className="space-y-1 text-sm">
          <div
            className={`${getStatusColor(frontendStatus)} flex items-center`}
          >
            <span className="w-2 h-2 rounded-full bg-current mr-2"></span>
            Frontend: {getStatusText(frontendStatus)}
          </div>
          <div className={`${getStatusColor(backendStatus)} flex items-center`}>
            <span className="w-2 h-2 rounded-full bg-current mr-2"></span>
            Backend: {getStatusText(backendStatus)}
          </div>
        </div>

        {/* Erweiterte Details */}
        {showDetails && (
          <div className="mt-4 space-y-2">
            <div className="flex space-x-2">
              <button
                onClick={checkBackendStatus}
                className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
              >
                🔄 Backend prüfen
              </button>
              <button
                onClick={testSearch}
                className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
              >
                🧪 Suche testen
              </button>
            </div>

            {/* Storacha Status eingebettet */}
            <div className="bg-gray-700 rounded p-2">
              <StorachaStatus />
            </div>

            <div className="text-xs text-gray-400 border-t border-gray-600 pt-2">
              Console: F12 → Console Tab
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DebugPanel;
