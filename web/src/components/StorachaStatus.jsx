import React, { useState, useEffect } from "react";
import {
  CloudIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import StorachaService from "../services/storachaService";

const StorachaStatus = () => {
  const [isAvailable, setIsAvailable] = useState(null);
  const [spaceDid, setSpaceDid] = useState("");
  const [lastUpload, setLastUpload] = useState(null);

  useEffect(() => {
    checkStorachaStatus();
    setSpaceDid(StorachaService.spaceDid);
  }, []);

  const checkStorachaStatus = async () => {
    try {
      const available = await StorachaService.isAvailable();
      setIsAvailable(available);
    } catch (error) {
      setIsAvailable(false);
    }
  };

  const testUpload = async () => {
    try {
      const testData = {
        test: true,
        timestamp: new Date().toISOString(),
        message: "Storacha Service Test",
      };

      const cid = await StorachaService.uploadReflection(testData);
      const url = StorachaService.getPublicUrl(cid);

      setLastUpload({ cid, url, timestamp: new Date().toISOString() });
      alert(`✅ Test erfolgreich!\n\nCID: ${cid}\nURL: ${url}`);
    } catch (error) {
      alert(`❌ Test fehlgeschlagen:\n\n${error.message}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <CloudIcon className="h-5 w-5 text-blue-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Storacha Status</h3>
        </div>
        <button
          onClick={checkStorachaStatus}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Aktualisieren
        </button>
      </div>

      <div className="space-y-3">
        {/* Service Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Service verfügbar:</span>
          <div className="flex items-center">
            {isAvailable === null ? (
              <span className="text-gray-400">Prüfe...</span>
            ) : isAvailable ? (
              <>
                <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                <span className="text-green-600 text-sm">Online</span>
              </>
            ) : (
              <>
                <XCircleIcon className="h-4 w-4 text-red-500 mr-1" />
                <span className="text-red-600 text-sm">Offline</span>
              </>
            )}
          </div>
        </div>

        {/* Space DID */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Space DID:</span>
          <span className="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded">
            {spaceDid.substring(0, 20)}...
          </span>
        </div>

        {/* Letzter Upload */}
        {lastUpload && (
          <div className="bg-green-50 border border-green-200 rounded p-3">
            <div className="text-sm text-green-800 font-medium mb-1">
              Letzter Upload erfolgreich:
            </div>
            <div className="text-xs text-green-600 space-y-1">
              <div>CID: {lastUpload.cid.substring(0, 30)}...</div>
              <div>Zeit: {new Date(lastUpload.timestamp).toLocaleString()}</div>
              <a
                href={lastUpload.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                Öffentliche URL →
              </a>
            </div>
          </div>
        )}

        {/* Test Button */}
        <button
          onClick={testUpload}
          disabled={!isAvailable}
          className="w-full mt-3 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Test Upload durchführen
        </button>
      </div>
    </div>
  );
};

export default StorachaStatus;
