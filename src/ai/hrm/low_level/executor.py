"""
HRM Low-Level Executor
Konkrete Ausführung und Detailanalyse für ASI Core
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .detail_analysis import DetailAnalyzer


class Executor:
    """
    Low-Level Executor für konkrete Aktionen und Detailausführung
    """

    def __init__(self):
        self.detail_analyzer = DetailAnalyzer()
        self.action_history = []
        self.available_actions = self._initialize_actions()

    def execute_analysis(
        self, abstract_plan: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Führt konkrete Schritte aus dem abstrakten Plan aus

        Args:
            abstract_plan: Abstrakter Plan vom High-Level Planner
            user_context: Kontext der aktuellen Reflexion

        Returns:
            Konkrete Aktion oder None
        """
        # Wähle den wichtigsten Schritt aus
        if abstract_plan.get("suggested_goals"):
            primary_goal = abstract_plan["suggested_goals"][0]

            # Detailanalyse für bessere Aktionsauswahl
            details = self.detail_analyzer.analyze_details(user_context)

            # Generiere konkrete Aktion
            action = self._generate_concrete_action(
                primary_goal, user_context, details, abstract_plan
            )

            # Speichere Aktion für Tracking
            if action:
                self._track_action(action, user_context)

            return action

        return self._generate_default_action(user_context)

    def _generate_concrete_action(
        self,
        goal: str,
        user_context: Dict[str, Any],
        details: Dict[str, Any],
        abstract_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generiert konkrete Aktion basierend auf Ziel und Kontext
        """
        goal_lower = goal.lower()
        current_time = datetime.now()

        # Fokus-optimierung
        if "fokus" in goal_lower:
            return self._create_focus_action(details, current_time)

        # Work-Life-Balance
        elif "work-life" in goal_lower or "balance" in goal_lower:
            return self._create_balance_action(details, current_time)

        # Gesundheit
        elif "gesundheit" in goal_lower or "health" in goal_lower:
            return self._create_health_action(details, current_time)

        # Gewohnheiten
        elif "gewohnheit" in goal_lower or "routine" in goal_lower:
            return self._create_habit_action(details, goal)

        # Stress-Management
        elif "stress" in goal_lower:
            return self._create_stress_action(details, current_time)

        # Lernen und Entwicklung
        elif "lern" in goal_lower or "entwickl" in goal_lower:
            return self._create_learning_action(details, goal)

        # Beziehungen
        elif "beziehung" in goal_lower or "sozial" in goal_lower:
            return self._create_relationship_action(details)

        # Fallback: Generische Aktion
        else:
            return self._create_generic_action(goal, details)

    def _create_focus_action(
        self, details: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Erstellt Fokus-spezifische Aktionen
        """
        # Tageszeit-spezifische Empfehlungen
        hour = current_time.hour

        if 6 <= hour <= 10:  # Morgen
            return {
                "action": "morning_focus_ritual",
                "type": "focus",
                "priority": "high",
                "status": "Morgen-Fokus-Ritual aktiviert",
                "params": {
                    "duration": 25,
                    "technique": "Pomodoro",
                    "break_interval": 5,
                },
                "suggestion": "Starte deinen Tag mit 25 Minuten fokussierter Arbeit. "
                "Nutze die morgendliche Klarheit für wichtige Aufgaben.",
                "implementation": [
                    "Wähle EINE wichtige Aufgabe für die nächsten 25 Minuten",
                    "Schalte alle Ablenkungen aus (Handy, Benachrichtigungen)",
                    "Arbeite konzentriert ohne Unterbrechung",
                    "Belohne dich nach den 25 Minuten mit einer 5-Minuten-Pause",
                ],
                "success_metrics": {
                    "completion": "25 Minuten ohne Unterbrechung",
                    "quality": "Gefühl von Fortschritt und Klarheit",
                },
            }

        elif 11 <= hour <= 15:  # Mittag
            return {
                "action": "midday_deep_work",
                "type": "focus",
                "priority": "high",
                "params": {"duration": 45, "environment": "quiet_space"},
                "suggestion": "Nutze die Mittagszeit für 45 Minuten Deep Work. "
                "Dein Energielevel ist optimal für anspruchsvolle Aufgaben.",
                "implementation": [
                    "Blockiere 45 Minuten in deinem Kalender",
                    "Finde einen ruhigen Arbeitsplatz",
                    "Definiere ein klares Ziel für diese Session",
                    "Arbeite an deiner wichtigsten Aufgabe des Tages",
                ],
            }

        else:  # Abend
            return {
                "action": "evening_reflection_focus",
                "type": "focus",
                "priority": "medium",
                "params": {"duration": 15, "technique": "reflection"},
                "suggestion": "Reflektiere über deinen Fokus heute. "
                "Was hat funktioniert? Was kann morgen besser werden?",
                "implementation": [
                    "Schreibe 3 Momente auf, in denen du heute fokussiert warst",
                    "Identifiziere den größten Fokus-Killer des Tages",
                    "Plane eine Verbesserung für morgen",
                ],
            }

    def _create_balance_action(
        self, details: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Erstellt Work-Life-Balance Aktionen
        """
        return {
            "action": "balance_check",
            "type": "life_balance",
            "priority": "medium",
            "params": {"areas": ["work", "family", "health", "hobbies", "rest"]},
            "suggestion": "Führe eine schnelle Balance-Überprüfung durch. "
            "Welcher Lebensbereich braucht mehr Aufmerksamkeit?",
            "implementation": [
                "Bewerte jede Kategorie von 1-10 (Zufriedenheit)",
                "Identifiziere den Bereich mit der niedrigsten Bewertung",
                "Plane eine kleine Verbesserung für diese Woche",
                "Setze eine konkrete Boundary zwischen Arbeit und Freizeit",
            ],
            "areas_to_evaluate": {
                "work": "Wie zufrieden bin ich mit meiner Arbeitsleistung?",
                "family": "Wie viel Quality Time verbringe ich mit Liebsten?",
                "health": "Wie gut kümmere ich mich um meinen Körper?",
                "hobbies": "Habe ich Zeit für Dinge, die mir Freude machen?",
                "rest": "Bekomme ich genug Erholung und Entspannung?",
            },
        }

    def _create_health_action(
        self, details: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Erstellt Gesundheits-spezifische Aktionen
        """
        hour = current_time.hour

        if hour < 12:  # Vormittag
            return {
                "action": "morning_health_boost",
                "type": "health",
                "priority": "high",
                "suggestion": "Starte gesund in den Tag mit einer einfachen Routine.",
                "implementation": [
                    "Trinke ein großes Glas Wasser nach dem Aufstehen",
                    "Mache 5 Minuten Stretching oder leichte Bewegung",
                    "Plane bewusst gesunde Mahlzeiten für heute",
                    "Setze dir ein Bewegungsziel für heute (z.B. 8000 Schritte)",
                ],
                "params": {
                    "water_goal": "2 Liter über den Tag",
                    "movement_goal": "mindestens 30 Minuten",
                    "nutrition_focus": "mehr Gemüse und Proteine",
                },
            }
        else:
            return {
                "action": "evening_wellness_routine",
                "type": "health",
                "priority": "medium",
                "suggestion": "Beende den Tag mit einer entspannenden Wellness-Routine.",
                "implementation": [
                    "Reflexiere über deine Gesundheitsentscheidungen heute",
                    "Plane eine entspannende Aktivität (Bad, Meditation, Lesen)",
                    "Bereite dich mental auf erholsamen Schlaf vor",
                    "Setze eine feste Bildschirmzeit-Grenze vor dem Schlafen",
                ],
            }

    def _create_habit_action(
        self, details: Dict[str, Any], goal: str
    ) -> Dict[str, Any]:
        """
        Erstellt gewohnheits-spezifische Aktionen
        """
        return {
            "action": "habit_formation_step",
            "type": "habit_building",
            "priority": "medium",
            "suggestion": f"Baue schrittweise neue Gewohnheiten auf: {goal}",
            "implementation": [
                "Wähle EINE kleine Gewohnheit, die du heute beginnen möchtest",
                "Verknüpfe sie mit einer existierenden Routine (Habit Stacking)",
                "Starte mit nur 2 Minuten - mache es lächerlich einfach",
                "Tracke deinen Erfolg visuell (Kalender, App, Journal)",
            ],
            "params": {
                "start_small": True,
                "duration": "2 Minuten",
                "frequency": "täglich",
                "tracking_method": "visual",
            },
            "habit_examples": {
                "morgen": "Nach dem Zähneputzen 2 Minuten meditieren",
                "arbeit": "Nach jedem Meeting 1 Minute aufstehen und atmen",
                "abend": "Nach dem Abendessen 5 Minuten Journal schreiben",
            },
        }

    def _create_stress_action(
        self, details: Dict[str, Any], current_time: datetime
    ) -> Dict[str, Any]:
        """
        Erstellt Stress-Management Aktionen
        """
        return {
            "action": "immediate_stress_relief",
            "type": "stress_management",
            "priority": "high",
            "suggestion": "Reduziere Stress mit sofort umsetzbaren Techniken.",
            "implementation": [
                "4-7-8 Atemtechnik: 4 Sek einatmen, 7 Sek halten, 8 Sek ausatmen",
                "Identifiziere den Hauptstressor von heute",
                "Frage: 'Kann ich das ändern?' Wenn ja: handle. Wenn nein: akzeptiere.",
                "Plane eine entspannende Aktivität für heute Abend",
            ],
            "immediate_techniques": {
                "breathing": "4-7-8 Atemtechnik (3x wiederholen)",
                "grounding": "5-4-3-2-1: 5 Dinge sehen, 4 hören, 3 fühlen, 2 riechen, 1 schmecken",
                "movement": "30 Sekunden auf der Stelle gehen oder Schultern kreisen",
                "perspective": "Frage: 'Wird das in 5 Jahren noch wichtig sein?'",
            },
            "params": {
                "urgency": "immediate",
                "duration": "5-10 Minuten",
                "effectiveness": "scientifically_proven",
            },
        }

    def _create_learning_action(
        self, details: Dict[str, Any], goal: str
    ) -> Dict[str, Any]:
        """
        Erstellt Lern- und Entwicklungsaktionen
        """
        return {
            "action": "learning_session",
            "type": "personal_development",
            "priority": "medium",
            "suggestion": f"Investiere in deine Entwicklung: {goal}",
            "implementation": [
                "Wähle ein Lernziel für diese Woche",
                "Plane täglich 15 Minuten für aktives Lernen",
                "Nutze die Feynman-Technik: Erkläre das Gelernte einfach",
                "Wende das Gelernte praktisch an",
            ],
            "learning_methods": {
                "active_reading": "Notizen machen, Fragen stellen",
                "spaced_repetition": "Wiederholung in Abständen",
                "practice": "Sofortige praktische Anwendung",
                "teaching": "Anderen erklären oder aufschreiben",
            },
            "time_blocks": [
                "Morgens: Neue Konzepte lernen (höchste Aufmerksamkeit)",
                "Mittags: Praktische Übungen",
                "Abends: Reflexion und Wiederholung",
            ],
        }

    def _create_relationship_action(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt beziehungs-spezifische Aktionen
        """
        return {
            "action": "relationship_nurturing",
            "type": "social_connection",
            "priority": "medium",
            "suggestion": "Stärke deine wichtigsten Beziehungen bewusst.",
            "implementation": [
                "Kontaktiere heute eine wichtige Person in deinem Leben",
                "Stelle eine offene Frage und höre aktiv zu",
                "Zeige Wertschätzung für etwas Spezifisches",
                "Plane Quality Time mit jemandem für diese Woche",
            ],
            "connection_ideas": {
                "quick": "Kurze Nachricht mit konkreter Wertschätzung senden",
                "medium": "15-Minuten-Anruf ohne Ablenkung",
                "deep": "Gemeinsame Aktivität oder längeres Gespräch planen",
            },
        }

    def _create_generic_action(
        self, goal: str, details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Erstellt generische Aktion für unspezifische Ziele
        """
        return {
            "action": "goal_breakdown",
            "type": "planning",
            "priority": "medium",
            "suggestion": f"Zerlege dein Ziel in konkrete Schritte: {goal}",
            "implementation": [
                "Schreibe dein Ziel spezifisch und messbar auf",
                "Teile es in 3-5 kleinere Schritte auf",
                "Plane den ersten Schritt für heute",
                "Setze dir eine realistische Deadline",
            ],
            "smart_framework": {
                "specific": "Was genau willst du erreichen?",
                "measurable": "Woran erkennst du Erfolg?",
                "achievable": "Ist es realistisch machbar?",
                "relevant": "Warum ist das wichtig für dich?",
                "timebound": "Bis wann willst du es erreichen?",
            },
        }

    def _generate_default_action(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generiert Standard-Aktion wenn keine spezifischen Ziele vorhanden
        """
        return {
            "action": "reflection_deepening",
            "type": "self_awareness",
            "priority": "low",
            "status": "Reflexion-Vertiefung empfohlen",
            "suggestion": "Vertiefe deine Selbstreflexion für bessere Einsichten.",
            "implementation": [
                "Stelle dir drei W-Fragen: Was? Warum? Wie?",
                "Was ist heute passiert? (Fakten)",
                "Warum war das wichtig? (Bedeutung)",
                "Wie kann ich das nutzen? (Anwendung)",
            ],
        }

    def _track_action(self, action: Dict[str, Any], context: Dict[str, Any]) -> None:
        """
        Verfolgt ausgeführte Aktionen für Lernzwecke
        """
        tracking_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action.get("type", "unknown"),
            "action_id": action.get("action", "unknown"),
            "priority": action.get("priority", "medium"),
            "context_tags": context.get("tags", []),
            "confidence": action.get("confidence", 0.8),
        }

        self.action_history.append(tracking_entry)

        # Behalte nur die letzten 100 Aktionen
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]

    def _initialize_actions(self) -> Dict[str, Any]:
        """
        Initialisiert verfügbare Aktionstypen
        """
        return {
            "focus": ["pomodoro", "deep_work", "distraction_elimination"],
            "health": ["exercise", "nutrition", "sleep", "hydration"],
            "stress": ["breathing", "meditation", "time_management"],
            "relationships": ["communication", "quality_time", "appreciation"],
            "learning": ["skill_development", "knowledge_acquisition", "practice"],
            "habits": ["routine_building", "habit_stacking", "tracking"],
            "planning": ["goal_setting", "task_breakdown", "prioritization"],
        }

    def get_action_analytics(self) -> Dict[str, Any]:
        """
        Analysiert die Aktionshistorie für Insights
        """
        if not self.action_history:
            return {"message": "Keine Aktionshistorie verfügbar"}

        recent_actions = self.action_history[-20:]  # Letzte 20 Aktionen

        # Häufigste Aktionstypen
        action_types = [a["action_type"] for a in recent_actions]
        type_frequency = {}
        for action_type in action_types:
            type_frequency[action_type] = type_frequency.get(action_type, 0) + 1

        # Prioritätsverteilung
        priorities = [a["priority"] for a in recent_actions]
        priority_dist = {}
        for priority in priorities:
            priority_dist[priority] = priority_dist.get(priority, 0) + 1

        return {
            "total_actions": len(self.action_history),
            "recent_actions": len(recent_actions),
            "most_common_type": (
                max(type_frequency.items(), key=lambda x: x[1])[0]
                if type_frequency
                else "none"
            ),
            "priority_distribution": priority_dist,
            "type_frequency": type_frequency,
            "recommendation": self._get_action_recommendation(
                type_frequency, priority_dist
            ),
        }

    def _get_action_recommendation(
        self, type_freq: Dict[str, int], priority_dist: Dict[str, int]
    ) -> str:
        """
        Gibt Empfehlungen basierend auf Aktionsmustern
        """
        if not type_freq:
            return "Beginne mit regelmäßigen konkreten Aktionen aus deinen Reflexionen."

        most_common = max(type_freq.items(), key=lambda x: x[1])[0]
        high_priority = priority_dist.get("high", 0)
        total_actions = sum(priority_dist.values())

        if high_priority / total_actions > 0.6:
            return f"Du fokussierst stark auf {most_common}. Überprüfe auch andere Lebensbereiche."
        elif high_priority / total_actions < 0.2:
            return "Erhöhe die Priorität wichtiger Aktionen für größere Wirkung."
        else:
            return f"Gute Balance! {most_common} ist dein Stärkenbereich - nutze das weiter."
