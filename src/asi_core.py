#!/usr/bin/env python3
"""
ASI-Core: Artificial Self-Intelligence System
Erweiterte Version mit Hybrid-Modell, State Management und Agent-Integration
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent.parent))

try:
    from asi_core.blockchain import ASIBlockchainClient, ASIBlockchainError
    from asi_core.state_management import ASIStateManager, suggest_state_from_text
    from asi_core.agent_manager import ASIAgentManager, create_agent_manager_from_config
except ImportError as e:
    print(f"⚠️ Import-Fehler: {e}")
    print("Versuche lokale Imports...")
    
    # Fallback: Direkte Pfad-Imports
    asi_core_path = Path(__file__).parent.parent / "asi_core"
    sys.path.insert(0, str(asi_core_path.parent))
    
    from asi_core.blockchain import ASIBlockchainClient, ASIBlockchainError
    from asi_core.state_management import ASIStateManager, suggest_state_from_text
    from asi_core.agent_manager import ASIAgentManager, create_agent_manager_from_config


class ASICore:
    """
    Hauptklasse für das ASI System mit Hybrid-Modell, State Management und Agent-Integration
    """

    def __init__(self, config_path="config/settings.json"):
        self.config = self.load_config(config_path)
        self.setup_directories()

        # State Management initialisieren
        self.state_manager = ASIStateManager()

        # Blockchain Client (optional)
        self.blockchain_client = None
        self._initialize_blockchain()

        # Agent Manager initialisieren
        self.agent_manager = None
        self._initialize_agent_system()

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

    def _initialize_agent_system(self):
        """Initialisiert das Agent-System mit Blockchain-Integration"""
        try:
            self.agent_manager = ASIAgentManager(
                data_dir="data/agents",
                blockchain_client=self.blockchain_client
            )
            
            # Haupt-ASI-Agent registrieren falls noch nicht vorhanden
            asi_agents = [agent for agent in self.agent_manager.list_agents() if agent.name == "ASI-Core"]
            
            if not asi_agents:
                agent_id = self.agent_manager.register_agent(
                    name="ASI-Core",
                    capabilities=[
                        "reflection", "state_management", "blockchain_integration",
                        "semantic_search", "pattern_recognition", "self_improvement"
                    ],
                    learning_goals=[
                        "improve_reflection_quality", "optimize_state_transitions",
                        "enhance_pattern_detection", "increase_prediction_accuracy"
                    ]
                )
                self.main_agent_id = agent_id
                print(f"🤖 Haupt-ASI-Agent registriert: {agent_id}")
            else:
                self.main_agent_id = asi_agents[0].agent_id
                print(f"🤖 Haupt-ASI-Agent geladen: {self.main_agent_id}")
                
        except Exception as e:
            print(f"⚠️ Agent-System-Initialisierung fehlgeschlagen: {e}")
            self.agent_manager = None
            self.main_agent_id = None

    def add_reflection(self, content, tags=None, auto_detect_state=True):
        """
        Fügt eine neue Reflexion hinzu mit automatischer Zustandserkennung

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

    def add_state_reflection(
        self, reflection_text: str, state_value: int, tags: Optional[List[str]] = None
    ):
        """
        Fügt eine Reflexion mit spezifischem Zustandswert hinzu (Agent-integriert).

        Args:
            reflection_text (str): Der Reflexionstext.
            state_value (int): Der Zustandswert (0-100).
            tags (Optional[List[str]]): Optionale Tags für die Reflexion.
        """
        timestamp = datetime.now().isoformat()
        reflection_id = f"refl_{len(self.reflections) + 1}"

        # Dummy-Embedding erstellen
        embedding_bytes = self._create_dummy_embedding(reflection_text)

        reflection = {
            "id": reflection_id,
            "text": reflection_text,
            "state_value": state_value,
            "tags": tags or [],
            "timestamp": timestamp,
            "embedding": embedding_bytes,
        }

        self.reflections.append(reflection)
        print(f"� Reflexion hinzugefügt (Zustand: {state_value}): {reflection_text[:50]}...")

        # Agent-Aktion protokollieren
        if self.agent_manager and self.main_agent_id:
            try:
                confidence = min(0.8 + (state_value / 1000), 1.0)  # Höhere States = höhere Confidence
                action_data = {
                    "reflection_length": len(reflection_text),
                    "state_value": state_value,
                    "tags_count": len(tags) if tags else 0,
                    "has_embedding": bool(embedding_bytes)
                }
                
                self.agent_manager.record_agent_action(
                    agent_id=self.main_agent_id,
                    action_type="state_reflection",
                    result_data=action_data,
                    confidence=confidence
                )
                print(f"🤖 Agent-Aktion protokolliert: state_reflection (Confidence: {confidence:.3f})")
                
            except Exception as e:
                print(f"⚠️ Agent-Protokollierung fehlgeschlagen: {e}")

        # Hybrid-Modell: Blockchain-Registrierung bei hohen Zustandswerten
        if (
            self.blockchain_client
            and self.blockchain_client.is_connected()
            and state_value >= 70  # Nur wichtige Reflexionen on-chain
        ):
            try:
                tx_hash = self.blockchain_client.register_hybrid_entry_on_chain(
                    cid=f"state_reflection_{reflection_id}",
                    tags=tags or [f"state:{state_value}"],
                    embedding=embedding_bytes,
                    state_value=state_value,
                    timestamp=int(datetime.now().timestamp()),
                )
                print(f"🔗 Blockchain-Eintrag erstellt: {tx_hash}")
                reflection["blockchain_tx"] = tx_hash
                
            except ASIBlockchainError as e:
                print(f"⚠️ Blockchain-Registrierung fehlgeschlagen: {e}")

        # State Management aktualisieren
        self.state_manager.update_statistics(state_value)

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

    # =============================================================================
    # Agent-spezifische Methoden
    # =============================================================================

    def get_agent_stats(self) -> Dict:
        """Ruft Statistiken über das Agent-System ab."""
        if not self.agent_manager:
            return {"error": "Agent-System nicht initialisiert"}
        
        return self.agent_manager.get_agent_statistics()

    def trigger_agent_learning(self, topic: str, learning_data: Dict = None) -> Optional[str]:
        """
        Löst einen Lernprozess für den Haupt-ASI-Agent aus.
        
        Args:
            topic (str): Lernthema.
            learning_data (Dict, optional): Zusätzliche Lerndaten.
        
        Returns:
            Optional[str]: Blockchain-Transaction-Hash oder None.
        """
        if not self.agent_manager or not self.main_agent_id:
            print("⚠️ Agent-System nicht verfügbar")
            return None
        
        # Lernfortschritt basierend auf aktuellen Reflexionen berechnen
        recent_reflections = self.reflections[-10:]  # Letzte 10 Reflexionen
        avg_state = sum(r.get("state_value", 50) for r in recent_reflections) / max(len(recent_reflections), 1)
        
        # Improvement Score basierend auf State-Trend
        improvement_score = min(avg_state / 100.0, 1.0)
        
        learning_data = learning_data or {}
        learning_data.update({
            "recent_reflections": len(recent_reflections),
            "avg_state_value": avg_state,
            "total_reflections": len(self.reflections)
        })
        
        return self.agent_manager.record_agent_learning(
            agent_id=self.main_agent_id,
            topic=topic,
            improvement_score=improvement_score,
            learning_data=learning_data
        )

    def create_sub_agent(self, name: str, specialization: List[str]) -> Optional[str]:
        """
        Erstellt einen spezialisierten Sub-Agenten.
        
        Args:
            name (str): Name des Sub-Agenten.
            specialization (List[str]): Spezialisierungsbereiche.
        
        Returns:
            Optional[str]: Agent-ID oder None bei Fehler.
        """
        if not self.agent_manager:
            print("⚠️ Agent-System nicht verfügbar")
            return None
        
        try:
            agent_id = self.agent_manager.register_agent(
                name=f"ASI-{name}",
                capabilities=specialization + ["asi_integration"],
                learning_goals=[f"improve_{spec}" for spec in specialization],
                collaboration_preferences={"parent_agent": self.main_agent_id}
            )
            
            print(f"🤖 Sub-Agent erstellt: {name} (ID: {agent_id})")
            return agent_id
            
        except Exception as e:
            print(f"⚠️ Sub-Agent-Erstellung fehlgeschlagen: {e}")
            return None

    def initiate_agent_collaboration(self, agents: List[str], task: str) -> Optional[str]:
        """
        Startet eine Kollaboration zwischen Agenten.
        
        Args:
            agents (List[str]): Liste der Agent-IDs.
            task (str): Kollaborationsaufgabe.
        
        Returns:
            Optional[str]: Kollaborations-ID oder None.
        """
        if not self.agent_manager:
            print("⚠️ Agent-System nicht verfügbar")
            return None
        
        # Haupt-Agent zur Kollaboration hinzufügen falls nicht enthalten
        if self.main_agent_id and self.main_agent_id not in agents:
            agents = [self.main_agent_id] + agents
        
        try:
            collab_id = self.agent_manager.initiate_collaboration(
                agent_ids=agents,
                collaboration_type=task,
                goals=[f"complete_{task}", "improve_collaboration", "share_knowledge"]
            )
            
            print(f"🤝 Kollaboration gestartet: {task} (ID: {collab_id})")
            return collab_id
            
        except Exception as e:
            print(f"⚠️ Kollaboration fehlgeschlagen: {e}")
            return None

    def show_agent_network(self):
        """Zeigt das gesamte Agent-Netzwerk an."""
        if not self.agent_manager:
            print("⚠️ Agent-System nicht verfügbar")
            return
        
        print("\n🕸️ Agent-Netzwerk:")
        print("=" * 18)
        
        agents = self.agent_manager.list_agents()
        
        for agent in agents:
            status = "🟢" if agent.agent_id == self.main_agent_id else "🔵"
            role = "MAIN" if agent.agent_id == self.main_agent_id else "SUB"
            
            print(f"{status} {agent.name} ({role})")
            print(f"   📋 {', '.join(agent.capabilities[:3])}{'...' if len(agent.capabilities) > 3 else ''}")
            print(f"   ⚡ {agent.total_actions} Aktionen, 💯 {agent.avg_confidence:.3f} Confidence")
        
        # Netzwerk-Statistiken
        stats = self.agent_manager.get_agent_statistics()
        print(f"\n📊 Netzwerk: {stats['total_agents']} Agenten, {stats['total_actions']} Aktionen, {stats['active_collaborations']} Kollaborationen")


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
