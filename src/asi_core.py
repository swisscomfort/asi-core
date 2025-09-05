#!/usr/bin/env python3
"""
ASI-Core: Artificial Self-Intelligence System
Erweiterte Version mit Hybrid-Modell und State Management
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent.parent))
from asi_core.blockchain import ASIBlockchainClient, ASIBlockchainError
from asi_core.state_management import ASIStateManager, suggest_state_from_text


class ASICore:
    """
    Hauptklasse für das ASI System mit Hybrid-Modell Support
    """

    def __init__(self, config_path="config/settings.json"):
        self.config = self.load_config(config_path)
        self.setup_directories()

        # State Management initialisieren
        self.state_manager = ASIStateManager()

        # Blockchain Client (optional)
        self.blockchain_client = None
        self._initialize_blockchain()

        # Reflexionshistorie
        self.reflections = []

    def load_config(self, config_path):
        """Lädt die Konfiguration"""
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            # Blockchain-Konfiguration aus Secrets laden
            secrets_path = "config/secrets.json"
            if Path(secrets_path).exists():
                with open(secrets_path, "r") as f:
                    secrets = json.load(f)
                    config.update(secrets)

            return config
        except FileNotFoundError:
            return {
                "asi_version": "1.0.0-hybrid",
                "environment": "development",
                "hybrid_model": True,
                "default_state": 0,
            }

    def setup_directories(self):
        """Erstellt notwendige Verzeichnisse"""
        Path("data/reflections").mkdir(parents=True, exist_ok=True)
        Path("data/backups").mkdir(parents=True, exist_ok=True)
        Path("data/state_exports").mkdir(parents=True, exist_ok=True)

    def _initialize_blockchain(self):
        """Initialisiert die Blockchain-Verbindung falls konfiguriert"""
        try:
            if all(
                key in self.config
                for key in ["rpc_url", "private_key", "contract_address"]
            ):
                self.blockchain_client = ASIBlockchainClient(
                    rpc_url=self.config["rpc_url"],
                    private_key=self.config["private_key"],
                    contract_address=self.config["contract_address"],
                )
                print("🔗 Blockchain-Verbindung hergestellt")
            else:
                print(
                    "⚠️ Blockchain-Konfiguration unvollständig - nur lokale Speicherung"
                )
        except Exception as e:
            print(f"⚠️ Blockchain-Verbindung fehlgeschlagen: {e}")

    def add_reflection(self, content, tags=None, auto_detect_state=True):
        """
        Fügt eine neue Reflexion hinzu (Legacy-Funktion mit Standardzustand)

        Args:
            content: Reflexionsinhalt
            tags: Liste von Tags
            auto_detect_state: Automatische Zustandserkennung aktivieren

        Returns:
            Dictionary mit Reflexionsdaten
        """
        if auto_detect_state:
            suggested_state = suggest_state_from_text(content)
        else:
            suggested_state = self.config.get("default_state", 0)

        return self.add_state_reflection(content, suggested_state, tags)

    async def add_state_reflection(
        self, reflection_text: str, state_value: int, tags: Optional[List[str]] = None
    ):
        """
        Fügt eine zustandsbasierte Reflexion hinzu (Hybrid-Modell)

        Args:
            reflection_text: Der Reflexionstext
            state_value: Zustandswert (0-255)
            tags: Liste von Tags

        Returns:
            Dictionary mit Reflexionsdaten
        """
        try:
            if tags is None:
                tags = []

            # Zustandsreflexion erstellen
            reflection_data = self.state_manager.create_state_reflection(
                reflection_text, state_value, tags
            )

            # Lokale Speicherung
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/reflections/state_{timestamp_str}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(reflection_data, f, indent=2, ensure_ascii=False)

            print(f"💾 Zustandsreflexion lokal gespeichert: {filename}")

            # Zur internen Historie hinzufügen
            self.reflections.append(reflection_data)

            # Blockchain-Registrierung (falls verfügbar)
            if self.blockchain_client:
                try:
                    # Dummy-Embedding für Demo (in Produktion würde hier echtes Embedding generiert)
                    embedding = self._create_dummy_embedding(reflection_text)

                    # CID für Demo (in Produktion würde hier IPFS/Arweave verwendet)
                    cid = f"demo-{timestamp_str}-{hash(reflection_text) % 10000}"

                    tx_hash = self.blockchain_client.register_hybrid_entry_on_chain(
                        cid=cid,
                        tags=tags,
                        embedding=embedding,
                        state_value=state_value,
                        timestamp=reflection_data["unix_timestamp"],
                    )

                    reflection_data["blockchain"] = {
                        "tx_hash": tx_hash,
                        "cid": cid,
                        "registered": True,
                    }

                    print(f"⛓️ Blockchain-Registrierung erfolgreich: {tx_hash[:10]}...")

                except ASIBlockchainError as e:
                    print(f"⚠️ Blockchain-Registrierung fehlgeschlagen: {e}")
                    reflection_data["blockchain"] = {
                        "registered": False,
                        "error": str(e),
                    }

            print(
                f"✅ Zustandsreflexion hinzugefügt: Zustand {state_value} ({self.state_manager.get_state_name(state_value)})"
            )

            return reflection_data

        except Exception as e:
            print(f"❌ Fehler beim Hinzufügen der Zustandsreflexion: {e}")
            raise

    def _create_dummy_embedding(self, text: str, size: int = 128) -> bytes:
        """Erstellt ein Dummy-Embedding für Demo-Zwecke"""
        import hashlib

        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        while len(hash_bytes) < size:
            hash_bytes += hash_obj.digest()

        return hash_bytes[:size]

    def search_by_state(self, state_value: int):
        """
        Sucht Reflexionen nach Zustandswert

        Args:
            state_value: Der zu suchende Zustandswert

        Returns:
            Liste der gefilterten Reflexionen
        """
        local_results = self.state_manager.filter_by_state(
            state_value, self.reflections
        )

        print(
            f"🔍 Lokale Suche für Zustand {state_value}: {len(local_results)} Ergebnisse"
        )

        # Blockchain-Suche (falls verfügbar)
        if self.blockchain_client:
            try:
                blockchain_entries = self.blockchain_client.get_entries_by_state(
                    state_value
                )
                print(
                    f"⛓️ Blockchain-Suche für Zustand {state_value}: {len(blockchain_entries)} Einträge"
                )
            except Exception as e:
                print(f"⚠️ Blockchain-Suche fehlgeschlagen: {e}")

        return local_results

    def show_state_statistics(self):
        """Zeigt Zustandsstatistiken an"""
        local_stats = self.state_manager.get_statistics()

        print("\n📊 Lokale Zustandsstatistiken:")
        print(f"   Gesamteinträge: {local_stats['total_entries']}")
        print(f"   Verschiedene Zustände: {local_stats['unique_states']}")

        if local_stats["state_distribution"]:
            print("\n   Verteilung:")
            for state, data in local_stats["state_distribution"].items():
                print(
                    f"   • Zustand {state} ({data['name']}): {data['count']} ({data['percentage']:.1f}%)"
                )

        # Blockchain-Statistiken (falls verfügbar)
        if self.blockchain_client:
            try:
                blockchain_stats = self.blockchain_client.get_state_statistics()
                print(f"\n⛓️ Blockchain-Statistiken:")
                print(f"   Gesamteinträge: {blockchain_stats['total_entries']}")
                print(f"   Verschiedene Zustände: {blockchain_stats['unique_states']}")
            except Exception as e:
                print(f"⚠️ Blockchain-Statistiken nicht verfügbar: {e}")

    def export_state_data(self, filename: Optional[str] = None):
        """Exportiert Zustandsdaten"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/state_exports/state_export_{timestamp}.json"

        self.state_manager.export_state_data(filename)
        print(f"📤 Zustandsdaten exportiert: {filename}")

    def load_reflections_from_directory(self, directory: str = "data/reflections"):
        """Lädt existierende Reflexionen aus Verzeichnis"""
        reflection_files = Path(directory).glob("*.json")
        loaded_count = 0

        for file_path in reflection_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reflection = json.load(f)

                # Nur Zustandsreflexionen laden
                if "state_value" in reflection:
                    self.reflections.append(reflection)
                    self.state_manager.update_statistics(reflection["state_value"])
                    loaded_count += 1

            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {file_path}: {e}")

        print(f"📂 {loaded_count} Zustandsreflexionen geladen")

    def get_available_states(self):
        """Gibt verfügbare Zustandsdefinitionen zurück"""
        return self.state_manager.STATE_DEFINITIONS


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
