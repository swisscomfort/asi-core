"""
ASI Core - Processor Module
Strukturierung, Anonymisierung und Aufbereitung von Reflexionen
"""

import re
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProcessedEntry:
    """Strukturierte und verarbeitete Reflexion"""

    original_hash: str
    anonymized_content: str
    structured_data: Dict
    privacy_level: str
    processing_timestamp: datetime
    tags: List[str]
    sentiment: Optional[str] = None
    key_themes: List[str] = None


class ReflectionProcessor:
    """Hauptklasse für die Verarbeitung von Reflexionen"""

    def __init__(self):
        self.anonymization_patterns = {
            "names": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
            "emails": r"\S+@\S+\.\S+",
            "phones": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "dates": r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
            "locations": r"\b(in|bei|nach|von)\s+[A-Z][a-z]+\b",
        }

        self.emotion_keywords = {
            "positive": ["glücklich", "froh", "dankbar", "stolz", "begeistert"],
            "negative": ["traurig", "ängstlich", "wütend", "frustriert", "enttäuscht"],
            "neutral": ["ruhig", "entspannt", "nachdenklich", "müde"],
        }

    def anonymize_content(self, content: str) -> str:
        """
        Anonymisiert persönliche Informationen in der Reflexion

        Args:
            content: Ursprünglicher Reflexionstext

        Returns:
            str: Anonymisierter Text
        """
        anonymized = content

        # Namen durch Platzhalter ersetzen
        anonymized = re.sub(
            self.anonymization_patterns["names"], "[PERSON]", anonymized
        )

        # E-Mails anonymisieren
        anonymized = re.sub(
            self.anonymization_patterns["emails"], "[EMAIL]", anonymized
        )

        # Telefonnummern entfernen
        anonymized = re.sub(
            self.anonymization_patterns["phones"], "[TELEFON]", anonymized
        )

        # Spezifische Daten anonymisieren
        anonymized = re.sub(self.anonymization_patterns["dates"], "[DATUM]", anonymized)

        # Ortsnamen entfernen
        anonymized = re.sub(
            self.anonymization_patterns["locations"], r"\1 [ORT]", anonymized
        )

        return anonymized

    def extract_emotions(self, content: str) -> Tuple[str, float]:
        """
        Extrahiert Emotionen aus dem Text

        Args:
            content: Text zur Analyse

        Returns:
            Tuple[str, float]: Emotionskategorie und Konfidenz
        """
        content_lower = content.lower()
        emotion_scores = {}

        for emotion_type, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            emotion_scores[emotion_type] = score

        if not any(emotion_scores.values()):
            return "neutral", 0.5

        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[dominant_emotion] / len(content.split())

        return dominant_emotion, min(confidence * 10, 1.0)

    def extract_themes(self, content: str) -> List[str]:
        """
        Extrahiert Hauptthemen aus der Reflexion

        Args:
            content: Text zur Analyse

        Returns:
            List[str]: Identifizierte Themen
        """
        # Einfache Themen-Extraktion basierend auf Schlüsselwörtern
        theme_patterns = {
            "arbeit": ["arbeit", "job", "beruf", "kollege", "chef", "projekt"],
            "beziehungen": ["freund", "familie", "partner", "beziehung", "liebe"],
            "gesundheit": ["gesundheit", "krank", "müde", "energie", "sport"],
            "persönlichkeit": ["ich", "selbst", "persönlich", "charakter"],
            "zukunft": ["zukunft", "plan", "ziel", "hoffnung", "traum"],
            "vergangenheit": ["vergangenheit", "erinnerung", "früher", "damals"],
        }

        content_lower = content.lower()
        identified_themes = []

        for theme, keywords in theme_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                identified_themes.append(theme)

        return identified_themes

    def structure_content(self, content: str) -> Dict:
        """
        Strukturiert den Inhalt in semantische Bereiche

        Args:
            content: Zu strukturierender Text

        Returns:
            Dict: Strukturierte Daten
        """
        sentences = content.split(".")

        structure = {
            "total_sentences": len(sentences),
            "word_count": len(content.split()),
            "character_count": len(content),
            "sections": [],
        }

        # Einfache Sektionierung basierend auf Absätzen
        paragraphs = content.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                structure["sections"].append(
                    {
                        "index": i,
                        "content": paragraph.strip(),
                        "word_count": len(paragraph.split()),
                        "type": "reflection",
                    }
                )

        return structure

    def process_reflection(self, reflection_data: Dict) -> ProcessedEntry:
        """
        Verarbeitet eine komplette Reflexion

        Args:
            reflection_data: Rohdaten der Reflexion

        Returns:
            ProcessedEntry: Verarbeitete Reflexion
        """
        original_content = reflection_data["content"]

        # Hash für Originalinhalt erstellen
        original_hash = hashlib.sha256(original_content.encode("utf-8")).hexdigest()[
            :16
        ]

        # Anonymisierung
        anonymized_content = self.anonymize_content(original_content)

        # Strukturierung
        structured_data = self.structure_content(anonymized_content)

        # Emotionsanalyse
        emotion, confidence = self.extract_emotions(anonymized_content)

        # Themen-Extraktion
        themes = self.extract_themes(anonymized_content)

        # Verarbeitete Reflexion erstellen
        processed = ProcessedEntry(
            original_hash=original_hash,
            anonymized_content=anonymized_content,
            structured_data=structured_data,
            privacy_level=reflection_data.get("privacy_level", "private"),
            processing_timestamp=datetime.now(),
            tags=reflection_data.get("tags", []),
            sentiment=f"{emotion}({confidence:.2f})",
            key_themes=themes,
        )

        return processed

    def batch_process(self, reflections: List[Dict]) -> List[ProcessedEntry]:
        """
        Verarbeitet mehrere Reflexionen

        Args:
            reflections: Liste von Reflexions-Daten

        Returns:
            List[ProcessedEntry]: Liste verarbeiteter Reflexionen
        """
        return [self.process_reflection(ref) for ref in reflections]

    def export_processed(self, processed_entry: ProcessedEntry) -> Dict:
        """
        Exportiert verarbeitete Daten

        Args:
            processed_entry: Verarbeitete Reflexion

        Returns:
            Dict: Exportierbare Daten
        """
        return {
            "hash": processed_entry.original_hash,
            "content": processed_entry.anonymized_content,
            "structure": processed_entry.structured_data,
            "privacy": processed_entry.privacy_level,
            "timestamp": processed_entry.processing_timestamp.isoformat(),
            "tags": processed_entry.tags,
            "sentiment": processed_entry.sentiment,
            "themes": processed_entry.key_themes,
        }


if __name__ == "__main__":
    # Beispiel-Nutzung
    processor = ReflectionProcessor()

    # Test-Reflexion
    test_reflection = {
        "content": """Heute hatte ich ein schwieriges Gespräch mit Max Mustermann. 
        Wir haben über die Zukunft unserer Beziehung gesprochen. 
        Ich fühle mich traurig aber auch hoffnungsvoll.
        Meine E-Mail max@example.com ist übrigens.""",
        "tags": ["beziehung", "gespräch"],
        "privacy_level": "anonymous",
    }

    # Verarbeitung
    processed = processor.process_reflection(test_reflection)

    # Ausgabe
    exported = processor.export_processed(processed)
    print(json.dumps(exported, indent=2, ensure_ascii=False))
