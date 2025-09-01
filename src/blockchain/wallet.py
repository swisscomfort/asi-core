"""
ASI Core - Wallet Module
Wallet-Management und Transaktions-Signierung
"""

import hashlib
import json
import os
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass
import secrets


@dataclass
class WalletInfo:
    """Wallet-Informationen"""

    address: str
    public_key: str
    balance_eth: float
    balance_tokens: Dict[str, float]
    transaction_count: int


class CryptoWallet:
    """Cryptocurrency Wallet für ASI System"""

    def __init__(self, wallet_file: str = None):
        self.wallet_file = wallet_file
        self.address = None
        self.private_key = None
        self.public_key = None
        self.is_unlocked = False
        self.transaction_history = []

    def create_new_wallet(self, password: str) -> Dict:
        """
        Erstellt eine neue Wallet

        Args:
            password: Passwort zum Verschlüsseln der Wallet

        Returns:
            Dict: Wallet-Informationen
        """
        # Generiere Private Key (32 Bytes)
        private_key_bytes = secrets.token_bytes(32)
        self.private_key = private_key_bytes.hex()

        # Simuliere Public Key Ableitung
        self.public_key = self._derive_public_key(self.private_key)

        # Generiere Ethereum-ähnliche Adresse
        self.address = self._derive_address(self.public_key)

        # Wallet-Daten für Speicherung vorbereiten
        wallet_data = {
            "address": self.address,
            "public_key": self.public_key,
            "encrypted_private_key": self._encrypt_private_key(
                self.private_key, password
            ),
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
        }

        # Wallet speichern
        if self.wallet_file:
            self._save_wallet_file(wallet_data)

        self.is_unlocked = True

        print(f"Neue Wallet erstellt: {self.address}")
        return {
            "address": self.address,
            "public_key": self.public_key,
            "mnemonic_hint": "Speichere dein Passwort sicher!",
        }

    def load_wallet(self, password: str) -> bool:
        """
        Lädt eine bestehende Wallet

        Args:
            password: Wallet-Passwort

        Returns:
            bool: Erfolg des Ladens
        """
        if not self.wallet_file or not os.path.exists(self.wallet_file):
            print("Wallet-Datei nicht gefunden")
            return False

        try:
            with open(self.wallet_file, "r") as f:
                wallet_data = json.load(f)

            # Private Key entschlüsseln
            encrypted_key = wallet_data["encrypted_private_key"]
            self.private_key = self._decrypt_private_key(encrypted_key, password)

            self.address = wallet_data["address"]
            self.public_key = wallet_data["public_key"]
            self.is_unlocked = True

            print(f"Wallet geladen: {self.address}")
            return True

        except Exception as e:
            print(f"Fehler beim Laden der Wallet: {e}")
            return False

    def get_wallet_info(self) -> Optional[WalletInfo]:
        """
        Ruft Wallet-Informationen ab

        Returns:
            Optional[WalletInfo]: Wallet-Informationen
        """
        if not self.is_unlocked:
            return None

        # Simuliere Balance-Abfrage
        balance_eth = self._get_eth_balance()
        balance_tokens = self._get_token_balances()
        tx_count = len(self.transaction_history)

        return WalletInfo(
            address=self.address,
            public_key=self.public_key,
            balance_eth=balance_eth,
            balance_tokens=balance_tokens,
            transaction_count=tx_count,
        )

    def sign_message(self, message: str) -> Dict:
        """
        Signiert eine Nachricht

        Args:
            message: Zu signierende Nachricht

        Returns:
            Dict: Signatur-Informationen
        """
        if not self.is_unlocked:
            return {"error": "Wallet nicht entsperrt"}

        # Nachricht hashen
        message_hash = hashlib.sha256(message.encode()).hexdigest()

        # Signatur simulieren (in Realität: echte ECDSA-Signatur)
        signature_data = f"{self.private_key}{message_hash}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()

        signature_info = {
            "message": message,
            "message_hash": message_hash,
            "signature": signature,
            "address": self.address,
            "timestamp": datetime.now().isoformat(),
        }

        return signature_info

    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Verifiziert eine Signatur

        Args:
            message: Ursprüngliche Nachricht
            signature: Zu verifizierende Signatur
            address: Adresse des Signierers

        Returns:
            bool: True wenn Signatur gültig
        """
        # Vereinfachte Verifikation (in Realität: ECDSA-Verifikation)
        message_hash = hashlib.sha256(message.encode()).hexdigest()

        # Prüfe ob Signatur zur Nachricht und Adresse passt
        # (Dies ist eine Simulation - echte Implementierung würde
        #  Public Key Recovery verwenden)

        return len(signature) == 64 and address == self.address

    def sign_transaction(self, transaction_data: Dict) -> Dict:
        """
        Signiert eine Blockchain-Transaktion

        Args:
            transaction_data: Transaktionsdaten

        Returns:
            Dict: Signierte Transaktion
        """
        if not self.is_unlocked:
            return {"error": "Wallet nicht entsperrt"}

        # Transaktion serialisieren
        tx_string = json.dumps(transaction_data, sort_keys=True)

        # Signatur erstellen
        signature_info = self.sign_message(tx_string)

        # Signierte Transaktion zusammenstellen
        signed_transaction = {
            "transaction": transaction_data,
            "signature": signature_info["signature"],
            "from_address": self.address,
            "signed_at": datetime.now().isoformat(),
        }

        # In Historie speichern
        self.transaction_history.append(
            {
                "type": "signed",
                "data": signed_transaction,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return signed_transaction

    def create_reflection_commitment(
        self, reflection_hash: str, storage_hash: str
    ) -> Dict:
        """
        Erstellt ein Commitment für eine Reflexion

        Args:
            reflection_hash: Hash der Reflexion
            storage_hash: Storage-Hash (IPFS/Arweave)

        Returns:
            Dict: Signiertes Commitment
        """
        commitment_data = {
            "reflection_hash": reflection_hash,
            "storage_hash": storage_hash,
            "user_address": self.address,
            "timestamp": datetime.now().isoformat(),
            "commitment_type": "reflection_storage",
        }

        # Commitment signieren
        commitment_string = json.dumps(commitment_data, sort_keys=True)
        signature_info = self.sign_message(commitment_string)

        signed_commitment = {
            "commitment": commitment_data,
            "signature": signature_info["signature"],
            "public_key": self.public_key,
        }

        return signed_commitment

    def verify_commitment(self, commitment: Dict) -> bool:
        """
        Verifiziert ein Reflexions-Commitment

        Args:
            commitment: Zu verifizierendes Commitment

        Returns:
            bool: True wenn gültig
        """
        try:
            commitment_data = commitment["commitment"]
            signature = commitment["signature"]

            # Commitment re-serialisieren
            commitment_string = json.dumps(commitment_data, sort_keys=True)

            # Signatur verifizieren
            return self.verify_signature(
                commitment_string, signature, commitment_data["user_address"]
            )

        except (KeyError, json.JSONDecodeError):
            return False

    def export_public_info(self) -> Dict:
        """
        Exportiert öffentliche Wallet-Informationen

        Returns:
            Dict: Öffentliche Informationen
        """
        if not self.is_unlocked:
            return {}

        return {
            "address": self.address,
            "public_key": self.public_key,
            "created_transactions": len(self.transaction_history),
        }

    def backup_wallet(self, backup_path: str, password: str) -> bool:
        """
        Erstellt Wallet-Backup

        Args:
            backup_path: Pfad für Backup
            password: Backup-Passwort

        Returns:
            bool: Erfolg des Backups
        """
        if not self.is_unlocked:
            return False

        try:
            backup_data = {
                "address": self.address,
                "public_key": self.public_key,
                "encrypted_private_key": self._encrypt_private_key(
                    self.private_key, password
                ),
                "transaction_history": self.transaction_history,
                "backup_created": datetime.now().isoformat(),
                "original_wallet": self.wallet_file,
            }

            with open(backup_path, "w") as f:
                json.dump(backup_data, f, indent=2)

            print(f"Wallet-Backup erstellt: {backup_path}")
            return True

        except Exception as e:
            print(f"Backup-Fehler: {e}")
            return False

    def _derive_public_key(self, private_key: str) -> str:
        """Ableitung des Public Keys (vereinfacht)"""
        # In Realität: ECDSA Public Key Ableitung
        pub_key_data = f"pub_{private_key}"
        return hashlib.sha256(pub_key_data.encode()).hexdigest()

    def _derive_address(self, public_key: str) -> str:
        """Ableitung der Ethereum-Adresse (vereinfacht)"""
        # In Realität: Keccak256 Hash der letzten 20 Bytes
        addr_data = f"addr_{public_key}"
        addr_hash = hashlib.sha256(addr_data.encode()).hexdigest()
        return f"0x{addr_hash[:40]}"

    def _encrypt_private_key(self, private_key: str, password: str) -> str:
        """Verschlüsselt Private Key (vereinfacht)"""
        # In Realität: AES-Verschlüsselung mit Key Derivation
        key_data = f"{private_key}_{password}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _decrypt_private_key(self, encrypted_key: str, password: str) -> str:
        """Entschlüsselt Private Key (vereinfacht)"""
        # In Realität: AES-Entschlüsselung
        # Hier: Simulation durch Re-Verschlüsselung und Vergleich
        # Das ist nur für Demo-Zwecke!
        return self.private_key  # Vereinfacht

    def _save_wallet_file(self, wallet_data: Dict):
        """Speichert Wallet-Datei"""
        os.makedirs(os.path.dirname(self.wallet_file), exist_ok=True)
        with open(self.wallet_file, "w") as f:
            json.dump(wallet_data, f, indent=2)

    def _get_eth_balance(self) -> float:
        """Simuliert ETH-Balance Abfrage"""
        if not self.address:
            return 0.0

        # Simulierte Balance basierend auf Adresse
        addr_int = int(self.address[-8:], 16)
        balance = (addr_int % 1000) / 100.0  # 0.00 - 9.99 ETH
        return balance

    def _get_token_balances(self) -> Dict[str, float]:
        """Simuliert Token-Balance Abfragen"""
        if not self.address:
            return {}

        # Simulierte Token-Balances
        tokens = {
            "ASI": 100.0,  # ASI Token
            "USDC": 50.0,  # Stablecoin
            "REFLECTION": 10.0,  # Reflexions-Token
        }

        return tokens


if __name__ == "__main__":
    # Beispiel-Nutzung
    wallet = CryptoWallet("data/test_wallet.json")

    print("=== Wallet System Test ===")

    # Neue Wallet erstellen
    wallet_info = wallet.create_new_wallet("test_password_123")
    print(f"Wallet-Adresse: {wallet_info['address']}")

    # Wallet-Informationen abrufen
    info = wallet.get_wallet_info()
    if info:
        print(f"ETH-Balance: {info.balance_eth:.4f}")
        print(f"Token-Balances: {info.balance_tokens}")

    # Nachricht signieren
    test_message = "Dies ist eine Test-Reflexion für ASI"
    signature_info = wallet.sign_message(test_message)
    print(f"Signatur erstellt: {signature_info['signature'][:16]}...")

    # Signatur verifizieren
    is_valid = wallet.verify_signature(
        test_message, signature_info["signature"], wallet.address
    )
    print(f"Signatur gültig: {is_valid}")

    # Reflexions-Commitment erstellen
    commitment = wallet.create_reflection_commitment(
        "test_reflection_hash", "QmTestStorageHash"
    )
    print(f"Commitment erstellt für Reflexion")

    # Commitment verifizieren
    commitment_valid = wallet.verify_commitment(commitment)
    print(f"Commitment gültig: {commitment_valid}")

    # Backup erstellen
    backup_success = wallet.backup_wallet("data/wallet_backup.json", "backup_pass")
    print(f"Backup erstellt: {backup_success}")
