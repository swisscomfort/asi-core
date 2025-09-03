import React, { useState, useRef } from "react";
import {
  XMarkIcon,
  CloudArrowUpIcon,
  TagIcon,
  CalendarIcon,
} from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";
import StorachaService from "../services/storachaService";
import {
  createReflection,
  createNote,
  createTodo,
  TODO_PRIORITIES,
} from "../core/data-model";

const NewReflectionModal = ({ isOpen, onClose, onReflectionCreated }) => {
  const [activeTab, setActiveTab] = useState("reflection");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState([]);
  const [currentTag, setCurrentTag] = useState("");
  const [isPublic, setIsPublic] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState(TODO_PRIORITIES.MEDIUM);
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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      alert("Bitte Titel und Inhalt eingeben.");
      return;
    }

    setIsSubmitting(true);
    setUploadProgress(0);

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
      setUploadProgress(100);

      // Callback mit der neuen Reflexion (wird in App.jsx in localStorage gespeichert)
      onReflectionCreated(reflection);

      // Modal schließen und Formular zurücksetzen
      handleClose();

      // Optional: Upload zu dezentraler Speicherung im Hintergrund (wenn online)
      if (navigator.onLine && isPublic) {
        try {
          console.log("☁️ Lade zu dezentraler Speicherung hoch...");
          const uploadResult = await StorachaService.uploadReflection(
            reflection
          );
          console.log("✅ Upload erfolgreich:", uploadResult);

          // Optional: CID zur API senden
          const apiResult = await AIApiService.createReflection({
            cid: uploadResult.cid,
            title: reflection.title,
            tags: reflection.tags,
            shared: reflection.shared,
            timestamp: reflection.timestamp,
          });
          console.log("✅ Reflexion in API erstellt:", apiResult);
        } catch (uploadError) {
          console.log(
            "⚠️ Hintergrund-Upload fehlgeschlagen:",
            uploadError.message
          );
        }
      }
    } catch (error) {
      console.error("❌ Fehler beim Erstellen der Reflexion:", error);
      alert(
        `Fehler beim Speichern: ${error.message}\n\nReflexion wurde lokal gespeichert.`
      );
    } finally {
      setIsSubmitting(false);
      setUploadProgress(0);
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
              onChange={(e) => setContent(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-vertical"
              placeholder="Teile deine Gedanken, Erfahrungen oder Erkenntnisse..."
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {content.length} Zeichen
            </p>
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
                Öffentlich teilen (andere können diese Reflexion sehen)
              </span>
            </label>
          </div>

          {/* Upload Progress */}
          {isSubmitting && (
            <div className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <CloudArrowUpIcon className="w-4 h-4 mr-2" />
                Speichere Reflexion...
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
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
              disabled={isSubmitting || !title.trim() || !content.trim()}
            >
              {isSubmitting ? "Speichere..." : "Reflexion erstellen"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewReflectionModal;
