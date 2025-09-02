import React, { useState } from "react";
import { Web3Storage } from "web3.storage";

const NewReflectionModal = ({ isOpen, onClose }) => {
  const [content, setContent] = useState("");
  const [shared, setShared] = useState(false);

  const extractTags = (text) => {
    const words = text.toLowerCase().match(/\b\w{3,}\b/g) || [];
    const uniqueWords = [...new Set(words)];
    return uniqueWords.slice(0, 5);
  };

  const handleSave = async () => {
    if (!content.trim()) return;

    const reflection = {
      content: content.trim(),
      tags: extractTags(content),
      timestamp: new Date().toISOString(),
      shared: shared,
    };

    console.log("Neue Reflexion:", reflection);

    try {
      // JSON in Datei umwandeln
      const jsonBlob = new Blob([JSON.stringify(reflection, null, 2)], {
        type: "application/json",
      });

      const file = new File([jsonBlob], `reflection_${Date.now()}.json`, {
        type: "application/json",
      });

      // Web3.Storage Client initialisieren
      const client = new Web3Storage({
        token: import.meta.env.VITE_WEB3_STORAGE_TOKEN,
      });

      // Datei auf IPFS hochladen
      const cid = await client.put([file]);

      console.log("IPFS CID:", cid);
    } catch (error) {
      console.error("Fehler beim IPFS-Upload:", error);
    }

    setContent("");
    setShared(false);
    onClose();
  };

  const handleClose = () => {
    setContent("");
    setShared(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Neue Reflexion
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ×
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Was willst du nicht vergessen?"
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={4}
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="shareReflection"
              checked={shared}
              onChange={(e) => setShared(e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <label
              htmlFor="shareReflection"
              className="text-sm text-gray-700 cursor-pointer"
            >
              Diese Reflexion anonym mit dem kollektiven Gedächtnis teilen
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              onClick={handleClose}
              className="px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Abbrechen
            </button>
            <button
              onClick={handleSave}
              disabled={!content.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Speichern & sichern
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewReflectionModal;
