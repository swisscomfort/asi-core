"""
ASI Core - Enhanced Processor with Storacha Integration
Strukturierung, Anonymisierung und dezentrale Speicherung von Reflexionen
"""

import re
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Import der Storacha-Integration
from src.storage.storacha_client_clean import StorachaUploader


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
    storacha_url: Optional[str] = None  # Neue Eigenschaft für dezentrale Speicherung


class EnhancedReflectionProcessor:
    """Erweiterte Hauptklasse für die Verarbeitung und dezentrale Speicherung von Reflexionen"""

    def __init__(self, enable_storacha: bool = True):
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

        # Storacha-Integration
        self.enable_storacha = enable_storacha
        self.storacha_uploader = None
        if enable_storacha:
            try:
                self.storacha_uploader = StorachaUploader("asi-reflections.log")
                if not self.storacha_uploader.check_cli_available():
                    print(
                        "⚠️ Storacha CLI nicht verfügbar - lokale Speicherung wird verwendet"
                    )
                    self.enable_storacha = False
            except ImportError:
                print(
                    "⚠️ Storacha-Integration nicht verfügbar - lokale Speicherung wird verwendet"
                )
                self.enable_storacha = False

    def anonymize_content(self, content: str) -> str:
        """
        Anonymisiert persönliche Informationen in der Reflexion
        """
        anonymized = content

        for pattern_name, pattern in self.anonymization_patterns.items():
            if pattern_name == "names":
                anonymized = re.sub(pattern, "[NAME]", anonymized)
            elif pattern_name == "emails":
                anonymized = re.sub(pattern, "[EMAIL]", anonymized)
            elif pattern_name == "phones":
                anonymized = re.sub(pattern, "[TELEFON]", anonymized)
            elif pattern_name == "dates":
                anonymized = re.sub(pattern, "[DATUM]", anonymized)
            elif pattern_name == "locations":
                anonymized = re.sub(
                    pattern, lambda m: f"{m.group(1)} [ORT]", anonymized
                )

        return anonymized

    def analyze_sentiment(self, content: str) -> str:
        """
        Analysiert die Stimmung der Reflexion
        """
        content_lower = content.lower()

        positive_count = sum(
            1 for word in self.emotion_keywords["positive"] if word in content_lower
        )
        negative_count = sum(
            1 for word in self.emotion_keywords["negative"] if word in content_lower
        )

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def extract_themes(self, content: str, tags: List[str]) -> List[str]:
        """
        Extrahiert Hauptthemen aus der Reflexion
        """
        themes = set(tags)

        # Themen-Keywords
        theme_patterns = {
            "arbeit": ["arbeit", "job", "beruf", "kollegen", "chef"],
            "beziehung": ["beziehung", "partner", "liebe", "freund"],
            "gesundheit": ["gesundheit", "krank", "arzt", "fitness"],
            "familie": ["familie", "mutter", "vater", "kind", "geschwister"],
            "zukunft": ["zukunft", "plane", "ziele", "träume"],
        }

        content_lower = content.lower()
        for theme, keywords in theme_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.add(theme)

        return list(themes)

    def process_reflection(self, reflection_data: Dict) -> ProcessedEntry:
        """
        Verarbeitet eine Reflexion vollständig
        """
        content = reflection_data["content"]
        tags = reflection_data.get("tags", [])
        privacy_level = reflection_data.get("privacy_level", "private")

        # Hash für Eindeutigkeit
        original_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Anonymisierung basierend auf Privacy Level
        if privacy_level in ["anonymous", "public"]:
            anonymized_content = self.anonymize_content(content)
        else:
            anonymized_content = content

        # Sentiment-Analyse
        sentiment = self.analyze_sentiment(content)

        # Themen-Extraktion
        key_themes = self.extract_themes(content, tags)

        # Strukturierte Daten
        structured_data = {
            "word_count": len(content.split()),
            "character_count": len(content),
            "contains_questions": "?" in content,
            "reflection_date": reflection_data.get("date", datetime.now().isoformat()),
            "metadata": reflection_data.get("metadata", {}),
        }

        # Processed Entry erstellen
        processed_entry = ProcessedEntry(
            original_hash=original_hash,
            anonymized_content=anonymized_content,
            structured_data=structured_data,
            privacy_level=privacy_level,
            processing_timestamp=datetime.now(),
            tags=tags,
            sentiment=sentiment,
            key_themes=key_themes,
            storacha_url=None,
        )

        # Dezentrale Speicherung wenn erlaubt
        if self.enable_storacha and privacy_level in ["public", "anonymous"]:
            storacha_url = self._store_to_storacha(processed_entry)
            processed_entry.storacha_url = storacha_url

        return processed_entry

    def _store_to_storacha(self, entry: ProcessedEntry) -> Optional[str]:
        """
        Speichert verarbeitete Reflexion in Storacha
        """
        if not self.storacha_uploader:
            return None

        try:
            # Temporäre Datei erstellen
            timestamp = entry.processing_timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"reflection_{entry.original_hash}_{timestamp}.json"

            # Entry zu JSON konvertieren (datetime serialisieren)
            entry_dict = asdict(entry)
            entry_dict["processing_timestamp"] = entry.processing_timestamp.isoformat()

            # In temporäre Datei schreiben
            with open(filename, "w", encoding="utf-8") as temp_file:
                json.dump(entry_dict, temp_file, indent=2, ensure_ascii=False)

            # Upload zu Storacha
            storacha_url = self.storacha_uploader.upload_file(filename)

            # Temporäre Datei löschen
            os.remove(filename)

            if storacha_url:
                print(f"✅ Reflexion dezentral gespeichert: {storacha_url}")

            return storacha_url

        except Exception as error:
            print(f"⚠️ Storacha-Upload fehlgeschlagen: {error}")
            return None

    def export_processed(self, entry: ProcessedEntry) -> Dict:
        """
        Exportiert verarbeitete Reflexion als Dictionary
        """
        exported = asdict(entry)
        exported["processing_timestamp"] = entry.processing_timestamp.isoformat()
        return exported

    def batch_process_reflections(
        self, reflections: List[Dict]
    ) -> List[ProcessedEntry]:
        """
        Verarbeitet mehrere Reflexionen in einem Batch
        """
        results = []
        for i, reflection in enumerate(reflections, 1):
            print(f"🔄 Verarbeite Reflexion {i}/{len(reflections)}...")
            processed = self.process_reflection(reflection)
            results.append(processed)

        # Batch-Upload für öffentliche Reflexionen
        if self.enable_storacha:
            self._batch_upload_summary(results)

        return results

    def _batch_upload_summary(self, entries: List[ProcessedEntry]):
        """
        Erstellt und uploadet eine Zusammenfassung des Batches
        """
        if not self.storacha_uploader:
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_filename = f"reflection_batch_summary_{timestamp}.json"

            # Zusammenfassung erstellen
            summary = {
                "batch_timestamp": datetime.now().isoformat(),
                "total_reflections": len(entries),
                "public_reflections": len(
                    [e for e in entries if e.privacy_level == "public"]
                ),
                "anonymous_reflections": len(
                    [e for e in entries if e.privacy_level == "anonymous"]
                ),
                "sentiment_distribution": {
                    "positive": len([e for e in entries if e.sentiment == "positive"]),
                    "negative": len([e for e in entries if e.sentiment == "negative"]),
                    "neutral": len([e for e in entries if e.sentiment == "neutral"]),
                },
                "common_themes": self._get_common_themes(entries),
                "reflection_hashes": [
                    e.original_hash for e in entries if e.storacha_url
                ],
            }

            # Summary-Datei schreiben
            with open(summary_filename, "w", encoding="utf-8") as summary_file:
                json.dump(summary, summary_file, indent=2, ensure_ascii=False)

            # Upload zu Storacha
            summary_url = self.storacha_uploader.upload_file(summary_filename)

            # Cleanup
            os.remove(summary_filename)

            if summary_url:
                print(f"📊 Batch-Zusammenfassung hochgeladen: {summary_url}")

        except Exception as error:
            print(f"⚠️ Batch-Summary Upload fehlgeschlagen: {error}")

    def _get_common_themes(self, entries: List[ProcessedEntry]) -> Dict[str, int]:
        """
        Ermittelt häufige Themen in einem Batch
        """
        theme_counts = {}
        for entry in entries:
            for theme in entry.key_themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

        # Sortiert nach Häufigkeit
        return dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10])


# Test und Beispiel-Verwendung
if __name__ == "__main__":
    print("🚀 ASI-Core Enhanced Processor mit Storacha-Integration")

    processor = EnhancedReflectionProcessor(enable_storacha=True)

    # Test-Reflexionen
    test_reflections = [
        {
            "content": """Heute hatte ich ein wichtiges Gespräch über meine Zukunft. 
            Ich fühle mich optimistisch und dankbar für die neuen Möglichkeiten.""",
            "tags": ["zukunft", "gespräch"],
            "privacy_level": "public",
        },
        {
            "content": """Schwieriger Tag im Büro. Mein Chef war wieder unzufrieden. 
            Ich frage mich, ob ich den richtigen Beruf gewählt habe.""",
            "tags": ["arbeit", "beruf"],
            "privacy_level": "anonymous",
        },
        {
            "content": """Vertrauliche persönliche Gedanken über meine Familie.""",
            "tags": ["familie"],
            "privacy_level": "private",
        },
    ]

    # Batch-Verarbeitung
    results = processor.batch_process_reflections(test_reflections)

    # Ausgabe
    print(f"\n📊 Verarbeitung abgeschlossen: {len(results)} Reflexionen")
    for i, result in enumerate(results, 1):
        print(f"\n--- Reflexion {i} ---")
        print(f"Hash: {result.original_hash}")
        print(f"Sentiment: {result.sentiment}")
        print(f"Themen: {', '.join(result.key_themes)}")
        print(f"Privacy: {result.privacy_level}")
        if result.storacha_url:
            print(f"🌐 Storacha: {result.storacha_url}")
        else:
            print("🔒 Lokal gespeichert")
