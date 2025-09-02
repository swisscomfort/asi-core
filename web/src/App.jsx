import { useState } from "react";
import NewReflectionModal from "./components/NewReflectionModal";

export default function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow-sm px-6 py-4">
        <h1 className="text-2xl font-bold text-indigo-600">ASI Core</h1>
      </header>

      <main className="flex-1 p-6 max-w-4xl mx-auto w-full">
        <section className="text-center py-12">
          <h2 className="text-3xl font-semibold mb-4">
            Dein digitales Gedächtnis
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Lokal. Anonym. Für immer.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-6 py-3 rounded-lg transition"
          >
            Neue Reflexion
          </button>
        </section>
      </main>

      <footer className="bg-gray-100 px-6 py-4 text-center text-sm text-gray-500">
        ASI Core v1.0.0 • Dezentral & kostenlos
      </footer>

      <NewReflectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
