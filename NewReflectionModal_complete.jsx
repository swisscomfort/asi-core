import React, { useState, useRef } from "react";
import {
  XMarkIcon,
  CloudArrowUpIcon,
  TagIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  WifiSlashIcon,
} from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";
import StorachaService from "../services/storacha";
import {
  createReflection,
  createNote,
  createTodo,
  TODO_PRIORITIES,
} from "../core/data-model";

const NewReflectionModal = ({
  isOpen,
  onClose,
  onReflectionCreated,
  onStorachaUpdate,
}) => {
  const [activeTab, setActiveTab] = useState("reflection");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState([]);
  const [currentTag, setCurrentTag] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadingToStoracha, setUploadingToStoracha] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [isOfflineMode, setIsOfflineMode] = useState(false);
  const [uploadCID, setUploadCID] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState(TODO_PRIORITIES.MEDIUM);
  const [cognitiveInsights, setCognitiveInsights] = useState(null);
  const [showInsights, setShowInsights] = useState(true);
  const textareaRef = useRef(null);

  const commonTags = [
    "#Arbeit",
    "#Gesundheit",
    "#Familie",
    "#Projekt",
    "#Lernen",
    "#Dringend",
    "#Routine",
    "#Kreativität",
    "#Social",
    "#Finanzen",
  ];

  const handleAddTag = () => {
    if (currentTag.trim() && !tags.includes(currentTag.trim())) {
      setTags([...tags, currentTag.trim()]);
      setCurrentTag("");
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && currentTag.trim()) {
      e.preventDefault();
      handleAddTag();
    }
  };

  // Kognitive Analyse-Funktionen
  const analyzeCognitiveContent = async (text) => {
    if (!text.trim() || text.length < 20) {
      setCognitiveInsights(null);
      return;
    }

    try {
      const response = await fetch("/api/cognitive-insights", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: text }),
      });

      if (response.ok) {
        const data = await response.json();
        setCognitiveInsights(data);
      } else {
        console.warn("Kognitive Analyse nicht verfügbar");
        setCognitiveInsights(null);
      }
    } catch (error) {
      console.warn("Fehler bei kognitiver Analyse:", error);
      setCognitiveInsights(null);
    }
  };

  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);

    // Debounced kognitive Analyse
    clearTimeout(window.cognitiveAnalysisTimeout);
    window.cognitiveAnalysisTimeout = setTimeout(() => {
      analyzeCognitiveContent(newContent);
    }, 1500);
  };

  const highlightBiases = (text, biases) => {
    if (!biases || biases.length === 0) return text;

    let highlightedText = text;
    const colors = {
      absolute_terms: "bg-yellow-200",
      overgeneralization: "bg-orange-200",
      circular_reasoning: "bg-red-200",
      emotional_extremes: "bg-purple-200",
    };

    biases.forEach((bias, biasIndex) => {
      bias.instances.forEach((instance, instanceIndex) => {
        const color = colors[bias.type] || "bg-gray-200";
        const replacement = `<mark class="${color} px-1 rounded" title="${bias.suggestion}">${instance}</mark>`;
        highlightedText = highlightedText.replace(
          new RegExp(`\\b${instance}\\b`, "gi"),
          replacement
        );
      });
    });

    return highlightedText;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      alert("Bitte Titel und Inhalt eingeben.");
      return;
    }

    setIsSubmitting(true);
    setUploadProgress(20);
    setUploadStatus("Erstelle Reflexion...");
    setUploadError("");
    setIsOfflineMode(false);
    setUploadCID("");

    try {
      // Erstelle Reflexions-Objekt
      const reflection = {
        title: title.trim(),
        content: content.trim(),
        tags: tags,
        timestamp: new Date().toISOString(),
        shared: isPublic,
      };

      console.log("📝 Erstelle neue Reflexion:", reflection);
      setUploadProgress(40);
      setUploadStatus("Speichere lokal...");

      // Speichere lokal (immer)
      onReflectionCreated(reflection);
      setUploadProgress(60);

      // Storacha Upload wenn "Anonym teilen" aktiviert ist
      if (isPublic) {
        setUploadingToStoracha(true);
        setUploadStatus("Prüfe Verbindung...");

        // Offline-Check
        if (!navigator.onLine) {
          setIsOfflineMode(true);
          setUploadStatus("Offline-Modus - nur lokal gespeichert");
          setUploadProgress(100);
        } else {
          try {
            setUploadStatus("Lädt hoch...");
            setUploadProgress(70);

            // Erstelle JSON-Objekt mit Reflexion
            const reflectionData = {
              type: "reflection",
              data: reflection,
              version: "1.0",
              uploadedAt: new Date().toISOString(),
            };

            console.log("☁️ Lade zu Storacha hoch...");
            const cid = await StorachaService.uploadReflection(reflectionData);

            setUploadProgress(90);
            setUploadCID(cid);
            setUploadStatus("Erfolgreich gespeichert");

            console.log("✅ Storacha Upload erfolgreich:", cid);

            // Aktualisiere StorachaStatus-Komponente
            if (onStorachaUpdate) {
              onStorachaUpdate();
            }

            setUploadProgress(100);
          } catch (uploadError) {
            console.warn(
              "⚠️ Storacha Upload fehlgeschlagen:",
              uploadError.message
            );

            // Spezifische Fehlerbehandlung
            let errorMessage = "Upload-Fehler";
            if (uploadError.message.includes("Internetverbindung")) {
              setIsOfflineMode(true);
              errorMessage = "Offline-Modus";
            } else if (
              uploadError.message.includes("authorization") ||
              uploadError.message.includes("Credentials")
            ) {
              errorMessage = "Ungültige Zugangsdaten";
            } else if (
              uploadError.message.includes("network") ||
              uploadError.message.includes("Netzwerk")
            ) {
              errorMessage = "Verbindungsproblem";
            }

            setUploadError(errorMessage);
            setUploadStatus(`${errorMessage} - lokal gespeichert`);
            setUploadProgress(100);
          }
        }
      } else {
        setUploadStatus("Erfolgreich gespeichert");
        setUploadProgress(100);
      }

      // Modal nach kurzer Verzögerung schließen
      setTimeout(
        () => {
          handleClose();
        },
        uploadError || isOfflineMode ? 3000 : isPublic ? 2000 : 1000
      );
    } catch (error) {
      console.error("❌ Fehler beim Erstellen der Reflexion:", error);
      setUploadError("Lokaler Speicherfehler");
      setUploadStatus("Fehler beim Speichern");
      alert(`Fehler beim Speichern: ${error.message}`);
    } finally {
      setIsSubmitting(false);
      setUploadingToStoracha(false);

      // Status nach Zeit zurücksetzen
      setTimeout(() => {
        setUploadProgress(0);
        setUploadStatus("");
        setUploadError("");
        setIsOfflineMode(false);
        setUploadCID("");
      }, 4000);
    }
  };

  const handleClose = () => {
    setTitle("");
    setContent("");
    setTags([]);
    setCurrentTag("");
    setIsPublic(false);
    setDueDate("");
    setPriority(TODO_PRIORITIES.MEDIUM);
    setActiveTab("reflection");
    setUploadProgress(0);
    setUploadStatus("");
    setUploadingToStoracha(false);
    setUploadError("");
    setIsOfflineMode(false);
    setUploadCID("");
    setCognitiveInsights(null);
    setShowInsights(true);

    // Timeout löschen
    if (window.cognitiveAnalysisTimeout) {
      clearTimeout(window.cognitiveAnalysisTimeout);
    }

    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            Neue Reflexion erstellen
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Titel */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Titel *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Kurze Beschreibung deiner Reflexion..."
              required
            />
          </div>

          {/* Inhalt */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Inhalt *
            </label>
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleContentChange}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-vertical"
              placeholder="Teile deine Gedanken, Erfahrungen oder Erkenntnisse..."
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {content.length} Zeichen
            </p>

            {/* Kognitive Insights */}
            {cognitiveInsights &&
              cognitiveInsights.biases &&
              cognitiveInsights.biases.length > 0 &&
              showInsights && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-blue-900 flex items-center">
                      <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
                      Reflexionshilfe
                    </h4>
                    <button
                      type="button"
                      onClick={() => setShowInsights(false)}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      Ausblenden
                    </button>
                  </div>

                  <div className="space-y-2">
                    {cognitiveInsights.biases.slice(0, 3).map((bias, index) => (
                      <div key={index} className="text-sm">
                        <div className="flex items-start space-x-2">
                          <div className="flex-shrink-0 w-2 h-2 rounded-full bg-yellow-400 mt-1.5"></div>
                          <div>
                            <p className="text-blue-800">
                              <strong>
                                {bias.type === "absolute_terms" &&
                                  "Absolute Begriffe: "}
                                {bias.type === "overgeneralization" &&
                                  "Übergeneralisierung: "}
                                {bias.type === "circular_reasoning" &&
                                  "Kreisdenken: "}
                                {bias.type === "emotional_reasoning" &&
                                  "Emotionale Begründung: "}
                                {bias.type === "binary_thinking" &&
                                  "Schwarz-Weiß-Denken: "}
                              </strong>
                              "{bias.instances.join('", "')}"
                            </p>
                            <p className="text-blue-600 mt-1 text-xs">
                              Schwere: {Math.round(bias.severity * 100)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}

                    {cognitiveInsights.suggestions &&
                      cognitiveInsights.suggestions.length > 0 && (
                        <div className="pt-2 border-t border-blue-200">
                          <p className="text-xs font-medium text-blue-900 mb-1">
                            Verbesserungsvorschläge:
                          </p>
                          <div className="space-y-2">
                            {cognitiveInsights.suggestions
                              .slice(0, 2)
                              .map((suggestion, i) => (
                                <div key={i} className="text-xs">
                                  <p className="text-blue-700 font-medium">
                                    💡 {suggestion.question}
                                  </p>
                                  {suggestion.alternatives && (
                                    <div className="mt-1">
                                      <p className="text-blue-600">
                                        Alternativen:
                                      </p>
                                      <ul className="text-blue-600 ml-2">
                                        {suggestion.alternatives.map(
                                          (alt, j) => (
                                            <li key={j}>
                                              "{alt.original}" →{" "}
                                              {alt.alternatives}
                                            </li>
                                          )
                                        )}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              ))}
                          </div>
                        </div>
                      )}

                    {cognitiveInsights.examples &&
                      cognitiveInsights.examples.length > 0 && (
                        <div className="pt-2 border-t border-blue-200">
                          <p className="text-xs font-medium text-blue-900 mb-1">
                            Beispiele für bessere Formulierungen:
                          </p>
                          <div className="space-y-1">
                            {cognitiveInsights.examples
                              .slice(0, 2)
                              .map((example, i) => (
                                <div key={i} className="text-xs text-blue-700">
                                  <p className="line-through text-gray-500">
                                    "{example.original}"
                                  </p>
                                  <p className="text-green-700">
                                    → "{example.alternative}"
                                  </p>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}

                    {cognitiveInsights.summary && (
                      <div className="pt-2 border-t border-blue-200">
                        <p className="text-xs text-blue-800 italic">
                          {cognitiveInsights.summary}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

            {/* Option zum Wiedereinblenden */}
            {cognitiveInsights &&
              cognitiveInsights.biases &&
              cognitiveInsights.biases.length > 0 &&
              !showInsights && (
                <button
                  type="button"
                  onClick={() => setShowInsights(true)}
                  className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
                >
                  Reflexionshilfe einblenden ({cognitiveInsights.biases.length}{" "}
                  Hinweise)
                </button>
              )}
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-indigo-100 text-indigo-800"
                >
                  <TagIcon className="w-3 h-3 mr-1" />
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-1 text-indigo-600 hover:text-indigo-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Tag hinzufügen..."
              />
              <button
                type="button"
                onClick={handleAddTag}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
              >
                +
              </button>
            </div>
          </div>

          {/* Sichtbarkeit */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Anonym teilen (dezentral auf Storacha speichern)
              </span>
            </label>
            {isPublic && (
              <p className="mt-1 text-xs text-gray-500">
                Wird verschlüsselt und dezentral gespeichert
              </p>
            )}
          </div>

          {/* Upload Progress */}
          {(isSubmitting || uploadingToStoracha || uploadStatus) && (
            <div className="space-y-3">
              <div className="flex items-center text-sm">
                {isOfflineMode ? (
                  <WifiSlashIcon className="w-4 h-4 mr-2 text-orange-500" />
                ) : uploadError ? (
                  <ExclamationTriangleIcon className="w-4 h-4 mr-2 text-red-500" />
                ) : (
                  <CloudArrowUpIcon className="w-4 h-4 mr-2 text-blue-600" />
                )}
                <span
                  className={`${
                    uploadError
                      ? "text-red-600"
                      : isOfflineMode
                      ? "text-orange-600"
                      : "text-gray-600"
                  }`}
                >
                  {uploadStatus || "Speichere Reflexion..."}
                </span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    uploadError
                      ? "bg-red-500"
                      : isOfflineMode
                      ? "bg-orange-500"
                      : uploadingToStoracha
                      ? "bg-blue-600"
                      : "bg-indigo-600"
                  }`}
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>

              {uploadingToStoracha && !uploadError && (
                <p className="text-xs text-blue-600">
                  Wird zu Storacha hochgeladen...
                </p>
              )}

              {uploadError && (
                <p className="text-xs text-red-600 flex items-center">
                  <ExclamationTriangleIcon className="w-3 h-3 mr-1" />
                  {uploadError} - Reflexion wurde trotzdem lokal gespeichert
                </p>
              )}

              {isOfflineMode && (
                <p className="text-xs text-orange-600 flex items-center">
                  <WifiSlashIcon className="w-3 h-3 mr-1" />
                  Keine Internetverbindung - nur lokale Speicherung
                </p>
              )}

              {uploadCID && (
                <div className="text-xs text-green-600 bg-green-50 p-2 rounded border">
                  <p className="font-medium">
                    ✅ Erfolgreich auf Storacha gespeichert
                  </p>
                  <p className="font-mono text-green-700 truncate">
                    CID: {uploadCID}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition"
              disabled={isSubmitting}
            >
              Abbrechen
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={
                isSubmitting ||
                uploadingToStoracha ||
                !title.trim() ||
                !content.trim()
              }
            >
              {isSubmitting
                ? "Speichere..."
                : uploadingToStoracha
                ? "Lade hoch..."
                : isPublic
                ? "Speichern & sichern"
                : "Reflexion erstellen"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewReflectionModal;
