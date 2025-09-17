# Oryn Ticket Verifier Service

Automatisierter Service für objektive Ticket-Prüfung und Smart Contract Integration.

## Features

- ✅ **Objektive Verifikation**: Automatisierte Checks für Code-Qualität, Tests, Dokumentation
- ✅ **IPFS Integration**: Evidence-Upload und Verifier-Report-Speicherung  
- ✅ **Smart Contract Integration**: Automatische Ticket-Approval via TicketRegistry
- ✅ **Kategorien-spezifische Checks**: Security, UI/A11y, Dokumentation, Translation
- ✅ **Daemon-Modus**: Kontinuierliche Überwachung neuer Submissions
- ✅ **Mock-Modus**: Entwicklung ohne echte Blockchain/IPFS

## Installation

```bash
cd oryn-verifier
pip install -r requirements.txt
```

### Abhängigkeiten

```txt
web3>=6.0.0
eth-account>=0.8.0
ipfshttpclient>=0.8.0a2
pyyaml>=6.0
requests>=2.28.0
asyncio
```

## Konfiguration

### config.yaml
```yaml
ipfs_enabled: false          # Echter IPFS oder Mock
web3_enabled: false          # Echte Blockchain oder Mock  
strict_mode: false           # Strenge Validierung
quality_threshold: 0.7       # Mindest-Score für Approval

supported_categories:
  - security
  - ui
  - docs
  - translation
  - testing

check_weights:
  code_review: 0.3
  tests_passing: 0.25
  documentation: 0.2
  accessibility: 0.15
  security_scan: 0.1
```

### Umgebungsvariablen

```bash
export MUMBAI_RPC_URL="https://rpc-mumbai.maticvigil.com/"
export PRIVATE_KEY="0x..."
export TICKET_REGISTRY_ADDRESS="0x..."
export IPFS_API_URL="/ip4/127.0.0.1/tcp/5001"
```

## Nutzung

### Einzelne Verifikation
```python
from ticket_verifier import TicketVerifier

verifier = TicketVerifier()

# Ticket verifizieren
result = await verifier.verify_ticket_evidence(
    ticket_id="ticket_001",
    evidence_cid="QmEvidence123"
)

# On-chain approval
if result.passed:
    tx_hash = await verifier.approve_ticket_on_chain(result)
```

### Daemon-Modus
```bash
python ticket_verifier.py
```

## Verifikations-Checks

### 1. Code Review Check
- GitHub PR-Analyse
- Maintainer-Approval
- Code-Qualität (Lint, Complexity)
- Review-Comments

### 2. Tests Check  
- Test-Suite Erfolg
- Code-Coverage
- Neue Tests für Features

### 3. Documentation Check
- README-Updates
- API-Dokumentation
- Code-Kommentare

### 4. Security Check (für Security-Tickets)
- Vulnerability-Scans
- Secure Coding Patterns
- Sensitive Data Handling

### 5. Accessibility Check (für UI-Tickets)
- Lighthouse-Score
- WCAG-Compliance
- Keyboard-Navigation

## Evidence-Format

```json
{
  "type": "code_submission",
  "github_pr": "https://github.com/oryn/repo/pull/123",
  "files_changed": ["src/auth.js", "tests/auth.test.js"],
  "description": "Implemented E2E encryption for chat",
  "tests_passing": true,
  "lint_passed": true,
  "documentation_updated": true
}
```

## Verifier-Report

```json
{
  "ticket_id": "ticket_001",
  "evidence_cid": "QmEvidence123", 
  "passed": true,
  "score": 0.85,
  "checks_performed": ["code_review", "tests_passing", "documentation"],
  "details": {
    "code_review": {
      "passed": true,
      "score": 0.85,
      "details": {
        "pr_url": "https://github.com/oryn/repo/pull/123",
        "approved_by_maintainer": true
      }
    }
  },
  "verification_timestamp": "2025-09-17T14:30:00Z",
  "verifier_version": "0.1.0-alpha"
}
```

## Smart Contract Integration

Der Verifier ruft automatisch `TicketRegistry.approveTicket()` auf:

```solidity
function approveTicket(
    bytes32 ticketId,
    bytes32 verifierReportCID
) external onlyRole(VERIFIER_ROLE)
```

## Entwicklung

### Mock-Modus
Für Entwicklung ohne echte Blockchain/IPFS:

```python
verifier = TicketVerifier()  # Verwendet automatisch Mocks
```

### Tests ausführen
```bash
python -m pytest tests/
```

### Neue Check-Types hinzufügen

```python
async def _check_performance(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Custom Performance Check"""
    lighthouse_score = evidence.get("lighthouse_performance", 0)
    
    return {
        "passed": lighthouse_score >= 90,
        "score": lighthouse_score / 100,
        "details": {"lighthouse_performance": lighthouse_score}
    }
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ticket_verifier.py .
COPY config.yaml .

CMD ["python", "ticket_verifier.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oryn-verifier
spec:
  replicas: 1
  selector:
    matchLabels:
      app: oryn-verifier
  template:
    metadata:
      labels:
        app: oryn-verifier
    spec:
      containers:
      - name: verifier
        image: oryn/ticket-verifier:latest
        env:
        - name: MUMBAI_RPC_URL
          valueFrom:
            secretKeyRef:
              name: oryn-secrets
              key: rpc-url
```

## Roadmap

### Phase 1 (aktuell)
- ✅ Basis-Verifier mit Mock-Clients
- ✅ Core Verification-Checks
- ✅ YAML-Konfiguration

### Phase 2
- [ ] Echte IPFS/Blockchain-Integration
- [ ] GitHub/GitLab API-Integration
- [ ] Lighthouse-Integration für A11y
- [ ] Security-Scanner (Semgrep, CodeQL)

### Phase 3  
- [ ] Machine Learning für Code-Quality
- [ ] Multi-Verifier Consensus
- [ ] Advanced Dispute Resolution
- [ ] Performance Monitoring