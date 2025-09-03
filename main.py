#!/usr/bin/env python3
"""
ASI Core - Hauptanwendung
Autonomous Self-Improvement System

Ein System für persönliche Reflexion, Anonymisierung und dezentrale Speicherung.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent))

from src.ai.embedding import ReflectionEmbedding
from src.ai.search import SemanticSearchEngine
from src.blockchain.contract import ASISmartContract
from src.blockchain.wallet import CryptoWallet
from src.core.input import InputHandler
from src.core.output import OutputGenerator
from src.core.processor import ReflectionProcessor
from src.storage.arweave_client import ArweaveClient
from src.storage.ipfs_client import IPFSClient
from src.storage.local_db import LocalDatabase


class ASICore:
    """Hauptklasse des ASI Systems"""

    def __init__(self, config_path: str = "config/secrets.json"):
        self.config = self._load_config(config_path)
        self._init_components()

    def _load_config(self, config_path: str) -> dict:
        """Lädt Konfiguration"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Konfigurationsdatei {config_path} nicht gefunden.")
            print("Verwende Beispiel-Konfiguration.")
            with open("config/secrets.example.json", "r") as f:
                return json.load(f)

    def _init_components(self):
        """Initialisiert alle System-Komponenten"""
        print("Initialisiere ASI Core System...")

        # Storage-Module
        self.local_db = LocalDatabase(
            self.config.get("database_path", "data/asi_local.db")
        )
        self.ipfs_client = IPFSClient(self.config.get("ipfs_api_url"))
        self.arweave_client = ArweaveClient(self.config.get("arweave_gateway"))

        # AI-Module
        self.embedding_system = ReflectionEmbedding()
        self.search_engine = SemanticSearchEngine(self.embedding_system, self.local_db)

        # Core-Module
        self.input_handler = InputHandler()
        self.processor = ReflectionProcessor(self.embedding_system, self.local_db)
        self.output_generator = OutputGenerator()

        # Blockchain-Module
        self.smart_contract = ASISmartContract()
        self.wallet = CryptoWallet()

        # HRM-Module (Hierarchical Reasoning Model)
        try:
            from src.ai.hrm.high_level.pattern_recognition import PatternRecognizer
            from src.ai.hrm.high_level.planner import Planner
            from src.ai.hrm.low_level.detail_analysis import DetailAnalyzer
            from src.ai.hrm.low_level.executor import Executor

            self.hrm_planner = Planner(self.embedding_system, self.local_db)
            self.hrm_pattern_recognizer = PatternRecognizer(
                self.embedding_system, self.local_db
            )
            self.hrm_executor = Executor()
            self.hrm_detail_analyzer = DetailAnalyzer()
            print("✅ HRM (Hierarchical Reasoning Model) aktiviert")
        except ImportError as e:
            print(f"⚠️ HRM-Module nicht verfügbar: {e}")
            self.hrm_planner = None

        print("✓ Alle Komponenten initialisiert")

    def process_reflection_workflow(
        self, content: str, tags: list = None, privacy_level: str = "private"
    ):
        """
        Kompletter Workflow für eine Reflexion

        Args:
            content: Reflexionsinhalt
            tags: Optionale Tags
            privacy_level: Privacy-Level (private, anonymous, public)
        """
        print("\n=== Reflexions-Workflow gestartet ===")

        # 1. Eingabe erfassen
        print("1. Erfasse Reflexion...")
        reflection_entry = self.input_handler.capture_reflection(content, tags or [])
        reflection_entry.privacy_level = privacy_level

        # 2. Verarbeitung und Anonymisierung
        print("2. Verarbeite und anonymisiere...")
        reflection_data = {
            "content": reflection_entry.content,
            "timestamp": reflection_entry.timestamp.isoformat(),
            "tags": reflection_entry.tags,
            "privacy_level": reflection_entry.privacy_level,
        }

        processed_reflection = self.processor.process_reflection(reflection_data)

        # 3. Lokale Speicherung
        print("3. Speichere lokal...")
        exported_data = self.processor.export_processed(processed_reflection)
        reflection_id = self.local_db.store_reflection(exported_data)

        # 4. Embedding erstellen
        print("4. Erstelle Embeddings...")
        embedding_info = self.embedding_system.create_reflection_embedding(
            exported_data
        )

        # 5. Optionale dezentrale Speicherung
        ipfs_hash = None
        arweave_tx = None

        if self.config.get("auto_upload_ipfs", False) and privacy_level in [
            "anonymous",
            "public",
        ]:
            print("5a. Lade zu IPFS hoch...")
            ipfs_hash = self.ipfs_client.upload_reflection(exported_data)
            if ipfs_hash:
                self.local_db.update_storage_reference(
                    exported_data["hash"], "ipfs", ipfs_hash
                )

        if self.config.get("auto_upload_arweave", False) and privacy_level == "public":
            print("5b. Lade zu Arweave hoch...")
            arweave_tx = self.arweave_client.upload_reflection(exported_data, ipfs_hash)
            if arweave_tx:
                self.local_db.update_storage_reference(
                    exported_data["hash"], "arweave", arweave_tx
                )

        # 6. Lokale Ausgabe und Hinweise
        print("6. Generiere Ausgabe und Hinweise...")
        local_file = self.output_generator.save_local_copy(exported_data)

        # 7. Erkenntnisse generieren
        recent_reflections = self.local_db.get_reflections(limit=10)
        insights = self.output_generator.generate_insights(
            [
                {
                    "hash": r.hash,
                    "content": self.local_db.get_reflection_by_hash(r.hash)["content"],
                    "themes": r.themes,
                    "sentiment": r.sentiment,
                }
                for r in recent_reflections
            ]
        )

        print("✓ Reflexions-Workflow abgeschlossen")

        return {
            "reflection_id": reflection_id,
            "hash": exported_data["hash"],
            "local_file": local_file,
            "ipfs_hash": ipfs_hash,
            "arweave_tx": arweave_tx,
            "insights": len(insights),
            "themes": exported_data["themes"],
        }

    def search_reflections(self, query: str, limit: int = 5):
        """
        Sucht in Reflexionen

        Args:
            query: Suchanfrage
            limit: Maximale Anzahl Ergebnisse
        """
        print(f"\n=== Suche nach: '{query}' ===")

        results = self.search_engine.search_by_text(query, limit=limit)

        if results:
            print(f"Gefunden: {len(results)} Reflexionen")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.content_preview[:60]}...")
                print(f"   Ähnlichkeit: {result.similarity_score:.3f}")
                print(f"   Themen: {', '.join(result.matching_themes)}")
                print(f"   Datum: {result.timestamp.strftime('%Y-%m-%d %H:%M')}")
                print()
        else:
            print("Keine passenden Reflexionen gefunden.")

        return results

    def show_statistics(self):
        """Zeigt System-Statistiken"""
        print("\n=== ASI Core Statistiken ===")

        # Datenbank-Statistiken
        db_stats = self.local_db.get_statistics()
        print(f"Gespeicherte Reflexionen: {db_stats['total_reflections']}")
        print(f"Letzte 7 Tage: {db_stats['reflections_last_7_days']}")
        print(f"Gesamte Wörter: {db_stats['total_words']:,}")

        # Privacy-Verteilung
        privacy_dist = db_stats.get("privacy_distribution", {})
        if privacy_dist:
            print("\nPrivacy-Level Verteilung:")
            for level, count in privacy_dist.items():
                print(f"  {level}: {count}")

        # IPFS-Status
        ipfs_running = self.ipfs_client.is_node_running()
        print(f"\nIPFS-Node: {'✓ Läuft' if ipfs_running else '✗ Nicht erreichbar'}")

        # Arweave-Status
        arweave_info = self.arweave_client.get_storage_info()
        print(f"Arweave-Status: {arweave_info['status']}")

        # Wallet-Status
        if self.wallet.is_unlocked:
            wallet_info = self.wallet.get_wallet_info()
            print(
                f"Wallet: {wallet_info.address[:10]}... ({wallet_info.balance_eth:.4f} ETH)"
            )
        else:
            print("Wallet: Nicht geladen")

    def interactive_mode(self):
        """Interaktiver Modus"""
        print("\n🧠 ASI Core - Autonomous Self-Improvement System")
        print("===============================================")
        print("Willkommen zu deinem persönlichen Reflexions-System!")
        print()

        while True:
            print("\nWas möchtest du tun?")
            print("1. Neue Reflexion erfassen")
            print("2. In Reflexionen suchen")
            print("3. Geführte Reflexion")
            print("4. Statistiken anzeigen")
            print("5. Wochenbericht erstellen")
            print("6. System beenden")

            choice = input("\nWähle eine Option (1-6): ").strip()

            if choice == "1":
                self._handle_new_reflection()
            elif choice == "2":
                self._handle_search()
            elif choice == "3":
                self._handle_guided_reflection()
            elif choice == "4":
                self.show_statistics()
            elif choice == "5":
                self._handle_weekly_report()
            elif choice == "6":
                print("Auf Wiedersehen! 🌟")
                break
            else:
                print("Ungültige Auswahl. Bitte wähle 1-6.")

    def _handle_new_reflection(self):
        """Behandelt neue Reflexions-Eingabe"""
        print("\n--- Neue Reflexion ---")
        content = input("Deine Reflexion: ")

        if not content.strip():
            print("Keine Reflexion eingegeben.")
            return

        tags_input = input("Tags (durch Komma getrennt, optional): ")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

        privacy = (
            input("Privacy-Level (private/anonymous/public) [private]: ").strip()
            or "private"
        )

        result = self.process_reflection_workflow(content, tags, privacy)

        print(f"\n✓ Reflexion gespeichert (ID: {result['reflection_id']})")
        print(f"Identifizierte Themen: {', '.join(result['themes'])}")
        if result["insights"] > 0:
            print(f"Neue Erkenntnisse generiert: {result['insights']}")

    def _handle_search(self):
        """Behandelt Such-Anfragen"""
        print("\n--- Suche in Reflexionen ---")
        query = input("Wonach suchst du? ")

        if not query.strip():
            print("Keine Suchanfrage eingegeben.")
            return

        self.search_reflections(query)

    def _handle_guided_reflection(self):
        """Behandelt geführte Reflexion"""
        print("\n--- Geführte Reflexion ---")
        reflection_entry = self.input_handler.guided_reflection()

        result = self.process_reflection_workflow(
            reflection_entry.content,
            reflection_entry.tags,
            reflection_entry.privacy_level,
        )

        print(f"\n✓ Geführte Reflexion gespeichert (ID: {result['reflection_id']})")

    def _handle_weekly_report(self):
        """Behandelt Wochenbericht"""
        print("\n--- Wochenbericht ---")
        report = self.output_generator.create_weekly_report()

        print(f"Zeitraum: {report['period']}")
        print(f"Reflexionen: {report['reflection_count']}")

        if report["insights"]:
            print("\nErkenntnisse:")
            for insight in report["insights"]:
                print(f"• {insight['title']}")
                if insight["actionable"]:
                    print(f"  💡 {insight['description']}")

        if report.get("next_prompt"):
            print(f"\nNächste Reflexion: {report['next_prompt']}")

    def hrm_demo(self, content: str):
        """HRM-Demo mit gegebenem Text"""
        print(f"\n=== HRM-Analyse: '{content}' ===")

        if not self.hrm_planner:
            print("⚠️ HRM-Module nicht verfügbar")
            return

        try:
            # High-Level Analyse
            user_context = {
                "content": content,
                "tags": [],
                "timestamp": datetime.now().isoformat(),
            }
            plan = self.hrm_planner.create_plan(user_context)
            patterns = self.hrm_pattern_recognizer.analyze_patterns(user_context)

            # Low-Level Analyse
            details = self.hrm_detail_analyzer.analyze_details(user_context)
            execution = self.hrm_executor.execute_analysis(plan, user_context)

            print(f"📋 Plan: {plan.get('summary', 'Keine Planung verfügbar')}")
            print(f"🔍 Muster: {len(patterns)} erkannt")
            details_conf = details.get("confidence_score", 0.0)
            print(f"⚙️ Details: {details_conf:.2f} Konfidenz")
            if execution:
                exec_status = execution.get(
                    "status", execution.get("action", "Unbekannt")
                )
                print(f"✅ Ausführung: {exec_status}")
            else:
                print("✅ Ausführung: Keine Aktion erforderlich")

        except Exception as e:
            print(f"❌ HRM-Fehler: {e}")

    def hrm_interactive_test(self):
        """Interaktiver HRM-Test"""
        print("\n🧠 HRM Interactive Test")
        print("=" * 30)

        if not self.hrm_planner:
            print("⚠️ HRM-Module nicht verfügbar")
            return

        test_cases = [
            "Ich fühle mich heute müde und unmotiviert",
            "Das Meeting war sehr produktiv und inspirierend",
            "Ich habe einen wichtigen Durchbruch in meinem Projekt erzielt",
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_case} ---")
            self.hrm_demo(test_case)

        print("\n✅ HRM-Test abgeschlossen")


def main():
    """Hauptfunktion"""
    print("Starte ASI Core System...")

    try:
        asi = ASICore()

        # Kommandozeilen-Argumente prüfen
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()

            if command == "stats":
                asi.show_statistics()
            elif command == "process" and len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                result = asi.process_reflection_workflow(content)
                print(f"Reflexion verarbeitet: {result['hash']}")
            elif command == "search" and len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                asi.search_reflections(query)
            elif command == "hrm" and len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                asi.hrm_demo(content)
            elif command == "hrm-test":
                asi.hrm_interactive_test()
            else:
                print("Verwendung:")
                print("  python main.py                    # Interaktiver Modus")
                print("  python main.py stats              # Statistiken anzeigen")
                print("  python main.py process <text>     # Reflexion verarbeiten")
                print("  python main.py search <query>     # Suche")
                print("  python main.py hrm <text>         # HRM-Analyse")
                print("  python main.py hrm-test           # HRM-Demo")
        else:
            # Interaktiver Modus
            asi.interactive_mode()

    except KeyboardInterrupt:
        print("\n\nProgramm beendet.")
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
