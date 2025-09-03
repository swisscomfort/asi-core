"""
HRM Pattern Recognition
Mustererkennung für ASI Core High-Level Reasoning
"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class PatternRecognizer:
    """
    Erkennt Muster in Reflexionen durch semantische und zeitliche Analyse
    """

    def __init__(self, embedding_system, local_db):
        """
        Initialisiert den PatternRecognizer.

        Args:
            embedding_system: Das Embedding-System.
            local_db: Die lokale Datenbank.
        """
        self.embedding_system = embedding_system
        self.local_db = local_db
        self.pattern_cache = {}
        self.temporal_window_days = 30  # 30 Tage für zeitliche Analyse

    def analyze_patterns(
        self,
        user_context: Dict[str, Any],
        threshold: float = 0.3,  # Niedrigerer Threshold
    ) -> List[Dict[str, Any]]:
        """
        Erkennt Muster im Nutzerkontext durch semantische Suche

        Args:
            user_context: Kontext der aktuellen Reflexion
            threshold: Mindest-Ähnlichkeitsschwelle (reduziert auf 0.3)

        Returns:
            Liste erkannter Muster
        """
        try:
            # Importiere Search hier um zirkuläre Importe zu vermeiden
            from src.ai.search import SemanticSearchEngine

            self.search = SemanticSearchEngine(self.embedding_system, self.local_db)

            # Debug: Zeige verfügbare Reflexionen
            if self.local_db:
                all_reflections = self.local_db.get_reflections(limit=50)
                print(f"🔍 Debug: {len(all_reflections)} Reflexionen in DB verfügbar")
            else:
                print("🔍 Debug: Keine Datenbank verfügbar")
                all_reflections = []

            # Suche nach ähnlichen vergangenen Reflexionen
            similar_entries = self._find_similar_entries(
                user_context.get("content", ""), threshold
            )

            print(
                f"🔍 Debug: {len(similar_entries)} ähnliche Einträge gefunden (threshold={threshold})"
            )

            # Analysiere zeitliche Muster
            temporal_patterns = self._analyze_temporal_patterns(similar_entries)

            # Analysiere thematische Muster
            thematic_patterns = self._analyze_thematic_patterns(similar_entries)

            # Analysiere emotionale Muster
            emotional_patterns = self._analyze_emotional_patterns(similar_entries)

            # Kombiniere alle Muster
            combined_patterns = self._combine_patterns(
                similar_entries,
                temporal_patterns,
                thematic_patterns,
                emotional_patterns,
            )

            print(f"🔍 Debug: {len(combined_patterns)} kombinierte Muster erstellt")
            return combined_patterns

        except ImportError:
            # Fallback wenn Search nicht verfügbar
            return self._generate_fallback_patterns(user_context)
        except Exception as e:
            print(f"Fehler bei Mustererkennung: {e}")
            return self._generate_fallback_patterns(user_context)

    def _find_similar_entries(
        self, content: str, threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Findet ähnliche Einträge durch semantische Suche
        """
        try:
            # Nutze die Search-Engine falls verfügbar
            if hasattr(self, "search"):
                # Reduziere min_similarity für mehr Ergebnisse
                results = self.search.search_by_text(content, min_similarity=threshold)

                # Konvertiere SearchResult zu Dictionary-Format
                similar_entries = []
                for r in results:
                    timestamp_str = ""
                    if r.timestamp:
                        timestamp_str = r.timestamp.isoformat()

                    similar_entries.append(
                        {
                            "content": r.content_preview,
                            "similarity": r.similarity_score,
                            "tags": r.matching_themes,
                            "timestamp": timestamp_str,
                            "id": r.reflection_hash,
                        }
                    )

                print(f"🔍 Debug: Search returned {len(similar_entries)} results")
                return similar_entries
            return []
        except Exception as e:
            print(f"🔍 Debug: Search error: {e}")
            return []

    def _analyze_temporal_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analysiert zeitliche Muster in den Einträgen
        """
        if not entries:
            return []

        # Sammle Tags mit Zeitstempeln
        tag_timeline = defaultdict(list)
        for entry in entries:
            timestamp = entry.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    for tag in entry.get("tags", []):
                        tag_timeline[tag].append(dt)
                except (ValueError, AttributeError):
                    continue

        # Analysiere Häufigkeiten und Trends
        temporal_patterns = []
        for tag, timestamps in tag_timeline.items():
            if len(timestamps) >= 2:
                # Sortiere Zeitstempel
                timestamps.sort()

                # Berechne Häufigkeit
                frequency = len(timestamps)

                # Berechne Trend (mehr in letzter Zeit?)
                recent_cutoff = datetime.now() - timedelta(days=14)
                recent_count = sum(1 for ts in timestamps if ts > recent_cutoff)
                older_count = frequency - recent_count

                trend = "increasing" if recent_count > older_count else "stable"
                if recent_count == 0 and older_count > 0:
                    trend = "decreasing"

                # Berechne durchschnittlichen Abstand
                if len(timestamps) > 1:
                    intervals = [
                        (timestamps[i] - timestamps[i - 1]).days
                        for i in range(1, len(timestamps))
                    ]
                    avg_interval = sum(intervals) / len(intervals)
                else:
                    avg_interval = 0

                temporal_patterns.append(
                    {
                        "tag": tag,
                        "frequency": frequency,
                        "trend": trend,
                        "avg_interval_days": round(avg_interval, 1),
                        "last_occurrence": timestamps[-1].isoformat(),
                        "consistency_score": self._calculate_consistency(timestamps),
                    }
                )

        # Sortiere nach Häufigkeit
        temporal_patterns.sort(key=lambda x: x["frequency"], reverse=True)
        return temporal_patterns[:10]  # Top 10

    def _analyze_thematic_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analysiert thematische Muster in den Inhalten
        """
        if not entries:
            return []

        # Sammle alle Inhalte
        all_content = " ".join([e.get("content", "") for e in entries])

        # Extrahiere Schlüsselwörter
        keywords = self._extract_keywords(all_content)

        # Analysiere Tag-Kombinationen
        tag_combinations = self._analyze_tag_combinations(entries)

        thematic_patterns = []

        # Füge Keyword-Muster hinzu
        for keyword, count in keywords.most_common(5):
            thematic_patterns.append(
                {
                    "type": "keyword",
                    "theme": keyword,
                    "frequency": count,
                    "relevance": min(count / len(entries), 1.0),
                }
            )

        # Füge Tag-Kombinationsmuster hinzu
        for combo, count in tag_combinations.most_common(3):
            thematic_patterns.append(
                {
                    "type": "tag_combination",
                    "theme": " + ".join(combo),
                    "frequency": count,
                    "relevance": count / len(entries),
                }
            )

        return thematic_patterns

    def _analyze_emotional_patterns(
        self, entries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analysiert emotionale Muster in den Reflexionen
        """
        emotional_keywords = {
            "positiv": [
                "gut",
                "toll",
                "super",
                "glücklich",
                "zufrieden",
                "erfolgreich",
            ],
            "negativ": ["schlecht", "müde", "gestresst", "traurig", "frustriert"],
            "neutral": ["okay", "normal", "durchschnittlich"],
            "energie": ["energie", "kraft", "motivation", "antrieb"],
            "ruhe": ["ruhe", "entspannt", "gelassen", "friedlich"],
        }

        emotion_counts = defaultdict(int)
        total_entries = len(entries)

        for entry in entries:
            content = entry.get("content", "").lower()
            for emotion, keywords in emotional_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        emotion_counts[emotion] += 1
                        break  # Nur einmal pro Eintrag zählen

        emotional_patterns = []
        for emotion, count in emotion_counts.items():
            if count > 0:
                emotional_patterns.append(
                    {
                        "type": "emotional",
                        "emotion": emotion,
                        "frequency": count,
                        "percentage": round((count / total_entries) * 100, 1),
                    }
                )

        return sorted(emotional_patterns, key=lambda x: x["frequency"], reverse=True)

    def _extract_keywords(self, text: str) -> Counter:
        """
        Extrahiert relevante Schlüsselwörter aus Text
        """
        # Einfache Keyword-Extraktion
        # Entferne Satzzeichen und konvertiere zu lowercase
        clean_text = re.sub(r"[^\w\s]", " ", text.lower())
        words = clean_text.split()

        # Filtere stopwords und kurze Wörter
        stopwords = {
            "der",
            "die",
            "das",
            "und",
            "oder",
            "aber",
            "ich",
            "du",
            "er",
            "sie",
            "es",
            "wir",
            "ihr",
            "sie",
            "ein",
            "eine",
            "ist",
            "war",
            "hat",
            "haben",
            "bin",
            "bist",
            "sind",
            "war",
            "waren",
            "zu",
            "von",
            "mit",
            "für",
            "auf",
            "an",
            "in",
            "über",
            "unter",
            "vor",
            "nach",
            "bei",
            "durch",
            "gegen",
            "ohne",
        }

        filtered_words = [
            word for word in words if len(word) > 3 and word not in stopwords
        ]

        return Counter(filtered_words)

    def _analyze_tag_combinations(self, entries: List[Dict[str, Any]]) -> Counter:
        """
        Analysiert häufige Tag-Kombinationen
        """
        combinations = Counter()

        for entry in entries:
            tags = entry.get("tags", [])
            if len(tags) >= 2:
                # Alle 2er-Kombinationen
                for i in range(len(tags)):
                    for j in range(i + 1, len(tags)):
                        combo = tuple(sorted([tags[i], tags[j]]))
                        combinations[combo] += 1

        return combinations

    def _calculate_consistency(self, timestamps: List[datetime]) -> float:
        """
        Berechnet Konsistenz-Score basierend auf Zeitstempel-Verteilung
        """
        if len(timestamps) < 2:
            return 0.0

        # Berechne Standardabweichung der Intervalle
        timestamps.sort()
        intervals = [
            (timestamps[i] - timestamps[i - 1]).days for i in range(1, len(timestamps))
        ]

        if not intervals:
            return 0.0

        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = variance**0.5

        # Konsistenz ist umgekehrt proportional zur Standardabweichung
        # Normalisiert auf 0-1 Skala
        consistency = max(0, 1 - (std_dev / max(avg_interval, 1)))
        return round(consistency, 2)

    def _combine_patterns(
        self,
        similar_entries: List[Dict[str, Any]],
        temporal_patterns: List[Dict[str, Any]],
        thematic_patterns: List[Dict[str, Any]],
        emotional_patterns: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Kombiniert alle Muster zu einem kohärenten Bild
        """
        combined_patterns = []

        # Muster aus ähnlichen Einträgen
        for entry in similar_entries[:3]:
            combined_patterns.append(
                {
                    "type": "similarity",
                    "content": (
                        entry["content"][:100] + "..."
                        if len(entry["content"]) > 100
                        else entry["content"]
                    ),
                    "similarity": entry["similarity"],
                    "tags": entry.get("tags", [])[:2],
                    "source": "semantic_search",
                }
            )

        # Zeitliche Muster
        for pattern in temporal_patterns[:3]:
            combined_patterns.append(
                {
                    "type": "temporal",
                    "tag": pattern["tag"],
                    "frequency": pattern["frequency"],
                    "trend": pattern["trend"],
                    "consistency": pattern["consistency_score"],
                    "source": "temporal_analysis",
                }
            )

        # Thematische Muster
        for pattern in thematic_patterns[:2]:
            combined_patterns.append(
                {
                    "type": "thematic",
                    "theme": pattern["theme"],
                    "frequency": pattern["frequency"],
                    "relevance": pattern["relevance"],
                    "source": "thematic_analysis",
                }
            )

        # Emotionale Muster
        for pattern in emotional_patterns[:2]:
            combined_patterns.append(
                {
                    "type": "emotional",
                    "emotion": pattern["emotion"],
                    "frequency": pattern["frequency"],
                    "percentage": pattern["percentage"],
                    "source": "emotional_analysis",
                }
            )

        return combined_patterns

    def _generate_fallback_patterns(
        self, user_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generiert Basis-Muster wenn keine historischen Daten verfügbar
        """
        content = user_context.get("content", "").lower()
        tags = user_context.get("tags", [])

        fallback_patterns = []

        # Basis-Analyse des aktuellen Inhalts
        if "arbeit" in content or "job" in content:
            fallback_patterns.append(
                {
                    "type": "thematic",
                    "theme": "arbeit",
                    "frequency": 1,
                    "relevance": 0.8,
                    "source": "content_analysis",
                }
            )

        if "stress" in content or "müde" in content:
            fallback_patterns.append(
                {
                    "type": "emotional",
                    "emotion": "negativ",
                    "frequency": 1,
                    "percentage": 100.0,
                    "source": "content_analysis",
                }
            )

        # Tag-basierte Muster
        for tag in tags[:2]:
            fallback_patterns.append(
                {
                    "type": "tag_based",
                    "tag": tag,
                    "frequency": 1,
                    "source": "current_tags",
                }
            )

        return fallback_patterns

    def get_pattern_insights(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generiert Meta-Einsichten über die erkannten Muster
        """
        if not patterns:
            return {"message": "Keine Muster erkannt"}

        pattern_types = Counter(p["type"] for p in patterns)

        insights = {
            "total_patterns": len(patterns),
            "pattern_diversity": len(pattern_types),
            "dominant_type": pattern_types.most_common(1)[0][0],
            "coverage": {
                "similarity": len([p for p in patterns if p["type"] == "similarity"]),
                "temporal": len([p for p in patterns if p["type"] == "temporal"]),
                "thematic": len([p for p in patterns if p["type"] == "thematic"]),
                "emotional": len([p for p in patterns if p["type"] == "emotional"]),
            },
        }

        # Qualitäts-Assessment
        high_quality_patterns = [
            p
            for p in patterns
            if (
                p.get("similarity", 0) > 0.7
                or p.get("frequency", 0) > 2
                or p.get("relevance", 0) > 0.6
            )
        ]

        insights["quality_score"] = len(high_quality_patterns) / len(patterns)
        insights["maturity_level"] = self._assess_pattern_maturity(insights)

        return insights

    def _assess_pattern_maturity(self, insights: Dict[str, Any]) -> str:
        """
        Bewertet die Reife der Mustererkennung
        """
        quality = insights["quality_score"]
        diversity = insights["pattern_diversity"]
        total = insights["total_patterns"]

        if quality > 0.7 and diversity >= 3 and total >= 5:
            return "Hoch - Reichhaltige Musterstruktur erkannt"
        elif quality > 0.5 and diversity >= 2 and total >= 3:
            return "Mittel - Solide Mustergrundlage vorhanden"
        else:
            return "Niedrig - Muster entwickeln sich noch"
