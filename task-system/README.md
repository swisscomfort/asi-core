# ASI Core Task System - Python Workflow Tools

Diese Python-Tools ermöglichen einen nahtlosen Workflow für Contributors im ASI Core Task System.

## 🛠️ Tools Übersicht

### 1. register_tasks.py - Task Registration Tool
**Für Maintainer**: Registriert Tasks aus YAML-Sheets auf der Blockchain.

```bash
# Einzelnen Task registrieren
python register_tasks.py --task M1-T001 --dry-run
python register_tasks.py --task M1-T001 --deploy

# Ganzen Milestone registrieren
python register_tasks.py --milestone M1

# Alle Tasks registrieren
python register_tasks.py --all

# Setup validieren
python register_tasks.py --validate

# Tasks auflisten
python register_tasks.py --list M1
```

**Features:**
- ✅ IPFS Integration für Task-Sheet Storage
- ✅ Smart Contract Interaction (TaskRegistry)
- ✅ Multi-Token Support (ASI, USDC, MATIC)
- ✅ Gas Estimation & Transaction Management
- ✅ Dry-Run Mode für Testing
- ✅ Batch Operations für Milestones

### 2. submit_evidence.py - Evidence Submission Tool
**Für Contributors**: Reicht Arbeitsnachweise für geclaimte Tasks ein.

```bash
# Evidence mit GitHub PR
python submit_evidence.py --task M1-T001 --github-pr 42 --demo-url https://demo.com

# Evidence mit Files
python submit_evidence.py --task M1-T001 --files src/ docs/ --description "MVP completed"

# Auto-packaging
python submit_evidence.py --task M1-T001 --auto-package --message "Final submission"

# Task Status checken
python submit_evidence.py --task M1-T001 --status
```

**Features:**
- ✅ Automated Evidence Packaging
- ✅ GitHub Integration (PR references, commit hashes)
- ✅ File Content Analysis & Packaging
- ✅ Deliverable Validation gegen Task-Sheet
- ✅ IPFS Upload für Evidence
- ✅ Smart Contract Evidence Submission
- ✅ Deadline & Status Checking

### 3. pin_to_ipfs.py - IPFS Pinning Tool
**Universell**: Pinnt Files, Directories und Content auf IPFS.

```bash
# File pinnen
python pin_to_ipfs.py --file evidence.json --name "task-evidence"

# Directory pinnen
python pin_to_ipfs.py --directory evidence/ --recursive

# JSON Data pinnen
python pin_to_ipfs.py --json '{"task": "M1-T001", "status": "complete"}'

# URL Content pinnen
python pin_to_ipfs.py --url https://example.com/file.pdf

# Services checken
python pin_to_ipfs.py --check-services

# Pins auflisten
python pin_to_ipfs.py --list
```

**Features:**
- ✅ Multi-Service Support (Local IPFS, Pinata)
- ✅ Automatic Service Failover
- ✅ Content Deduplication
- ✅ URL Download & Pin
- ✅ Directory Recursive Pinning
- ✅ Pin Cache & Metadata
- ✅ Status Monitoring

## 🔧 Setup & Konfiguration

### 1. Dependencies installieren
```bash
pip install web3 requests pyyaml eth-account
```

### 2. Konfiguration erstellen
```json
{
  "rpc_url": "https://rpc-mumbai.maticvigil.com/",
  "task_registry_address": "0x...",
  "reward_vault_address": "0x...",
  "asi_token_address": "0x...",
  "ipfs_api_url": "http://127.0.0.1:5001",
  "use_pinata": false,
  "pinata_api_key": "your-key",
  "pinata_secret_key": "your-secret"
}
```

Speichern als `config/task-registry.json` oder `config/ipfs-config.json`.

### 3. Environment Variables
```bash
export PRIVATE_KEY="0x..."
export RPC_URL="https://rpc-mumbai.maticvigil.com/"
export TASK_REGISTRY_ADDRESS="0x..."
export REWARD_VAULT_ADDRESS="0x..."
export IPFS_API_URL="http://127.0.0.1:5001"
export GITHUB_USERNAME="yourusername"
export GITHUB_REPO="asi-org/asi-core"
```

## 🚀 Contributor Workflow

### 1. Task claimen (via Web UI oder direkt)
```bash
# Task Status checken
python submit_evidence.py --task M1-T001 --status
```

### 2. Arbeit erledigen
- Code schreiben
- Documentation erstellen
- Tests implementieren
- Demo deployen

### 3. Evidence einreichen
```bash
# Auto-Discovery mit GitHub Integration
python submit_evidence.py \
  --task M1-T001 \
  --github-pr 42 \
  --demo-url https://your-demo.vercel.app \
  --auto-package \
  --description "MVP mit vollständiger Integration"
```

### 4. Verifikation abwarten
Das Verifier Service analysiert automatisch:
- ✅ GitHub PR Status
- ✅ CI/CD Results
- ✅ Demo Functionality
- ✅ Code Quality
- ✅ Documentation Completeness

## 🏗️ Maintainer Workflow

### 1. Task-Sheets erstellen
```yaml
# tasks/M1/M1-T001.yaml
task_id: "M1-T001"
title: "Progressive Web App Foundation"
bounty:
  token: "ASI"
  amount: 2500
dependencies: ["M0-T001", "M0-T002"]
deliverables:
  - "GitHub Pull Request with PWA implementation"
  - "Live demo URL with working offline functionality"
  - "Documentation covering setup and usage"
```

### 2. Tasks registrieren
```bash
# Milestone validieren
python register_tasks.py --list M1

# Dry-run für Testing
python register_tasks.py --milestone M1 --dry-run

# Production deployment
python register_tasks.py --milestone M1
```

### 3. System monitoring
```bash
# Service Status
python pin_to_ipfs.py --check-services

# Setup validieren
python register_tasks.py --validate
```

## 🔐 Security Features

### Smart Contract Integration
- ✅ Role-based Access Control
- ✅ Deadline Enforcement
- ✅ Evidence Verification Requirements
- ✅ Automatic Payout Protection

### IPFS Security
- ✅ Content Addressing (immutable CIDs)
- ✅ Multi-Service Redundancy
- ✅ Cache & Backup Systems
- ✅ Access Control via Private Nodes

### Transaction Safety
- ✅ Gas Estimation & Limits
- ✅ Transaction Receipt Verification
- ✅ Dry-run Mode für Testing
- ✅ Error Handling & Rollback

## 📊 Monitoring & Analytics

### Evidence Tracking
```bash
# Pin Status für Evidence CID
python pin_to_ipfs.py --status QmYourEvidenceCID

# Task Status on-chain
python submit_evidence.py --task M1-T001 --status
```

### System Health
```bash
# IPFS Services
python pin_to_ipfs.py --check-services

# Blockchain Connection
python register_tasks.py --validate
```

## 🚀 Skalierung & Performance

### Batch Operations
- ✅ Multi-Task Registration
- ✅ Directory Pinning
- ✅ Rate Limiting zwischen Requests

### Caching & Optimization
- ✅ IPFS Pin Cache
- ✅ File Deduplication
- ✅ Content Compression
- ✅ Smart Contract Call Optimization

### Error Recovery
- ✅ Service Failover
- ✅ Transaction Retry Logic
- ✅ Partial Success Handling

## 🎯 Nächste Schritte

1. **Testing**: Alle Tools mit Mumbai Testnet testen
2. **UI Integration**: Web Interface für einfachere Nutzung
3. **Monitoring Dashboard**: Real-time Task & Evidence Tracking
4. **Mobile App**: Native App für Contributors
5. **Advanced Analytics**: KPIs, Performance Metrics, Contributor Rankings

Die Python Tools bilden das **Backend-Fundament** für das revolutionäre ASI Core Task System - von hier aus können Millionen von Contributors nahtlos zusammenarbeiten! 🌍✨