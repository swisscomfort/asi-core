import React, { useState, useRef, useEffect } from "react";
import {
  XMarkIcon,
  CloudArrowUpIcon,
  TagIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  WifiSlashIcon,
  CheckCircleIcon,
  SparklesIcon,
  CurrencyDollarIcon,
  GiftIcon,
} from "@heroicons/react/24/outline";
import AIApiService from "../services/aiApiService";
import StorachaService from "../services/storacha";
import {
  createReflection,
  createNote,
  createTodo,
  TODO_PRIORITIES,
} from "../core/data-model";
import HybridModel from "../src/modules/hybrid-model/index.js";
import TokenDashboard from "../web/src/components/TokenDashboard.jsx";

const STATES = [
  { key: 'walked', label: 'Spaziergang/Gehen' },
  { key: 'focused', label: 'Fokussiert gearbeitet' },
  { key: 'slept_well', label: 'Gut geschlafen' },
  { key: 'meditated', label: 'Meditiert' },
  { key: 'productive_morning', label: 'Produktiver Morgen' },
  { key: 'exercised', label: 'Sport gemacht' },
  { key: 'read', label: 'Gelesen' },
  { key: 'journaled', label: 'Tagebuch geschrieben' },
  { key: 'socialized', label: 'Zeit mit anderen verbracht' },
  { key: 'creative_work', label: 'Kreativ tätig' }
];

const MOOD_OPTIONS = [
  { value: 'terrible', label: '😞 Schrecklich' },
  { value: 'bad', label: '😔 Schlecht' },
  { value: 'stressed', label: '😤 Gestresst' },
  { value: 'neutral', label: '😐 Neutral' },
  { value: 'okay', label: '🙂 Okay' },
  { value: 'good', label: '😊 Gut' },
  { value: 'calm', label: '😌 Ruhig' },
  { value: 'great', label: '😄 Großartig' },
  { value: 'excellent', label: '🤩 Exzellent' }
];

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
  const [selectedStates, setSelectedStates] = useState([]);
  const [showStateSelector, setShowStateSelector] = useState(false);
  const [currentStateConfig, setCurrentStateConfig] = useState(null);
  const [hybridInsights, setHybridInsights] = useState([]);
  const [privacyValidation, setPrivacyValidation] = useState(null);
  const [shareAnonymously, setShareAnonymously] = useState(false);
  const [userWalletAddress, setUserWalletAddress] = useState(null);
  const [tokenBalance, setTokenBalance] = useState(0);
  const [showTokenReward, setShowTokenReward] = useState(false);
  const [rewardAmount, setRewardAmount] = useState(0);
  const textareaRef = useRef(null);
  const hybridModel = useRef(new HybridModel());

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

    // Initialize hybrid model and wallet
  useEffect(() => {
    const initHybridModel = async () => {
      await hybridModel.current.initialize();
      // Load initial insights
      const insights = await hybridModel.current.getInsights();
      setHybridInsights(insights);
    };
    
    // Initialize wallet address (from localStorage or generate)
    const initWallet = () => {
      let address = localStorage.getItem('asi_wallet_address');
      if (!address) {
        // Generate seed-based wallet address
        const seed = localStorage.getItem('asi_wallet_seed') || Math.random().toString(36).substring(2);
        localStorage.setItem('asi_wallet_seed', seed);
        
        // Simple address generation (in production, use proper cryptography)
        address = '0x' + Array.from(seed).map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('').substring(0, 40);
        localStorage.setItem('asi_wallet_address', address);
      }
      setUserWalletAddress(address);
    };
    
    initHybridModel();
    initWallet();
  }, []);

  // State management functions
  const handleStateSelection = (state) => {
    setCurrentStateConfig({
      ...state,
      value: 1,
      moodBefore: '',
      moodAfter: '',
      duration: '',
      notes: ''
    });
    setShowStateSelector(false);
  };

  const addSelectedState = () => {
    if (currentStateConfig) {
      const existing = selectedStates.find(s => s.key === currentStateConfig.key);
      if (!existing) {
        setSelectedStates([...selectedStates, currentStateConfig]);
      }
      setCurrentStateConfig(null);
    }
  };

  const removeSelectedState = (stateKey) => {
    setSelectedStates(selectedStates.filter(s => s.key !== stateKey));
  };

  const updateStateConfig = (stateKey, field, value) => {
    setSelectedStates(selectedStates.map(state => 
      state.key === stateKey 
        ? { ...state, [field]: value }
        : state
    ));
  };

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

    // Privacy validation
    clearTimeout(window.privacyValidationTimeout);
    window.privacyValidationTimeout = setTimeout(async () => {
      if (newContent.trim().length > 10) {
        const validation = await hybridModel.current.validatePrivacy(newContent);
        setPrivacyValidation(validation);
      }
    }, 1000);
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
    setUploadStatus("Verarbeite Reflexion...");
    setUploadError("");
    setIsOfflineMode(false);
    setUploadCID("");

    try {
      // Process with hybrid model
      setUploadProgress(40);
      setUploadStatus("Analyse läuft...");
      
      const hybridResult = await hybridModel.current.processReflection(
        title.trim(),
        content.trim(),
        selectedStates,
        shareAnonymously
      );

      setUploadProgress(60);
      setUploadStatus("Speichere lokal...");

      // Create reflection object for backwards compatibility
      const reflection = {
        title: title.trim(),
        content: content.trim(),
        tags: tags,
        timestamp: new Date().toISOString(),
        shared: isPublic,
        hybridData: hybridResult,
        selectedStates: selectedStates
      };

      console.log("📝 Erstelle neue Reflexion:", reflection);

      // Store locally (always)
      onReflectionCreated(reflection);
      setUploadProgress(80);

      // Store selected states with context
      for (const state of selectedStates) {
        await hybridModel.current.stateTracker.setLocalState(state.key, 1, {
          mood_before: state.moodBefore,
          mood_after: state.moodAfter,
          duration: parseInt(state.duration) || null,
          notes: state.notes,
          reflection_id: Date.now().toString()
        });
      }

      // Update insights
      const newInsights = await hybridModel.current.getInsights();
      setHybridInsights(newInsights);

      // Handle blockchain/storage sharing
      if (shareAnonymously && hybridResult.blockchainResults) {
        setUploadProgress(90);
        setUploadStatus("Anonym geteilt...");
        
        // Process anonymized data
        const anonymized = await hybridModel.current.anonymizer.anonymize({
          title: title.trim(),
          content: content.trim(),
          states: selectedStates.map(s => ({ key: s.key, value: 1 }))
        });
        
        // Upload to IPFS
        const cid = await hybridModel.current.chainInterface.uploadToIPFS(anonymized);
        
        // Log state to blockchain
        await hybridModel.current.chainInterface.logState('reflection_uploaded', 1, cid);
        
        if (hybridResult.blockchainResults.cid) {
          setUploadCID(hybridResult.blockchainResults.cid);
        }
      }

      // Legacy Storacha upload if public
      if (isPublic && !shareAnonymously) {
        setUploadingToStoracha(true);
        setUploadStatus("Prüfe Verbindung...");

        if (!navigator.onLine) {
          setIsOfflineMode(true);
          setUploadStatus("Offline-Modus - nur lokal gespeichert");
        } else {
          try {
            setUploadStatus("Lädt hoch...");
            setUploadProgress(90);

            const reflectionData = {
              type: "reflection",
              data: reflection,
              version: "1.0",
              uploadedAt: new Date().toISOString(),
            };

            const cid = await StorachaService.uploadReflection(reflectionData);
            setUploadCID(cid);

            if (onStorachaUpdate) {
              onStorachaUpdate({
                type: "reflection",
                cid: cid,
                title: reflection.title,
                timestamp: reflection.timestamp,
              });
            }

            setUploadStatus("Erfolgreich hochgeladen!");
          } catch (uploadError) {
            console.error("Storacha Upload Fehler:", uploadError);
            setUploadError(
              "Upload fehlgeschlagen. Reflexion wurde lokal gespeichert."
            );
            setUploadStatus("Upload-Fehler");
          }
        }
        setUploadingToStoracha(false);
      }

      setUploadProgress(100);
      setUploadStatus("Reflexion erfolgreich gespeichert!");

      // Award $MEM token for saved reflection
      await handleRewardClaim('reflection_saved', 1);

      // Reset form after successful submission
      setTimeout(() => {
        resetForm();
        onClose();
      }, 1500);

          }
        }
        setUploadingToStoracha(false);
      }

      // Reset form
      setTitle("");
      setContent("");
      setTags([]);
      setIsPublic(false);
      setCognitiveInsights(null);
      setUploadProgress(100);
      setUploadStatus("Erfolgreich gespeichert!");

      // Schließe Modal nach kurzer Verzögerung
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error("Fehler beim Speichern der Reflexion:", error);
      setUploadError("Fehler beim Speichern. Bitte versuche es erneut.");
    } finally {
      setIsSubmitting(false);
    }
  };
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
    resetForm();
    setActiveTab("reflection");

    // Timeout löschen
    if (window.cognitiveAnalysisTimeout) {
      clearTimeout(window.cognitiveAnalysisTimeout);
    }
    if (window.privacyValidationTimeout) {
      clearTimeout(window.privacyValidationTimeout);
    }

    onClose();
  };

  const resetForm = () => {
          user_address: userWalletAddress,
          activity_type: activityType
        })
      });
      
      const result = await response.json();
      
      if (!result.error) {
        setRewardAmount(amount);
        setShowTokenReward(true);
        
        // Update balance
        await fetchTokenBalance();
        
        // Hide reward notification after 3 seconds
        setTimeout(() => {
          setShowTokenReward(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Error claiming reward:', error);
    }
  };
    setTitle("");
    setContent("");
    setTags([]);
    setCurrentTag("");
    setIsPublic(false);
    setSelectedStates([]);
    setShareAnonymously(false);
    setCurrentStateConfig(null);
    setCognitiveInsights(null);
    setPrivacyValidation(null);
    setHybridInsights([]);
    setDueDate("");
    setPriority(TODO_PRIORITIES.MEDIUM);
    setUploadProgress(0);
    setUploadStatus("");
    setUploadError("");
    setUploadCID("");
    setIsOfflineMode(false);
    setUploadingToStoracha(false);
    setShowInsights(true);
  };
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
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Neue Reflexion erstellen
            </h2>
            {userWalletAddress && (
              <div className="flex items-center mt-2 text-sm text-gray-600">
                <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                <span>{tokenBalance.toFixed(2)} $MEM</span>
              </div>
            )}
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Token Reward Notification */}
        {showTokenReward && (
          <div className="bg-green-50 border-l-4 border-green-400 p-4 mx-6 mt-4 rounded-r-lg">
            <div className="flex">
              <GiftIcon className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-700">
                  🎉 Du hast {rewardAmount} $MEM Token erhalten!
                </p>
              </div>
            </div>
          </div>
        )}

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

          {/* Zustandsauswahl (Hybrid Model) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Heutige Aktivitäten/Zustände
            </label>
            
            {/* Selected States */}
            {selectedStates.length > 0 && (
              <div className="mb-3 space-y-2">
                {selectedStates.map((state) => (
                  <div key={state.key} className="flex items-center justify-between bg-green-50 border border-green-200 rounded-md p-3">
                    <div className="flex items-center">
                      <CheckCircleIcon className="w-4 h-4 text-green-600 mr-2" />
                      <span className="text-sm font-medium text-green-800">
                        {state.label || state.key}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSelectedState(state.key)}
                      className="text-green-600 hover:text-green-800 text-sm"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Add State Button */}
            <button
              type="button"
              onClick={() => setShowStateSelector(!showStateSelector)}
              className="inline-flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
            >
              <SparklesIcon className="w-4 h-4 mr-2" />
              Aktivität hinzufügen
            </button>

            {/* State Selector */}
            {showStateSelector && (
              <div className="mt-3 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-3">
                  Wähle eine Aktivität:
                </h4>
                <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                  {STATES.map((state) => (
                    <button
                      key={state.key}
                      type="button"
                      onClick={() => handleStateSelection(state)}
                      disabled={selectedStates.some(s => s.key === state.key)}
                      className={`text-left p-2 text-xs rounded transition ${
                        selectedStates.some(s => s.key === state.key)
                          ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                          : 'bg-white border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50'
                      }`}
                    >
                      {state.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* State Configuration Modal */}
            {currentStateConfig && (
              <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-3">
                  Details für "{currentStateConfig.label}":
                </h4>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">
                        Stimmung vorher
                      </label>
                      <select
                        value={currentStateConfig.moodBefore}
                        onChange={(e) => setCurrentStateConfig({
                          ...currentStateConfig,
                          moodBefore: e.target.value
                        })}
                        className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                      >
                        <option value="">Optional</option>
                        {MOOD_OPTIONS.map(mood => (
                          <option key={mood.value} value={mood.value}>
                            {mood.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">
                        Stimmung nachher
                      </label>
                      <select
                        value={currentStateConfig.moodAfter}
                        onChange={(e) => setCurrentStateConfig({
                          ...currentStateConfig,
                          moodAfter: e.target.value
                        })}
                        className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                      >
                        <option value="">Optional</option>
                        {MOOD_OPTIONS.map(mood => (
                          <option key={mood.value} value={mood.value}>
                            {mood.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">
                      Dauer (Minuten)
                    </label>
                    <input
                      type="number"
                      value={currentStateConfig.duration}
                      onChange={(e) => setCurrentStateConfig({
                        ...currentStateConfig,
                        duration: e.target.value
                      })}
                      className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                      placeholder="z.B. 30"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">
                      Notizen (optional)
                    </label>
                    <input
                      type="text"
                      value={currentStateConfig.notes}
                      onChange={(e) => setCurrentStateConfig({
                        ...currentStateConfig,
                        notes: e.target.value
                      })}
                      className="w-full text-xs border border-gray-300 rounded px-2 py-1"
                      placeholder="Zusätzliche Details..."
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      onClick={() => setCurrentStateConfig(null)}
                      className="px-3 py-1 text-xs text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Abbrechen
                    </button>
                    <button
                      type="button"
                      onClick={addSelectedState}
                      className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Hinzufügen
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Privacy Validation */}
          {privacyValidation && privacyValidation.piiFound.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
                <div>
                  <h4 className="text-sm font-medium text-yellow-800">
                    Datenschutz-Hinweis
                  </h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    Persönliche Informationen erkannt: {privacyValidation.piiFound.map(p => p.type).join(', ')}
                  </p>
                  {privacyValidation.recommendations.length > 0 && (
                    <ul className="text-xs text-yellow-600 mt-2 space-y-1">
                      {privacyValidation.recommendations.map((rec, i) => (
                        <li key={i}>• {rec}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Hybrid Insights */}
          {hybridInsights.length > 0 && (
            <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
              <h4 className="text-sm font-medium text-indigo-900 mb-2">
                💡 Erkenntnisse für dich
              </h4>
              <div className="space-y-2">
                {hybridInsights.slice(0, 3).map((insight, i) => (
                  <div key={insight.id || i} className="text-sm">
                    <p className="text-indigo-700">{insight.message}</p>
                    {insight.confidence && (
                      <p className="text-xs text-indigo-600">
                        Vertrauen: {Math.round(insight.confidence * 100)}%
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sichtbarkeit */}
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Öffentlich teilen (Storacha)
              </span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={shareAnonymously}
                onChange={(e) => setShareAnonymously(e.target.checked)}
                className="rounded border-gray-300 text-green-600 focus:ring-green-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Muster anonymisiert teilen 
                <span className="text-green-600 font-medium">(+10 $MEM)</span>
              </span>
            </label>
            
            {shareAnonymously && (
              <div className="bg-green-50 border-l-4 border-green-400 p-3 ml-6">
                <div className="flex">
                  <GiftIcon className="h-5 w-5 text-green-400" />
                  <div className="ml-3">
                    <p className="text-sm text-green-700">
                      Du erhältst 10 $MEM Token für das anonyme Teilen deiner Reflexionsmuster.
                      Deine Identität bleibt dabei vollständig geschützt.
                    </p>
                  </div>
                </div>
              </div>
            )}
                onChange={(e) => setShareAnonymously(e.target.checked)}
                className="rounded border-gray-300 text-green-600 focus:ring-green-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Anonym teilen (Blockchain + IPFS)
              </span>
            </label>
            
            {shareAnonymously && (
              <div className="pl-6 text-xs text-gray-600">
                <p>✓ Automatische Anonymisierung</p>
                <p>✓ Nur Zustände und Muster werden geteilt</p>
                <p>✓ Keine persönlichen Daten</p>
              </div>
            )}
            
            {isPublic && (
              <p className="mt-1 text-xs text-gray-500">
                Wird verschlüsselt und dezentral gespeichert</p>
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
