import { useState, useEffect } from "react";
import NewReflectionModal from "./components/NewReflectionModal";
import AISearch from "./components/AISearch";
import ReflectionsList from "./components/ReflectionsList";
import AIInsights from "./components/AIInsights";
import DebugPanel from "./components/DebugPanel";
import { PWAInstallPrompt } from "./components/PWAInstallPrompt";
import { ConnectionStatus } from "./components/ConnectionStatus";
import { OfflineStats } from "./components/OfflineStats";
import { TodoList } from "./components/TodoList";
import { TodoStats } from "./components/TodoStats";
import ASIDashboard from "./components/ASIDashboard";
import TicketBoard from "./components/TicketBoard";
import { localStorageService } from "./services/localStorage";
import { syncService } from "./services/syncService";
import { NOTE_TYPES } from "./core/data-model";

export default function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [selectedReflection, setSelectedReflection] = useState(null);
  const [activeTab, setActiveTab] = useState("search"); // 'search', 'insights', 'todos', 'asi-core', 'tickets'

  useEffect(() => {
    localStorageService.init();
  }, []);

  const handleSearchResults = (results) => {
    setSearchResults(results);
    setActiveTab("search");
  };

  const handleReflectionSelect = (reflection) => {
    setSelectedReflection(reflection);
    setActiveTab("insights");
  };

  const handleTodoSelect = (todo) => {
    setSelectedReflection(todo);
    setActiveTab("insights");
  };

  const handleReflectionCreated = async (newItem) => {
    // Save to local storage based on type
    if (newItem.type === NOTE_TYPES.TODO) {
      await localStorageService.saveTodo(newItem);
    } else {
      await localStorageService.saveReflection(newItem);
    }

    setSelectedReflection(newItem);
    setActiveTab(newItem.type === NOTE_TYPES.TODO ? "todos" : "insights");
    // Refresh der Liste durch Zurücksetzen der Suchergebnisse
    setSearchResults(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm px-6 py-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">ASI Core</h1>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-lg transition"
          >
            Neu erstellen
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Linke Spalte: Suche & Liste */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI Search */}
            <AISearch onSearchResults={handleSearchResults} />

            {/* Navigation Tabs */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab("search")}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "search"
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    📚 Reflexionen
                  </button>
                  <button
                    onClick={() => setActiveTab("todos")}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "todos"
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    ✅ To-Dos
                  </button>
                  <button
                    onClick={() => setActiveTab("insights")}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "insights"
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    🧠 KI-Insights
                  </button>
                  <button
                    onClick={() => setActiveTab("asi-core")}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "asi-core"
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    🚀 ASI Core
                  </button>
                  <button
                    onClick={() => setActiveTab("tickets")}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === "tickets"
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    }`}
                  >
                    🎫 Oryn Tickets
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {activeTab === "search" && (
                  <ReflectionsList
                    searchResults={searchResults}
                    onReflectionSelect={handleReflectionSelect}
                  />
                )}
                {activeTab === "todos" && (
                  <TodoList onTodoSelect={handleTodoSelect} />
                )}
                {activeTab === "tickets" && (
                  <TicketBoard />
                )}
                {activeTab === "insights" && selectedReflection && (
                  <AIInsights currentReflection={selectedReflection} />
                )}
                {activeTab === "insights" && !selectedReflection && (
                  <div className="text-center py-8">
                    <div className="text-gray-400 text-4xl mb-4">🧠</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Wähle ein Item aus
                    </h3>
                    <p className="text-gray-600">
                      Klicke auf eine Reflexion oder ein To-Do, um KI-Insights
                      und Mustererkennungen zu sehen.
                    </p>
                  </div>
                )}
                {activeTab === "asi-core" && (
                  <div className="bg-transparent">
                    <ASIDashboard className="border-0 shadow-none" />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Rechte Spalte: Zusätzliche Info */}
          <div className="space-y-6">
            {/* Todo Stats Card */}
            <TodoStats />

            {/* Offline Stats Card */}
            <OfflineStats />

            {/* Welcome Card */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4">
                🚀 Dein digitales Gedächtnis
              </h2>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                ASI Core nutzt künstliche Intelligenz, um deine Gedanken zu
                verstehen, Muster zu erkennen und dir dabei zu helfen, dich
                selbst besser kennenzulernen.
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  Offline-First & PWA
                </div>
                <div className="flex items-center text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  Lokal & dezentral gespeichert
                </div>
                <div className="flex items-center text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  KI-gestützte Mustererkennung
                </div>
                <div className="flex items-center text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  Semantische Suche
                </div>
                <div className="flex items-center text-gray-600">
                  <span className="text-green-500 mr-2">✓</span>
                  Anonymer Austausch möglich
                </div>
              </div>
            </div>

            {/* Stats Card */}
            {selectedReflection && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold mb-4">📊 Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Erstellt:</span>
                    <span className="font-medium">
                      {new Date(
                        selectedReflection.timestamp
                      ).toLocaleDateString("de-DE")}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Tags:</span>
                    <span className="font-medium">
                      {selectedReflection.tags?.length || 0}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <span className="font-medium">
                      {selectedReflection.shared ? "🌐 Geteilt" : "🔒 Privat"}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Sync:</span>
                    <span className="font-medium">
                      {selectedReflection.synced ? "✅ Sync" : "⏳ Wartend"}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-white border-t px-6 py-4 text-center text-sm text-gray-500">
        ASI Core v2.0.0 PWA • Offline-First & Dezentral • Made with ❤️
      </footer>

      <NewReflectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onReflectionCreated={handleReflectionCreated}
      />

      <DebugPanel />
      <PWAInstallPrompt />
      <ConnectionStatus />
    </div>
  );
}
