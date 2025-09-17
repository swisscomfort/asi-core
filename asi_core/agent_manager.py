"""ASI Agent Manager - Autonome Agent-Verwaltung"""
import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path

from .blockchain import ASIBlockchainClient, ASIBlockchainError, create_dummy_embedding

@dataclass
class AgentProfile:
    """Agent-Profil für autonome KI-Agenten"""
    agent_id: str
    name: str
    version: str
    capabilities: List[str]
    learning_goals: List[str]
    collaboration_preferences: Dict[str, Any]
    blockchain_address: Optional[str] = None
    created_at: str = ""
    last_active: str = ""
    total_actions: int = 0
    avg_confidence: float = 0.0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.last_active:
            self.last_active = self.created_at

class ASIAgentManager:
    """
    Manager für autonome ASI-Agenten mit Blockchain-Integration.
    
    Verwaltet Agent-Profile, Aktionen und Kollaborationen.
    """
    
    def __init__(self, data_dir: str = "data/agents", blockchain_client: Optional[ASIBlockchainClient] = None):
        """
        Initialisiert den Agent-Manager.
        
        Args:
            data_dir (str): Verzeichnis für Agent-Daten.
            blockchain_client (Optional[ASIBlockchainClient]): Blockchain-Client für On-Chain-Operationen.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.blockchain_client = blockchain_client
        self.agents: Dict[str, AgentProfile] = {}
        self.active_collaborations: Dict[str, Dict] = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Agent-Daten laden
        self._load_agents()
    
    def _load_agents(self) -> None:
        """Lädt alle gespeicherten Agent-Profile."""
        agents_file = self.data_dir / "agents.json"
        
        if agents_file.exists():
            try:
                with open(agents_file, 'r', encoding='utf-8') as f:
                    agents_data = json.load(f)
                    
                for agent_id, agent_data in agents_data.items():
                    self.agents[agent_id] = AgentProfile(**agent_data)
                    
                self.logger.info(f"Geladen: {len(self.agents)} Agent-Profile")
                
            except Exception as e:
                self.logger.error(f"Fehler beim Laden der Agent-Profile: {e}")
    
    def _save_agents(self) -> None:
        """Speichert alle Agent-Profile."""
        agents_file = self.data_dir / "agents.json"
        
        try:
            agents_data = {
                agent_id: asdict(profile) 
                for agent_id, profile in self.agents.items()
            }
            
            with open(agents_file, 'w', encoding='utf-8') as f:
                json.dump(agents_data, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Gespeichert: {len(self.agents)} Agent-Profile")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Agent-Profile: {e}")
    
    def register_agent(self, name: str, capabilities: List[str], learning_goals: List[str] = None, **kwargs) -> str:
        """
        Registriert einen neuen autonomen Agenten.
        
        Args:
            name (str): Name des Agenten.
            capabilities (List[str]): Liste der Agent-Fähigkeiten.
            learning_goals (List[str], optional): Lernziele des Agenten.
            **kwargs: Zusätzliche Agent-Parameter.
        
        Returns:
            str: Die generierte Agent-ID.
        """
        agent_id = str(uuid.uuid4())[:8]  # Kurze, eindeutige ID
        
        profile = AgentProfile(
            agent_id=agent_id,
            name=name,
            version="1.0.0",
            capabilities=capabilities,
            learning_goals=learning_goals or [],
            collaboration_preferences=kwargs.get('collaboration_preferences', {}),
            blockchain_address=kwargs.get('blockchain_address')
        )
        
        self.agents[agent_id] = profile
        self._save_agents()
        
        self.logger.info(f"Agent registriert: {name} (ID: {agent_id})")
        
        # Optional: Auf Blockchain registrieren
        if self.blockchain_client and self.blockchain_client.is_connected():
            try:
                registration_data = {
                    "action": "register",
                    "name": name,
                    "capabilities": capabilities,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                embedding = create_dummy_embedding(f"agent_registration:{name}:{agent_id}")
                result_cid = f"agent_reg_{agent_id}_{int(datetime.now().timestamp())}"
                
                tx_hash = self.blockchain_client.register_agent_action(
                    agent_id=agent_id,
                    action_type="register",
                    result_cid=result_cid,
                    confidence=1.0
                )
                
                self.logger.info(f"Agent {agent_id} auf Blockchain registriert: {tx_hash}")
                
            except ASIBlockchainError as e:
                self.logger.warning(f"Blockchain-Registrierung für Agent {agent_id} fehlgeschlagen: {e}")
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """
        Ruft ein Agent-Profil ab.
        
        Args:
            agent_id (str): Die Agent-ID.
        
        Returns:
            Optional[AgentProfile]: Das Agent-Profil oder None.
        """
        return self.agents.get(agent_id)
    
    def list_agents(self, capabilities_filter: List[str] = None) -> List[AgentProfile]:
        """
        Listet alle Agenten auf, optional gefiltert nach Fähigkeiten.
        
        Args:
            capabilities_filter (List[str], optional): Filter nach Fähigkeiten.
        
        Returns:
            List[AgentProfile]: Liste der Agent-Profile.
        """
        agents = list(self.agents.values())
        
        if capabilities_filter:
            agents = [
                agent for agent in agents 
                if any(cap in agent.capabilities for cap in capabilities_filter)
            ]
        
        return sorted(agents, key=lambda x: x.last_active, reverse=True)
    
    def record_agent_action(self, agent_id: str, action_type: str, result_data: Dict, confidence: float = 0.8) -> Optional[str]:
        """
        Zeichnet eine Agent-Aktion auf und registriert sie optional auf der Blockchain.
        
        Args:
            agent_id (str): Die Agent-ID.
            action_type (str): Typ der Aktion.
            result_data (Dict): Ergebnisdaten der Aktion.
            confidence (float): Vertrauenswert der Aktion.
        
        Returns:
            Optional[str]: Blockchain-Transaction-Hash oder None.
        """
        if agent_id not in self.agents:
            self.logger.error(f"Unbekannte Agent-ID: {agent_id}")
            return None
        
        # Agent-Profil aktualisieren
        agent = self.agents[agent_id]
        agent.last_active = datetime.now(timezone.utc).isoformat()
        agent.total_actions += 1
        agent.avg_confidence = (agent.avg_confidence * (agent.total_actions - 1) + confidence) / agent.total_actions
        
        self._save_agents()
        
        # Blockchain-Registrierung
        tx_hash = None
        if self.blockchain_client and self.blockchain_client.is_connected():
            try:
                result_cid = f"action_{agent_id}_{action_type}_{int(datetime.now().timestamp())}"
                
                tx_hash = self.blockchain_client.register_agent_action(
                    agent_id=agent_id,
                    action_type=action_type,
                    result_cid=result_cid,
                    confidence=confidence
                )
                
                self.logger.info(f"Agent-Aktion registriert: {agent_id} -> {action_type} (TX: {tx_hash})")
                
            except ASIBlockchainError as e:
                self.logger.warning(f"Blockchain-Registrierung der Aktion fehlgeschlagen: {e}")
        
        return tx_hash
    
    def record_agent_learning(self, agent_id: str, topic: str, improvement_score: float, learning_data: Dict) -> Optional[str]:
        """
        Zeichnet einen Lernprozess eines Agenten auf.
        
        Args:
            agent_id (str): Die Agent-ID.
            topic (str): Lernthema.
            improvement_score (float): Verbesserungswert (0.0 - 1.0).
            learning_data (Dict): Detaillierte Lerndaten.
        
        Returns:
            Optional[str]: Blockchain-Transaction-Hash oder None.
        """
        if agent_id not in self.agents:
            self.logger.error(f"Unbekannte Agent-ID: {agent_id}")
            return None
        
        # Lern-Embedding erstellen
        learning_content = f"{topic}:{improvement_score}:{json.dumps(learning_data, sort_keys=True)}"
        embedding = create_dummy_embedding(learning_content)
        
        # Lerndaten strukturieren
        structured_learning_data = {
            "topic": topic,
            "improvement_score": improvement_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **learning_data
        }
        
        # Blockchain-Registrierung
        tx_hash = None
        if self.blockchain_client and self.blockchain_client.is_connected():
            try:
                tx_hash = self.blockchain_client.register_agent_learning(
                    agent_id=agent_id,
                    learning_data=structured_learning_data,
                    embedding=embedding
                )
                
                self.logger.info(f"Agent-Lernprozess registriert: {agent_id} -> {topic} (TX: {tx_hash})")
                
            except ASIBlockchainError as e:
                self.logger.warning(f"Blockchain-Registrierung des Lernprozesses fehlgeschlagen: {e}")
        
        return tx_hash
    
    def initiate_collaboration(self, agent_ids: List[str], collaboration_type: str, goals: List[str]) -> str:
        """
        Startet eine Kollaboration zwischen mehreren Agenten.
        
        Args:
            agent_ids (List[str]): Liste der beteiligten Agent-IDs.
            collaboration_type (str): Art der Zusammenarbeit.
            goals (List[str]): Kollaborationsziele.
        
        Returns:
            str: Kollaborations-ID.
        """
        if len(agent_ids) < 2:
            raise ValueError("Kollaboration benötigt mindestens 2 Agenten.")
        
        # Validierung: Alle Agenten müssen existieren
        missing_agents = [aid for aid in agent_ids if aid not in self.agents]
        if missing_agents:
            raise ValueError(f"Unbekannte Agent-IDs: {missing_agents}")
        
        collab_id = str(uuid.uuid4())[:12]
        
        collaboration = {
            "id": collab_id,
            "agents": agent_ids,
            "type": collaboration_type,
            "goals": goals,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "actions": []
        }
        
        self.active_collaborations[collab_id] = collaboration
        
        # Blockchain-Registrierung
        if self.blockchain_client and self.blockchain_client.is_connected():
            try:
                result_cid = f"collaboration_{collab_id}_{int(datetime.now().timestamp())}"
                
                tx_hash = self.blockchain_client.register_agent_collaboration(
                    agents=agent_ids,
                    collaboration_type=collaboration_type,
                    result_cid=result_cid
                )
                
                collaboration["blockchain_tx"] = tx_hash
                self.logger.info(f"Kollaboration gestartet: {collab_id} mit {len(agent_ids)} Agenten (TX: {tx_hash})")
                
            except ASIBlockchainError as e:
                self.logger.warning(f"Blockchain-Registrierung der Kollaboration fehlgeschlagen: {e}")
        
        return collab_id
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Ruft Statistiken über alle verwalteten Agenten ab.
        
        Returns:
            Dict[str, Any]: Agent-Statistiken.
        """
        if not self.agents:
            return {
                "total_agents": 0,
                "active_agents": 0,
                "total_actions": 0,
                "avg_confidence": 0.0,
                "most_common_capabilities": [],
                "active_collaborations": 0
            }
        
        total_actions = sum(agent.total_actions for agent in self.agents.values())
        total_confidence = sum(agent.avg_confidence * agent.total_actions for agent in self.agents.values())
        avg_confidence = total_confidence / max(total_actions, 1)
        
        # Häufigste Fähigkeiten
        all_capabilities = []
        for agent in self.agents.values():
            all_capabilities.extend(agent.capabilities)
        
        capability_counts = {}
        for cap in all_capabilities:
            capability_counts[cap] = capability_counts.get(cap, 0) + 1
        
        most_common_capabilities = sorted(
            capability_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Aktive Agenten (letzte 24h)
        now = datetime.now(timezone.utc)
        active_agents = 0
        for agent in self.agents.values():
            try:
                last_active = datetime.fromisoformat(agent.last_active.replace('Z', '+00:00'))
                if (now - last_active).total_seconds() < 24 * 3600:
                    active_agents += 1
            except:
                pass
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "total_actions": total_actions,
            "avg_confidence": round(avg_confidence, 3),
            "most_common_capabilities": most_common_capabilities,
            "active_collaborations": len(self.active_collaborations)
        }
    
    def get_blockchain_network_stats(self) -> Dict[str, Any]:
        """
        Ruft Blockchain-Netzwerk-Statistiken ab.
        
        Returns:
            Dict[str, Any]: Blockchain-Netzwerk-Statistiken.
        """
        if not self.blockchain_client or not self.blockchain_client.is_connected():
            return {"error": "Keine Blockchain-Verbindung"}
        
        try:
            return self.blockchain_client.get_agent_network_stats()
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Blockchain-Statistiken: {e}")
            return {"error": str(e)}
    
    def cleanup_inactive_agents(self, days_threshold: int = 30) -> int:
        """
        Entfernt inaktive Agenten aus der Verwaltung.
        
        Args:
            days_threshold (int): Schwellwert für Inaktivität in Tagen.
        
        Returns:
            int: Anzahl der entfernten Agenten.
        """
        now = datetime.now(timezone.utc)
        inactive_agents = []
        
        for agent_id, agent in self.agents.items():
            try:
                last_active = datetime.fromisoformat(agent.last_active.replace('Z', '+00:00'))
                if (now - last_active).total_seconds() > days_threshold * 24 * 3600:
                    inactive_agents.append(agent_id)
            except:
                # Fehlerhafte Zeitstempel als inaktiv behandeln
                inactive_agents.append(agent_id)
        
        for agent_id in inactive_agents:
            del self.agents[agent_id]
            self.logger.info(f"Inaktiver Agent entfernt: {agent_id}")
        
        if inactive_agents:
            self._save_agents()
        
        return len(inactive_agents)

def create_agent_manager_from_config(blockchain_client: Optional[ASIBlockchainClient] = None) -> ASIAgentManager:
    """
    Erstellt einen Agent-Manager aus Umgebungsvariablen.
    
    Args:
        blockchain_client (Optional[ASIBlockchainClient]): Optional Blockchain-Client.
    
    Returns:
        ASIAgentManager: Konfigurierter Agent-Manager.
    """
    data_dir = os.getenv("AGENTS_DATA_DIR", "data/agents")
    
    return ASIAgentManager(
        data_dir=data_dir,
        blockchain_client=blockchain_client
    )
