#!/usr/bin/env bash

# ASI-Core Initial Setup Script
# Führt die erstmalige Einrichtung des Systems durch

set -e

echo "🛠️  ASI-Core Initial Setup"
echo "=========================="
echo ""

# Funktion für User-Input mit Default
get_input() {
    local prompt="$1"
    local default="$2"
    local input
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        echo "${input:-$default}"
    else
        read -p "$prompt: " input
        echo "$input"
    fi
}

# Funktion für Ja/Nein Fragen
ask_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local input
    
    read -p "$prompt [y/n] [$default]: " input
    input="${input:-$default}"
    
    if [[ "$input" =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# 1. System-Check
echo "📋 System Requirements Check"
echo "----------------------------"

# Python prüfen
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo "✓ Python $python_version found"
else
    echo "✗ Python 3 not found! Please install Python 3.10+"
    exit 1
fi

# Git prüfen
if command -v git &> /dev/null; then
    echo "✓ Git found"
else
    echo "✗ Git not found! Please install git"
    exit 1
fi

echo ""

# 2. Konfiguration
echo "⚙️  Configuration"
echo "----------------"

# Environment auswählen
environment=$(get_input "Environment (development/production)" "development")

# Blockchain-Setup
if ask_yes_no "Enable blockchain features?"; then
    enable_blockchain="true"
    echo ""
    echo "🔗 Blockchain Configuration"
    rpc_url=$(get_input "RPC URL" "https://rpc-mumbai.maticvigil.com/")
    echo "⚠️  Private key will be needed in .env file (DO NOT COMMIT!)"
else
    enable_blockchain="false"
fi

# IPFS-Setup
if ask_yes_no "Enable IPFS storage?"; then
    enable_ipfs="true"
    ipfs_url=$(get_input "IPFS API URL" "http://localhost:5001")
else
    enable_ipfs="false"
fi

# Arweave-Setup
if ask_yes_no "Enable Arweave storage?"; then
    enable_arweave="true"
    arweave_gateway=$(get_input "Arweave Gateway" "https://arweave.net")
else
    enable_arweave="false"
fi

echo ""

# 3. Dateien erstellen
echo "📁 Creating Files"
echo "-----------------"

# .env Datei erstellen
cat > .env << EOF
# ASI-Core Environment Configuration
# Generated: $(date)

# Environment
ENVIRONMENT=$environment

# Blockchain
ENABLE_BLOCKCHAIN=$enable_blockchain
MUMBAI_RPC_URL=${rpc_url:-}
PRIVATE_KEY=
ASI_CONTRACT_ADDRESS=

# Storage
ENABLE_IPFS=$enable_ipfs
IPFS_API_URL=${ipfs_url:-http://localhost:5001}
ENABLE_ARWEAVE=$enable_arweave
ARWEAVE_GATEWAY=${arweave_gateway:-https://arweave.net}

# API Settings
ASI_DEBUG=true
ASI_HOST=0.0.0.0
ASI_PORT=5000
ASI_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Features
AUTO_UPLOAD_IPFS=false
AUTO_UPLOAD_ARWEAVE=false
AUTO_REGISTER_ON_CHAIN=false
EOF

echo "✓ Created .env file"

# Config-Dateien kopieren
if [ ! -f "config/settings.json" ]; then
    if [ -f "config/settings.example.json" ]; then
        cp config/settings.example.json config/settings.json
        echo "✓ Created config/settings.json"
    fi
fi

if [ ! -f "config/secrets.json" ]; then
    if [ -f "config/secrets.example.json" ]; then
        cp config/secrets.example.json config/secrets.json
        echo "✓ Created config/secrets.json"
    fi
fi

# .gitignore prüfen
if ! grep -q ".env" .gitignore 2>/dev/null; then
    echo -e "\n# Environment files\n.env\nconfig/secrets.json\ndata/local/wallet.json" >> .gitignore
    echo "✓ Updated .gitignore"
fi

echo ""

# 4. Dependencies installieren
echo "📦 Installing Dependencies"
echo "-------------------------"

# Virtual Environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Created virtual environment"
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

echo ""

# 5. Verzeichnisse erstellen
echo "📂 Creating Directories"
echo "----------------------"

directories=(
    "data/reflections"
    "data/backups"
    "data/states"
    "data/state_exports"
    "data/search"
    "data/local"
    "contracts"
    "logs"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "✓ $dir"
done

echo ""

# 6. Optional: Test-Daten
if ask_yes_no "Generate test data?"; then
    python tests/generate_test_data.py
    echo "✓ Test data generated"
fi

echo ""

# 7. Abschluss
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your private keys (if using blockchain)"
echo "2. Review config/settings.json for your preferences"
echo "3. Run './start.sh' to start the system"
echo ""
echo "Documentation: https://github.com/swisscomfort/asi-core"
echo ""
echo "Happy reflecting! 🧠✨"
