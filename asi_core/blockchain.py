"""
ASI Core - Blockchain Integration
Verbindung zwischen Python Backend und Smart Contract
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from eth_account import Account
from web3 import Web3
from web3.contract import Contract

# PoA Middleware für Polygon wird bei Bedarf geladen

# Logger konfigurieren
logger = logging.getLogger(__name__)


class ASIBlockchainError(Exception):
    """Custom Exception für Blockchain-Operationen"""

    pass


class ASIBlockchainClient:
    """Client für Interaktion mit dem ASIIndex Smart Contract"""

    def __init__(
        self,
        rpc_url: str,
        private_key: str,
        contract_address: str,
        contract_abi: Optional[List] = None,
    ):
        """
        Initialisiert den Blockchain Client

        Args:
            rpc_url: RPC-Endpunkt der Blockchain
            private_key: Private Key für Transaktionen
            contract_address: Adresse des deployed ASIIndex Contracts
            contract_abi: ABI des Contracts (wird automatisch geladen falls None)
        """
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.contract_address = Web3.to_checksum_address(contract_address)

        # Web3 Instanz erstellen
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # PoA Middleware für Polygon/Mumbai (falls erforderlich)
        try:
            from web3.middleware import geth_poa_middleware

            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except ImportError:
            # Neuere web3 Versionen verwenden andere Middleware
            pass  # Account aus Private Key erstellen
        self.account = Account.from_key(private_key)
        self.wallet_address = self.account.address

        # Contract ABI laden
        if contract_abi is None:
            self.contract_abi = self._load_contract_abi()
        else:
            self.contract_abi = contract_abi

        # Contract Instanz erstellen
        self.contract = self.w3.eth.contract(
            address=self.contract_address, abi=self.contract_abi
        )

        # Verbindung prüfen
        self._verify_connection()

    def _load_contract_abi(self) -> List:
        """Lädt die Contract ABI aus den Hardhat Artefakten"""
        try:
            # Pfad zur ABI-Datei
            abi_file = (
                Path(__file__).parent.parent.parent
                / "web/contracts/deployments/ASIIndex-ABI.json"
            )

            if not abi_file.exists():
                # Fallback: Aus Hardhat Artefakten laden
                artifacts_file = (
                    Path(__file__).parent.parent.parent
                    / "web/contracts/artifacts/contracts/ASIIndex.sol/ASIIndex.json"
                )
                if artifacts_file.exists():
                    with open(artifacts_file, "r") as f:
                        artifacts = json.load(f)
                        return artifacts["abi"]

            with open(abi_file, "r") as f:
                return json.load(f)

        except Exception as e:
            raise ASIBlockchainError(f"Konnte Contract ABI nicht laden: {e}")

    def _verify_connection(self):
        """Überprüft die Blockchain-Verbindung"""
        try:
            if not self.w3.is_connected():
                raise ASIBlockchainError(f"Keine Verbindung zu {self.rpc_url}")

            # Balance prüfen
            balance = self.w3.eth.get_balance(self.wallet_address)
            balance_eth = self.w3.from_wei(balance, "ether")

            logger.info(f"✅ Blockchain verbunden: {self.rpc_url}")
            logger.info(f"💰 Wallet: {self.wallet_address}")
            logger.info(f"💸 Balance: {balance_eth:.4f} ETH")
            logger.info(f"📄 Contract: {self.contract_address}")

            # Contract-Verbindung testen
            total_entries = self.contract.functions.getTotalEntries().call()
            logger.info(f"📊 Total Entries im Contract: {total_entries}")

        except Exception as e:
            raise ASIBlockchainError(f"Verbindungstest fehlgeschlagen: {e}")

    def register_hybrid_entry_on_chain(
        self,
        cid: str,
        tags: List[str],
        embedding: bytes,
        state_value: int,
        timestamp: int,
    ) -> str:
        """
        Registriert einen neuen Hybrid-Eintrag mit Zustandswert auf der Blockchain

        Args:
            cid: Content Identifier (IPFS/Arweave)
            tags: Liste von Tags für Kategorisierung
            embedding: AI-Embedding als Bytes
            state_value: Zustandswert (0-255)
            timestamp: Unix-Timestamp der Erstellung

        Returns:
            Transaction Hash als String
        """
        try:
            logger.info(
                f"📝 Registriere Hybrid-Eintrag auf Blockchain: {cid} (Zustand: {state_value})"
            )

            # Parameter validieren
            if not cid:
                raise ValueError("CID darf nicht leer sein")
            if len(tags) > 10:  # MAX_TAGS aus Contract
                raise ValueError("Zu viele Tags (max. 10)")
            if len(embedding) > 1024:  # MAX_EMBEDDING_SIZE aus Contract
                raise ValueError("Embedding zu groß (max. 1024 bytes)")
            if not (0 <= state_value <= 255):  # uint8 Bereich
                raise ValueError(
                    f"Ungültiger Zustandswert: {state_value} (muss 0-255 sein)"
                )

            # Transaction Parameter
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            gas_price = self.w3.eth.gas_price

            # Contract-Funktion aufbauen
            function = self.contract.functions.registerHybridEntry(
                cid, tags, embedding, state_value, timestamp
            )

            # Gas schätzen
            try:
                gas_estimate = function.estimate_gas({"from": self.wallet_address})
                gas_limit = int(gas_estimate * 1.2)  # 20% Buffer
            except Exception as e:
                logger.warning(f"Gas-Schätzung fehlgeschlagen: {e}")
                gas_limit = 350000  # Etwas höherer Fallback für Hybrid-Funktion

            # Transaction erstellen
            transaction = function.build_transaction(
                {
                    "chainId": self.w3.eth.chain_id,
                    "gas": gas_limit,
                    "gasPrice": gas_price,
                    "nonce": nonce,
                    "from": self.wallet_address,
                }
            )

            # Transaction signieren
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, self.private_key
            )

            # Transaction senden
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()

            logger.info(f"📤 Hybrid-Transaction gesendet: {tx_hash_hex}")

            # Auf Bestätigung warten (optional)
            try:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                if receipt.status == 1:
                    logger.info(
                        f"✅ Hybrid-Transaction bestätigt in Block {receipt.blockNumber}"
                    )

                    # Event-Logs extrahieren
                    events = self.contract.events.EntryRegistered().process_receipt(
                        receipt
                    )
                    if events:
                        entry_id = events[0]["args"]["entryId"]
                        event_state = events[0]["args"]["stateValue"]
                        logger.info(f"🆔 Entry ID: {entry_id}, Zustand: {event_state}")

                else:
                    logger.error(f"❌ Hybrid-Transaction fehlgeschlagen: {receipt}")

            except Exception as e:
                logger.warning(f"⏰ Timeout beim Warten auf Bestätigung: {e}")

            return tx_hash_hex

        except Exception as e:
            logger.error(f"❌ Hybrid-Blockchain-Registrierung fehlgeschlagen: {e}")
            raise ASIBlockchainError(f"Hybrid-Entry-Registrierung fehlgeschlagen: {e}")

    def register_entry_on_chain(
        self, cid: str, tags: List[str], embedding: bytes, timestamp: int
    ) -> str:
        """
        Registriert einen neuen Eintrag auf der Blockchain (Legacy-Funktion)

        Args:
            cid: Content Identifier (IPFS/Arweave)
            tags: Liste von Tags für Kategorisierung
            embedding: AI-Embedding als Bytes
            timestamp: Unix-Timestamp der Erstellung

        Returns:
            Transaction Hash als String
        """
        # Ruft die neue Hybrid-Funktion mit Standardzustand 0 auf
        return self.register_hybrid_entry_on_chain(cid, tags, embedding, 0, timestamp)

    def get_entry(self, entry_id: int) -> Dict:
        """
        Holt einen Eintrag von der Blockchain

        Args:
            entry_id: ID des Eintrags

        Returns:
            Dictionary mit Entry-Daten
        """
        try:
            entry = self.contract.functions.getEntry(entry_id).call()

            return {
                "entryId": entry[0],
                "cid": entry[1],
                "tags": entry[2],
                "embedding": entry[3],
                "stateValue": entry[4],  # Neues Feld für Zustandswert
                "timestamp": entry[5],
                "owner": entry[6],
                "isActive": entry[7],
            }

        except Exception as e:
            raise ASIBlockchainError(
                f"Entry {entry_id} konnte nicht geladen werden: {e}"
            )

    def get_entries_by_owner(self, owner_address: Optional[str] = None) -> List[int]:
        """
        Holt alle Entry-IDs eines Owners

        Args:
            owner_address: Adresse des Owners (Standard: eigene Adresse)

        Returns:
            Liste von Entry-IDs
        """
        if owner_address is None:
            owner_address = self.wallet_address

        try:
            entry_ids = self.contract.functions.getEntriesByOwner(owner_address).call()
            return list(entry_ids)

        except Exception as e:
            raise ASIBlockchainError(
                f"Entries für Owner {owner_address} konnten nicht geladen werden: {e}"
            )

    def get_entries_by_tag(self, tag: str) -> List[int]:
        """
        Holt alle Entry-IDs mit einem bestimmten Tag

        Args:
            tag: Der zu suchende Tag

        Returns:
            Liste von Entry-IDs
        """
        try:
            entry_ids = self.contract.functions.getEntriesByTag(tag).call()
            return list(entry_ids)

        except Exception as e:
            raise ASIBlockchainError(
                f"Entries für Tag '{tag}' konnten nicht geladen werden: {e}"
            )

    def get_entries_by_state(self, state_value: int) -> List[int]:
        """
        Holt alle Entry-IDs mit einem bestimmten Zustandswert

        Args:
            state_value: Der zu suchende Zustandswert (0-255)

        Returns:
            Liste von Entry-IDs
        """
        try:
            entry_ids = self.contract.functions.getEntriesByState(state_value).call()
            return list(entry_ids)

        except Exception as e:
            raise ASIBlockchainError(
                f"Entries für Zustand {state_value} konnten nicht geladen werden: {e}"
            )

    def get_state_statistics(self) -> Dict:
        """
        Holt Zustandsstatistiken vom Smart Contract

        Returns:
            Dictionary mit Zustandsstatistiken
        """
        try:
            states, counts = self.contract.functions.getStateStatistics().call()

            statistics = {
                "total_entries": sum(counts),
                "unique_states": len(states),
                "state_distribution": {},
            }

            for i, state in enumerate(states):
                statistics["state_distribution"][state] = {
                    "count": counts[i],
                    "percentage": (
                        (counts[i] / sum(counts) * 100) if sum(counts) > 0 else 0
                    ),
                }

            return statistics

        except Exception as e:
            raise ASIBlockchainError(
                f"Zustandsstatistiken konnten nicht geladen werden: {e}"
            )

    def get_total_entries(self) -> int:
        """
        Gibt die Gesamtanzahl der registrierten Einträge zurück

        Returns:
            Anzahl der Einträge
        """
        try:
            return self.contract.functions.getTotalEntries().call()
        except Exception as e:
            raise ASIBlockchainError(
                f"Gesamtanzahl der Entries konnte nicht geladen werden: {e}"
            )

    def is_entry_active(self, entry_id: int) -> bool:
        """
        Überprüft ob ein Eintrag aktiv ist

        Args:
            entry_id: ID des Eintrags

        Returns:
            True wenn aktiv, False sonst
        """
        try:
            return self.contract.functions.isEntryActive(entry_id).call()
        except Exception as e:
            raise ASIBlockchainError(
                f"Status von Entry {entry_id} konnte nicht geprüft werden: {e}"
            )

    def get_gas_price(self) -> int:
        """Gibt den aktuellen Gas-Preis zurück"""
        return self.w3.eth.gas_price

    def get_balance(self) -> float:
        """Gibt die ETH-Balance der Wallet zurück"""
        balance_wei = self.w3.eth.get_balance(self.wallet_address)
        return self.w3.from_wei(balance_wei, "ether")


def register_entry_on_chain(
    cid: str,
    tags: List[str],
    embedding: bytes,
    timestamp: int,
    contract_address: str,
    private_key: str,
    rpc_url: str,
) -> str:
    """
    Convenience-Funktion zum Registrieren eines Eintrags

    Args:
        cid: Content Identifier
        tags: Liste von Tags
        embedding: AI-Embedding
        timestamp: Unix-Timestamp
        contract_address: Contract-Adresse
        private_key: Private Key für Transaktionen
        rpc_url: RPC-Endpunkt

    Returns:
        Transaction Hash
    """
    client = ASIBlockchainClient(rpc_url, private_key, contract_address)
    return client.register_entry_on_chain(cid, tags, embedding, timestamp)


def create_blockchain_client_from_config(config: Dict) -> ASIBlockchainClient:
    """
    Erstellt einen Blockchain Client aus einer Konfiguration

    Args:
        config: Dictionary mit Konfigurationsdaten

    Returns:
        ASIBlockchainClient Instanz
    """
    required_keys = ["rpc_url", "private_key", "contract_address"]
    for key in required_keys:
        if key not in config:
            raise ASIBlockchainError(f"Fehlende Konfiguration: {key}")

    return ASIBlockchainClient(
        rpc_url=config["rpc_url"],
        private_key=config["private_key"],
        contract_address=config["contract_address"],
    )


def create_dummy_embedding(text: str, size: int = 128) -> bytes:
    """
    Erstellt ein Dummy-Embedding für Tests

    Args:
        text: Text für Seed
        size: Größe des Embeddings

    Returns:
        Dummy-Embedding als Bytes
    """
    import hashlib

    # Hash des Textes erstellen
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()

    # Auf gewünschte Größe erweitern/kürzen
    while len(hash_bytes) < size:
        hash_bytes += hash_obj.digest()

    return hash_bytes[:size]
