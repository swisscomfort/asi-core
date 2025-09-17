#!/usr/bin/env bash

# ASI-Core Startup Script
# Automatisches Setup und Start des Systems

set -e  # Exit on error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🚀 ASI-Core System Starter          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Funktion für Statusmeldungen
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Python Version prüfen
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    log_info "Python $python_version detected (OK)"
else
    log_error "Python $python_version detected (minimum required: $required_version)"
    exit 1
fi

# Verzeichnisse erstellen
echo -e "\n${BLUE}Creating necessary directories...${NC}"
directories=(
    "data/reflections"
    "data/backups"
    "data/states"
    "data/state_exports"
    "data/search"
    "data/local"
    "contracts"
    "logs"
    "config"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    log_info "Directory: $dir"
done

# Virtual Environment prüfen/erstellen
echo -e "\n${BLUE}Setting up Python environment...${NC}"
if [ ! -d ".venv" ]; then
    log_warning "Virtual environment not found, creating..."
    python3 -m venv .venv
    log_info "Virtual environment created"
else
    log_info "Virtual environment found"
fi

# Aktiviere venv
source .venv/bin/activate
log_info "Virtual environment activated"

# Requirements installieren
echo -e "\n${BLUE}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    log_info "Dependencies installed"
else
    log_error "requirements.txt not found!"
    exit 1
fi

# Config-Dateien prüfen
echo -e "\n${BLUE}Checking configuration...${NC}"
if [ ! -f "config/settings.json" ]; then
    if [ -f "config/settings.example.json" ]; then
        cp config/settings.example.json config/settings.json
        log_warning "Created config/settings.json from example"
    else
        log_error "No configuration found!"
    fi
else
    log_info "Configuration found"
fi

if [ ! -f "config/secrets.json" ]; then
    if [ -f "config/secrets.example.json" ]; then
        cp config/secrets.example.json config/secrets.json
        log_warning "Created config/secrets.json from example (UPDATE REQUIRED!)"
    fi
else
    log_info "Secrets configuration found"
fi

# IPFS prüfen (optional)
echo -e "\n${BLUE}Checking optional services...${NC}"
if command -v ipfs &> /dev/null; then
    log_info "IPFS detected"
    # IPFS daemon im Hintergrund starten falls nicht läuft
    if ! pgrep -x "ipfs" > /dev/null; then
        log_warning "Starting IPFS daemon in background..."
        ipfs daemon --init &> logs/ipfs.log &
        sleep 2
    else
        log_info "IPFS daemon already running"
    fi
else
    log_warning "IPFS not installed (optional - for decentralized storage)"
fi

# Test-Daten generieren (falls leer)
echo -e "\n${BLUE}Checking test data...${NC}"
if [ ! "$(ls -A data/reflections 2>/dev/null)" ]; then
    log_warning "No reflections found, generating test data..."
    python tests/generate_test_data.py
    log_info "Test data generated"
else
    reflection_count=$(ls -1 data/reflections/*.json 2>/dev/null | wc -l)
    log_info "Found $reflection_count existing reflections"
fi

# Start-Optionen
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}ASI-Core is ready!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""
echo "Choose startup mode:"
echo "  1) Interactive CLI Mode"
echo "  2) Web Interface (Flask)"
echo "  3) API Server only"
echo "  4) Run Tests"
echo "  5) Generate Documentation"
echo "  6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Interactive CLI...${NC}"
        python main.py
        ;;
    2)
        echo -e "\n${GREEN}Starting Web Interface...${NC}"
        python main.py serve
        ;;
    3)
        echo -e "\n${GREEN}Starting API Server...${NC}"
        python api_server.py
        ;;
    4)
        echo -e "\n${GREEN}Running Tests...${NC}"
        pytest tests/ -v
        ;;
    5)
        echo -e "\n${GREEN}Generating Documentation...${NC}"
        python -m pydoc -w src/
        log_info "Documentation generated in current directory"
        ;;
    6)
        echo -e "\n${BLUE}Goodbye!${NC}"
        exit 0
        ;;
    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac
