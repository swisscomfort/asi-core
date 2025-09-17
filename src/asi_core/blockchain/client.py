#!/usr/bin/env python3
"""
ASI Core - Blockchain Client
Vollständige Implementierung für Polygon Mumbai Integration
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from eth_account import Account
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ASIBlockchainError(Exception):
    """Custom exception for blockchain-related errors."""
    pass


class ASIBlockchainClient:
    """
    Client für die Interaktion mit dem ASI Smart Contract.
    
    Unterstützt Polygon Mumbai Testnet und Mainnet.
    """
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        """
        Initialisiert den Blockchain Client.
        
        Args:
            rpc_url: Ethereum JSON-RPC Endpoint URL
            private_key: Private Key des Accounts (ohne 0x Prefix)
            contract_address: Adresse des ASI Smart Contracts
            
        Raises:
            ASIBlockchainError: Bei Verbindungsfehlern
        """
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.is_connected():
            raise ASIBlockchainError(f"Konnte nicht zu {rpc_url} verbinden")
        
        # Account Setup
        try:
            self.account = Account.from_key(private_key)
            logger.info(f"Account geladen: {self.account.address}")
        except Exception as e:
            logger.error(f"Ungültiger Private Key: {e}")
            raise ASIBlockchainError("Ungültiger Private Key")
        
        # Contract ABI laden
        abi_path = Path(__file__).parent.parent.parent.parent / "contracts" / "ASI.json"
        if not abi_path.exists():
            # Fallback ABI
            abi = self._get_fallback_abi()
        else:
            with open(abi_path, 'r') as f:
                contract_data = json.load(f)
                abi = contract_data.get('abi', self._get_fallback_abi())
        
        # Contract initialisieren
        try:
            self.contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=abi
            )
            self.contract_address = contract_address
            logger.info(f"Contract initialisiert: {contract_address}")
        except Exception as e:
            logger.error(f"Contract-Initialisierung fehlgeschlagen: {e}")
            raise ASIBlockchainError(f"Contract konnte nicht geladen werden: {e}")
    
    def _get_fallback_abi(self) -> List[Dict]:
        """Gibt minimales ABI zurück falls Datei fehlt."""
        return [
            {
                "inputs": [
                    {"name": "cid", "type": "string"},
                    {"name": "tags", "type": "string[]"},
                    {"name": "embedding", "type": "bytes"},
                    {"name": "timestamp", "type": "uint256"}
                ],
                "name": "registerEntry",
                "outputs": [{"name": "", "type": "bytes32"}],
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getStateStatistics",
                "outputs": [
                    {"name": "totalEntries", "type": "uint256"},
                    {"name": "uniqueStates", "type": "uint256"}
                ],
                "type": "function",
                "stateMutability": "view"
            }
        ]
    
    def is_connected(self) -> bool:
        """
        Prüft ob der Client mit der Blockchain verbunden ist.
        
        Returns:
            True wenn verbunden, sonst False
        """
        try:
            self.web3.eth.block_number
            return True
        except Exception:
            return False
    
    def register_entry_on_chain(
        self, 
        cid: str, 
        tags: List[str], 
        embedding: bytes, 
        timestamp: int
    ) -> str:
        """
        Registriert einen Eintrag auf der Blockchain.
        
        Args:
            cid: Content Identifier (IPFS Hash)
            tags: Liste von Tags (max 10)
            embedding: 128-byte Embedding-Vektor
            timestamp: Unix-Timestamp
            
        Returns:
            Transaction Hash als Hex-String
            
        Raises:
            ASIBlockchainError: Bei Transaktionsfehlern
        """
        if not self.is_connected():
            raise ASIBlockchainError("Nicht mit Blockchain verbunden")
        
        logger.info(f"Registriere CID {cid} on-chain")
        
        # Validierung
        if len(tags) > 10:
            tags = tags[:10]
            logger.warning("Tags auf 10 limitiert")
        
        if len(embedding) != 128:
            logger.warning(f"Embedding-Größe: {len(embedding)} bytes (erwartet: 128)")
            # Padding oder Truncation
            if len(embedding) < 128:
                embedding = embedding + bytes(128 - len(embedding))
            else:
                embedding = embedding[:128]
        
        try:
            # Transaction bauen
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            # Gas-Preis ermitteln
            gas_price = self.web3.eth.gas_price
            
            # Transaction Data
            transaction = self.contract.functions.registerEntry(
                cid, tags, embedding, timestamp
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id
            })
            
            # Signieren
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key=self.account.key
            )
            
            # Senden
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hex = tx_hash.hex()
            
            logger.info(f"Transaction gesendet: {tx_hex}")
            return tx_hex
            
        except ContractLogicError as e:
            logger.error(f"Contract-Fehler: {e}")
            raise ASIBlockchainError(f"Contract-Ausführung fehlgeschlagen: {e}")
        except Exception as e:
            logger.error(f"Transaction-Fehler: {e}")
            raise ASIBlockchainError(f"Transaction fehlgeschlagen: {e}")
    
    def get_transaction_status(self, tx_hash: str) -> str:
        """
        Prüft den Status einer Transaction.
        
        Args:
            tx_hash: Transaction Hash
            
        Returns:
            Status: 'pending', 'success', 'failed', oder 'not_found'
        """
        logger.debug(f"Prüfe Status für {tx_hash}")
        
        try:
            # Receipt abrufen
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if receipt is None:
                return "pending"
            
            if receipt['status'] == 1:
                logger.info(f"Transaction {tx_hash[:10]}... erfolgreich")
                return "success"
            else:
                logger.warning(f"Transaction {tx_hash[:10]}... fehlgeschlagen")
                return "failed"
                
        except TransactionNotFound:
            logger.warning(f"Transaction {tx_hash[:10]}... nicht gefunden")
            return "not_found"
        except Exception as e:
            logger.error(f"Fehler beim Status-Check: {e}")
            raise ASIBlockchainError(f"Status-Abfrage fehlgeschlagen: {e}")
    
    def get_state_statistics(self) -> Dict:
        """
        Ruft Statistiken vom Smart Contract ab.
        
        Returns:
            Dictionary mit Statistiken
        """
        if not self.is_connected():
            raise ASIBlockchainError("Nicht mit Blockchain verbunden")
        
        logger.debug("Rufe State-Statistiken ab")
        
        try:
            # Contract Call
            result = self.contract.functions.getStateStatistics().call()
            
            stats = {
                'total_entries': result[0],
                'unique_states': result[1],
                'last_update_timestamp': datetime.now().isoformat(),
                'contract_address': self.contract_address,
                'network': self._get_network_name()
            }
            
            logger.info(f"Statistiken abgerufen: {stats['total_entries']} Einträge")
            return stats
            
        except Exception as e:
            logger.error(f"Statistik-Abruf fehlgeschlagen: {e}")
            raise ASIBlockchainError(f"Konnte Statistiken nicht abrufen: {e}")
    
    def _get_network_name(self) -> str:
        """Ermittelt den Netzwerknamen basierend auf Chain ID."""
        chain_id = self.web3.eth.chain_id
        networks = {
            1: "Ethereum Mainnet",
            137: "Polygon Mainnet",
            80001: "Polygon Mumbai",
            1337: "Local Network"
        }
        return networks.get(chain_id, f"Unknown (ID: {chain_id})")
    
    def wait_for_confirmation(self, tx_hash: str, timeout: int = 120) -> Dict:
        """
        Wartet auf Transaction-Bestätigung.
        
        Args:
            tx_hash: Transaction Hash
            timeout: Maximale Wartezeit in Sekunden
            
        Returns:
            Transaction Receipt
        """
        logger.info(f"Warte auf Bestätigung für {tx_hash[:10]}...")
        
        try:
            receipt = self.web3.eth.wait_for_transaction_receipt(
                tx_hash, 
                timeout=timeout
            )
            
            if receipt['status'] == 1:
                logger.info(f"Transaction bestätigt in Block {receipt['blockNumber']}")
            else:
                logger.warning("Transaction fehlgeschlagen")
                
            return dict(receipt)
            
        except Exception as e:
            logger.error(f"Timeout oder Fehler: {e}")
            raise ASIBlockchainError(f"Bestätigung fehlgeschlagen: {e}")
