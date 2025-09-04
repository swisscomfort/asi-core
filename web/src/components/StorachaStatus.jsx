import React, { useState, useEffect } from "react";
import { CloudIcon, WifiIcon, XCircleIcon } from "@heroicons/react/24/outline";
import StorachaService from "../services/storacha.js";

const StorachaStatus = () => {
  const [status, setStatus] = useState({ connected: false, checking: true });
  const [storedCIDs, setStoredCIDs] = useState([]);

  useEffect(() => {
    checkStatus();
    loadStoredCIDs();
  }, []);

  const checkStatus = async () => {
    try {
      const connectionStatus = await StorachaService.getConnectionStatus();
      setStatus({ ...connectionStatus, checking: false });
    } catch (error) {
      setStatus({
        connected: false,
        reason: "Fehler beim Status-Check",
        checking: false,
      });
    }
  };

  const loadStoredCIDs = () => {
    const cids = StorachaService.getStoredCIDs();
    setStoredCIDs(cids);
  };

  const getStatusIcon = () => {
    if (status.checking) {
      return <CloudIcon className="w-4 h-4 animate-pulse text-gray-400" />;
    }

    if (status.connected) {
      return <WifiIcon className="w-4 h-4 text-green-500" />;
    }

    return <XCircleIcon className="w-4 h-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (status.checking) return "Prüfe Verbindung...";
    if (status.connected) return "Verbunden";
    return status.reason || "Getrennt";
  };

  const getStatusColor = () => {
    if (status.checking) return "text-gray-500";
    if (status.connected) return "text-green-600";
    return "text-red-600";
  };

  return (
    <div className="bg-white rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">Storacha Status</h3>
        <button
          onClick={checkStatus}
          className="text-xs text-gray-500 hover:text-gray-700 transition"
        >
          Aktualisieren
        </button>
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Space:</span>
          <span className="text-sm font-mono text-gray-900">asi-core</span>
        </div>

        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`text-sm ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Gespeicherte CIDs:</span>
          <span className="text-sm font-semibold text-indigo-600">
            {storedCIDs.length}
          </span>
        </div>
      </div>

      {storedCIDs.length > 0 && (
        <div className="pt-2 border-t">
          <details className="group">
            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
              CID-Liste anzeigen
            </summary>
            <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
              {storedCIDs.slice(-5).map((item, index) => (
                <div key={index} className="text-xs text-gray-600 font-mono">
                  <div className="truncate">{item.cid}</div>
                  <div className="text-gray-400">
                    {item.filename} •{" "}
                    {new Date(item.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
              {storedCIDs.length > 5 && (
                <div className="text-xs text-gray-400">
                  ... und {storedCIDs.length - 5} weitere
                </div>
              )}
            </div>
          </details>
        </div>
      )}
    </div>
  );
};

export default StorachaStatus;
