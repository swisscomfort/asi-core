"""
ASI Core - Search Module
Semantische Suche in Reflexionen
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re


@dataclass
class SearchResult:
    """Suchergebnis-Struktur"""

    reflection_hash: str
    content_preview: str
    similarity_score: float
    matching_themes: List[str]
    timestamp: datetime
    privacy_level: str
    tags: List[str] = None
    state_value: Optional[int] = None
    state_name: Optional[str] = None


class SemanticSearchEngine:
    """Semantische Suchmaschine für Reflexionen"""

    def __init__(self, embedding_system, local_db):
        self.embedding_system = embedding_system
        self.local_db = local_db
        self.search_history = []

    def search_by_text(
        self,
        query_text: str,
        limit: int = 10,
        min_similarity: float = 0.6,
        privacy_filter: str = None,
        date_range: Tuple[datetime, datetime] = None,
    ) -> List[SearchResult]:
        """
        Sucht Reflexionen basierend auf Text-Query

        Args:
            query_text: Suchtext
            limit: Maximale Anzahl Ergebnisse
            min_similarity: Mindest-Ähnlichkeit
            privacy_filter: Filter nach Privacy-Level
            date_range: Optionaler Datumsbereich

        Returns:
            List[SearchResult]: Suchergebnisse
        """
        # Query-Embedding erstellen
        query_embedding = self.embedding_system.model.encode_text(query_text)

        # Reflexionen aus Datenbank laden
        db_reflections = self.local_db.get_reflections(
            limit=1000,  # Große Anzahl für umfassende Suche
            privacy_level=privacy_filter,
        )

        # Datumsfilter anwenden
        if date_range:
            start_date, end_date = date_range
            db_reflections = [
                r for r in db_reflections if start_date <= r.timestamp <= end_date
            ]

        search_results = []

        for db_reflection in db_reflections:
            # Reflexion für Embedding vorbereiten
            reflection_data = {
                "hash": db_reflection.hash,
                "content": self.local_db.get_reflection_by_hash(db_reflection.hash)[
                    "content"
                ],
                "themes": db_reflection.themes,
                "sentiment": db_reflection.sentiment,
            }

            # Embedding für Reflexion erstellen
            reflection_embedding_info = (
                self.embedding_system.create_reflection_embedding(reflection_data)
            )
            reflection_embedding = reflection_embedding_info["combined_embedding"]

            # Ähnlichkeit berechnen
            similarity = self.embedding_system.compute_similarity(
                query_embedding.tolist(), reflection_embedding
            )

            if similarity >= min_similarity:
                # Matching themes finden
                matching_themes = self._find_matching_themes(
                    query_text, db_reflection.themes
                )

                result = SearchResult(
                    reflection_hash=db_reflection.hash,
                    content_preview=db_reflection.content_preview,
                    similarity_score=similarity,
                    matching_themes=matching_themes,
                    timestamp=db_reflection.timestamp,
                    privacy_level=db_reflection.privacy_level,
                )

                search_results.append(result)

        # Nach Ähnlichkeit sortieren
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)

        # Suchanfrage speichern
        self._save_search_query(query_text, len(search_results))

        return search_results[:limit]

    def search_by_themes(
        self,
        themes: List[str],
        limit: int = 10,
        date_range: Tuple[datetime, datetime] = None,
    ) -> List[SearchResult]:
        """
        Sucht Reflexionen basierend auf Themen

        Args:
            themes: Liste der Suchthemen
            limit: Maximale Anzahl Ergebnisse
            date_range: Optionaler Datumsbereich

        Returns:
            List[SearchResult]: Suchergebnisse
        """
        # Reflexionen aus Datenbank laden
        db_reflections = self.local_db.get_reflections(limit=1000)

        # Datumsfilter anwenden
        if date_range:
            start_date, end_date = date_range
            db_reflections = [
                r for r in db_reflections if start_date <= r.timestamp <= end_date
            ]

        search_results = []

        for db_reflection in db_reflections:
            # Themen-Überschneidung berechnen
            common_themes = set(themes) & set(db_reflection.themes)
            theme_score = len(common_themes) / len(themes) if themes else 0

            if theme_score > 0:
                result = SearchResult(
                    reflection_hash=db_reflection.hash,
                    content_preview=db_reflection.content_preview,
                    similarity_score=theme_score,
                    matching_themes=list(common_themes),
                    timestamp=db_reflection.timestamp,
                    privacy_level=db_reflection.privacy_level,
                )

                search_results.append(result)

        # Nach Theme-Score sortieren
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)

        return search_results[:limit]

    def search_by_sentiment(
        self,
        sentiment_type: str,
        limit: int = 10,
        date_range: Tuple[datetime, datetime] = None,
    ) -> List[SearchResult]:
        """
        Sucht Reflexionen basierend auf Sentiment

        Args:
            sentiment_type: 'positive', 'negative', 'neutral'
            limit: Maximale Anzahl Ergebnisse
            date_range: Optionaler Datumsbereich

        Returns:
            List[SearchResult]: Suchergebnisse
        """
        # Reflexionen aus Datenbank laden
        db_reflections = self.local_db.get_reflections(limit=1000)

        # Datumsfilter anwenden
        if date_range:
            start_date, end_date = date_range
            db_reflections = [
                r for r in db_reflections if start_date <= r.timestamp <= end_date
            ]

        search_results = []

        for db_reflection in db_reflections:
            if db_reflection.sentiment and sentiment_type in db_reflection.sentiment:
                # Konfidenz aus Sentiment extrahieren
                try:
                    confidence_str = db_reflection.sentiment.split("(")[1].split(")")[0]
                    confidence = float(confidence_str)
                except (IndexError, ValueError):
                    confidence = 0.5

                result = SearchResult(
                    reflection_hash=db_reflection.hash,
                    content_preview=db_reflection.content_preview,
                    similarity_score=confidence,
                    matching_themes=[],
                    timestamp=db_reflection.timestamp,
                    privacy_level=db_reflection.privacy_level,
                )

                search_results.append(result)

        # Nach Konfidenz sortieren
        search_results.sort(key=lambda x: x.similarity_score, reverse=True)

        return search_results[:limit]

    def search_timeline(self, query_text: str, days_back: int = 30) -> Dict:
        """
        Erstellt eine Timeline-Suche

        Args:
            query_text: Suchtext
            days_back: Tage zurück

        Returns:
            Dict: Timeline-Daten
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Suche in Zeitraum
        results = self.search_by_text(
            query_text, limit=100, min_similarity=0.5, date_range=(start_date, end_date)
        )

        # Gruppierung nach Wochen
        weekly_groups = {}
        for result in results:
            # Woche berechnen (ISO-Woche)
            year, week, _ = result.timestamp.isocalendar()
            week_key = f"{year}-W{week:02d}"

            if week_key not in weekly_groups:
                weekly_groups[week_key] = []

            weekly_groups[week_key].append(result)

        # Timeline-Struktur erstellen
        timeline = {
            "query": query_text,
            "period": f"{days_back} Tage",
            "total_results": len(results),
            "weeks": {},
        }

        for week_key, week_results in weekly_groups.items():
            timeline["weeks"][week_key] = {
                "count": len(week_results),
                "avg_similarity": np.mean([r.similarity_score for r in week_results]),
                "top_themes": self._get_top_themes_from_results(week_results),
                "results": [
                    {
                        "hash": r.reflection_hash,
                        "preview": r.content_preview,
                        "similarity": r.similarity_score,
                        "date": r.timestamp.strftime("%Y-%m-%d"),
                    }
                    for r in week_results[:3]  # Top 3 pro Woche
                ],
            }

        return timeline

    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Gibt Suchvorschläge basierend auf partieller Eingabe

        Args:
            partial_query: Teilweise eingegebene Suchanfrage

        Returns:
            List[str]: Suchvorschläge
        """
        suggestions = []

        # Vorschläge aus häufigen Themen
        db_reflections = self.local_db.get_reflections(limit=100)
        all_themes = []
        for reflection in db_reflections:
            all_themes.extend(reflection.themes)

        # Häufigste Themen
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        # Passende Themen finden
        for theme, count in sorted(
            theme_counts.items(), key=lambda x: x[1], reverse=True
        ):
            if partial_query.lower() in theme.lower():
                suggestions.append(theme)
                if len(suggestions) >= 5:
                    break

        # Vorschläge aus Suchhistorie
        for search_query in self.search_history:
            if partial_query.lower() in search_query["query"].lower():
                suggestions.append(search_query["query"])
                if len(suggestions) >= 10:
                    break

        return list(set(suggestions))  # Duplikate entfernen

    def get_related_reflections(
        self, reflection_hash: str, limit: int = 5
    ) -> List[SearchResult]:
        """
        Findet verwandte Reflexionen zu einer gegebenen Reflexion

        Args:
            reflection_hash: Hash der Referenz-Reflexion
            limit: Maximale Anzahl Ergebnisse

        Returns:
            List[SearchResult]: Verwandte Reflexionen
        """
        # Referenz-Reflexion laden
        ref_reflection_data = self.local_db.get_reflection_by_hash(reflection_hash)
        if not ref_reflection_data:
            return []

        # Alle anderen Reflexionen laden
        all_reflections = self.local_db.get_reflections(limit=1000)
        other_reflections = [r for r in all_reflections if r.hash != reflection_hash]

        # Ähnlichkeit zu Referenz-Reflexion berechnen
        ref_reflection = {
            "hash": ref_reflection_data["hash"],
            "content": ref_reflection_data["content"],
            "themes": ref_reflection_data["themes"],
            "sentiment": ref_reflection_data["sentiment"],
        }

        similar_reflections = self.embedding_system.find_similar_reflections(
            ref_reflection,
            [
                {
                    "hash": r.hash,
                    "content": self.local_db.get_reflection_by_hash(r.hash)["content"],
                    "themes": r.themes,
                    "sentiment": r.sentiment,
                }
                for r in other_reflections
            ],
            threshold=0.6,
        )

        # In SearchResult-Format konvertieren
        results = []
        for reflection_data, similarity in similar_reflections[:limit]:
            db_reflection = next(
                (r for r in other_reflections if r.hash == reflection_data["hash"]),
                None,
            )
            if db_reflection:
                result = SearchResult(
                    reflection_hash=db_reflection.hash,
                    content_preview=db_reflection.content_preview,
                    similarity_score=similarity,
                    matching_themes=db_reflection.themes,
                    timestamp=db_reflection.timestamp,
                    privacy_level=db_reflection.privacy_level,
                )
                results.append(result)

        return results

    def _find_matching_themes(
        self, query_text: str, reflection_themes: List[str]
    ) -> List[str]:
        """
        Findet passende Themen zwischen Query und Reflexion

        Args:
            query_text: Suchtext
            reflection_themes: Themen der Reflexion

        Returns:
            List[str]: Passende Themen
        """
        query_words = set(re.findall(r"\w+", query_text.lower()))
        matching_themes = []

        for theme in reflection_themes:
            theme_words = set(re.findall(r"\w+", theme.lower()))
            if query_words & theme_words:  # Schnittmenge vorhanden
                matching_themes.append(theme)

        return matching_themes

    def _get_top_themes_from_results(self, results: List[SearchResult]) -> List[str]:
        """
        Extrahiert die häufigsten Themen aus Suchergebnissen

        Args:
            results: Suchergebnisse

        Returns:
            List[str]: Top-Themen
        """
        all_themes = []
        for result in results:
            all_themes.extend(result.matching_themes)

        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        return [
            theme
            for theme, _ in sorted(
                theme_counts.items(), key=lambda x: x[1], reverse=True
            )[:3]
        ]

    def _save_search_query(self, query: str, result_count: int):
        """
        Speichert Suchanfrage in Historie

        Args:
            query: Suchanfrage
            result_count: Anzahl gefundener Ergebnisse
        """
        search_entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": result_count,
        }

        self.search_history.append(search_entry)

        # Historie begrenzen
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]

    def search_by_state(self, state_value: int, tolerance: int = 10) -> List[SearchResult]:
        """
        Sucht Reflexionen nach Zustandswert.
        
        Args:
            state_value: Gesuchter Zustandswert (0-255)
            tolerance: Toleranzbereich
            
        Returns:
            Liste von SearchResult Objekten
        """
        print(f"🔍 Suche Reflexionen mit State {state_value} ±{tolerance}")
        
        db_reflections = self.local_db.get_reflections(limit=200)
        results = []
        
        for db_ref in db_reflections:
            reflection_data = self.local_db.get_reflection_by_hash(db_ref.hash)
            if reflection_data and 'state_value' in reflection_data:
                ref_state = reflection_data['state_value']
                
                # Prüfe ob im Toleranzbereich
                if abs(ref_state - state_value) <= tolerance:
                    # Ähnlichkeit basierend auf Abstand berechnen
                    distance = abs(ref_state - state_value)
                    similarity = 1.0 - (distance / max(tolerance, 1))
                    
                    content = reflection_data.get('content', '')
                    preview = content[:200] + '...' if len(content) > 200 else content
                    
                    result = SearchResult(
                        reflection_hash=db_ref.hash,
                        content_preview=preview,
                        similarity_score=similarity,
                        matching_themes=db_ref.themes,
                        timestamp=db_ref.timestamp,
                        privacy_level=reflection_data.get('privacy_level', 'private'),
                        tags=db_ref.tags,
                        state_value=ref_state,
                        state_name=reflection_data.get('state_name', f"State {ref_state}")
                    )
                    results.append(result)
        
        # Nach Ähnlichkeit sortieren
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        print(f"✅ Gefunden: {len(results)} Reflexionen im Zustandsbereich")
        return results

    def search_by_state_range(self, min_state: int, max_state: int) -> List[SearchResult]:
        """
        Sucht Reflexionen in einem Zustandsbereich.
        
        Args:
            min_state: Minimaler Zustandswert
            max_state: Maximaler Zustandswert
            
        Returns:
            Liste von SearchResult Objekten
        """
        print(f"🔍 Suche Reflexionen zwischen State {min_state} und {max_state}")
        
        db_reflections = self.local_db.get_reflections(limit=200)
        results = []
        
        for db_ref in db_reflections:
            reflection_data = self.local_db.get_reflection_by_hash(db_ref.hash)
            if reflection_data and 'state_value' in reflection_data:
                ref_state = reflection_data['state_value']
                
                # Prüfe ob im Bereich
                if min_state <= ref_state <= max_state:
                    # Relative Position im Bereich als Score
                    range_size = max_state - min_state
                    if range_size > 0:
                        position = (ref_state - min_state) / range_size
                        similarity = 1.0 - abs(position - 0.5) * 2  # Höher in der Mitte
                    else:
                        similarity = 1.0
                    
                    content = reflection_data.get('content', '')
                    preview = content[:200] + '...' if len(content) > 200 else content
                    
                    result = SearchResult(
                        reflection_hash=db_ref.hash,
                        content_preview=preview,
                        similarity_score=similarity,
                        matching_themes=db_ref.themes,
                        timestamp=db_ref.timestamp,
                        privacy_level=reflection_data.get('privacy_level', 'private'),
                        tags=db_ref.tags,
                        state_value=ref_state,
                        state_name=reflection_data.get('state_name', f"State {ref_state}")
                    )
                    results.append(result)
        
        # Nach State-Wert sortieren
        results.sort(key=lambda x: x.state_value)
        
        print(f"✅ Gefunden: {len(results)} Reflexionen im Bereich")
        return results

    def get_state_distribution(self) -> Dict:
        """
        Analysiert die Verteilung der Zustandswerte.
        
        Returns:
            Dictionary mit Verteilungsstatistiken
        """
        db_reflections = self.local_db.get_reflections(limit=1000)
        state_values = []
        state_counts = {}
        
        for db_ref in db_reflections:
            reflection_data = self.local_db.get_reflection_by_hash(db_ref.hash)
            if reflection_data and 'state_value' in reflection_data:
                state_value = reflection_data['state_value']
                state_values.append(state_value)
                state_counts[state_value] = state_counts.get(state_value, 0) + 1
        
        if not state_values:
            return {"message": "Keine State-Daten verfügbar"}
        
        # Statistiken berechnen
        mean_state = np.mean(state_values)
        std_state = np.std(state_values)
        min_state = min(state_values)
        max_state = max(state_values)
        
        # Häufigste States
        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Bereiche definieren
        ranges = {
            "Low (0-63)": sum(1 for s in state_values if 0 <= s <= 63),
            "Medium-Low (64-127)": sum(1 for s in state_values if 64 <= s <= 127),
            "Medium-High (128-191)": sum(1 for s in state_values if 128 <= s <= 191),
            "High (192-255)": sum(1 for s in state_values if 192 <= s <= 255)
        }
        
        return {
            "total_reflections": len(state_values),
            "mean_state": round(mean_state, 2),
            "std_state": round(std_state, 2),
            "min_state": min_state,
            "max_state": max_state,
            "unique_states": len(state_counts),
            "top_states": top_states,
            "range_distribution": ranges,
            "state_counts": state_counts
        }

    def get_search_analytics(self) -> Dict:
        """
        Erstellt Analytik zu Suchverhalten

        Returns:
            Dict: Such-Analytik
        """
        if not self.search_history:
            return {"message": "Keine Suchhistorie vorhanden"}

        # Häufigste Suchbegriffe
        all_queries = [entry["query"] for entry in self.search_history]
        query_counts = {}
        for query in all_queries:
            query_counts[query] = query_counts.get(query, 0) + 1

        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Durchschnittliche Ergebnisse
        avg_results = np.mean([entry["result_count"] for entry in self.search_history])

        return {
            "total_searches": len(self.search_history),
            "top_queries": top_queries,
            "average_results": avg_results,
            "recent_searches": self.search_history[-5:],
        }


if __name__ == "__main__":
    # Beispiel-Nutzung (benötigt initialisierte Embedding- und DB-Systeme)
    print("=== Semantic Search Test ===")
    print(
        "Hinweis: Vollständiger Test benötigt initialisierte Embedding- und DB-Systeme"
    )

    # Beispiel für Such-Funktionalitäten
    example_queries = [
        "Arbeit und Stress",
        "Familie und Dankbarkeit",
        "Zukunft und Pläne",
        "Emotionen und Gefühle",
    ]

    print("Beispiel-Suchanfragen:")
    for query in example_queries:
        print(f"  - {query}")

    print("\nSuch-Features:")
    print("  ✓ Semantische Textsuche")
    print("  ✓ Themen-basierte Suche")
    print("  ✓ Sentiment-Suche")
    print("  ✓ Timeline-Analyse")
    print("  ✓ Verwandte Reflexionen")
    print("  ✓ Suchvorschläge")
    print("  ✓ Such-Analytik")
