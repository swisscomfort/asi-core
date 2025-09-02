import React,  const checkBackendStatus = async () => {
    try {
      const re  const testSearch = async () => {      <button 
        onClick={checkBackendStatus}
        className="mt-2 px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs mr-2"
      >
        🔄 Backend prüfen
      </button>
      <button 
        onClick={testSearch}
        className="mt-2 px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
      >
        🧪 Suche testen
      </button>
      <div className="mt-2 text-xs text-gray-400">
        Console: F12 → Console Tab
      </div>{
      console.log('🧪 Teste Suchfunktion...');
      const url = new URL('http://localhost:8000/api/search');
      url.searchParams.append('q', 'test');
      url.searchParams.append('limit', '5');
      
      const response = await fetch(url);
      const data = await response.json();
      console.log('✅ Suchtest erfolgreich:', data);
      alert(`Suchtest erfolgreich! ${data.results?.length || 0} Ergebnisse gefunden.`);
    } catch (error) {
      console.error('❌ Suchtest fehlgeschlagen:', error);
      alert(`Suchtest fehlgeschlagen: ${error.message}`);
    }
  };

  if (process.env.NODE_ENV === 'production') {ponse = await fetch('http://localhost:8000/api/health', {
        method: 'GET',
        timeout: 5000
      });
      if (response.ok) {
        const data = await response.json();
        console.log('🏥 Backend Health Check:', data);
        setBackendStatus('connected');
      } else {
        console.error('🚨 Backend Health Check failed:', response.status);
        setBackendStatus('error');
      }
    } catch (error) {
      console.log('❌ Backend nicht erreichbar:', error);
      setBackendStatus('disconnected');
    }
  };Effect } from "react";

const DebugPanel = () => {
  const [backendStatus, setBackendStatus] = useState("checking");
  const [frontendStatus] = useState("running");

  useEffect(() => {
    checkBackendStatus();
    // Überprüfe den Backend-Status alle 10 Sekunden
    const interval = setInterval(checkBackendStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/health", {
        method: "GET",
        timeout: 5000,
      });
      if (response.ok) {
        setBackendStatus("connected");
      } else {
        setBackendStatus("error");
      }
    } catch (error) {
      console.log("Backend nicht erreichbar:", error);
      setBackendStatus("disconnected");
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
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-3 rounded-lg shadow-lg text-sm z-50">
      <div className="font-semibold mb-2">🐛 Debug Status</div>
      <div className="space-y-1">
        <div className={`${getStatusColor(frontendStatus)} flex items-center`}>
          <span className="w-3 h-3 rounded-full bg-current mr-2"></span>
          Frontend (Port 5173): {getStatusText(frontendStatus)}
        </div>
        <div className={`${getStatusColor(backendStatus)} flex items-center`}>
          <span className="w-3 h-3 rounded-full bg-current mr-2"></span>
          Backend (Port 8000): {getStatusText(backendStatus)}
        </div>
      </div>
      <button
        onClick={checkBackendStatus}
        className="mt-2 px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
      >
        🔄 Backend prüfen
      </button>
      <div className="mt-2 text-xs text-gray-400">
        Console: F12 → Console Tab
      </div>
    </div>
  );
};

export default DebugPanel;
