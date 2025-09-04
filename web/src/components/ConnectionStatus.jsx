import React, { useState, useEffect } from "react";
import { syncService } from "../services/syncService.js";

export const ConnectionStatus = () => {
  const [status, setStatus] = useState(syncService.getConnectionStatus());

  useEffect(() => {
    const updateStatus = () => {
      setStatus(syncService.getConnectionStatus());
    };

    window.addEventListener("online", updateStatus);
    window.addEventListener("offline", updateStatus);

    return () => {
      window.removeEventListener("online", updateStatus);
      window.removeEventListener("offline", updateStatus);
    };
  }, []);

  return (
    <div
      className={`fixed top-4 right-4 px-3 py-2 rounded-lg text-xs z-40 ${
        status.online
          ? "bg-green-900 text-green-100 border border-green-700"
          : "bg-orange-900 text-orange-100 border border-orange-700"
      }`}
    >
      <div className="flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full ${
            status.online ? "bg-green-400" : "bg-orange-400"
          }`}
        />
        <span>{status.message}</span>
      </div>
    </div>
  );
};
