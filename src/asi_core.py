#!/usr/bin/env python3
"""
ASI-Core: Artificial Self-Intelligence System
Erste funktionsfähige Version für Codespace-Entwicklung
"""

import json
import os
from datetime import datetime
from pathlib import Path


class ASICore:
    def __init__(self, config_path="config/settings.json"):
        self.config = self.load_config(config_path)
        self.setup_directories()

    def load_config(self, config_path):
        """Lädt die Konfiguration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"asi_version": "0.1.0", "environment": "development"}

    def setup_directories(self):
        """Erstellt notwendige Verzeichnisse"""
        Path("data/reflections").mkdir(parents=True, exist_ok=True)
        Path("data/backups").mkdir(parents=True, exist_ok=True)

    def add_reflection(self, content, tags=None):
        """Fügt eine neue Reflexion hinzu"""
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "tags": tags or [],
            "type": "reflection",
        }

        # Lokale Speicherung
        filename = f"data/reflections/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(reflection, f, indent=2)

        print(f"✅ Reflexion gespeichert: {filename}")
        return reflection


def main():
    """Erste Testfunktion"""
    print("🧠 ASI-Core System gestartet")

    asi = ASICore()

    # Test-Reflexion hinzufügen
    test_reflection = asi.add_reflection(
        "Erste Gedanken zum ASI-System im Codespace. Das System nimmt Form an.",
        tags=["development", "first_thoughts", "codespace"],
    )

    print(f"📊 System-Info: {asi.config}")
    print("🎯 ASI-Core läuft erfolgreich!")


if __name__ == "__main__":
    main()
