import React, { useState, useEffect } from "react";
import { localStorage } from "../services/localStorage";

export const OfflineStats = () => {
  const [stats, setStats] = useState({ total: 0, unsynced: 0, synced: 0 });

  useEffect(() => {
    const updateStats = async () => {
      try {
        const newStats = await localStorage.getOfflineStats();
        setStats(newStats);
      } catch (error) {
        console.error("Fehler beim Laden der Offline-Statistiken:", error);
      }
    };

    updateStats();
    const interval = setInterval(updateStats, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        💾 Lokale Daten
        {stats.unsynced > 0 && (
          <span className="ml-2 bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
            {stats.unsynced} wartend
          </span>
        )}
      </h2>
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Gesamt:</span>
          <span className="font-medium">{stats.total}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Synchronisiert:</span>
          <span className="font-medium text-green-600">{stats.synced}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Wartet auf Sync:</span>
          <span className="font-medium text-orange-600">{stats.unsynced}</span>
        </div>
        {stats.total > 0 && (
          <div className="pt-2 border-t">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(stats.synced / stats.total) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {Math.round((stats.synced / stats.total) * 100)}% synchronisiert
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
