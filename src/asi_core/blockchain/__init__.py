#!/usr/bin/env python3
"""
ASI Core - Blockchain Package
Exportiert alle blockchain Komponenten und Factory-Funktionen
"""

import os
import logging
from typing import Optional

from .client import ASIBlockchainClient, ASIBlockchainError

logger = logging.getLogger(__name__)

__all__ = [
    'ASIBlockchainClient',
    'ASIBlockchainError', 
    'create_blockchain_client_from_config'
]


def create_blockchain_client_from_config() -> Optional[ASIBlockchainClient]:
    """
    Erstellt einen ASI Blockchain Client aus Umgebungsvariablen.
    
    Erwartet folgende Umgebungsvariablen:
    - ASI_RPC_URL: Ethereum JSON-RPC Endpoint
    - ASI_PRIVATE_KEY: Private Key (ohne 0x Prefix)  
    - ASI_CONTRACT_ADDRESS: Smart Contract Adresse
    
    Returns:
        ASIBlockchainClient oder None bei fehlender Konfiguration
        
    Raises:
        ASIBlockchainError: Bei Verbindungsfehlern
    """
    try:
        # Lade Konfiguration aus .env
        rpc_url = os.getenv('ASI_RPC_URL')
        private_key = os.getenv('ASI_PRIVATE_KEY')
        contract_address = os.getenv('ASI_CONTRACT_ADDRESS')
        
        if not all([rpc_url, private_key, contract_address]):
            logger.warning(
                "Blockchain Konfiguration unvollständig. "
                "Benötigt: ASI_RPC_URL, ASI_PRIVATE_KEY, ASI_CONTRACT_ADDRESS"
            )
            return None
            
        # Entferne 0x Prefix falls vorhanden
        if private_key.startswith('0x'):
            private_key = private_key[2:]
            
        # Erstelle Client
        client = ASIBlockchainClient(
            rpc_url=rpc_url,
            private_key=private_key,
            contract_address=contract_address
        )
        
        logger.info("ASI Blockchain Client erfolgreich konfiguriert")
        return client
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Blockchain Clients: {e}")
        raise ASIBlockchainError(f"Client-Erstellung fehlgeschlagen: {e}")
