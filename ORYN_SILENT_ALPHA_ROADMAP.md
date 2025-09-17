# 🗺️ Oryn "Silent Alpha" Entwicklungsroadmap

> **Ziel**: Transformation des ASI-Core Systems zum dezentralen Oryn Bürgerprojekt
> **Basis**: Vorhandene Smart Contracts, Agent-System und Blockchain-Integration
> **Timeline**: 11-22 Wochen bis "Go-Public"

---

## 📊 **Übersicht der Silent Alpha-Phasen**

| Phase | Dauer | Schwerpunkt | Deliverables |
|-------|-------|-------------|--------------|
| **Phase 1** | 2-4 Wochen | Grundgerüst | Core Smart Contracts, MVP Ticket-Board |
| **Phase 2** | 3-6 Wochen | Autopilot | Automatisierte Ticket-Generierung |
| **Phase 3** | 6-12 Wochen | Governance | Dispute-Resolution, Recovery-Flows |

---

## 🏗️ **Phase 1: Grundgerüst (2-4 Wochen)**

### **Woche 1-2: Smart Contract Transformation**

#### **1.1 Oryn Core Contracts entwickeln**
- [ ] **TicketRegistry.sol** (erweitert bestehende TaskRegistry.sol)
  ```solidity
  struct Ticket {
    bytes32 id;
    string title;
    string doD;  // Definition of Done (YAML)
    uint256 creditReward;
    address claimedBy;
    TicketState state;  // open → claimed → submitted → approved
    string evidenceCID;
    uint256 createdAt;
  }
  ```

- [ ] **CreditLedger.sol** (nicht handelbare Credits)
  ```solidity
  mapping(address => uint256) private credits;
  mapping(address => bool) private canTransfer; // immer false
  ```

- [ ] **ReputationSBT.sol** (Soulbound Token)
  ```solidity
  struct ReputationProfile {
    uint256 totalContributions;
    uint256 qualityScore;
    uint256 lastActivity;
    uint256 decayTimestamp;
  }
  ```

- [ ] **MilestoneOrchestrator.sol** (bereits vorhanden, erweitern)
  - Integration mit TicketRegistry
  - Meilenstein-basierte Ticket-Freischaltung

#### **1.2 Verifier-Service (Python-Stub)**
- [ ] **Basis-Verifier implementieren**
  ```python
  class TicketVerifier:
    def verify_evidence(self, evidence_cid: str) -> VerificationResult
    def generate_signed_report(self, result: VerificationResult) -> str
    def call_approve_ticket(self, ticket_id: str, report_cid: str)
  ```

- [ ] **Prüftypen implementieren**
  - Code-Quality-Checks (Lint, Tests)
  - Dokumentation-Vollständigkeit
  - Barrierefreiheit (Lighthouse/a11y)
  - Community-Standards

### **Woche 3-4: PWA Ticket-Board MVP**

#### **1.3 Grundfunktionen des Ticket-Boards**
- [ ] **Ticket-Browser Interface**
  - Liste verfügbarer Tickets
  - Filter nach Kategorie/Schwierigkeit
  - "Claim Ticket" Funktionalität

- [ ] **Submission Interface**
  - Evidence-Upload zu IPFS
  - Ticket-Einreichung mit CID
  - Status-Tracking

- [ ] **Wallet-Integration**
  - MetaMask/WalletConnect
  - Polygon Mumbai Testnet
  - Gas-optimierte Transaktionen

#### **1.4 Basis-Tickets erstellen (10-15 Stück)**
```yaml
# Beispiel: ticket-001.yaml
title: "Chat-Funktion E2E-Verschlüsselung hinzufügen"
category: "security"
difficulty: "medium"
credit_reward: 50
dod: |
  - WebCrypto API für E2E-Verschlüsselung implementiert
  - Schlüsselaustausch über Signal-Protokoll
  - Unit-Tests für Verschlüsselung/Entschlüsselung
  - Dokumentation der Sicherheitsarchitektur
evidence_requirements:
  - code_review: true
  - tests_passing: true
  - security_audit: true
```

#### **1.5 Deployment & Testing**
- [ ] **Contracts auf Mumbai deployen**
- [ ] **IPFS-Cluster für Evidence-Storage**
- [ ] **PWA auf Vercel/Netlify**
- [ ] **End-to-End Tests**

---

## ⚙️ **Phase 2: Autopilot (3-6 Wochen)**

### **Woche 5-7: Automatisierte Ticket-Generierung**

#### **2.1 NeedsIngestor**
```python
class NeedsIngestor:
    def scan_github_issues(self) -> List[Need]
    def detect_i18n_gaps(self) -> List[Need]
    def analyze_user_feedback(self) -> List[Need]
    def prioritize_needs(self, needs: List[Need]) -> List[Need]
```

- [ ] **GitHub Integration**
  - Issues, PRs, und Bugs automatisch erfassen
  - Complexity-Scoring basierend auf Labels/Comments
  - Community-Prioritäten extrahieren

- [ ] **Accessibility Scanner**
  - Lighthouse-Reports automatisch erstellen
  - A11y-Gaps in Tickets umwandeln
  - WCAG-Compliance-Tracking

#### **2.2 TicketFactory**
```python
class TicketFactory:
    def generate_from_template(self, need: Need) -> Ticket
    def calculate_fair_reward(self, complexity: int, impact: int) -> int
    def ensure_deterministic_output(self, input_hash: str) -> Ticket
```

- [ ] **Template-System**
  - Vordefinierte Ticket-Templates
  - Dynamische DoD-Generierung
  - Skill-Level-Matching

- [ ] **Reward-Algorithmus**
  ```python
  credit_reward = (complexity_score * 10) + (impact_multiplier * 20) + base_reward
  ```

### **Woche 8-10: Credit-Allokation & Community-Features**

#### **2.3 CreditAllocator**
- [ ] **Faire Belohnungsverteilung**
  - Qualitäts-basierte Multiplikatoren
  - Streak-Boni für konsistente Beiträge
  - Kollaborations-Prämien

- [ ] **Credit-Verwendung implementieren**
  - Erweiterte Speicher-Quotas
  - Übersetzungsdienste
  - Premium-KI-Features

#### **2.4 Community-Wachstum Features**
- [ ] **Onboarding-Flow**
  - Interactive Tutorial
  - Erste einfache Tickets
  - Mentor-Matching

- [ ] **Leaderboards & Stats**
  - Anonyme Reputation-Rankings
  - Kollektive Erfolgsmetriken
  - Fortschritts-Visualisierung

---

## 🏛️ **Phase 3: Governance (6-12 Wochen)**

### **Woche 11-16: Fortgeschrittene Governance**

#### **3.1 Reputation-Decay System**
```solidity
function calculateCurrentReputation(address user) external view returns (uint256) {
    ReputationProfile memory profile = reputations[user];
    uint256 timePassed = block.timestamp - profile.lastActivity;
    uint256 decayFactor = calculateDecayFactor(timePassed);
    return (profile.totalReputation * decayFactor) / 1000;
}
```

- [ ] **Decay-Algorithmus implementieren**
  - Exponentieller Verfall nach 6 Monaten Inaktivität
  - Ausnahmen für kritische Infrastruktur-Beiträge
  - Reaktivierungs-Mechanismen

#### **3.2 Dispute-Panel System**
```solidity
contract DisputeResolution {
    struct DisputePanel {
        address[] reviewers;
        bytes32 ticketId;
        uint256 deadline;
        mapping(address => bool) votes;
    }
    
    function createRandomPanel(bytes32 ticketId) external returns (bytes32 panelId)
    function submitPanelVote(bytes32 panelId, bool approve) external
    function resolveDispute(bytes32 panelId) external
}
```

- [ ] **Zufällige Reviewer-Auswahl**
  - VRF (Verifiable Random Function) für Fairness
  - Reputation-gewichtete Auswahl
  - Interessenkonflikt-Vermeidung

### **Woche 17-22: Recovery & Launch-Vorbereitung**

#### **3.3 Schlüsselverlust-Recovery**
```solidity
contract KeyRecovery {
    struct RecoveryRequest {
        address oldAddress;
        address newAddress;
        uint256 requestTime;
        address[] attestors;
        mapping(address => bool) attestations;
    }
}
```

- [ ] **Neuanfang-Prozess**
  - 7-Tage-Wartezeit für Recovery
  - Community-basierte Attestierung
  - Reputation-Transfer-Mechanismen

#### **3.4 One-Human-Atteste**
- [ ] **Privacy-freundliche ID-Verifizierung**
  - WorldCoin/Gitcoin Passport Integration
  - Zero-Knowledge-Proofs für Menschlichkeit
  - Sybil-Resistance ohne PII

#### **3.5 Go-Public Vorbereitung**
- [ ] **Manifest & Bauplan veröffentlichen**
- [ ] **Community-Dokumentation**
- [ ] **100+ Launch-Tickets vorbereiten**
- [ ] **Presse & Marketing-Material**

---

## 📈 **Meilensteine & KPIs**

### **Phase 1 Success Metrics:**
- ✅ 4 Core Smart Contracts deployed
- ✅ 15 Basis-Tickets verfügbar
- ✅ PWA funktionsfähig auf Testnet
- ✅ 10 Beta-Tester erfolgreich onboarded

### **Phase 2 Success Metrics:**
- ✅ 50+ automatisch generierte Tickets
- ✅ Durchschnittlich 80% Approval-Rate
- ✅ 5+ aktive Contributors
- ✅ Credit-System voll funktionsfähig

### **Phase 3 Success Metrics:**
- ✅ Dispute-Resolution getestet
- ✅ Recovery-Flow implementiert
- ✅ 100+ Community-Members
- ✅ Selbsttragendes Ecosystem

---

## 🔧 **Technische Anforderungen**

### **Entwicklungsumgebung:**
- **Blockchain**: Polygon Mumbai (Testnet) → Polygon Mainnet
- **Frontend**: Progressive Web App (PWA)
- **Backend**: Python (Flask/FastAPI) für Verifier
- **Storage**: IPFS + Arweave für Evidence
- **Deployment**: Vercel/Netlify + Docker

### **Abhängigkeiten:**
- **Bestehende ASI-Core Basis** ✅
- **OpenZeppelin Contracts** ✅
- **Web3.py/Ethers.js** ✅
- **IPFS API** ✅
- **MetaMask Integration** ✅

---

## 🚀 **Sofortige nächste Schritte**

### **Diese Woche startbar:**

1. **TicketRegistry.sol erweitern** (bestehende TaskRegistry.sol anpassen)
2. **CreditLedger.sol implementieren** (nicht-handelbare Variante)
3. **Erste 5 Basis-Tickets erstellen** (basierend auf bestehenden TODOs)
4. **PWA Ticket-Board wireframe** (erweitert bestehende Web-UI)

### **Parallelisierbar:**
- Smart Contract-Entwicklung ⚡ Verifier-Service ⚡ PWA-Frontend

---

## 💡 **Besonderheiten der ASI-zu-Oryn Transformation**

### **Vorteile der bestehenden Basis:**
- ✅ **Agent-System**: Kann als "Contributor-Profil" System wiederverwendet werden
- ✅ **State-Tracking**: Perfekt für anonyme Beitrags-Metriken
- ✅ **Blockchain-Integration**: Bereits Mumbai-ready
- ✅ **Modulare Architektur**: Ideal für Ticket-basierte Entwicklung

### **Synergie-Potentiale:**
- **Bestehende Reflexions-Features** → **Contributor-Analytics**
- **AI-Embedding-System** → **Skill-Matching für Tickets**
- **Hybrid-Model** → **Community + Individual Insights**
- **PWA-Basis** → **Offline-fähiges Ticket-Board**

---

*Diese Roadmap nutzt optimal die bestehende ASI-Core Infrastruktur und transformiert sie schrittweise zum Oryn-System. Jede Phase baut logisch auf der vorherigen auf und kann parallel entwickelt werden.*