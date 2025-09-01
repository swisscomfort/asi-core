"""
ASI Core - Input Module
Eingabe von Reflexionen und ersten Strukturierung
"""

import json
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ReflectionEntry:
    """Datenstruktur für eine Reflexion"""

    content: str
    timestamp: datetime.datetime
    tags: List[str]
    mood: Optional[str] = None
    privacy_level: str = "private"  # private, anonymous, public


class InputHandler:
    """Hauptklasse für die Eingabe von Reflexionen"""

    def __init__(self):
        self.current_session = []

    def capture_reflection(
        self, content: str, tags: List[str] = None, mood: str = None
    ) -> ReflectionEntry:
        """
        Erfasst eine neue Reflexion

        Args:
            content: Der Reflexionstext
            tags: Optionale Tags für Kategorisierung
            mood: Optionale Stimmungsangabe

        Returns:
            ReflectionEntry: Die strukturierte Reflexion
        """
        if tags is None:
            tags = []

        entry = ReflectionEntry(
            content=content, timestamp=datetime.datetime.now(), tags=tags, mood=mood
        )

        self.current_session.append(entry)
        return entry

    def guided_reflection(self) -> ReflectionEntry:
        """
        Interaktive geführte Reflexion mit Leitfragen

        Returns:
            ReflectionEntry: Die erfasste Reflexion
        """
        print("=== Geführte Reflexion ===")
        print("Nimm dir einen Moment Zeit für dich...")

        # Leitfragen
        questions = [
            "Was beschäftigt dich gerade?",
            "Welche Gefühle nimmst du wahr?",
            "Was hast du heute gelernt?",
            "Wofür bist du dankbar?",
        ]

        responses = []
        for question in questions:
            answer = input(f"\n{question}\n> ")
            if answer.strip():
                responses.append(f"{question} {answer}")

        content = "\n\n".join(responses)

        # Tags erfassen
        tags_input = input("\nMöchtest du Tags hinzufügen? (durch Komma getrennt)\n> ")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        # Stimmung erfassen
        mood = input("\nWie würdest du deine aktuelle Stimmung beschreiben?\n> ")

        return self.capture_reflection(content, tags, mood if mood.strip() else None)

    def quick_note(self, content: str) -> ReflectionEntry:
        """
        Schnelle Notiz ohne weitere Abfragen

        Args:
            content: Der Notizinhalt

        Returns:
            ReflectionEntry: Die erfasste Notiz
        """
        return self.capture_reflection(content, tags=["quick-note"])

    def voice_to_text_placeholder(self, audio_data: bytes) -> str:
        """
        Platzhalter für Sprache-zu-Text Funktionalität

        Args:
            audio_data: Audiodaten

        Returns:
            str: Transkribierter Text
        """
        # Hier würde eine Speech-to-Text API integriert
        return "Sprache-zu-Text noch nicht implementiert"

    def export_session(self) -> Dict:
        """
        Exportiert die aktuelle Session

        Returns:
            Dict: Session-Daten als Dictionary
        """
        return {
            "session_start": (
                self.current_session[0].timestamp.isoformat()
                if self.current_session
                else None
            ),
            "entry_count": len(self.current_session),
            "entries": [
                {
                    "content": entry.content,
                    "timestamp": entry.timestamp.isoformat(),
                    "tags": entry.tags,
                    "mood": entry.mood,
                    "privacy_level": entry.privacy_level,
                }
                for entry in self.current_session
            ],
        }

    def clear_session(self):
        """Leert die aktuelle Session"""
        self.current_session = []


if __name__ == "__main__":
    # Beispiel-Nutzung
    handler = InputHandler()

    print("ASI Core - Reflexions-Eingabe")
    print("1. Geführte Reflexion")
    print("2. Schnelle Notiz")
    print("3. Session exportieren")

    choice = input("Wähle eine Option (1-3): ")

    if choice == "1":
        entry = handler.guided_reflection()
        print(f"\nReflexion gespeichert: {len(entry.content)} Zeichen")
    elif choice == "2":
        content = input("Deine Notiz: ")
        entry = handler.quick_note(content)
        print("Notiz gespeichert!")
    elif choice == "3":
        session_data = handler.export_session()
        print(json.dumps(session_data, indent=2, ensure_ascii=False))
