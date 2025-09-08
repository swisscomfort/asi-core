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

# Flask für API-Integration
try:
    from flask import Flask, jsonify, request

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Environment Variables laden
from dotenv import load_dotenv

load_dotenv()

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent))

# Blockchain Integration
from asi_core.blockchain import (
    ASIBlockchainClient,
    ASIBlockchainError,
    create_blockchain_client_from_config,
)

# Neue Embedding und Suche Module
from asi_core.search import ASIEmbeddingGenerator, ASISemanticSearch
from src.ai.embedding import ReflectionEmbedding
from src.ai.search import SemanticSearchEngine
from src.blockchain.contract import ASISmartContract

# Memory Token Integration
from src.blockchain.memory_token import memory_token_service, token_bp
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
        # ASI Embedding und Suche System
        self.asi_embedding_generator = ASIEmbeddingGenerator()
        self.asi_search_engine = ASISemanticSearch(self.asi_embedding_generator)

        # Original AI Module
        self.embedding_system = ReflectionEmbedding()
        self.search_engine = SemanticSearchEngine(self.embedding_system, self.local_db)

        # Core-Module
        self.input_handler = InputHandler()
        self.processor = ReflectionProcessor(self.embedding_system, self.local_db)
        self.output_generator = OutputGenerator()

        # Blockchain-Module
        self.smart_contract = ASISmartContract()
        self.wallet = CryptoWallet()

        # Blockchain-Client initialisieren (falls konfiguriert)
        self.blockchain_client = None
        if self._init_blockchain_client():
            print("✅ Blockchain-Client initialisiert")
        else:
            print("⚠️ Blockchain-Client nicht verfügbar")

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

    def _init_blockchain_client(self) -> bool:
        """
        Initialisiert den Blockchain-Client basierend auf Umgebungsvariablen

        Returns:
            True wenn erfolgreich initialisiert, False sonst
        """
        try:
            # Environment Variables prüfen
            rpc_url = os.getenv("MUMBAI_RPC_URL") or os.getenv("POLYGON_RPC_URL")
            private_key = os.getenv("PRIVATE_KEY")
            contract_address = os.getenv("ASI_CONTRACT_ADDRESS")
            enable_blockchain = (
                os.getenv("ENABLE_BLOCKCHAIN", "false").lower() == "true"
            )

            if not enable_blockchain:
                return False

            if not all([rpc_url, private_key, contract_address]):
                print("⚠️ Blockchain-Konfiguration unvollständig")
                return False

            # Blockchain-Client erstellen
            self.blockchain_client = ASIBlockchainClient(
                rpc_url=rpc_url,
                private_key=private_key,
                contract_address=contract_address,
            )

            return True

        except Exception as e:
            print(f"❌ Blockchain-Client Initialisierung fehlgeschlagen: {e}")
            return False

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

        # 4. ASI Embedding erstellen
        print("4. Erstelle ASI-Semantik-Embedding...")
        asi_embedding_bytes = self.asi_embedding_generator.generate_embedding(
            exported_data["content"]
        )

        # Embedding im lokalen Cache speichern (mit CID falls verfügbar)
        text_preview = exported_data["content"][:200]
        temp_id = exported_data.get("hash", f"temp_{reflection_id}")
        self.asi_search_engine.store_embedding(
            temp_id, asi_embedding_bytes, text_preview
        )

        # 5. Original Embedding System (für Kompatibilität)
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
                # Update embedding cache mit tatsächlicher CID
                self.asi_search_engine.store_embedding(
                    ipfs_hash, asi_embedding_bytes, text_preview
                )

        if self.config.get("auto_upload_arweave", False) and privacy_level == "public":
            print("5b. Lade zu Arweave hoch...")
            arweave_tx = self.arweave_client.upload_reflection(exported_data, ipfs_hash)
            if arweave_tx:
                self.local_db.update_storage_reference(
                    exported_data["hash"], "arweave", arweave_tx
                )

        # 6. Blockchain-Registrierung (falls aktiviert)
        blockchain_tx = None
        if (
            self.blockchain_client
            and os.getenv("AUTO_REGISTER_ON_CHAIN", "false").lower() == "true"
            and privacy_level in ["anonymous", "public"]
            and (ipfs_hash or arweave_tx)
        ):

            print("6. Registriere auf Blockchain...")
            try:
                # Content Identifier bestimmen (IPFS bevorzugt, dann Arweave)
                cid = ipfs_hash if ipfs_hash else arweave_tx

                # ASI Semantic Embedding verwenden
                blockchain_embedding = asi_embedding_bytes

                # Tags aus exported_data extrahieren
                blockchain_tags = exported_data.get("tags", [])[:10]  # Max 10

                # Timestamp aus exported_data
                timestamp = int(
                    datetime.fromisoformat(
                        exported_data["timestamp"].replace("Z", "+00:00")
                    ).timestamp()
                )

                # Auf Blockchain registrieren
                blockchain_tx = self.blockchain_client.register_entry_on_chain(
                    cid=cid,
                    tags=blockchain_tags,
                    embedding=blockchain_embedding,
                    timestamp=timestamp,
                )

                print(f"✅ Blockchain-Registrierung erfolgreich: {blockchain_tx}")

                # Blockchain-Referenz in lokaler DB speichern
                self.local_db.update_storage_reference(
                    exported_data["hash"], "blockchain", blockchain_tx
                )

            except Exception as e:
                print(f"❌ Blockchain-Registrierung fehlgeschlagen: {e}")
                blockchain_tx = None

        # 7. Lokale Ausgabe und Hinweise
        print("7. Generiere Ausgabe und Hinweise...")
        local_file = self.output_generator.save_local_copy(exported_data)

        # 8. Erkenntnisse generieren
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

        # 9. Beispiel-Suche demonstrieren (falls Embeddings vorhanden)
        stats = self.asi_search_engine.get_cache_stats()
        if stats["total_embeddings"] > 0:
            print("\n🔍 Demonstration der semantischen Suche:")
            # Verwende die ersten paar Wörter der aktuellen Reflexion als Testquery
            test_query = " ".join(exported_data["content"].split()[:3])
            demo_results = self.search_asi_memories(test_query, 3)

        return {
            "reflection_id": reflection_id,
            "hash": exported_data["hash"],
            "local_file": local_file,
            "ipfs_hash": ipfs_hash,
            "arweave_tx": arweave_tx,
            "blockchain_tx": blockchain_tx,
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

    def search_asi_memories(self, query: str, num_results: int = 5):
        """
        Sucht in gespeicherten ASI-Reflektionen mit semantischer Suche

        Args:
            query: Suchtext
            num_results: Anzahl der Ergebnisse

        Returns:
            List: Suchergebnisse mit CID und Ähnlichkeitswerten
        """
        print(f"🔍 ASI Semantische Suche nach: '{query}'")

        try:
            results = self.asi_search_engine.search_ASI_memory(query, num_results)

            if not results:
                print("Keine Ergebnisse gefunden.")
                return []

            print(f"\n📋 {len(results)} Ergebnisse gefunden:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. CID: {result['cid']}")
                print(f"   Ähnlichkeit: {result['similarity']:.3f}")
                print(f"   Vorschau: {result['text_preview'][:100]}...")
                if result["timestamp"]:
                    print(f"   Zeitstempel: {result['timestamp']}")

            return results

        except Exception as e:
            print(f"❌ Fehler bei der Suche: {e}")
            return []

    def show_search_stats(self):
        """Zeigt Statistiken über den Embedding-Cache"""
        stats = self.asi_search_engine.get_cache_stats()

        print("\n📊 ASI Semantische Suche - Statistiken:")
        print(f"Gespeicherte Embeddings: {stats['total_embeddings']}")
        print(f"Cache-Datei existiert: {stats['cache_file_exists']}")
        print(f"Cache-Größe: {stats['cache_file_size']} Bytes")

        if stats["oldest_entry"]:
            print(f"Ältester Eintrag: {stats['oldest_entry']}")
        if stats["newest_entry"]:
            print(f"Neuester Eintrag: {stats['newest_entry']}")

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
            elif command == "search-asi" and len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                asi.search_asi_memories(query)
            elif command == "search-stats":
                asi.show_search_stats()
            elif command == "hrm" and len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                asi.hrm_demo(content)
            elif command == "hrm-test":
                asi.hrm_interactive_test()
            else:
                print("Verwendung:")
                print("  python main.py                    # Interaktiv")
                print("  python main.py stats              # Statistiken")
                print("  python main.py process <text>     # Reflexion")
                print("  python main.py search <query>     # Suche")
                print("  python main.py search-asi <query> # ASI Suche")
                print("  python main.py search-stats       # Suche Stats")
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


# Flask API für Web-Interface
if FLASK_AVAILABLE:
    app = Flask(__name__)
    asi_instance = None

    def get_asi_instance():
        global asi_instance
        if asi_instance is None:
            asi_instance = ASICore()
        return asi_instance

    # Import hybrid model modules for API endpoints
    try:
        import sys
        from pathlib import Path

        hybrid_model_path = str(Path(__file__).parent / "src" / "modules")
        if hybrid_model_path not in sys.path:
            sys.path.append(hybrid_model_path)

        # For Python API, we'll create simple wrapper classes
        class StateTrackerAPI:
            def get_state_history(self, key, days):
                # This would interface with the JS module via a bridge
                return []

            def calculate_streak(self, history):
                return 0

            def set_local_state(self, key, value, context):
                return {"key": key, "value": value, "context": context}

            def get_all_states_for_key(self, key):
                return []

        class InsightEngineAPI:
            def get_personal_insights(self, days):
                return []

        state_tracker = StateTrackerAPI()
        insight_engine = InsightEngineAPI()

        HYBRID_MODEL_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Hybrid Model nicht verfügbar: {e}")
        HYBRID_MODEL_AVAILABLE = False

    # Registriere cognitive insights Blueprint
    from src.modules.cognitive_insights import cognitive_insights_bp

    app.register_blueprint(cognitive_insights_bp)

    # Registriere Memory Token Blueprint
    app.register_blueprint(token_bp)
    print("✅ Memory Token API endpoints registered")

    # Registriere Wallet Blueprint
    try:
        from src.blockchain.wallet import wallet_bp

        app.register_blueprint(wallet_bp)
        print("✅ Wallet API endpoints registered")
    except ImportError as e:
        print(f"⚠️ Wallet Blueprint nicht verfügbar: {e}") @ app.route(
            "/api/health", methods=["GET"]
        )

    def health_check():
        """Gesundheitscheck für die API"""
        return jsonify(
            {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "features": [
                    "cognitive_insights",
                    "hybrid_model" if HYBRID_MODEL_AVAILABLE else None,
                ],
            }
        )

    @app.route("/api/states", methods=["GET"])
    def get_states():
        """Get user states from hybrid model"""
        if not HYBRID_MODEL_AVAILABLE:
            return jsonify({"error": "Hybrid model not available"}), 503

        days = int(request.args.get("days", 7))

        try:
            # Get states for all known state types
            state_types = [
                "walked",
                "focused",
                "slept_well",
                "meditated",
                "productive_morning",
                "exercised",
                "read",
                "journaled",
                "socialized",
                "creative_work",
            ]

            user_states = {}
            for state_type in state_types:
                history = state_tracker.get_state_history(state_type, days)
                if history:
                    streak_data = history[-7:] if len(history) >= 7 else history
                    user_states[state_type] = {
                        "history": history,
                        "streak": state_tracker.calculate_streak(streak_data),
                        "last_activity": (
                            history[-1]["timestamp"] if history else None
                        ),
                    }

            return jsonify(user_states)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/insights", methods=["GET"])
    def get_insights():
        """Get personal insights from hybrid model"""
        if not HYBRID_MODEL_AVAILABLE:
            return jsonify({"error": "Hybrid model not available"}), 503

        days = int(request.args.get("days", 7))

        try:
            insights = insight_engine.get_personal_insights(days)
            return jsonify(insights)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/states/aggregate", methods=["GET"])
    def get_aggregate_states():
        """Get aggregate state data for collective insights"""
        if not HYBRID_MODEL_AVAILABLE:
            return jsonify({"error": "Hybrid model not available"}), 503

        state_keys = request.args.get("keys", "").split(",")
        if not state_keys or state_keys == [""]:
            state_keys = [
                "walked",
                "focused",
                "slept_well",
                "meditated",
                "productive_morning",
            ]

        try:
            aggregate_data = {}
            default_states = [
                "walked",
                "focused",
                "slept_well",
                "meditated",
                "productive_morning",
            ]
            if not state_keys or state_keys == [""]:
                state_keys = default_states

            for key in state_keys:
                # Integrate with smart contract in real implementation
                history = state_tracker.get_all_states_for_key(key)
                if history:
                    total_entries = len(history)
                    positive_count = sum(
                        1 for entry in history if entry.get("value", 0) == 1
                    )
                    success_rate = (
                        (positive_count / total_entries * 100)
                        if total_entries > 0
                        else 0
                    )

                    last_updated = (
                        max(entry.get("timestamp", 0) for entry in history)
                        if history
                        else None
                    )

                    aggregate_data[key] = {
                        "total_entries": total_entries,
                        "positive_count": positive_count,
                        "success_rate": success_rate,
                        "last_updated": last_updated,
                    }
                else:
                    aggregate_data[key] = {
                        "total_entries": 0,
                        "positive_count": 0,
                        "success_rate": 0,
                        "last_updated": None,
                    }

            return jsonify(aggregate_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/states/log", methods=["POST"])
    def log_state():
        """Log a new state entry"""
        if not HYBRID_MODEL_AVAILABLE:
            return jsonify({"error": "Hybrid model not available"}), 503

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["key", "value"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            context = {
                "mood_before": data.get("moodBefore"),
                "mood_after": data.get("moodAfter"),
                "duration": data.get("duration"),
                "notes": data.get("notes"),
                "reflection_id": data.get("reflectionId"),
            }

            result = state_tracker.set_local_state(data["key"], data["value"], context)

            return jsonify(
                {
                    "success": True,
                    "state_entry": result,
                    "message": f"State '{data['key']}' logged successfully",
                }
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/recommendations", methods=["GET"])
    def get_recommendations():
        """Get proactive recommendations based on patterns"""
        if not HYBRID_MODEL_AVAILABLE:
            return jsonify({"error": "Hybrid model not available"}), 503

        try:
            recommendations = []

            # Generate time-based recommendations
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 10:
                recommendations.append(
                    {
                        "type": "time_based",
                        "message": "Guter Zeitpunkt für einen Spaziergang oder Meditation",
                        "actions": ["walked", "meditated"],
                        "confidence": 0.8,
                    }
                )
            elif 14 <= current_hour <= 16:
                recommendations.append(
                    {
                        "type": "time_based",
                        "message": "Nachmittag ist ideal für fokussierte Arbeit",
                        "actions": ["focused"],
                        "confidence": 0.7,
                    }
                )

            # Pattern-based recommendations from insights
            insights = insight_engine.get_personal_insights(7)
            for insight in insights:
                if (
                    insight.get("type") == "streak"
                    and insight.get("confidence", 0) > 0.7
                ):
                    recommendations.append(
                        {
                            "type": "pattern_based",
                            "message": f"Setze deine {insight.get('state_key', 'Aktivität')}-Serie fort!",
                            "actions": [insight.get("state_key")],
                            "confidence": insight.get("confidence", 0.5),
                        }
                    )

            return jsonify(recommendations)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def handle_command_line():
    """Erweiterte Kommandozeilen-Behandlung für Hybrid-Modell"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ASI Core - Hybrid-Modell mit Zustandsmanagement"
    )
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Kommandos")

    # Legacy add-Befehl
    add_parser = subparsers.add_parser("add", help="Fügt eine Reflexion hinzu")
    add_parser.add_argument("content", help="Reflexionsinhalt")
    add_parser.add_argument(
        "--tags", nargs="*", default=[], help="Tags für die Reflexion"
    )

    # Neuer add-state Befehl
    state_parser = subparsers.add_parser(
        "add-state", help="Fügt eine Zustandsreflexion hinzu"
    )
    state_parser.add_argument("content", help="Reflexionsinhalt")
    state_parser.add_argument(
        "--state", type=int, default=0, help="Zustandswert (0-255)"
    )
    state_parser.add_argument(
        "--tags", nargs="*", default=[], help="Tags für die Reflexion"
    )

    # Suchbefehle
    search_parser = subparsers.add_parser("search-state", help="Sucht nach Zustand")
    search_parser.add_argument("state", type=int, help="Zustandswert zum Suchen")

    # Statistiken
    stats_parser = subparsers.add_parser("stats", help="Zeigt Zustandsstatistiken")

    # Export
    export_parser = subparsers.add_parser("export", help="Exportiert Zustandsdaten")
    export_parser.add_argument("--filename", help="Ausgabedatei (optional)")

    # Zustände auflisten
    list_states_parser = subparsers.add_parser(
        "list-states", help="Listet verfügbare Zustände auf"
    )

    args = parser.parse_args()

    if not args.command:
        print("🤖 ASI Core - Hybrid-Modell")
        print("Verwende --help für verfügbare Kommandos")
        return

    # ASI System initialisieren
    import asyncio

    from src.asi_core import ASICore

    asi = ASICore()

    # Existierende Reflexionen laden
    asi.load_reflections_from_directory()

    try:
        if args.command == "add":
            # Legacy-Befehl mit automatischer Zustandserkennung
            result = asi.add_reflection(args.content, args.tags)
            print(f"📝 Reflexion hinzugefügt mit automatischem Zustand")

        elif args.command == "add-state":
            # Neuer Zustandsbefehl
            result = asyncio.run(
                asi.add_state_reflection(args.content, args.state, args.tags)
            )
            print(f"📝 Zustandsreflexion hinzugefügt: Zustand {args.state}")

        elif args.command == "search-state":
            results = asi.search_by_state(args.state)
            print(f"\n🔍 Suchergebnisse für Zustand {args.state}:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['reflection_text'][:100]}...")
                print(f"   Tags: {', '.join(result['tags'])}")
                print(f"   Zeit: {result['timestamp']}")
                print()

        elif args.command == "stats":
            asi.show_state_statistics()

        elif args.command == "export":
            asi.export_state_data(args.filename)

        elif args.command == "list-states":
            states = asi.get_available_states()
            print("\n📋 Verfügbare Zustände:")
            for state_id, info in states.items():
                print(f"{state_id}: {info['name']} - {info['description']}")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    # Nur starten wenn direkt ausgeführt
    if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "serve":
        print("Starte Flask API Server...")
        debug_flag = os.getenv("ASI_MAIN_DEBUG", "true").lower()
        debug_enabled = debug_flag in {"1", "true", "yes"}
        default_host = "127.0.0.1" if not debug_enabled else "0.0.0.0"
        host = os.getenv("ASI_MAIN_HOST", default_host)
        port = int(os.getenv("ASI_MAIN_PORT", "5000"))
        app.run(host=host, port=port, debug=debug_enabled)
    elif __name__ == "__main__" and len(sys.argv) > 1:
        handle_command_line()
    elif __name__ == "__main__":
        print("🤖 ASI Core - Hybrid-Modell")
        print("Verwende 'python main.py --help' für verfügbare Kommandos")
        print("Verwende 'python main.py serve' für den Flask-Server")
