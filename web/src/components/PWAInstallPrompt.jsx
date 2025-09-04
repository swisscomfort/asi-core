import React, { useState, useEffect } from "react";

export const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener(
        "beforeinstallprompt",
        handleBeforeInstallPrompt
      );
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === "accepted") {
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  const handleDismiss = () => {
    setShowInstallPrompt(false);
    setDeferredPrompt(null);
  };

  if (!showInstallPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 bg-black text-white p-4 rounded-lg shadow-lg border border-gray-700 z-50">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-sm">ASI Core installieren</h3>
          <p className="text-xs text-gray-300 mt-1">
            Möchtest du ASI Core auf deinem Gerät installieren?
          </p>
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={handleDismiss}
            className="px-3 py-1 text-xs text-gray-400 hover:text-white transition-colors"
          >
            Später
          </button>
          <button
            onClick={handleInstallClick}
            className="px-3 py-1 text-xs bg-white text-black rounded hover:bg-gray-200 transition-colors"
          >
            Installieren
          </button>
        </div>
      </div>
    </div>
  );
};
