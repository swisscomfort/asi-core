"""ASI Blockchain Client - Minimale Implementation"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

try:
    from web3 import Web3
    from web3.exceptions import Web3Exception, TransactionNotFound
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ASIBlockchainError(Exception):
    pass

class ASIBlockchainClient:
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        """
        Initialisiert den ASI Blockchain Client.

        Args:
            rpc_url (str): Die URL des Blockchain RPC-Endpunkts.
            private_key (str): Der private Schlüssel für Transaktionen.
            contract_address (str): Die Adresse des ASI Smart Contracts.
        
        Raises:
            ASIBlockchainError: Wenn Web3 nicht verfügbar ist oder die Initialisierung fehlschlägt.
        """
        if not WEB3_AVAILABLE:
            raise ASIBlockchainError("Web3-Bibliothek ist nicht verfügbar. Installieren Sie web3.py.")
        
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.web3 = None
        self.contract = None
        self.account = None
        self.abi = self._load_contract_abi()
        self.connected = self._connect()

    def _load_contract_abi(self) -> List[Dict]:
        """
        Lädt die ABI des ASI Smart Contracts aus der JSON-Datei.
        
        Returns:
            List[Dict]: Die ABI-Definition des Contracts.
            
        Raises:
            ASIBlockchainError: Wenn die ABI-Datei nicht gefunden oder gelesen werden kann.
        """
        try:
            # Pfad relativ zur aktuellen Datei bestimmen
            current_dir = Path(__file__).parent
            abi_path = current_dir.parent / "contracts" / "ASI.json"
            
            if not abi_path.exists():
                logging.warning(f"ABI-Datei nicht gefunden unter {abi_path}. Verwende Standard-ABI.")
                # Standard-ABI für die registerEntry Funktion
                return [
                    {
                        "inputs": [
                            {"name": "cid", "type": "string"},
                            {"name": "tags", "type": "string[]"},
                            {"name": "embedding", "type": "bytes"},
                            {"name": "timestamp", "type": "uint256"}
                        ],
                        "name": "registerEntry",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ]
            
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
                return contract_data.get('abi', [])
                
        except Exception as e:
            logging.error(f"Fehler beim Laden der Contract-ABI: {e}")
            raise ASIBlockchainError(f"ABI konnte nicht geladen werden: {e}") from e

    def _connect(self) -> bool:
        """
        Stellt eine Verbindung zum RPC-Endpunkt her und initialisiert Web3-Instanzen.
        
        Returns:
            bool: True wenn die Verbindung erfolgreich ist, sonst False.
        """
        try:
            logging.info(f"Verbinde mit RPC-Endpunkt unter {self.rpc_url}...")
            
            # Web3-Instanz erstellen
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            # Verbindung testen
            if not self.web3.is_connected():
                logging.error("Verbindung zum RPC-Endpunkt fehlgeschlagen.")
                return False
            
            # Account aus privatem Schlüssel erstellen
            self.account = Account.from_key(self.private_key)
            logging.info(f"Account-Adresse: {self.account.address}")
            
            # Contract-Instanz erstellen
            self.contract = self.web3.eth.contract(
                address=self.contract_address,
                abi=self.abi
            )
            
            # Chain-ID für Polygon Mumbai
            chain_id = self.web3.eth.chain_id
            logging.info(f"Verbunden mit Chain ID: {chain_id}")
            
            if chain_id != 80001:  # Mumbai Testnet Chain ID
                logging.warning(f"Unerwartete Chain ID: {chain_id}. Erwartet: 80001 (Mumbai)")
            
            logging.info("Verbindung erfolgreich hergestellt.")
            return True
            
        except Exception as e:
            logging.error(f"Fehler bei der Verbindung: {e}")
            return False

    def _connect(self) -> bool:
        """Stellt eine Verbindung zum RPC-Endpunkt her."""
        logging.info(f"Verbinde mit RPC-Endpunkt unter {self.rpc_url}...")
        # In einer echten Implementierung würde hier die Verbindung geprüft.
        # Für diese Mock-Implementierung geben wir einfach True zurück.
        self.connected = True
        logging.info("Verbindung erfolgreich hergestellt.")
        return self.connected

    def is_connected(self) -> bool:
        """
        Prüft, ob die Verbindung zum RPC-Endpunkt aktiv ist.

        Returns:
            bool: True, wenn eine Verbindung besteht, sonst False.
        """
        if not self.web3:
            return False
        
        try:
            return self.web3.is_connected()
        except Exception as e:
            logging.error(f"Fehler bei der Verbindungsprüfung: {e}")
            return False

    def register_entry_on_chain(self, cid: str, tags: List[str], embedding: bytes, timestamp: int) -> str:
        """
        Registriert einen neuen Eintrag auf der Blockchain.

        Args:
            cid (str): Die Content ID des Eintrags.
            tags (List[str]): Eine Liste von Tags für den Eintrag (max. 10).
            embedding (bytes): Das Vektor-Embedding des Eintrags (128 bytes).
            timestamp (int): Der Zeitstempel des Eintrags.

        Returns:
            str: Der Transaktions-Hash des erfolgreichen Eintrags.

        Raises:
            ASIBlockchainError: Wenn keine Verbindung zur Blockchain besteht oder die Transaktion fehlschlägt.
        """
        if not self.is_connected():
            raise ASIBlockchainError("Keine Verbindung zur Blockchain. Transaktion kann nicht gesendet werden.")

        # Validierung der Eingabeparameter
        if len(tags) > 10:
            raise ASIBlockchainError("Maximal 10 Tags sind erlaubt.")
        
        if len(embedding) != 128:
            raise ASIBlockchainError("Embedding muss genau 128 bytes lang sein.")

        try:
            logging.info(f"Registriere Eintrag für CID {cid[:10]}... auf der Blockchain.")
            
            # Gas-Preis und Nonce abrufen
            gas_price = self.web3.eth.gas_price
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            logging.info(f"Gas-Preis: {gas_price}, Nonce: {nonce}")
            
            # Contract-Funktion aufrufen
            function = self.contract.functions.registerEntry(cid, tags, embedding, timestamp)
            
            # Gas-Limit schätzen
            try:
                gas_limit = function.estimate_gas({'from': self.account.address})
                logging.info(f"Geschätztes Gas-Limit: {gas_limit}")
            except Exception as e:
                logging.warning(f"Gas-Schätzung fehlgeschlagen: {e}. Verwende Standard-Limit.")
                gas_limit = 500000
            
            # Transaktion erstellen
            transaction = function.build_transaction({
                'chainId': self.web3.eth.chain_id,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'from': self.account.address
            })
            
            logging.info(f"Transaktion erstellt: {transaction}")
            
            # Transaktion signieren
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Transaktion senden
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            logging.info(f"Transaktion gesendet. Hash: {tx_hash_hex}")
            
            # Auf Bestätigung warten (optional, kann für bessere Performance entfernt werden)
            try:
                receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                if receipt.status == 1:
                    logging.info(f"Transaktion erfolgreich bestätigt in Block {receipt.blockNumber}")
                else:
                    logging.error(f"Transaktion fehlgeschlagen. Receipt: {receipt}")
                    raise ASIBlockchainError("Transaktion auf der Blockchain fehlgeschlagen.")
            except Exception as e:
                logging.warning(f"Fehler beim Warten auf Bestätigung: {e}. Transaktion wurde gesendet.")
            
            logging.info(f"Eintrag erfolgreich registriert. Transaktions-Hash: {tx_hash_hex}")
            return tx_hash_hex
            
        except ASIBlockchainError:
            raise
        except Exception as e:
            logging.error(f"Unerwarteter Fehler bei der Registrierung des Eintrags für CID {cid[:10]}: {e}")
            raise ASIBlockchainError(f"Transaktion fehlgeschlagen: {e}") from e

    def register_hybrid_entry_on_chain(self, cid: str, tags: List[str], embedding: bytes, state_value: int, timestamp: int) -> str:
        """
        Registriert einen hybriden Eintrag (On-Chain-Daten und Off-Chain-State).

        Args:
            cid (str): Die Content ID des Eintrags.
            tags (List[str]): Eine Liste von Tags für den Eintrag.
            embedding (bytes): Das Vektor-Embedding des Eintrags.
            state_value (int): Der Zustandswert, der mit dem Eintrag verknüpft ist.
            timestamp (int): Der Zeitstempel des Eintrags.

        Returns:
            str: Der Transaktions-Hash des erfolgreichen Eintrags.
        """
        # Diese Methode ruft die Hauptregistrierungsmethode auf.
        # In einer echten Implementierung könnte hier eine andere Smart-Contract-Funktion aufgerufen werden.
        return self.register_entry_on_chain(cid, tags, embedding, timestamp)

    def get_transaction_status(self, tx_hash: str) -> str:
        """
        Fragt den Status einer bestimmten Transaktion ab.

        Args:
            tx_hash (str): Der zu prüfende Transaktions-Hash.

        Returns:
            str: Der Status der Transaktion ('pending', 'success', 'failed').
        """
        if not self.is_connected():
            logging.warning("Keine Verbindung zur Blockchain. Kann Transaktionsstatus nicht abrufen.")
            return "failed"

        try:
            logging.info(f"Frage Status für Transaktion {tx_hash[:10]}... ab.")
            
            # Transaktion Receipt abrufen
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if receipt is None:
                # Transaktion noch im Mempool
                return "pending"
            elif receipt.status == 1:
                logging.info(f"Transaktion {tx_hash[:10]}... erfolgreich in Block {receipt.blockNumber}")
                return "success"
            else:
                logging.error(f"Transaktion {tx_hash[:10]}... fehlgeschlagen")
                return "failed"
                
        except TransactionNotFound:
            logging.warning(f"Transaktion {tx_hash[:10]}... nicht gefunden")
            return "failed"
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des Transaktionsstatus für {tx_hash[:10]}: {e}")
            return "failed"

    def get_entries_by_state(self, state_value: int) -> List[Dict]:
        """
        Ruft alle Einträge mit einem bestimmten Zustandswert von der Blockchain ab.

        Args:
            state_value (int): Der abzufragende Zustandswert.

        Returns:
            List[Dict]: Eine Liste von Einträgen, die dem Zustand entsprechen.
        """
        logging.info(f"Suche nach Einträgen mit Zustand {state_value}.")
        # Mock-Implementierung, gibt immer eine leere Liste zurück.
        return []

    def get_state_statistics(self) -> Dict:
        """
        Ruft aggregierte Statistiken über die Zustände auf der Blockchain ab.

        Returns:
            Dict: Ein Dictionary mit Statistiken, einschließlich 'total_entries',
                  'unique_states' und 'last_update_timestamp'.
        """
        logging.info("Rufe Zustandsstatistiken ab.")
        # Mock-Implementierung
        return {
            "total_entries": 0,
            "unique_states": 0,
            "last_update_timestamp": datetime.now(timezone.utc).isoformat()
        }

    # =============================================================================
    # Agent-spezifische Methoden für autonome KI-Agenten
    # =============================================================================

    def register_agent_action(self, agent_id: str, action_type: str, result_cid: str, confidence: float) -> str:
        """
        Registriert eine autonome Agent-Aktion auf der Blockchain.

        Args:
            agent_id (str): Eindeutige ID des Agenten (max. 32 Zeichen).
            action_type (str): Typ der Aktion (z.B. "reflect", "analyze", "learn").
            result_cid (str): CID des Aktionsergebnisses in IPFS.
            confidence (float): Vertrauenswert der Aktion (0.0 - 1.0).

        Returns:
            str: Der Transaktions-Hash der Agent-Registrierung.

        Raises:
            ASIBlockchainError: Bei ungültigen Parametern oder Transaktionsfehlern.
        """
        if not self.is_connected():
            raise ASIBlockchainError("Keine Blockchain-Verbindung für Agent-Registrierung.")

        # Parameter-Validierung
        if len(agent_id) > 32:
            raise ASIBlockchainError("Agent-ID darf max. 32 Zeichen haben.")
        
        if not 0.0 <= confidence <= 1.0:
            raise ASIBlockchainError("Confidence muss zwischen 0.0 und 1.0 liegen.")

        # Agent-spezifische Tags erstellen
        agent_tags = [f"agent:{agent_id}", f"action:{action_type}", f"confidence:{confidence:.2f}"]
        
        # Dummy-Embedding für Agent-Metadaten
        agent_metadata = f"{agent_id}:{action_type}:{confidence}"
        agent_embedding = self._create_agent_embedding(agent_metadata)
        
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        logging.info(f"Registriere Agent-Aktion: {agent_id} -> {action_type} (Confidence: {confidence:.2f})")
        
        return self.register_entry_on_chain(result_cid, agent_tags, agent_embedding, timestamp)

    def _create_agent_embedding(self, metadata: str) -> bytes:
        """
        Erstellt ein deterministisches Embedding für Agent-Metadaten.

        Args:
            metadata (str): Agent-Metadaten als String.

        Returns:
            bytes: 128-Byte Embedding für die Blockchain.
        """
        import hashlib
        
        # Deterministisches Embedding basierend auf Metadaten
        hash_obj = hashlib.sha256(metadata.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Auf 128 Bytes erweitern durch Wiederholung
        embedding = (hash_bytes * 4)[:128]
        
        return embedding

    def get_agent_actions(self, agent_id: str) -> List[Dict]:
        """
        Ruft alle Aktionen eines spezifischen Agenten von der Blockchain ab.

        Args:
            agent_id (str): Die Agent-ID zum Filtern.

        Returns:
            List[Dict]: Liste aller Aktionen des Agenten.
        """
        if not self.is_connected():
            logging.warning("Keine Blockchain-Verbindung für Agent-Abfrage.")
            return []

        try:
            logging.info(f"Suche Aktionen für Agent: {agent_id}")
            
            # In einer echten Implementierung würde hier ein Smart-Contract-Call erfolgen
            # Für Mock-Zwecke geben wir eine leere Liste zurück
            return []
            
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Agent-Aktionen für {agent_id}: {e}")
            return []

    def register_agent_learning(self, agent_id: str, learning_data: Dict, embedding: bytes) -> str:
        """
        Registriert einen Lernprozess eines Agenten auf der Blockchain.

        Args:
            agent_id (str): ID des lernenden Agenten.
            learning_data (Dict): Metadaten über den Lernprozess.
            embedding (bytes): Vektor-Embedding des Lerninhalts.

        Returns:
            str: Transaction-Hash der Lern-Registrierung.
        """
        learning_cid = f"learning_{agent_id}_{int(datetime.now().timestamp())}"
        learning_tags = [
            f"agent:{agent_id}",
            "type:learning",
            f"topic:{learning_data.get('topic', 'general')}",
            f"improvement:{learning_data.get('improvement_score', 0.0):.2f}"
        ]
        
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        logging.info(f"Registriere Lernprozess für Agent {agent_id}: {learning_data.get('topic', 'general')}")
        
        return self.register_entry_on_chain(learning_cid, learning_tags, embedding, timestamp)

    def get_agent_network_stats(self) -> Dict:
        """
        Ruft Statistiken über das gesamte Agent-Netzwerk ab.

        Returns:
            Dict: Netzwerk-Statistiken aller Agenten.
        """
        if not self.is_connected():
            return {
                "total_agents": 0,
                "total_actions": 0,
                "active_agents_24h": 0,
                "average_confidence": 0.0
            }

        try:
            logging.info("Rufe Agent-Netzwerk-Statistiken ab...")
            
            # Mock-Implementierung für Demo
            return {
                "total_agents": 0,
                "total_actions": 0,
                "active_agents_24h": 0,
                "average_confidence": 0.0,
                "last_update": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Netzwerk-Statistiken: {e}")
            return {"error": str(e)}

    def register_agent_collaboration(self, agents: List[str], collaboration_type: str, result_cid: str) -> str:
        """
        Registriert eine Kollaboration zwischen mehreren Agenten.

        Args:
            agents (List[str]): Liste der beteiligten Agent-IDs.
            collaboration_type (str): Art der Zusammenarbeit.
            result_cid (str): CID des Kollaborationsergebnisses.

        Returns:
            str: Transaction-Hash der Kollaborations-Registrierung.
        """
        if len(agents) < 2:
            raise ASIBlockchainError("Kollaboration benötigt mindestens 2 Agenten.")

        # Kollaborations-Tags erstellen
        collab_tags = [
            f"collaboration:{collaboration_type}",
            f"agents:{len(agents)}",
            *[f"agent:{agent_id}" for agent_id in agents[:5]]  # Max 5 Agent-Tags
        ]
        
        # Kollaborations-Embedding
        collab_metadata = f"{collaboration_type}:{':'.join(sorted(agents))}"
        collab_embedding = self._create_agent_embedding(collab_metadata)
        
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        logging.info(f"Registriere Kollaboration: {collaboration_type} zwischen {len(agents)} Agenten")
        
        return self.register_entry_on_chain(result_cid, collab_tags, collab_embedding, timestamp)

def create_blockchain_client_from_config() -> Optional[ASIBlockchainClient]:
    """
    Erstellt einen Blockchain-Client aus Umgebungsvariablen.

    Returns:
        Optional[ASIBlockchainClient]: Blockchain-Client oder None wenn Konfiguration fehlt.
    """
    rpc_url = os.getenv("MUMBAI_RPC_URL")
    private_key = os.getenv("PRIVATE_KEY")
    contract_address = os.getenv("ASI_CONTRACT_ADDRESS")
    
    if all([rpc_url, private_key, contract_address]):
        return ASIBlockchainClient(rpc_url, private_key, contract_address)
    return None

def create_dummy_embedding(text: str, size: int = 128) -> bytes:
    """
    Hilfsfunktion zum Erstellen von Dummy-Embeddings für Tests.

    Args:
        text (str): Text für das Embedding.
        size (int): Größe des Embeddings in Bytes.

    Returns:
        bytes: Dummy-Embedding der gewünschten Größe.
    """
    import hashlib
    
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Auf gewünschte Größe erweitern
    return (hash_bytes * ((size // 32) + 1))[:size]
