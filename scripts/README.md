# ASI Core Python Workflow Scripts

Vollständige Python-basierte Workflow-Tools für das ASI Core Task-Registry System.

## 🎯 Überblick

Diese Scripts ermöglichen es jedem Contributor, nahtlos am ASI Core Projekt zu partizipieren:

- **Task-Registration**: Maintainer können Tasks on-chain registrieren
- **Evidence Submission**: Contributors können Beweise für erledigte Tasks einreichen  
- **IPFS Management**: Dezentrale Speicherung aller Artefakte
- **Workflow Management**: Kompletter Lifecycle von Claim bis Payout

## 📁 Scripts

### 1. `register_tasks.py` - Task Registration (Maintainer)
```bash
# Alle Tasks auflisten
python register_tasks.py list

# Tasks eines Milestones auflisten  
python register_tasks.py list M1

# Tasks on-chain registrieren
python register_tasks.py register M1

# Setup (Contracts deployen)
python register_tasks.py setup
```

### 2. `submit_evidence.py` - Evidence Submission (Contributor)
```bash
# Task claimen
python submit_evidence.py claim M1-T001

# Evidence submitten
python submit_evidence.py submit M1-T001 https://github.com/org/repo/pull/123 ./artifacts/

# Nur Evidence Package erstellen (ohne on-chain)
python submit_evidence.py package M1-T001 https://github.com/org/repo/pull/123

# Payout claimen nach Approval
python submit_evidence.py payout M1-T001

# Task Status checken
python submit_evidence.py status M1-T001
```

### 3. `pin_to_ipfs.py` - IPFS Management
```bash
# IPFS Daemon Status
python pin_to_ipfs.py status

# IPFS Daemon starten
python pin_to_ipfs.py start

# File pinnen
python pin_to_ipfs.py pin ./path/to/file.yaml "task-description"

# Directory pinnen
python pin_to_ipfs.py pin ./evidence/ "evidence-package"

# Alle Pins auflisten
python pin_to_ipfs.py list

# Content von IPFS holen
python pin_to_ipfs.py get QmHashExample ./output.file

# Pin Status verifizieren
python pin_to_ipfs.py verify QmHashExample

# Alle Task-YAML Files bulk pinnen
python pin_to_ipfs.py bulk-tasks
```

### 4. `workflow_manager.py` - Complete Workflow (Contributor)
```bash
# Setup für neue Contributors
python workflow_manager.py setup

# Tasks auflisten
python workflow_manager.py list

# Task starten (claimen)
python workflow_manager.py start M1-T001

# Evidence submitten  
python workflow_manager.py submit M1-T001 https://github.com/org/repo/pull/123 ./artifacts/

# Payout claimen
python workflow_manager.py payout M1-T001

# Status checken
python workflow_manager.py status M1-T001
```

## 🔧 Setup & Installation

### 1. Abhängigkeiten installieren
```bash
pip install web3 pyyaml requests eth-account
```

### 2. IPFS installieren und starten
```bash
# IPFS installieren (Linux)
curl -sSL https://dist.ipfs.tech/kubo/v0.22.0/kubo_v0.22.0_linux-amd64.tar.gz | tar -xz
sudo install kubo/ipfs /usr/local/bin/

# IPFS initialisieren
ipfs init

# IPFS Daemon starten
ipfs daemon
```

### 3. Environment Variables setzen
```bash
# Für Contributors
export CONTRIBUTOR_PRIVATE_KEY="your_private_key_without_0x"

# Für Maintainer  
export DEPLOYER_PRIVATE_KEY="your_deployer_private_key_without_0x"
```

### 4. Contract Adressen konfigurieren
```python
# In den Scripts anpassen:
REGISTRY_ADDRESS = "0xYourTaskRegistryAddress"
VAULT_ADDRESS = "0xYourRewardVaultAddress"
```

## 🚀 Typischer Contributor Workflow

```bash
# 1. Setup
python workflow_manager.py setup

# 2. Verfügbare Tasks anschauen
python workflow_manager.py list M1

# 3. Task claimen
python workflow_manager.py start M1-T001

# 4. Arbeit erledigen:
#    - Task YAML lesen für Requirements
#    - Code schreiben, Tests erstellen
#    - PR erstellen
#    - Screenshots/Artefakte sammeln

# 5. Evidence submitten
python workflow_manager.py submit M1-T001 https://github.com/swisscomfort/asi-core/pull/123 ./build/ ./screenshots/

# 6. Warten auf Verifier Approval

# 7. Payout claimen
python workflow_manager.py payout M1-T001
```

## 📋 Task YAML Format

Jeder Task ist als YAML-Datei definiert:

```yaml
task_id: "M1-T001"
title: "PWA Grundgerüst implementieren"
bounty: 
  token: "ASI"
  amount: 2500
deadline: "2025-10-15"
dependencies: ["M0-T000"]
deliverables:
  - "GitHub PR mit PWA Skeleton (Next.js)"
  - "README mit Setup-Anleitung"
definition_of_done:
  - "CI grün (build+lint+test)"
  - "Lighthouse PWA Score ≥ 90"
  - "E2E-Test: Offline-Funktionalität"
reviewers:
  - "0xReviewerAddress..."
license: "AGPL-3.0"
```

## 🔐 Security Features

- **Private Keys**: Nur lokal gespeichert, nie übertragen
- **IPFS Pinning**: Dezentrale Evidence-Speicherung  
- **On-Chain Verification**: Unveränderbare Task-Records
- **Cryptographic Proofs**: Signierte Verifier Reports

## 📊 Evidence Package Structure

```
evidence/
├── evidence.json          # Metadata  
├── artifacts/            # Code, builds, docs
├── screenshots/          # UI screenshots
└── M1-T001_evidence.zip  # Complete package for IPFS
```

## 🎯 Nächste Schritte

1. **Smart Contracts deployen** auf Testnet
2. **IPFS Cluster** für Redundanz setup
3. **Verifier Service** als automatischen Daemon laufen lassen
4. **Web UI** für non-technical Contributors erstellen

## 💡 Troubleshooting

### IPFS Probleme
```bash
# IPFS neu starten
pkill ipfs
ipfs daemon

# IPFS Repository reparieren
ipfs repo gc
```

### Web3 Connection Issues
```bash
# RPC URL prüfen
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' https://rpc.ankr.com/polygon_mumbai
```

### Private Key Format
```bash
# Korrekt (ohne 0x prefix)
export CONTRIBUTOR_PRIVATE_KEY="abcd1234..."

# Falsch (mit 0x prefix)  
export CONTRIBUTOR_PRIVATE_KEY="0xabcd1234..."
```

---

🚀 **ASI Core = Bürger-getriebene Innovation durch verteilte Tasks!**