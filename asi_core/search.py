"""
ASI Core - Semantische Suche und Embedding-Generierung
Implementierung von Vektor-Embeddings und semantischer Suche für das ASI-System
"""

import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

# Logger konfigurieren
logger = logging.getLogger(__name__)

# Globaler Cache für Embeddings (simuliert lokale Speicherung)
EMBEDDING_CACHE = {}
EMBEDDING_METADATA = {}


class ASIEmbeddingGenerator:
    """Generator für semantische Embeddings mit sentence-transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialisiert den Embedding-Generator

        Args:
            model_name: Name des vortrainierten sentence-transformers Modells
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Lädt das sentence-transformers Modell"""
        try:
            logger.info(f"Lade sentence-transformers Modell: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Modell erfolgreich geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden des Modells: {e}")
            raise

    def generate_embedding(self, text: str) -> bytes:
        """
        Generiert ein Embedding für den gegebenen Text

        Args:
            text: Text für den das Embedding generiert werden soll

        Returns:
            bytes: Embedding als Bytes-Array
        """
        try:
            if not self.model:
                self._load_model()

            # Text-Preprocessing
            cleaned_text = self._preprocess_text(text)

            # Embedding generieren
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)

            # Als Bytes zurückgeben
            embedding_bytes = embedding.tobytes()

            logger.debug(
                f"Embedding generiert für Text ({len(text)} Zeichen) -> {len(embedding_bytes)} Bytes"
            )
            return embedding_bytes

        except Exception as e:
            logger.error(f"Fehler bei Embedding-Generierung: {e}")
            raise

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocesst den Text für bessere Embeddings

        Args:
            text: Rohtext

        Returns:
            str: Bereinigter Text
        """
        # Entferne übermäßige Leerzeichen
        text = " ".join(text.split())

        # Begrenze Textlänge (sentence-transformers haben typisch ein Limit)
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]

        return text

    def bytes_to_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Konvertiert Bytes zurück zu numpy array

        Args:
            embedding_bytes: Embedding als Bytes

        Returns:
            np.ndarray: Embedding als numpy array
        """
        try:
            # Dimensionen des Modells abrufen
            if not self.model:
                self._load_model()

            # Beispiel-Embedding generieren um Dimensionen zu ermitteln
            sample_embedding = self.model.encode("test", convert_to_numpy=True)
            expected_shape = sample_embedding.shape
            expected_dtype = sample_embedding.dtype

            # Bytes zu numpy array konvertieren
            embedding = np.frombuffer(embedding_bytes, dtype=expected_dtype)
            embedding = embedding.reshape(expected_shape)

            return embedding

        except Exception as e:
            logger.error(f"Fehler bei Bytes-zu-Embedding Konvertierung: {e}")
            raise


class ASISemanticSearch:
    """Semantische Suchmaschine für ASI-Reflektionen"""

    def __init__(self, embedding_generator: ASIEmbeddingGenerator):
        """
        Initialisiert die Suchmaschine

        Args:
            embedding_generator: Instanz des Embedding-Generators
        """
        self.embedding_generator = embedding_generator
        self.cache_file = Path("data/embedding_cache.pkl")
        self._load_cache()

    def _load_cache(self):
        """Lädt den Embedding-Cache aus der Datei"""
        global EMBEDDING_CACHE, EMBEDDING_METADATA

        try:
            if self.cache_file.exists():
                with open(self.cache_file, "rb") as f:
                    cache_data = pickle.load(f)
                    EMBEDDING_CACHE = cache_data.get("embeddings", {})
                    EMBEDDING_METADATA = cache_data.get("metadata", {})
                logger.info(f"Embedding-Cache geladen: {len(EMBEDDING_CACHE)} Einträge")
            else:
                logger.info("Neuer Embedding-Cache erstellt")

        except Exception as e:
            logger.error(f"Fehler beim Laden des Caches: {e}")
            EMBEDDING_CACHE = {}
            EMBEDDING_METADATA = {}

    def _save_cache(self):
        """Speichert den Embedding-Cache in eine Datei"""
        try:
            # Verzeichnis erstellen falls es nicht existiert
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {"embeddings": EMBEDDING_CACHE, "metadata": EMBEDDING_METADATA}

            with open(self.cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            logger.debug(
                f"Embedding-Cache gespeichert: {len(EMBEDDING_CACHE)} Einträge"
            )

        except Exception as e:
            logger.error(f"Fehler beim Speichern des Caches: {e}")

    def store_embedding(self, cid: str, embedding_bytes: bytes, text_preview: str = ""):
        """
        Speichert ein Embedding im lokalen Cache

        Args:
            cid: Content ID (IPFS/Arweave)
            embedding_bytes: Embedding als Bytes
            text_preview: Kurze Textvorschau für die Anzeige
        """
        global EMBEDDING_CACHE, EMBEDDING_METADATA

        try:
            EMBEDDING_CACHE[cid] = embedding_bytes
            EMBEDDING_METADATA[cid] = {
                "text_preview": text_preview[:200],  # Erste 200 Zeichen
                "timestamp": datetime.now().isoformat(),
                "embedding_size": len(embedding_bytes),
            }

            self._save_cache()
            logger.info(f"Embedding gespeichert für CID: {cid}")

        except Exception as e:
            logger.error(f"Fehler beim Speichern des Embeddings: {e}")

    def search_ASI_memory(self, query_text: str, num_results: int = 5) -> List[Dict]:
        """
        Sucht in den gespeicherten ASI-Reflektionen basierend auf semantischer Ähnlichkeit

        Args:
            query_text: Suchtext
            num_results: Anzahl der zurückzugebenden Ergebnisse

        Returns:
            List[Dict]: Liste der ähnlichsten Einträge mit CID, Vorschau und Ähnlichkeitswert
        """
        try:
            if not EMBEDDING_CACHE:
                logger.warning("Keine Embeddings im Cache gefunden")
                return []

            # Query-Embedding generieren
            query_embedding_bytes = self.embedding_generator.generate_embedding(
                query_text
            )
            query_embedding = self.embedding_generator.bytes_to_embedding(
                query_embedding_bytes
            )

            # Ähnlichkeiten berechnen
            similarities = []

            for cid, stored_embedding_bytes in EMBEDDING_CACHE.items():
                try:
                    # Gespeichertes Embedding laden
                    stored_embedding = self.embedding_generator.bytes_to_embedding(
                        stored_embedding_bytes
                    )

                    # Cosinus-Ähnlichkeit berechnen
                    similarity = self._cosine_similarity(
                        query_embedding, stored_embedding
                    )

                    # Metadata abrufen
                    metadata = EMBEDDING_METADATA.get(cid, {})

                    similarities.append(
                        {
                            "cid": cid,
                            "similarity": float(similarity),
                            "text_preview": metadata.get("text_preview", ""),
                            "timestamp": metadata.get("timestamp", ""),
                            "embedding_size": metadata.get("embedding_size", 0),
                        }
                    )

                except Exception as e:
                    logger.error(
                        f"Fehler bei Ähnlichkeitsberechnung für CID {cid}: {e}"
                    )
                    continue

            # Nach Ähnlichkeit sortieren und top N zurückgeben
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:num_results]

            logger.info(
                f"Semantische Suche abgeschlossen: {len(results)} Ergebnisse für '{query_text}'"
            )

            return results

        except Exception as e:
            logger.error(f"Fehler bei semantischer Suche: {e}")
            return []

    def _cosine_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Berechnet die Cosinus-Ähnlichkeit zwischen zwei Embeddings

        Args:
            embedding1: Erstes Embedding
            embedding2: Zweites Embedding

        Returns:
            float: Cosinus-Ähnlichkeit (-1 bis 1)
        """
        try:
            # Flatten der Arrays falls mehrdimensional
            emb1 = embedding1.flatten()
            emb2 = embedding2.flatten()

            # Cosinus-Ähnlichkeit berechnen
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return similarity

        except Exception as e:
            logger.error(f"Fehler bei Cosinus-Ähnlichkeitsberechnung: {e}")
            return 0.0

    def get_cache_stats(self) -> Dict:
        """
        Gibt Statistiken über den Embedding-Cache zurück

        Returns:
            Dict: Cache-Statistiken
        """
        return {
            "total_embeddings": len(EMBEDDING_CACHE),
            "cache_file_exists": self.cache_file.exists(),
            "cache_file_size": (
                self.cache_file.stat().st_size if self.cache_file.exists() else 0
            ),
            "oldest_entry": min(
                [meta.get("timestamp", "") for meta in EMBEDDING_METADATA.values()],
                default="",
            ),
            "newest_entry": max(
                [meta.get("timestamp", "") for meta in EMBEDDING_METADATA.values()],
                default="",
            ),
        }


# Convenience Functions für einfache Nutzung


def generate_embedding(text: str) -> bytes:
    """
    Convenience-Funktion zur Embedding-Generierung

    Args:
        text: Text für das Embedding

    Returns:
        bytes: Embedding als Bytes
    """
    generator = ASIEmbeddingGenerator()
    return generator.generate_embedding(text)


def search_ASI_memory(query_text: str, num_results: int = 5) -> List[Dict]:
    """
    Convenience-Funktion für semantische Suche

    Args:
        query_text: Suchtext
        num_results: Anzahl Ergebnisse

    Returns:
        List[Dict]: Suchergebnisse
    """
    generator = ASIEmbeddingGenerator()
    search_engine = ASISemanticSearch(generator)
    return search_engine.search_ASI_memory(query_text, num_results)


# Beispiel für Testing und Demonstration
if __name__ == "__main__":
    # Logging konfigurieren
    logging.basicConfig(level=logging.INFO)

    # Generator und Suchmaschine initialisieren
    generator = ASIEmbeddingGenerator()
    search_engine = ASISemanticSearch(generator)

    # Beispiel-Texte für Testing
    test_texts = [
        "Heute war ein sehr stressiger Tag bei der Arbeit. Viele Meetings und Deadline-Druck.",
        "Ich bin glücklich über den schönen Sonnenuntergang am Strand. Sehr entspannend.",
        "Probleme in der Beziehung sorgen für Unruhe. Kommunikation ist schwierig.",
        "Erfolgreiches Projekt abgeschlossen. Team-Arbeit funktioniert sehr gut.",
        "Gesundheitliche Probleme bereiten mir Sorgen. Arztbesuch steht an.",
    ]

    # Test-Embeddings generieren und speichern
    print("Generiere Test-Embeddings...")
    for i, text in enumerate(test_texts):
        embedding = generator.generate_embedding(text)
        cid = f"test_cid_{i+1}"
        search_engine.store_embedding(cid, embedding, text)

    # Cache-Statistiken anzeigen
    stats = search_engine.get_cache_stats()
    print(f"Cache-Statistiken: {stats}")

    # Test-Suchen durchführen
    test_queries = [
        "Stress und Arbeit",
        "Glück und Entspannung",
        "Beziehungsprobleme",
        "Erfolg im Team",
        "Gesundheit und Sorgen",
    ]

    print("\nFühre Test-Suchen durch...")
    for query in test_queries:
        print(f"\nSuche: '{query}'")
        results = search_engine.search_ASI_memory(query, 3)
        for i, result in enumerate(results, 1):
            print(
                f"  {i}. CID: {result['cid']}, Ähnlichkeit: {result['similarity']:.3f}"
            )
            print(f"     Text: {result['text_preview']}")
