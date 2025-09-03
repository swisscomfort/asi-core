"""
HRM Detail Analyzer
Detailanalyse für kontextbewusste Aktionsplanung
"""

import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List


class DetailAnalyzer:
    """
    Analysiert Details im Nutzerkontext für präzise Low-Level Aktionen
    """

    def __init__(self):
        self.emotion_patterns = self._load_emotion_patterns()
        self.context_indicators = self._load_context_indicators()
        self.urgency_markers = self._load_urgency_markers()

    def analyze_details(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt detaillierte Kontextanalyse durch

        Args:
            user_context: Kontext der aktuellen Reflexion

        Returns:
            Detaillierte Analyse-Ergebnisse
        """
        content = user_context.get("content", "")
        tags = user_context.get("tags", [])
        timestamp = user_context.get("timestamp", datetime.now().isoformat())

        analysis = {
            "emotional_state": self._analyze_emotional_state(content),
            "urgency_level": self._analyze_urgency(content),
            "time_context": self._analyze_time_context(timestamp),
            "energy_level": self._analyze_energy_indicators(content),
            "stress_indicators": self._analyze_stress_level(content),
            "motivation_factors": self._analyze_motivation(content),
            "context_type": self._classify_context_type(content, tags),
            "actionability": self._assess_actionability(content),
            "complexity_level": self._assess_complexity(content),
            "personal_patterns": self._detect_personal_patterns(content, tags),
        }

        # Meta-Analyse
        analysis["confidence_score"] = self._calculate_analysis_confidence(analysis)
        analysis["recommendations"] = self._generate_detail_recommendations(analysis)

        return analysis

    def _analyze_emotional_state(self, content: str) -> Dict[str, Any]:
        """
        Analysiert emotionalen Zustand aus dem Inhalt
        """
        content_lower = content.lower()
        emotions = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "energetic": 0,
            "calm": 0,
            "stressed": 0,
        }

        # Scoring basierend auf Emotion-Patterns
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    emotions[emotion] += 1

        # Normalisiere Scores
        total_indicators = sum(emotions.values())
        if total_indicators > 0:
            normalized_emotions = {
                k: round(v / total_indicators, 2) for k, v in emotions.items()
            }
        else:
            normalized_emotions = emotions

        # Bestimme dominante Emotion
        dominant_emotion = max(normalized_emotions.items(), key=lambda x: x[1])

        return {
            "scores": normalized_emotions,
            "dominant": dominant_emotion[0],
            "confidence": dominant_emotion[1],
            "indicators_found": total_indicators,
            "overall_valence": self._calculate_valence(normalized_emotions),
        }

    def _analyze_urgency(self, content: str) -> Dict[str, Any]:
        """
        Analysiert Dringlichkeitslevel
        """
        content_lower = content.lower()
        urgency_score = 0
        found_markers = []

        for marker in self.urgency_markers:
            if marker in content_lower:
                urgency_score += 1
                found_markers.append(marker)

        # Bestimme Urgency Level
        if urgency_score >= 3:
            level = "high"
        elif urgency_score >= 1:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "score": urgency_score,
            "markers": found_markers,
            "recommendation": self._get_urgency_recommendation(level),
        }

    def _analyze_time_context(self, timestamp: str) -> Dict[str, Any]:
        """
        Analysiert zeitlichen Kontext
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            dt = datetime.now()

        hour = dt.hour
        weekday = dt.weekday()  # 0 = Montag, 6 = Sonntag

        # Time of Day
        if 5 <= hour < 12:
            time_period = "morning"
            energy_expectation = "high"
        elif 12 <= hour < 17:
            time_period = "afternoon"
            energy_expectation = "medium"
        elif 17 <= hour < 22:
            time_period = "evening"
            energy_expectation = "medium"
        else:
            time_period = "night"
            energy_expectation = "low"

        # Day of Week
        if weekday < 5:  # Montag-Freitag
            day_type = "weekday"
            work_context = True
        else:  # Wochenende
            day_type = "weekend"
            work_context = False

        return {
            "hour": hour,
            "time_period": time_period,
            "day_type": day_type,
            "work_context": work_context,
            "expected_energy": energy_expectation,
            "optimal_activities": self._get_optimal_activities(time_period, day_type),
        }

    def _analyze_energy_indicators(self, content: str) -> Dict[str, Any]:
        """
        Analysiert Energie-Indikatoren
        """
        content_lower = content.lower()

        high_energy_words = [
            "energie",
            "motiviert",
            "aktiv",
            "produktiv",
            "kraftvoll",
            "lebendig",
            "dynamisch",
            "begeistert",
        ]

        low_energy_words = [
            "müde",
            "erschöpft",
            "schlapp",
            "antriebslos",
            "lethargisch",
            "kraftlos",
            "ausgelaugt",
            "schwermütig",
        ]

        high_count = sum(1 for word in high_energy_words if word in content_lower)
        low_count = sum(1 for word in low_energy_words if word in content_lower)

        if high_count > low_count:
            level = "high"
            confidence = high_count / (high_count + low_count + 1)
        elif low_count > high_count:
            level = "low"
            confidence = low_count / (high_count + low_count + 1)
        else:
            level = "medium"
            confidence = 0.5

        return {
            "level": level,
            "confidence": round(confidence, 2),
            "high_indicators": high_count,
            "low_indicators": low_count,
            "recommendation": self._get_energy_recommendation(level),
        }

    def _analyze_stress_level(self, content: str) -> Dict[str, Any]:
        """
        Analysiert Stress-Level
        """
        content_lower = content.lower()

        stress_indicators = [
            "stress",
            "druck",
            "überwältigt",
            "angespannt",
            "nervös",
            "sorge",
            "panik",
            "hektik",
            "zeitdruck",
            "belastet",
        ]

        relief_indicators = [
            "entspannt",
            "ruhig",
            "gelassen",
            "friedlich",
            "ausgeglichen",
            "erleichtert",
            "befreit",
            "locker",
        ]

        stress_count = sum(1 for word in stress_indicators if word in content_lower)
        relief_count = sum(1 for word in relief_indicators if word in content_lower)

        # Berechne Stress-Score
        net_stress = stress_count - relief_count

        if net_stress >= 2:
            level = "high"
        elif net_stress >= 1:
            level = "medium"
        elif net_stress <= -1:
            level = "low"
        else:
            level = "normal"

        return {
            "level": level,
            "stress_indicators": stress_count,
            "relief_indicators": relief_count,
            "net_score": net_stress,
            "needs_attention": level in ["high", "medium"],
            "recommendation": self._get_stress_recommendation(level),
        }

    def _analyze_motivation(self, content: str) -> Dict[str, Any]:
        """
        Analysiert Motivationsfaktoren
        """
        content_lower = content.lower()

        motivation_types = {
            "achievement": ["erfolg", "ziel", "schaffen", "erreichen", "leistung"],
            "growth": ["lernen", "entwickeln", "wachsen", "verbessern", "fortschritt"],
            "connection": ["freunde", "familie", "team", "zusammen", "beziehung"],
            "autonomy": ["selbst", "frei", "unabhängig", "entscheiden", "kontrolle"],
            "purpose": ["sinn", "zweck", "bedeutung", "wichtig", "beitrag"],
        }

        motivation_scores = {}
        for mot_type, keywords in motivation_types.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            motivation_scores[mot_type] = score

        # Finde dominante Motivation
        if any(motivation_scores.values()):
            dominant = max(motivation_scores.items(), key=lambda x: x[1])
            total_indicators = sum(motivation_scores.values())
        else:
            dominant = ("unknown", 0)
            total_indicators = 0

        return {
            "scores": motivation_scores,
            "dominant_type": dominant[0],
            "strength": dominant[1],
            "total_indicators": total_indicators,
            "recommendation": self._get_motivation_recommendation(dominant[0]),
        }

    def _classify_context_type(self, content: str, tags: List[str]) -> Dict[str, Any]:
        """
        Klassifiziert den Kontext-Typ
        """
        content_lower = content.lower()

        context_categories = {
            "work": ["arbeit", "job", "projekt", "meeting", "kollege", "chef"],
            "personal": ["ich", "persönlich", "privat", "gefühl", "emotion"],
            "health": ["gesundheit", "sport", "essen", "schlaf", "körper"],
            "relationships": ["freund", "familie", "partner", "beziehung", "sozial"],
            "learning": ["lernen", "buch", "kurs", "wissen", "skill", "fähigkeit"],
            "leisure": ["freizeit", "hobby", "spaß", "entspannung", "urlaub"],
        }

        # Score basierend auf Content
        content_scores = {}
        for category, keywords in context_categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            content_scores[category] = score

        # Score basierend auf Tags
        tag_scores = {}
        for category, keywords in context_categories.items():
            score = sum(
                1 for tag in tags for keyword in keywords if keyword in tag.lower()
            )
            tag_scores[category] = score

        # Kombiniere Scores
        combined_scores = {}
        for category in context_categories.keys():
            combined_scores[category] = (
                content_scores[category] + tag_scores[category] * 2
            )  # Tags gewichten mehr

        # Bestimme primären Kontext
        if any(combined_scores.values()):
            primary = max(combined_scores.items(), key=lambda x: x[1])
        else:
            primary = ("general", 0)

        return {
            "primary_type": primary[0],
            "confidence": primary[1],
            "all_scores": combined_scores,
            "is_mixed": len([s for s in combined_scores.values() if s > 0]) > 2,
        }

    def _assess_actionability(self, content: str) -> Dict[str, Any]:
        """
        Bewertet wie actionable der Inhalt ist
        """
        content_lower = content.lower()

        # Action-Indikatoren
        action_words = [
            "machen",
            "tun",
            "starten",
            "beginnen",
            "planen",
            "umsetzen",
            "ändern",
            "verbessern",
            "entwickeln",
            "arbeiten",
            "lernen",
        ]

        # Problem-Indikatoren
        problem_words = [
            "problem",
            "schwierigkeit",
            "hindernis",
            "herausforderung",
            "blockiert",
            "festgefahren",
            "unsicher",
        ]

        # Reflexion-Indikatoren
        reflection_words = [
            "denke",
            "fühle",
            "merke",
            "erkenne",
            "verstehe",
            "reflektiere",
            "überlege",
            "bewusst",
        ]

        action_count = sum(1 for word in action_words if word in content_lower)
        problem_count = sum(1 for word in problem_words if word in content_lower)
        reflection_count = sum(1 for word in reflection_words if word in content_lower)

        total_indicators = action_count + problem_count + reflection_count

        if total_indicators == 0:
            actionability = "low"
            primary_mode = "unclear"
        elif action_count >= max(problem_count, reflection_count):
            actionability = "high"
            primary_mode = "action_oriented"
        elif problem_count > reflection_count:
            actionability = "medium"
            primary_mode = "problem_focused"
        else:
            actionability = "medium"
            primary_mode = "reflection_focused"

        return {
            "level": actionability,
            "primary_mode": primary_mode,
            "action_indicators": action_count,
            "problem_indicators": problem_count,
            "reflection_indicators": reflection_count,
            "recommendation": self._get_actionability_recommendation(
                actionability, primary_mode
            ),
        }

    def _assess_complexity(self, content: str) -> Dict[str, Any]:
        """
        Bewertet die Komplexität des beschriebenen Themas
        """
        # Indikatoren für Komplexität
        complexity_indicators = [
            "komplex",
            "kompliziert",
            "schwierig",
            "vielschichtig",
            "mehrere",
            "verschiedene",
            "sowohl",
            "einerseits",
            "andererseits",
        ]

        # Einfachheits-Indikatoren
        simplicity_indicators = [
            "einfach",
            "klar",
            "eindeutig",
            "simpel",
            "direkt",
            "schnell",
        ]

        content_lower = content.lower()
        complexity_count = sum(
            1 for indicator in complexity_indicators if indicator in content_lower
        )
        simplicity_count = sum(
            1 for indicator in simplicity_indicators if indicator in content_lower
        )

        # Zusätzliche Komplexitäts-Faktoren
        sentence_count = len([s for s in content.split(".") if s.strip()])
        word_count = len(content.split())

        # Bestimme Komplexitätslevel
        if complexity_count > simplicity_count and word_count > 100:
            level = "high"
        elif complexity_count > 0 or word_count > 50:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "complexity_indicators": complexity_count,
            "simplicity_indicators": simplicity_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "recommendation": self._get_complexity_recommendation(level),
        }

    def _detect_personal_patterns(
        self, content: str, tags: List[str]
    ) -> Dict[str, Any]:
        """
        Erkennt persönliche Muster und Themen
        """
        # Hier könnte eine komplexere Mustererkennung implementiert werden
        # Für jetzt eine einfache Version

        frequent_words = Counter(
            word.lower() for word in content.split() if len(word) > 4 and word.isalpha()
        ).most_common(5)

        return {
            "frequent_topics": [word for word, count in frequent_words if count > 1],
            "tag_patterns": tags,
            "word_frequency": dict(frequent_words),
            "personal_indicators": self._find_personal_indicators(content),
        }

    def _find_personal_indicators(self, content: str) -> List[str]:
        """
        Findet persönliche Indikatoren im Text
        """
        indicators = []
        content_lower = content.lower()

        personal_patterns = [
            ("self_reference", ["ich", "mein", "mir", "mich"]),
            ("time_reference", ["heute", "gestern", "morgen", "letzte woche"]),
            ("emotional_expression", ["fühle", "empfinde", "spüre"]),
            ("decision_making", ["entscheiden", "wählen", "überlegen"]),
        ]

        for pattern_name, keywords in personal_patterns:
            if any(keyword in content_lower for keyword in keywords):
                indicators.append(pattern_name)

        return indicators

    def _calculate_analysis_confidence(self, analysis: Dict[str, Any]) -> float:
        """
        Berechnet Vertrauen in die Analyse (vereinfacht und robuster)
        """
        confidence_factors = []

        # Basis-Konfidenz wenn Inhalt vorhanden
        base_confidence = 0.5
        confidence_factors.append(base_confidence)

        # Emotionale Analyse Konfidenz
        try:
            emotional_indicators = analysis["emotional_state"]["indicators_found"]
            if emotional_indicators > 0:
                emotion_conf = min(emotional_indicators / 3.0, 0.8)
                confidence_factors.append(emotion_conf)
        except (KeyError, TypeError):
            pass

        # Urgency Level Konfidenz
        try:
            urgency_score = analysis["urgency_level"]["score"]
            urgency_conf = min(urgency_score / 10.0, 0.7)
            confidence_factors.append(urgency_conf)
        except (KeyError, TypeError):
            pass

        # Kontext-Typ Konfidenz
        try:
            context_conf = analysis["context_type"]["confidence"] / 10.0
            confidence_factors.append(min(context_conf, 0.6))
        except (KeyError, TypeError):
            pass

        # Actionability Konfidenz
        try:
            actionability = analysis["actionability"]
            total_indicators = (
                actionability.get("action_indicators", 0)
                + actionability.get("problem_indicators", 0)
                + actionability.get("reflection_indicators", 0)
            )
            action_conf = min(total_indicators / 5.0, 0.8)
            confidence_factors.append(action_conf)
        except (KeyError, TypeError):
            pass

        # Durchschnittliche Konfidenz mit Mindest- und Höchstwerten
        if confidence_factors:
            avg_confidence = sum(confidence_factors) / len(confidence_factors)
            # Stelle sicher, dass Konfidenz zwischen 0.1 und 0.9 liegt
            return round(max(0.15, min(0.85, avg_confidence)), 2)
        else:
            return 0.25  # Fallback-Konfidenz

    def _generate_detail_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generiert detaillierte Empfehlungen basierend auf der Analyse
        """
        recommendations = []

        # Stress-basierte Empfehlungen
        if analysis["stress_indicators"]["needs_attention"]:
            recommendations.append(
                f"Stress-Level ist {analysis['stress_indicators']['level']} - "
                "priorisiere Entspannungstechniken"
            )

        # Energie-basierte Empfehlungen
        energy_level = analysis["energy_level"]["level"]
        if energy_level == "low":
            recommendations.append(
                "Niedriges Energielevel erkannt - wähle leichte, erreichbare Aktionen"
            )
        elif energy_level == "high":
            recommendations.append(
                "Hohes Energielevel - perfekt für anspruchsvolle Aufgaben"
            )

        # Zeit-basierte Empfehlungen
        time_context = analysis["time_context"]
        recommendations.append(
            f"Optimal für {time_context['time_period']}: "
            f"{', '.join(time_context['optimal_activities'][:2])}"
        )

        # Komplexitäts-basierte Empfehlungen
        if analysis["complexity_level"]["level"] == "high":
            recommendations.append(
                "Komplexes Thema - teile in kleinere, manageable Schritte auf"
            )

        return recommendations

    # Hilfsmethoden für Pattern-Loading
    def _load_emotion_patterns(self) -> Dict[str, List[str]]:
        """Lädt Emotion-Pattern"""
        return {
            "positive": [
                "gut",
                "toll",
                "super",
                "fantastisch",
                "glücklich",
                "zufrieden",
                "erfolgreich",
                "stolz",
                "freude",
                "begeistert",
                "dankbar",
            ],
            "negative": [
                "schlecht",
                "mies",
                "furchtbar",
                "traurig",
                "deprimiert",
                "frustriert",
                "ärgerlich",
                "enttäuscht",
                "sorge",
                "angst",
            ],
            "energetic": [
                "energie",
                "dynamisch",
                "aktiv",
                "lebhaft",
                "motiviert",
                "kraftvoll",
                "lebendig",
                "antrieb",
            ],
            "calm": [
                "ruhig",
                "entspannt",
                "gelassen",
                "friedlich",
                "ausgeglichen",
                "besonnen",
                "still",
            ],
            "stressed": [
                "gestresst",
                "überwältigt",
                "unter druck",
                "angespannt",
                "nervös",
                "hektisch",
                "chaotisch",
            ],
        }

    def _load_context_indicators(self) -> Dict[str, List[str]]:
        """Lädt Kontext-Indikatoren"""
        return {
            "work": ["arbeit", "job", "büro", "kollege", "meeting", "projekt"],
            "personal": ["persönlich", "privat", "familie", "freunde"],
            "health": ["gesundheit", "sport", "fitness", "ernährung"],
            "learning": ["lernen", "studium", "kurs", "weiterbildung"],
        }

    def _load_urgency_markers(self) -> List[str]:
        """Lädt Dringlichkeits-Marker"""
        return [
            "dringend",
            "sofort",
            "schnell",
            "eilig",
            "deadline",
            "frist",
            "heute noch",
            "asap",
            "wichtig",
            "kritisch",
            "problem",
            "krise",
            "notfall",
        ]

    # Empfehlungs-Methoden
    def _get_urgency_recommendation(self, level: str) -> str:
        recommendations = {
            "high": "Sofortige Aufmerksamkeit erforderlich - priorisiere entsprechende Aktionen",
            "medium": "Zeitnahe Bearbeitung empfohlen - plane in den nächsten Tagen",
            "low": "Kann in normaler Priorität behandelt werden",
        }
        return recommendations.get(level, "Keine spezifische Empfehlung")

    def _get_energy_recommendation(self, level: str) -> str:
        recommendations = {
            "high": "Nutze diese Energie für anspruchsvolle oder wichtige Aufgaben",
            "medium": "Gute Zeit für moderate Aktivitäten und Planung",
            "low": "Fokussiere auf Erholung und leichte, entspannende Aktivitäten",
        }
        return recommendations.get(level, "Passe Aktivitäten an dein Energielevel an")

    def _get_stress_recommendation(self, level: str) -> str:
        recommendations = {
            "high": "Priorität auf Stressreduktion - Atemübungen, Pausen, Perspektivwechsel",
            "medium": "Achte auf Work-Life-Balance und plane bewusste Entspannung",
            "low": "Entspannter Zustand - gute Zeit für neue Herausforderungen",
            "normal": "Ausgeglichener Zustand - normale Aktivitäten möglich",
        }
        return recommendations.get(level, "Achte auf dein Stresslevel")

    def _get_motivation_recommendation(self, dominant_type: str) -> str:
        recommendations = {
            "achievement": "Setze klare, messbare Ziele und feiere kleine Erfolge",
            "growth": "Plane Lernaktivitäten und Entwicklungsmöglichkeiten",
            "connection": "Integriere soziale Aspekte in deine Pläne",
            "autonomy": "Schaffe Wahlmöglichkeiten und Selbstbestimmung",
            "purpose": "Verbinde Aktivitäten mit deinen Werten und größeren Zielen",
            "unknown": "Reflektiere über deine Kernmotivationen",
        }
        return recommendations.get(dominant_type, "Erkunde deine Motivationsquellen")

    def _get_actionability_recommendation(self, level: str, mode: str) -> str:
        if mode == "action_oriented":
            return "Klare Handlungsbereitschaft - erstelle konkrete nächste Schritte"
        elif mode == "problem_focused":
            return "Problem identifiziert - entwickle Lösungsstrategien"
        elif mode == "reflection_focused":
            return "Reflexive Phase - vertiefe Erkenntnisse vor Aktionsplanung"
        else:
            return "Kläre zunächst Intention und gewünschte Richtung"

    def _get_complexity_recommendation(self, level: str) -> str:
        recommendations = {
            "high": "Komplexes Thema - systematisch angehen, in Teilschritte zerlegen",
            "medium": "Moderates Thema - strukturiert aber flexibel vorgehen",
            "low": "Einfaches Thema - direkte Umsetzung möglich",
        }
        return recommendations.get(level, "Passe Ansatz an Komplexität an")

    def _calculate_valence(self, emotions: Dict[str, float]) -> str:
        """Berechnet emotionale Valenz (positiv/negativ)"""
        positive_score = (
            emotions.get("positive", 0)
            + emotions.get("energetic", 0)
            + emotions.get("calm", 0)
        )
        negative_score = emotions.get("negative", 0) + emotions.get("stressed", 0)

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"

    def _get_optimal_activities(self, time_period: str, day_type: str) -> List[str]:
        """Gibt optimale Aktivitäten für Tageszeit und -typ zurück"""
        activities = {
            "morning": {
                "weekday": ["Planning", "Deep Work", "Exercise", "Learning"],
                "weekend": ["Reflection", "Self-Care", "Hobbies", "Exercise"],
            },
            "afternoon": {
                "weekday": [
                    "Meetings",
                    "Collaboration",
                    "Implementation",
                    "Communication",
                ],
                "weekend": ["Social Activities", "Errands", "Projects", "Exploration"],
            },
            "evening": {
                "weekday": [
                    "Reflection",
                    "Planning Tomorrow",
                    "Relaxation",
                    "Family Time",
                ],
                "weekend": ["Entertainment", "Social Time", "Hobbies", "Reflection"],
            },
            "night": {
                "weekday": [
                    "Rest",
                    "Light Reading",
                    "Meditation",
                    "Preparation for Sleep",
                ],
                "weekend": ["Rest", "Light Entertainment", "Reflection", "Relaxation"],
            },
        }

        return activities.get(time_period, {}).get(day_type, ["Rest", "Reflection"])
