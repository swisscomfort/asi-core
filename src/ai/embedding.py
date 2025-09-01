"""
ASI Core - Embedding Module
Vektor-Erstellung mit lokalen Modellen für semantische Suche
"""

import numpy as np
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class LocalEmbeddingModel:
    """Einfaches lokales Embedding-Modell für Prototyping"""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.vocabulary = {}
        self.word_vectors = {}
        self.idf_scores = {}

        # Initialisiere mit deutschen Grundwörtern
        self._init_basic_vocabulary()

    def _init_basic_vocabulary(self):
        """Initialisiert grundlegendes deutsches Vokabular"""
        # Emotionswörter
        emotion_words = [
            "glücklich",
            "traurig",
            "ängstlich",
            "wütend",
            "froh",
            "müde",
            "entspannt",
            "gestresst",
            "hoffnungsvoll",
            "enttäuscht",
            "begeistert",
            "frustriert",
            "ruhig",
            "aufgeregt",
            "zufrieden",
        ]

        # Themen-Wörter
        theme_words = [
            "arbeit",
            "familie",
            "freunde",
            "gesundheit",
            "zukunft",
            "vergangenheit",
            "beziehung",
            "geld",
            "ziele",
            "träume",
            "probleme",
            "erfolg",
            "lernen",
            "wachstum",
            "veränderung",
        ]

        # Häufige Wörter
        common_words = [
            "ich",
            "mich",
            "mir",
            "mein",
            "heute",
            "gestern",
            "morgen",
            "denken",
            "fühlen",
            "sein",
            "haben",
            "machen",
            "gehen",
            "sehen",
            "wissen",
            "können",
            "wollen",
            "müssen",
            "sollen",
        ]

        all_words = emotion_words + theme_words + common_words

        for i, word in enumerate(all_words):
            self.vocabulary[word] = i
            # Einfache Vektor-Generierung (in Realität: trainierte Embeddings)
            self.word_vectors[word] = self._generate_word_vector(word, i)

    def _generate_word_vector(self, word: str, index: int) -> np.ndarray:
        """
        Generiert einen Vektor für ein Wort

        Args:
            word: Das Wort
            index: Index im Vokabular

        Returns:
            np.ndarray: Embedding-Vektor
        """
        # Deterministische Vektor-Generierung basierend auf Wort
        seed = int(hashlib.md5(word.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)

        # Normalisierter zufälliger Vektor
        vector = np.random.normal(0, 1, self.embedding_dim)
        vector = vector / np.linalg.norm(vector)

        return vector

    def preprocess_text(self, text: str) -> List[str]:
        """
        Vorverarbeitung des Textes

        Args:
            text: Eingabetext

        Returns:
            List[str]: Liste der Tokens
        """
        # Kleinbuchstaben
        text = text.lower()

        # Satzzeichen entfernen
        text = re.sub(r"[^\w\s]", " ", text)

        # Mehrere Leerzeichen reduzieren
        text = re.sub(r"\s+", " ", text)

        # Tokenisierung
        tokens = text.strip().split()

        # Stopwörter entfernen (vereinfacht)
        stopwords = {"der", "die", "das", "und", "oder", "aber", "ist", "sind"}
        tokens = [token for token in tokens if token not in stopwords]

        return tokens

    def get_word_embedding(self, word: str) -> Optional[np.ndarray]:
        """
        Ruft Embedding für ein Wort ab

        Args:
            word: Das Wort

        Returns:
            Optional[np.ndarray]: Embedding-Vektor oder None
        """
        if word in self.word_vectors:
            return self.word_vectors[word]

        # Für unbekannte Wörter: generiere neuen Vektor
        if len(word) > 2:  # Nur für sinnvolle Wörter
            vector = self._generate_word_vector(word, len(self.vocabulary))
            self.vocabulary[word] = len(self.vocabulary)
            self.word_vectors[word] = vector
            return vector

        return None

    def encode_text(self, text: str) -> np.ndarray:
        """
        Erstellt Embedding für einen Text

        Args:
            text: Eingabetext

        Returns:
            np.ndarray: Text-Embedding
        """
        tokens = self.preprocess_text(text)

        if not tokens:
            return np.zeros(self.embedding_dim)

        # Sammle Wort-Embeddings
        embeddings = []
        for token in tokens:
            embedding = self.get_word_embedding(token)
            if embedding is not None:
                embeddings.append(embedding)

        if not embeddings:
            return np.zeros(self.embedding_dim)

        # Durchschnitt der Wort-Embeddings
        text_embedding = np.mean(embeddings, axis=0)

        # Normalisierung
        norm = np.linalg.norm(text_embedding)
        if norm > 0:
            text_embedding = text_embedding / norm

        return text_embedding


class ReflectionEmbedding:
    """Spezialisierte Embedding-Klasse für Reflexionen"""

    def __init__(self):
        self.model = LocalEmbeddingModel()
        self.reflection_embeddings = {}

    def create_reflection_embedding(self, reflection_data: Dict) -> Dict:
        """
        Erstellt Embedding für eine Reflexion

        Args:
            reflection_data: Reflexionsdaten

        Returns:
            Dict: Embedding-Informationen
        """
        content = reflection_data.get("content", "")
        reflection_hash = reflection_data.get("hash", "")

        # Text-Embedding erstellen
        content_embedding = self.model.encode_text(content)

        # Themen-Embeddings
        themes = reflection_data.get("themes", [])
        theme_embeddings = []
        for theme in themes:
            theme_emb = self.model.encode_text(theme)
            theme_embeddings.append(theme_emb)

        # Sentiment-Embedding
        sentiment = reflection_data.get("sentiment", "")
        sentiment_embedding = self.model.encode_text(sentiment)

        # Kombiniertes Embedding
        combined_embedding = content_embedding
        if theme_embeddings:
            theme_avg = np.mean(theme_embeddings, axis=0)
            combined_embedding = 0.7 * content_embedding + 0.3 * theme_avg

        embedding_info = {
            "hash": reflection_hash,
            "content_embedding": content_embedding.tolist(),
            "theme_embeddings": [emb.tolist() for emb in theme_embeddings],
            "sentiment_embedding": sentiment_embedding.tolist(),
            "combined_embedding": combined_embedding.tolist(),
            "embedding_dim": self.model.embedding_dim,
            "created_at": datetime.now().isoformat(),
        }

        # Speichere für spätere Verwendung
        self.reflection_embeddings[reflection_hash] = embedding_info

        return embedding_info

    def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        Berechnet Cosinus-Ähnlichkeit zwischen zwei Embeddings

        Args:
            embedding1: Erstes Embedding
            embedding2: Zweites Embedding

        Returns:
            float: Ähnlichkeitswert (0-1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosinus-Ähnlichkeit
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Auf Bereich 0-1 normalisieren
        return (similarity + 1) / 2

    def find_similar_reflections(
        self,
        query_reflection: Dict,
        existing_reflections: List[Dict],
        threshold: float = 0.7,
    ) -> List[Tuple[Dict, float]]:
        """
        Findet ähnliche Reflexionen

        Args:
            query_reflection: Suchreflexion
            existing_reflections: Bestehende Reflexionen
            threshold: Mindest-Ähnlichkeit

        Returns:
            List[Tuple[Dict, float]]: Ähnliche Reflexionen mit Scores
        """
        # Query-Embedding erstellen
        query_embedding_info = self.create_reflection_embedding(query_reflection)
        query_embedding = query_embedding_info["combined_embedding"]

        similar_reflections = []

        for reflection in existing_reflections:
            # Embedding für Vergleichsreflexion
            reflection_embedding_info = self.create_reflection_embedding(reflection)
            reflection_embedding = reflection_embedding_info["combined_embedding"]

            # Ähnlichkeit berechnen
            similarity = self.compute_similarity(query_embedding, reflection_embedding)

            if similarity >= threshold:
                similar_reflections.append((reflection, similarity))

        # Nach Ähnlichkeit sortieren
        similar_reflections.sort(key=lambda x: x[1], reverse=True)

        return similar_reflections

    def cluster_reflections(
        self, reflections: List[Dict], num_clusters: int = 5
    ) -> Dict:
        """
        Clustert Reflexionen basierend auf Ähnlichkeit

        Args:
            reflections: Liste der Reflexionen
            num_clusters: Anzahl gewünschter Cluster

        Returns:
            Dict: Cluster-Informationen
        """
        if len(reflections) < num_clusters:
            num_clusters = len(reflections)

        # Embeddings erstellen
        embeddings = []
        for reflection in reflections:
            embedding_info = self.create_reflection_embedding(reflection)
            embeddings.append(embedding_info["combined_embedding"])

        # Einfaches K-Means Clustering (vereinfacht)
        embeddings_array = np.array(embeddings)

        # Zufällige Zentroide initialisieren
        np.random.seed(42)
        centroids = embeddings_array[
            np.random.choice(len(embeddings_array), num_clusters, replace=False)
        ]

        clusters = {i: [] for i in range(num_clusters)}

        # Reflexionen zu nächstem Zentroid zuordnen
        for i, embedding in enumerate(embeddings):
            distances = [
                1 - self.compute_similarity(embedding, centroid.tolist())
                for centroid in centroids
            ]
            closest_cluster = np.argmin(distances)
            clusters[closest_cluster].append(
                {"reflection": reflections[i], "embedding": embedding}
            )

        # Cluster-Beschreibungen generieren
        cluster_info = {}
        for cluster_id, cluster_items in clusters.items():
            if cluster_items:
                # Häufige Themen im Cluster
                all_themes = []
                for item in cluster_items:
                    themes = item["reflection"].get("themes", [])
                    all_themes.extend(themes)

                theme_counts = {}
                for theme in all_themes:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1

                top_themes = sorted(
                    theme_counts.items(), key=lambda x: x[1], reverse=True
                )[:3]

                cluster_info[cluster_id] = {
                    "size": len(cluster_items),
                    "top_themes": [theme for theme, _ in top_themes],
                    "reflections": [item["reflection"] for item in cluster_items],
                }

        return cluster_info

    def save_embeddings(self, filepath: str):
        """
        Speichert Embeddings in Datei

        Args:
            filepath: Pfad zur Ausgabedatei
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.reflection_embeddings, f, indent=2, ensure_ascii=False)

    def load_embeddings(self, filepath: str):
        """
        Lädt Embeddings aus Datei

        Args:
            filepath: Pfad zur Eingabedatei
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.reflection_embeddings = json.load(f)
        except FileNotFoundError:
            print(f"Embedding-Datei {filepath} nicht gefunden")


if __name__ == "__main__":
    # Beispiel-Nutzung
    embedding_system = ReflectionEmbedding()

    print("=== Embedding System Test ===")

    # Test-Reflexionen
    test_reflections = [
        {
            "hash": "test1",
            "content": "Heute war ein schwieriger Tag bei der Arbeit. Ich fühle mich gestresst.",
            "themes": ["arbeit", "stress"],
            "sentiment": "negative(0.7)",
        },
        {
            "hash": "test2",
            "content": "Ich bin dankbar für meine Familie und unsere gemeinsame Zeit.",
            "themes": ["familie", "dankbarkeit"],
            "sentiment": "positive(0.8)",
        },
        {
            "hash": "test3",
            "content": "Die Arbeit macht mir momentan keinen Spaß. Ich überlege zu wechseln.",
            "themes": ["arbeit", "zukunft"],
            "sentiment": "negative(0.6)",
        },
    ]

    # Embeddings erstellen
    for reflection in test_reflections:
        embedding_info = embedding_system.create_reflection_embedding(reflection)
        print(f"Embedding erstellt für: {reflection['hash']}")

    # Ähnlichkeitssuche
    query = test_reflections[0]
    similar = embedding_system.find_similar_reflections(
        query, test_reflections[1:], threshold=0.5
    )

    print(f"\nÄhnliche Reflexionen zu '{query['hash']}':")
    for reflection, score in similar:
        print(f"  {reflection['hash']}: {score:.3f}")

    # Clustering
    clusters = embedding_system.cluster_reflections(test_reflections, num_clusters=2)
    print(f"\nClustering in {len(clusters)} Gruppen:")
    for cluster_id, info in clusters.items():
        print(f"  Cluster {cluster_id}: {info['size']} Reflexionen")
        print(f"    Top-Themen: {info['top_themes']}")
