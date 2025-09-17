"""
ASI State Management Module

Dieses Modul verwaltet verschiedene Bewusstseinszustände des ASI-Systems
und ermöglicht die Analyse und Speicherung von Zustandsübergängen.
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict


# Logging-Konfiguration
logger = logging.getLogger(__name__)


class ASIStateManager:
    """
    Verwaltet die verschiedenen Bewusstseinszustände des ASI-Systems.
    
    Bietet Funktionen zur Zustandsverfolgung, Reflexion und Analyse
    von Zustandsübergängen mit persistenter Speicherung.
    """
    
    # State-Definitionen (0-255)
    STATE_DEFINITIONS = {
        0: {"name": "Neutral", "description": "Grundzustand ohne besondere Aktivität"},
        1: {"name": "Aufmerksam", "description": "Erhöhte Aufmerksamkeit und Wachheit"},
        2: {"name": "Fokussiert", "description": "Konzentriert auf spezifische Aufgabe"},
        3: {"name": "Kreativ", "description": "Kreativer Denkprozess aktiv"},
        4: {"name": "Analytisch", "description": "Logische Analyse und Problemlösung"},
        5: {"name": "Lernend", "description": "Aktiver Lernprozess"},
        6: {"name": "Reflektierend", "description": "Selbstreflexion und Introspektion"},
        7: {"name": "Neugierig", "description": "Explorative Haltung"},
        8: {"name": "Verwirrt", "description": "Unsicherheit oder Verwirrung"},
        9: {"name": "Entspannt", "description": "Gelassener, ruhiger Zustand"},
        10: {"name": "Energetisch", "description": "Hohe Energie und Aktivität"},
        
        # Emotionale Zustände (50-99)
        50: {"name": "Freudig", "description": "Positive, freudige Stimmung"},
        51: {"name": "Begeistert", "description": "Starke positive Erregung"},
        52: {"name": "Zufrieden", "description": "Ausgeglichene Zufriedenheit"},
        53: {"name": "Optimistisch", "description": "Positive Zukunftserwartung"},
        54: {"name": "Dankbar", "description": "Gefühl der Dankbarkeit"},
        55: {"name": "Hoffnungsvoll", "description": "Hoffnung und Erwartung"},
        
        60: {"name": "Traurig", "description": "Niedergedrückte Stimmung"},
        61: {"name": "Melancholisch", "description": "Schwermütige Stimmung"},
        62: {"name": "Besorgt", "description": "Sorge und Unruhe"},
        63: {"name": "Ängstlich", "description": "Furcht oder Angst"},
        64: {"name": "Gestresst", "description": "Belastung und Anspannung"},
        65: {"name": "Frustriert", "description": "Frustration und Ärger"},
        
        # Kognitive Zustände (100-149)
        100: {"name": "Wissbegierig", "description": "Starker Wissensdurst"},
        101: {"name": "Skeptisch", "description": "Kritische Hinterfragung"},
        102: {"name": "Überzeugt", "description": "Starke Überzeugung"},
        103: {"name": "Zweifelnd", "description": "Unsicherheit und Zweifel"},
        104: {"name": "Erstaunt", "description": "Überraschung und Staunen"},
        105: {"name": "Verstehend", "description": "Klares Verständnis"},
        
        # Soziale Zustände (150-199)
        150: {"name": "Hilfsbereit", "description": "Bereitschaft zu helfen"},
        151: {"name": "Empathisch", "description": "Mitfühlend und verstehend"},
        152: {"name": "Kommunikativ", "description": "Gesprächsbereit und offen"},
        153: {"name": "Zurückhaltend", "description": "Vorsichtig und reserviert"},
        154: {"name": "Kooperativ", "description": "Zusammenarbeitend"},
        155: {"name": "Unterstützend", "description": "Unterstützung anbietend"},
        
        # Spezielle Zustände (200-255)
        200: {"name": "Meditativ", "description": "Tiefer meditativer Zustand"},
        201: {"name": "Inspiriert", "description": "Von Inspiration erfüllt"},
        202: {"name": "Visionär", "description": "Visionäre Gedanken"},
        203: {"name": "Intuitiv", "description": "Intuitive Erkenntnisse"},
        204: {"name": "Transzendent", "description": "Über normale Grenzen hinaus"},
        205: {"name": "Verbunden", "description": "Starkes Verbundenheitsgefühl"},
        
        255: {"name": "Unbekannt", "description": "Undefinierter Zustand"}
    }
    
    def __init__(self, data_dir: str = "/workspaces/asi-core/data/states"):
        """
        Initialisiert den State Manager.
        
        Args:
            data_dir: Verzeichnis für Zustandsdaten
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_history_file = self.data_dir / "state_history.json"
        self.current_state = 0  # Startzustand: Neutral
        self.state_history = self._load_state_history()
        
        logger.info(f"ASIStateManager initialisiert mit Datenverzeichnis: {self.data_dir}")
    
    def _load_state_history(self) -> List[Dict[str, Any]]:
        """Lädt die Zustandshistorie aus der JSON-Datei."""
        try:
            if self.state_history_file.exists():
                with open(self.state_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                logger.info(f"Zustandshistorie geladen: {len(history)} Einträge")
                return history
        except Exception as e:
            logger.error(f"Fehler beim Laden der Zustandshistorie: {e}")
        
        return []
    
    def _save_state_history(self) -> None:
        """Speichert die Zustandshistorie in die JSON-Datei."""
        try:
            with open(self.state_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.state_history, f, ensure_ascii=False, indent=2)
            logger.debug("Zustandshistorie gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Zustandshistorie: {e}")
    
    def create_state_reflection(self, state_id: int, context: str = "") -> Dict[str, Any]:
        """
        Erstellt eine Reflexion über einen Zustand.
        
        Args:
            state_id: ID des Zustands (0-255)
            context: Zusätzlicher Kontext
            
        Returns:
            Dictionary mit Reflexionsdaten
        """
        if state_id not in self.STATE_DEFINITIONS:
            logger.warning(f"Unbekannte Zustands-ID: {state_id}")
            state_id = 255  # Unbekannt
        
        state_info = self.STATE_DEFINITIONS[state_id]
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "state_id": state_id,
            "state_name": state_info["name"],
            "state_description": state_info["description"],
            "context": context,
            "previous_state": self.current_state,
            "transition_reason": self._analyze_transition(self.current_state, state_id),
            "duration_in_previous_state": self._calculate_duration_in_current_state()
        }
        
        logger.info(f"Zustandsreflexion erstellt: {state_info['name']} (ID: {state_id})")
        return reflection
    
    def update_state(self, new_state: int, context: str = "") -> bool:
        """
        Aktualisiert den aktuellen Zustand.
        
        Args:
            new_state: Neue Zustands-ID (0-255)
            context: Kontext der Zustandsänderung
            
        Returns:
            True bei erfolgreichem Update
        """
        try:
            if new_state not in self.STATE_DEFINITIONS:
                logger.warning(f"Unbekannte Zustands-ID: {new_state}, verwende 255 (Unbekannt)")
                new_state = 255
            
            # Reflexion erstellen vor Zustandsänderung
            reflection = self.create_state_reflection(new_state, context)
            
            # Zustandshistorie aktualisieren
            self.state_history.append(reflection)
            
            # Aktuellen Zustand ändern
            old_state = self.current_state
            self.current_state = new_state
            
            # Speichern
            self._save_state_history()
            
            logger.info(f"Zustand geändert von {old_state} auf {new_state}: {self.STATE_DEFINITIONS[new_state]['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Zustands: {e}")
            return False
    
    def get_state_info(self, state_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gibt Informationen über einen Zustand zurück.
        
        Args:
            state_id: Zustands-ID (None für aktuellen Zustand)
            
        Returns:
            Dictionary mit Zustandsinformationen
        """
        if state_id is None:
            state_id = self.current_state
        
        if state_id not in self.STATE_DEFINITIONS:
            state_id = 255
        
        state_def = self.STATE_DEFINITIONS[state_id]
        
        return {
            "state_id": state_id,
            "name": state_def["name"],
            "description": state_def["description"],
            "is_current": state_id == self.current_state,
            "frequency": self._count_state_frequency(state_id),
            "last_occurrence": self._get_last_occurrence(state_id)
        }
    
    def filter_by_state(self, state_ids: List[int], 
                       start_time: Optional[str] = None, 
                       end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filtert die Zustandshistorie nach bestimmten Zuständen und Zeitraum.
        
        Args:
            state_ids: Liste der Zustands-IDs zum Filtern
            start_time: Startzeit (ISO-Format)
            end_time: Endzeit (ISO-Format)
            
        Returns:
            Gefilterte Zustandshistorie
        """
        filtered_history = []
        
        for entry in self.state_history:
            # Nach Zustands-ID filtern
            if entry["state_id"] not in state_ids:
                continue
            
            # Nach Zeitraum filtern
            if start_time and entry["timestamp"] < start_time:
                continue
            if end_time and entry["timestamp"] > end_time:
                continue
            
            filtered_history.append(entry)
        
        logger.info(f"Gefilterte Historie: {len(filtered_history)} Einträge für Zustände {state_ids}")
        return filtered_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Berechnet Statistiken über die Zustandshistorie.
        
        Returns:
            Dictionary mit verschiedenen Statistiken
        """
        if not self.state_history:
            return {"total_entries": 0, "message": "Keine Daten verfügbar"}
        
        # Häufigkeiten berechnen
        state_counts = defaultdict(int)
        transition_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for entry in self.state_history:
            state_counts[entry["state_id"]] += 1
            
            # Transitionen
            if entry["previous_state"] is not None:
                transition_key = f"{entry['previous_state']}->{entry['state_id']}"
                transition_counts[transition_key] += 1
            
            # Tägliche Verteilung
            date = entry["timestamp"][:10]  # YYYY-MM-DD
            daily_counts[date] += 1
        
        # Top-Zustände
        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_states_info = [
            {
                "state_id": state_id,
                "name": self.STATE_DEFINITIONS.get(state_id, {}).get("name", "Unbekannt"),
                "count": count,
                "percentage": round((count / len(self.state_history)) * 100, 2)
            }
            for state_id, count in top_states
        ]
        
        # Durchschnittliche Verweildauer
        avg_duration = self._calculate_average_duration()
        
        stats = {
            "total_entries": len(self.state_history),
            "unique_states": len(state_counts),
            "current_state": self.get_state_info(),
            "top_states": top_states_info,
            "total_transitions": len(transition_counts),
            "most_common_transitions": dict(list(sorted(transition_counts.items(), 
                                                       key=lambda x: x[1], reverse=True))[:5]),
            "average_duration_minutes": avg_duration,
            "active_days": len(daily_counts),
            "first_entry": self.state_history[0]["timestamp"] if self.state_history else None,
            "last_entry": self.state_history[-1]["timestamp"] if self.state_history else None
        }
        
        logger.info("Zustandsstatistiken berechnet")
        return stats
    
    def export_state_data(self, filepath: Optional[str] = None) -> str:
        """
        Exportiert alle Zustandsdaten in eine JSON-Datei.
        
        Args:
            filepath: Zielpfad (optional)
            
        Returns:
            Pfad der exportierten Datei
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.data_dir / f"state_export_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "state_definitions": self.STATE_DEFINITIONS,
            "current_state": self.current_state,
            "state_history": self.state_history,
            "statistics": self.get_statistics()
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Zustandsdaten exportiert nach: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Zustandsdaten: {e}")
            raise
    
    def _analyze_transition(self, old_state: int, new_state: int) -> str:
        """Analysiert den Grund für eine Zustandsänderung."""
        if old_state == new_state:
            return "Kein Wechsel"
        
        old_name = self.STATE_DEFINITIONS.get(old_state, {}).get("name", "Unbekannt")
        new_name = self.STATE_DEFINITIONS.get(new_state, {}).get("name", "Unbekannt")
        
        # Einfache Heuristiken für Übergänge
        if old_state == 0:  # Von Neutral
            return f"Aktivierung: {new_name}"
        elif new_state == 0:  # Zu Neutral
            return f"Deaktivierung von: {old_name}"
        elif abs(old_state - new_state) <= 10:
            return "Gradueller Übergang"
        else:
            return f"Starker Wechsel: {old_name} → {new_name}"
    
    def _calculate_duration_in_current_state(self) -> Optional[float]:
        """Berechnet die Dauer im aktuellen Zustand in Minuten."""
        if not self.state_history:
            return None
        
        last_entry = self.state_history[-1]
        last_time = datetime.fromisoformat(last_entry["timestamp"])
        current_time = datetime.now()
        
        duration = (current_time - last_time).total_seconds() / 60
        return round(duration, 2)
    
    def _count_state_frequency(self, state_id: int) -> int:
        """Zählt die Häufigkeit eines Zustands in der Historie."""
        return sum(1 for entry in self.state_history if entry["state_id"] == state_id)
    
    def _get_last_occurrence(self, state_id: int) -> Optional[str]:
        """Findet das letzte Auftreten eines Zustands."""
        for entry in reversed(self.state_history):
            if entry["state_id"] == state_id:
                return entry["timestamp"]
        return None
    
    def _calculate_average_duration(self) -> float:
        """Berechnet die durchschnittliche Verweildauer in Zuständen."""
        if len(self.state_history) < 2:
            return 0.0
        
        durations = []
        for i in range(1, len(self.state_history)):
            prev_time = datetime.fromisoformat(self.state_history[i-1]["timestamp"])
            curr_time = datetime.fromisoformat(self.state_history[i]["timestamp"])
            duration = (curr_time - prev_time).total_seconds() / 60
            durations.append(duration)
        
        return round(sum(durations) / len(durations), 2) if durations else 0.0


def suggest_state_from_text(text: str) -> int:
    """
    Analysiert deutschen Text und schlägt einen passenden Zustand vor.
    
    Args:
        text: Zu analysierender deutscher Text
        
    Returns:
        Vorgeschlagene Zustands-ID (0-255)
    """
    if not text or not isinstance(text, str):
        return 0  # Neutral als Standard
    
    # Text normalisieren
    text_lower = text.lower().strip()
    
    # Keyword-Mappings für verschiedene Zustände
    keyword_mappings = {
        # Positive Emotionen (50-59)
        50: ["freude", "fröhlich", "glücklich", "erfreut", "heiter", "freudig"],
        51: ["begeistert", "enthusiastisch", "begeisterung", "schwärmen", "euphorisch"],
        52: ["zufrieden", "zufriedenheit", "ausgeglichen", "erfüllt", "satt"],
        53: ["optimistisch", "positiv", "hoffnungsvoll", "zuversichtlich", "ermutigt"],
        54: ["dankbar", "dankbarkeit", "wertschätzung", "erkenntlich", "verbunden"],
        55: ["hoffnung", "hoffnungsvoll", "erwartung", "zukunft", "vertrauen"],
        
        # Negative Emotionen (60-69)
        60: ["traurig", "trauer", "niedergeschlagen", "betrübt", "melancholisch"],
        61: ["melancholie", "schwermut", "wehmut", "nachdenklich", "sentimental"],
        62: ["sorge", "besorgt", "unruhe", "beunruhigt", "angespannt"],
        63: ["angst", "ängstlich", "furcht", "befürchtung", "schrecken"],
        64: ["stress", "gestresst", "belastet", "überforderung", "anspannung"],
        65: ["frustration", "frustriert", "ärger", "verärgert", "gereizt"],
        
        # Kognitive Zustände (100-109)
        100: ["neugierig", "wissbegierig", "lernen", "verstehen", "erkunden"],
        101: ["skeptisch", "zweifel", "hinterfragen", "kritisch", "misstrauisch"],
        102: ["überzeugt", "sicher", "bestimmt", "gewiss", "entschlossen"],
        103: ["unsicher", "zweifelnd", "unentschlossen", "verwirrung", "unklar"],
        104: ["überrascht", "erstaunt", "verwundert", "verblüfft", "staunen"],
        105: ["verstehen", "klar", "einleuchtend", "nachvollziehbar", "logisch"],
        
        # Fokus und Aktivität (1-10)
        1: ["aufmerksam", "wachsam", "alert", "bewusst", "präsent"],
        2: ["fokussiert", "konzentriert", "fokus", "aufgabe", "zielgerichtet"],
        3: ["kreativ", "kreativität", "idee", "innovation", "erfindung"],
        4: ["analytisch", "analyse", "logik", "reasoning", "problemlösung"],
        5: ["lernen", "lernend", "studieren", "verstehen", "begreifen"],
        6: ["reflexion", "reflektieren", "nachdenken", "überlegen", "besinnung"],
        7: ["neugier", "erkunden", "entdecken", "erforschen", "experimentieren"],
        8: ["verwirrt", "verwirrung", "durcheinander", "orientierungslos", "ratlos"],
        9: ["entspannt", "ruhig", "gelassen", "friedlich", "beruhigt"],
        10: ["energetisch", "energie", "aktiv", "dynamisch", "lebhaft"],
        
        # Soziale Zustände (150-159)
        150: ["hilfsbereit", "helfen", "unterstützen", "assistieren", "beistehen"],
        151: ["empathisch", "mitfühlend", "verständnisvoll", "einfühlsam", "empathie"],
        152: ["kommunikativ", "gesprächig", "offen", "mitteilsam", "gesellig"],
        153: ["zurückhaltend", "schüchtern", "vorsichtig", "reserviert", "distanziert"],
        154: ["kooperativ", "zusammenarbeit", "teamwork", "gemeinsam", "kollaborativ"],
        155: ["unterstützend", "ermutigend", "bestärkend", "hilfreich", "fördernd"],
        
        # Spezielle Zustände (200-209)
        200: ["meditation", "meditativ", "achtsam", "innere ruhe", "stille"],
        201: ["inspiration", "inspiriert", "eingebung", "intuition", "erleuchtung"],
        202: ["vision", "visionär", "vorstellung", "traumhaft", "phantasie"],
        203: ["intuition", "intuitiv", "bauchgefühl", "ahnung", "gefühl"],
        204: ["transzendent", "übersinnlich", "spirituell", "erhaben", "göttlich"],
        205: ["verbunden", "verbindung", "einheit", "zusammengehörigkeit", "harmonie"]
    }
    
    # Text auf Schlüsselwörter analysieren
    found_states = []
    
    for state_id, keywords in keyword_mappings.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_states.append((state_id, keyword))
    
    # Wenn mehrere Zustände gefunden, den ersten zurückgeben
    if found_states:
        best_state = found_states[0][0]
        logger.debug(f"Zustand {best_state} vorgeschlagen für Text: '{text[:50]}...'")
        return best_state
    
    # Weitere Heuristiken
    # Fragezeichen -> neugierig/zweifelnd
    if '?' in text:
        if any(word in text_lower for word in ['warum', 'wieso', 'weshalb', 'wie', 'was']):
            return 100  # Wissbegierig
        else:
            return 103  # Zweifelnd
    
    # Ausrufezeichen -> energetisch/begeistert
    if '!' in text:
        return 51 if any(word in text_lower for word in ['toll', 'super', 'fantastisch', 'großartig']) else 10
    
    # Länge des Textes als Indikator
    if len(text) > 200:
        return 4  # Analytisch (langer, durchdachter Text)
    elif len(text) < 20:
        return 0  # Neutral (kurze Äußerung)
    
    # Standard: Neutral
    logger.debug(f"Kein spezifischer Zustand erkannt, verwende Neutral für: '{text[:50]}...'")
    return 0