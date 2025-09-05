"""
ASI Core - State Management
Zustandsbasierte Datenverarbeitung für das Hybrid-Modell
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class ASIStateError(Exception):
    """Custom Exception für State Management Operationen"""

    pass


class ASIStateManager:
    """
    Verwaltet zustandsbasierte Reflexionen im Hybrid-Modell

    Unterstützte Zustände:
    - 0: Neutral/Standard
    - 1: Positiv/Fokussiert
    - 2: Negativ/Herausfordernd
    - 3: Kritisch/Wichtig
    - 4: Experimentell/Testend
    - 5: Archiviert/Historisch
    """

    STATE_DEFINITIONS = {
        0: {
            "name": "Neutral",
            "description": "Standard-Zustand ohne besondere Bewertung",
        },
        1: {
            "name": "Positiv",
            "description": "Erfolgreiche, fokussierte oder motivierende Erfahrung",
        },
        2: {
            "name": "Negativ",
            "description": "Herausfordernde oder problematische Erfahrung",
        },
        3: {
            "name": "Kritisch",
            "description": "Wichtige Erkenntnisse oder kritische Momente",
        },
        4: {
            "name": "Experimentell",
            "description": "Experimentelle Ansätze oder Tests",
        },
        5: {
            "name": "Archiviert",
            "description": "Historische oder archivierte Einträge",
        },
    }

    def __init__(self):
        """Initialisiert den State Manager"""
        self.state_history: List[Dict] = []
        self.state_statistics: Dict[int, int] = {}

    def validate_state(self, state_value: int) -> bool:
        """
        Validiert einen Zustandswert

        Args:
            state_value: Der zu validierende Zustandswert

        Returns:
            True wenn gültig, False sonst
        """
        return 0 <= state_value <= 255  # uint8 Bereich

    def get_state_name(self, state_value: int) -> str:
        """
        Gibt den Namen eines Zustandswerts zurück

        Args:
            state_value: Der Zustandswert

        Returns:
            Name des Zustands oder "Unbekannt"
        """
        if state_value in self.STATE_DEFINITIONS:
            return self.STATE_DEFINITIONS[state_value]["name"]
        return f"Benutzerdefiniert-{state_value}"

    def get_state_description(self, state_value: int) -> str:
        """
        Gibt die Beschreibung eines Zustandswerts zurück

        Args:
            state_value: Der Zustandswert

        Returns:
            Beschreibung des Zustands
        """
        if state_value in self.STATE_DEFINITIONS:
            return self.STATE_DEFINITIONS[state_value]["description"]
        return f"Benutzerdefinierter Zustand mit Wert {state_value}"

    def create_state_reflection(
        self,
        reflection_text: str,
        state_value: int,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Erstellt eine neue zustandsbasierte Reflexion

        Args:
            reflection_text: Der Reflexionstext
            state_value: Der Zustandswert (0-255)
            tags: Optional Liste von Tags
            metadata: Optional zusätzliche Metadaten

        Returns:
            Dictionary mit Reflexionsdaten

        Raises:
            ASIStateError: Bei ungültigen Parametern
        """
        # Validierungen
        if not reflection_text or not reflection_text.strip():
            raise ASIStateError("Reflexionstext darf nicht leer sein")

        if not self.validate_state(state_value):
            raise ASIStateError(f"Ungültiger Zustandswert: {state_value}")

        if tags is None:
            tags = []

        if metadata is None:
            metadata = {}

        # Automatische Tags basierend auf Zustand hinzufügen
        state_tag = f"#zustand-{state_value}"
        state_name_tag = f"#{self.get_state_name(state_value).lower()}"

        if state_tag not in tags:
            tags.append(state_tag)
        if state_name_tag not in tags:
            tags.append(state_name_tag)

        # Reflexionsdaten erstellen
        timestamp = datetime.now()

        reflection_data = {
            "reflection_text": reflection_text.strip(),
            "state_value": state_value,
            "state_name": self.get_state_name(state_value),
            "state_description": self.get_state_description(state_value),
            "tags": tags,
            "timestamp": timestamp.isoformat(),
            "unix_timestamp": int(timestamp.timestamp()),
            "metadata": metadata,
            "version": "hybrid-1.0",
        }

        # Zur Historie hinzufügen
        self.state_history.append(reflection_data)

        # Statistiken aktualisieren
        self.update_statistics(state_value)

        logger.info(
            f"📊 Zustandsreflexion erstellt: Zustand={state_value} ({self.get_state_name(state_value)})"
        )

        return reflection_data

    def update_statistics(self, state_value: int):
        """
        Aktualisiert die Zustandsstatistiken

        Args:
            state_value: Der Zustandswert
        """
        if state_value not in self.state_statistics:
            self.state_statistics[state_value] = 0
        self.state_statistics[state_value] += 1

    def get_statistics(self) -> Dict:
        """
        Gibt aktuelle Zustandsstatistiken zurück

        Returns:
            Dictionary mit Statistiken
        """
        total_entries = sum(self.state_statistics.values())

        stats = {
            "total_entries": total_entries,
            "unique_states": len(self.state_statistics),
            "state_distribution": {},
            "most_used_state": None,
            "least_used_state": None,
        }

        # Verteilung berechnen
        for state, count in self.state_statistics.items():
            percentage = (count / total_entries * 100) if total_entries > 0 else 0
            stats["state_distribution"][state] = {
                "count": count,
                "percentage": round(percentage, 2),
                "name": self.get_state_name(state),
                "description": self.get_state_description(state),
            }

        # Meist und am wenigsten verwendete Zustände
        if self.state_statistics:
            most_used = max(self.state_statistics.items(), key=lambda x: x[1])
            least_used = min(self.state_statistics.items(), key=lambda x: x[1])

            stats["most_used_state"] = {
                "state": most_used[0],
                "count": most_used[1],
                "name": self.get_state_name(most_used[0]),
            }

            stats["least_used_state"] = {
                "state": least_used[0],
                "count": least_used[1],
                "name": self.get_state_name(least_used[0]),
            }

        return stats

    def filter_by_state(
        self, state_value: int, reflections: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Filtert Reflexionen nach Zustandswert

        Args:
            state_value: Der Zustandswert zum Filtern
            reflections: Optional Liste von Reflexionen (Standard: self.state_history)

        Returns:
            Liste der gefilterten Reflexionen
        """
        if reflections is None:
            reflections = self.state_history

        return [r for r in reflections if r.get("state_value") == state_value]

    def filter_by_state_range(
        self, min_state: int, max_state: int, reflections: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Filtert Reflexionen nach Zustandsbereich

        Args:
            min_state: Minimaler Zustandswert (inklusive)
            max_state: Maximaler Zustandswert (inklusive)
            reflections: Optional Liste von Reflexionen

        Returns:
            Liste der gefilterten Reflexionen
        """
        if reflections is None:
            reflections = self.state_history

        return [
            r for r in reflections if min_state <= r.get("state_value", 0) <= max_state
        ]

    def export_state_data(self, filepath: str):
        """
        Exportiert Zustandsdaten in JSON-Datei

        Args:
            filepath: Pfad zur Ausgabedatei
        """
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "state_definitions": self.STATE_DEFINITIONS,
            "state_history": self.state_history,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Zustandsdaten exportiert nach: {filepath}")

    def import_state_data(self, filepath: str):
        """
        Importiert Zustandsdaten aus JSON-Datei

        Args:
            filepath: Pfad zur Eingabedatei
        """
        with open(filepath, "r", encoding="utf-8") as f:
            import_data = json.load(f)

        # Daten zusammenführen
        if "state_history" in import_data:
            self.state_history.extend(import_data["state_history"])

        # Statistiken neu berechnen
        self.state_statistics = {}
        for reflection in self.state_history:
            state_value = reflection.get("state_value", 0)
            self.update_statistics(state_value)

        logger.info(f"📂 Zustandsdaten importiert aus: {filepath}")


def create_quick_state_reflection(
    text: str, state: int, tags: Optional[List[str]] = None
) -> Dict:
    """
    Convenience-Funktion zum schnellen Erstellen einer Zustandsreflexion

    Args:
        text: Reflexionstext
        state: Zustandswert
        tags: Optional Tags

    Returns:
        Reflexionsdaten
    """
    manager = ASIStateManager()
    return manager.create_state_reflection(text, state, tags)


def parse_state_from_tags(tags: List[str]) -> Optional[int]:
    """
    Versucht, einen Zustandswert aus Tags zu extrahieren

    Args:
        tags: Liste von Tags

    Returns:
        Zustandswert oder None wenn nicht gefunden
    """
    for tag in tags:
        if tag.startswith("#zustand-"):
            try:
                state_str = tag.replace("#zustand-", "")
                return int(state_str)
            except ValueError:
                continue

        # Benannte Zustände
        state_mapping = {
            "#neutral": 0,
            "#positiv": 1,
            "#negativ": 2,
            "#kritisch": 3,
            "#experimentell": 4,
            "#archiviert": 5,
            "#fokus": 1,
            "#herausforderung": 2,
            "#wichtig": 3,
            "#test": 4,
        }

        if tag.lower() in state_mapping:
            return state_mapping[tag.lower()]

    return None


def suggest_state_from_text(text: str) -> int:
    """
    Schlägt einen Zustandswert basierend auf Textinhalt vor

    Args:
        text: Der Reflexionstext

    Returns:
        Vorgeschlagener Zustandswert
    """
    text_lower = text.lower()

    # Positive Indikatoren
    positive_words = [
        "erfolgreich",
        "gut",
        "toll",
        "fantastisch",
        "fortschritt",
        "gelöst",
        "geschafft",
        "fokussiert",
        "motiviert",
        "produktiv",
    ]

    # Negative Indikatoren
    negative_words = [
        "problem",
        "fehler",
        "schwierig",
        "herausforderung",
        "gestresst",
        "müde",
        "konfusion",
        "blockiert",
    ]

    # Kritische Indikatoren
    critical_words = [
        "wichtig",
        "entscheidend",
        "kritisch",
        "durchbruch",
        "erkenntnis",
        "aha",
        "lernen",
        "verstehen",
    ]

    # Experimentelle Indikatoren
    experimental_words = [
        "test",
        "experimentell",
        "versuch",
        "probe",
        "ausprobieren",
        "neuer ansatz",
    ]

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    critical_count = sum(1 for word in critical_words if word in text_lower)
    experimental_count = sum(1 for word in experimental_words if word in text_lower)

    # Höchste Punktzahl gewinnt
    scores = {
        1: positive_count,
        2: negative_count,
        3: critical_count,
        4: experimental_count,
    }

    if max(scores.values()) == 0:
        return 0  # Neutral wenn keine Indikatoren gefunden

    return max(scores.items(), key=lambda x: x[1])[0]
