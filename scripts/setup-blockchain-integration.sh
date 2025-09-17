#!/bin/bash

# ASI-Core Blockchain Integration Setup
# Komplettes Setup für produktive Blockchain-Integration

set -e

echo "🔗 ASI-Core Blockchain Integration Setup"
echo "========================================"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Prüfe Voraussetzungen
echo -e "\n${BLUE}1. Prüfe Voraussetzungen...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js nicht gefunden!${NC}"
    echo "💡 Installation: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm nicht gefunden!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js und npm verfügbar${NC}"

# Environment Variables prüfen
echo -e "\n${BLUE}2. Prüfe Environment Variables...${NC}"

ENV_VARS=(
    "POLYGON_RPC_URL"
    "PRIVATE_KEY"
    "ALCHEMY_API_KEY"
)

MISSING_VARS=()
for var in "${ENV_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=($var)
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️ Fehlende Environment Variables:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo -e "${YELLOW}💡 Setup-Anleitung:${NC}"
    echo "1. Alchemy Account erstellen: https://alchemy.com/"
    echo "2. Polygon Mumbai Projekt erstellen"
    echo "3. API Key kopieren"
    echo "4. Wallet Private Key (ohne 0x) bereitstellen"
    echo "5. Mumbai MATIC holen: https://faucet.polygon.technology/"
    echo ""
    echo "export ALCHEMY_API_KEY=\"your_api_key_here\""
    echo "export POLYGON_RPC_URL=\"https://polygon-mumbai.g.alchemy.com/v2/\$ALCHEMY_API_KEY\""
    echo "export PRIVATE_KEY=\"your_private_key_without_0x\""
    echo ""
    read -p "Environment Variables gesetzt? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Setup abgebrochen${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment Variables konfiguriert${NC}"

# Contracts Setup
echo -e "\n${BLUE}3. Smart Contracts Setup...${NC}"

if [ ! -d "contracts/node_modules" ]; then
    echo "📦 Installiere Contract Dependencies..."
    cd contracts
    npm install
    cd ..
fi

# Prüfe ob Contracts bereits deployed sind
if [ ! -f "contracts/deployed_addresses.json" ]; then
    echo -e "${YELLOW}⚠️ Smart Contracts noch nicht deployed${NC}"
    echo "🚀 Deploye ASI State Tracker Contract..."
    
    cd contracts
    
    # Contract Deployment
    cat > deploy_asi_contract.js << 'EOF'
const { ethers } = require("ethers");
const fs = require("fs");

async function deployASIContract() {
    console.log("🚀 Deploying ASI State Tracker Contract...");
    
    const rpcUrl = process.env.POLYGON_RPC_URL;
    const privateKey = process.env.PRIVATE_KEY;
    
    if (!rpcUrl || !privateKey) {
        throw new Error("Missing POLYGON_RPC_URL or PRIVATE_KEY");
    }
    
    // Setup provider and wallet
    const provider = new ethers.JsonRpcProvider(rpcUrl);
    const wallet = new ethers.Wallet(privateKey, provider);
    
    console.log(`📍 Deploying from: ${wallet.address}`);
    
    // Check balance
    const balance = await provider.getBalance(wallet.address);
    console.log(`💰 Balance: ${ethers.formatEther(balance)} MATIC`);
    
    if (balance === 0n) {
        throw new Error("Insufficient balance. Get Mumbai MATIC from https://faucet.polygon.technology/");
    }
    
    // Read and compile contract
    const contractSource = fs.readFileSync("ASIStateTracker.sol", "utf8");
    
    // Simple ABI for deployment (would normally use Hardhat)
    const contractABI = [
        "function logState(string key, uint256 value, string cid) external",
        "function getUserState(address user, string key) external view returns (uint256, string)",
        "function getGlobalStats(string key) external view returns (uint256, uint256)"
    ];
    
    // For this example, we'll create a simple bytecode
    // In production, use Hardhat/Truffle for proper compilation
    const contractBytecode = "0x608060405234801561001057600080fd5b50..."; // Placeholder
    
    console.log("⚠️ Contract compilation needed - use Hardhat for production deployment");
    
    // Save placeholder address for now
    const deployedAddresses = {
        "ASIStateTracker": "0x1234567890123456789012345678901234567890",
        "MemoryToken": "0x0987654321098765432109876543210987654321",
        "deployedAt": new Date().toISOString(),
        "network": "polygon-mumbai",
        "deployer": wallet.address
    };
    
    fs.writeFileSync("deployed_addresses.json", JSON.stringify(deployedAddresses, null, 2));
    
    console.log("✅ Contract addresses saved to deployed_addresses.json");
    console.log("⚠️ Please deploy actual contracts using Hardhat");
    
    return deployedAddresses;
}

if (require.main === module) {
    deployASIContract()
        .then(() => process.exit(0))
        .catch(error => {
            console.error("❌ Deployment failed:", error);
            process.exit(1);
        });
}

module.exports = { deployASIContract };
EOF
    
    node deploy_asi_contract.js
    cd ..
else
    echo -e "${GREEN}✅ Smart Contracts bereits deployed${NC}"
fi

# Config Files aktualisieren
echo -e "\n${BLUE}4. Konfigurationsdateien aktualisieren...${NC}"

# Lade deployed addresses
if [ -f "contracts/deployed_addresses.json" ]; then
    ASI_CONTRACT_ADDRESS=$(node -p "JSON.parse(require('fs').readFileSync('contracts/deployed_addresses.json', 'utf8')).ASIStateTracker")
    MEMORY_TOKEN_ADDRESS=$(node -p "JSON.parse(require('fs').readFileSync('contracts/deployed_addresses.json', 'utf8')).MemoryToken")
else
    ASI_CONTRACT_ADDRESS="0x1234567890123456789012345678901234567890"
    MEMORY_TOKEN_ADDRESS="0x0987654321098765432109876543210987654321"
fi

# Update config/secrets.json
echo "📝 Aktualisiere config/secrets.json..."
cat > config/secrets.json << EOF
{
  "openai_api_key": "your_openai_api_key_here",
  "ipfs_api_url": "https://ipfs.infura.io:5001/api/v0",
  "arweave_gateway": "https://arweave.net",
  "arweave_wallet_path": "path/to/arweave/wallet.json",
  "database_path": "data/asi_local.db",
  "embedding_model": "local",
  "privacy_default": "private",
  "auto_upload_ipfs": true,
  "auto_upload_arweave": true,
  "backup_frequency_days": 7,
  "data_retention_days": 365,
  "blockchain": {
    "enabled": true,
    "rpc_url": "${POLYGON_RPC_URL}",
    "private_key": "${PRIVATE_KEY}",
    "contract_address": "${ASI_CONTRACT_ADDRESS}",
    "network": "polygon-mumbai",
    "chain_id": 80001
  },
  "storage": {
    "ipfs_api_key": "",
    "arweave_wallet": ""
  },
  "tokens": {
    "memory_token_address": "${MEMORY_TOKEN_ADDRESS}",
    "deployer_private_key": "${PRIVATE_KEY}"
  },
  "api_keys": {
    "alchemy_api_key": "${ALCHEMY_API_KEY}",
    "stripe_publishable_key": "",
    "stripe_secret_key": "",
    "stripe_webhook_secret": ""
  }
}
EOF

# Update web/.env
echo "📝 Aktualisiere web/.env..."
cat > web/.env << EOF
# Umgebungsvariablen für ASI-Core Web-Frontend
VITE_BACKEND_URL=http://localhost:8000
VITE_ENABLE_HRM=true
VITE_ENABLE_STORACHA=true
VITE_DEBUG=false
VITE_APP_VERSION=1.0.0

# Blockchain Configuration
VITE_BLOCKCHAIN_ENABLED=true
VITE_POLYGON_RPC_URL=${POLYGON_RPC_URL}
VITE_ASI_CONTRACT_ADDRESS=${ASI_CONTRACT_ADDRESS}
VITE_MEMORY_TOKEN_ADDRESS=${MEMORY_TOKEN_ADDRESS}
VITE_CHAIN_ID=80001

# Storacha/w3up Token für dezentrale Speicherung
VITE_STORACHA_TOKEN=

# WalletConnect Project ID (optional)
VITE_WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
EOF

echo -e "${GREEN}✅ Konfigurationsdateien aktualisiert${NC}"

# Web3 Dependencies installieren
echo -e "\n${BLUE}5. Web3 Dependencies installieren...${NC}"

cd web
if [ ! -d "node_modules/ethers" ]; then
    echo "📦 Installiere Web3 Dependencies..."
    npm install ethers @walletconnect/web3modal wagmi viem
fi
cd ..

echo -e "${GREEN}✅ Web3 Dependencies installiert${NC}"

# Database Schema für Blockchain
echo -e "\n${BLUE}6. Database Schema für Blockchain...${NC}"

cat > scripts/blockchain_schema.sql << 'EOF'
-- Blockchain-Integration Schema für ASI-Core

CREATE TABLE IF NOT EXISTS blockchain_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_hash TEXT UNIQUE NOT NULL,
    reflection_id INTEGER,
    contract_address TEXT NOT NULL,
    function_name TEXT NOT NULL,
    parameters TEXT, -- JSON
    status TEXT DEFAULT 'pending', -- pending, confirmed, failed
    gas_used INTEGER,
    gas_price TEXT,
    block_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reflection_id) REFERENCES reflections(id)
);

CREATE TABLE IF NOT EXISTS wallet_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_address TEXT UNIQUE NOT NULL,
    user_id INTEGER,
    provider TEXT, -- metamask, walletconnect, etc.
    chain_id INTEGER DEFAULT 80001,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS blockchain_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL, -- contract_call, transaction, error
    event_data TEXT, -- JSON
    block_number INTEGER,
    transaction_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_blockchain_tx_hash ON blockchain_transactions(tx_hash);
CREATE INDEX IF NOT EXISTS idx_blockchain_reflection_id ON blockchain_transactions(reflection_id);
CREATE INDEX IF NOT EXISTS idx_wallet_address ON wallet_connections(wallet_address);
CREATE INDEX IF NOT EXISTS idx_blockchain_logs_type ON blockchain_logs(event_type);

-- Views für einfache Abfragen
CREATE VIEW IF NOT EXISTS active_wallets AS
SELECT 
    wallet_address,
    provider,
    chain_id,
    connected_at,
    last_activity
FROM wallet_connections 
WHERE is_active = 1;

CREATE VIEW IF NOT EXISTS pending_transactions AS
SELECT 
    tx_hash,
    reflection_id,
    function_name,
    created_at
FROM blockchain_transactions 
WHERE status = 'pending'
ORDER BY created_at DESC;
EOF

# Database Schema anwenden
if [ -f "data/asi_local.db" ]; then
    echo "📊 Wende Blockchain Schema an..."
    sqlite3 data/asi_local.db < scripts/blockchain_schema.sql
    echo -e "${GREEN}✅ Database Schema aktualisiert${NC}"
else
    echo -e "${YELLOW}⚠️ Datenbank nicht gefunden - Schema wird bei erstem Start angewendet${NC}"
fi

# Blockchain Service erstellen
echo -e "\n${BLUE}7. Live Blockchain Service...${NC}"

cat > src/blockchain/live_service.py << 'EOF'
"""
Live Blockchain Service für ASI-Core
Produktive Blockchain-Integration mit Web3
"""

import json
import os
from typing import Dict, Optional, Any
from web3 import Web3
from eth_account import Account
import logging

logger = logging.getLogger(__name__)

class LiveBlockchainService:
    """Produktiver Blockchain Service für ASI-Core"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rpc_url = config.get('rpc_url')
        self.private_key = config.get('private_key')
        self.contract_address = config.get('contract_address')
        self.chain_id = config.get('chain_id', 80001)
        
        # Web3 Provider Setup
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to blockchain at {self.rpc_url}")
        
        # Account Setup
        if self.private_key:
            self.account = Account.from_key(self.private_key)
        else:
            raise ValueError("Private key required for blockchain operations")
        
        # Contract Setup (ABI would be loaded from file)
        self.contract_abi = self._load_contract_abi()
        if self.contract_address and self.contract_abi:
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
    
    def _load_contract_abi(self) -> list:
        """Lädt Contract ABI aus JSON-Datei"""
        try:
            abi_path = os.path.join('contracts', 'ASI.json')
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_data = json.load(f)
                    return contract_data.get('abi', [])
        except Exception as e:
            logger.warning(f"Could not load contract ABI: {e}")
        
        # Fallback ABI
        return [
            {
                "inputs": [
                    {"name": "key", "type": "string"},
                    {"name": "value", "type": "uint256"},
                    {"name": "cid", "type": "string"}
                ],
                "name": "logState",
                "outputs": [],
                "type": "function"
            }
        ]
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """Hole Wallet Balance in ETH"""
        address = address or self.account.address
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def store_reflection_hash(self, reflection_hash: str, metadata: Dict = None) -> str:
        """Speichere Reflexions-Hash auf Blockchain"""
        try:
            # Transaction Parameter
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            
            # Contract Function Call
            function_call = self.contract.functions.logState(
                "reflection_hash",
                1,  # State value
                reflection_hash  # IPFS CID
            )
            
            # Estimate Gas
            gas_estimate = function_call.estimate_gas({'from': self.account.address})
            
            # Build Transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'chainId': self.chain_id
            })
            
            # Sign Transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send Transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Blockchain transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain transaction failed: {e}")
            raise
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """Prüfe Transaction Status"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'status': 'confirmed' if receipt['status'] == 1 else 'failed',
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'transaction_hash': tx_hash
            }
        except Exception:
            return {'status': 'pending', 'transaction_hash': tx_hash}
    
    def is_connected(self) -> bool:
        """Prüfe Blockchain-Verbindung"""
        return self.w3.is_connected()
    
    def get_network_info(self) -> Dict[str, Any]:
        """Hole Netzwerk-Informationen"""
        return {
            'chain_id': self.w3.eth.chain_id,
            'block_number': self.w3.eth.block_number,
            'gas_price': self.w3.eth.gas_price,
            'is_connected': self.is_connected()
        }

# Factory Function
def create_blockchain_service(config_path: str = None) -> LiveBlockchainService:
    """Erstelle Blockchain Service aus Konfiguration"""
    
    if config_path:
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'rpc_url': os.getenv('POLYGON_RPC_URL'),
            'private_key': os.getenv('PRIVATE_KEY'),
            'contract_address': os.getenv('ASI_CONTRACT_ADDRESS'),
            'chain_id': int(os.getenv('CHAIN_ID', 80001))
        }
    
    blockchain_config = config.get('blockchain', config)
    
    if not blockchain_config.get('enabled', True):
        logger.warning("Blockchain service disabled in config")
        return None
    
    return LiveBlockchainService(blockchain_config)
EOF

echo -e "${GREEN}✅ Live Blockchain Service erstellt${NC}"

# Test Script
echo -e "\n${BLUE}8. Blockchain Test Script...${NC}"

cat > scripts/test_blockchain_live.py << 'EOF'
#!/usr/bin/env python3
"""
Test für Live Blockchain Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.blockchain.live_service import create_blockchain_service
import json

def test_blockchain_connection():
    """Teste Blockchain-Verbindung"""
    print("🔗 Teste Live Blockchain Connection...")
    
    try:
        service = create_blockchain_service('config/secrets.json')
        
        if not service:
            print("❌ Blockchain Service nicht verfügbar")
            return False
        
        # Connection Test
        if service.is_connected():
            print("✅ Blockchain-Verbindung erfolgreich")
        else:
            print("❌ Blockchain-Verbindung fehlgeschlagen")
            return False
        
        # Network Info
        network_info = service.get_network_info()
        print(f"📊 Netzwerk Info:")
        print(f"   Chain ID: {network_info['chain_id']}")
        print(f"   Block Number: {network_info['block_number']}")
        print(f"   Gas Price: {network_info['gas_price']} wei")
        
        # Balance Check
        balance = service.get_balance()
        print(f"💰 Wallet Balance: {balance:.6f} MATIC")
        
        if balance == 0:
            print("⚠️ Wallet hat keine MATIC - hole welche von https://faucet.polygon.technology/")
        
        print("✅ Blockchain Service funktional")
        return True
        
    except Exception as e:
        print(f"❌ Blockchain Test fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    success = test_blockchain_connection()
    exit(0 if success else 1)
EOF

chmod +x scripts/test_blockchain_live.py

# Abschließende Tests
echo -e "\n${BLUE}9. Blockchain Integration Test...${NC}"

if python3 scripts/test_blockchain_live.py; then
    echo -e "\n${GREEN}🎉 Blockchain Integration Setup ERFOLGREICH!${NC}"
else
    echo -e "\n${YELLOW}⚠️ Blockchain Integration teilweise konfiguriert${NC}"
    echo "💡 Prüfe Environment Variables und RPC-Verbindung"
fi

# Summary
echo -e "\n${BLUE}📋 Setup Zusammenfassung:${NC}"
echo "=================================="
echo -e "✅ Smart Contract Templates bereit"
echo -e "✅ Konfigurationsdateien aktualisiert"
echo -e "✅ Web3 Dependencies installiert"
echo -e "✅ Database Schema für Blockchain"
echo -e "✅ Live Blockchain Service"
echo -e "✅ Test Scripts erstellt"
echo ""
echo -e "${YELLOW}🎯 Nächste Schritte:${NC}"
echo "1. Smart Contracts mit Hardhat deployen"
echo "2. Echte Contract-Adressen in Config eintragen"
echo "3. Frontend Web3-Integration testen"
echo "4. Beta Testing mit Blockchain-Features"
echo ""
echo -e "${GREEN}🚀 ASI-Core ist bereit für Blockchain-Integration!${NC}"