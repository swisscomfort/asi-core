# ASI Hybrid Model

Das **ASI Hybrid Model** verbindet **lokale Tiefe** mit **dezentraler, verifizierbarer Wahrheit** im Einklang mit der Philosophie „**Lokal. Anonym. Für immer.**"

## 🏗️ Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Lokale Ebene  │    │ Anonymisierung  │    │ Dezentrale Ebene│
│                 │    │                 │    │                 │
│ • Volltext      │───▶│ • PII Removal   │───▶│ • Nur Zustände  │
│ • Kontext       │    │ • Embeddings    │    │ • CID Links     │
│ • Muster        │    │ • Sentiment     │    │ • Kollektive    │
│ • Privatsphäre  │    │ • Tags          │    │   Statistiken   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Module Übersicht

### `state-tracker.js`

- **Zweck**: Lokale Zustandserfassung und Musteranalyse
- **Features**:
  - Zustände wie `walked`, `meditated`, `focused` tracken
  - Lokale Speicherung in IndexedDB
  - Kontext (Dauer, Stimmung, Zeit) erfassen
  - Muster und Trends analysieren
  - Streak-Berechnung

### `anonymizer.js`

- **Zweck**: Automatische Anonymisierung vor Upload
- **Features**:
  - PII-Erkennung (Namen, Orte, Daten)
  - Lokale Embedding-Generierung
  - Sentiment-Analyse
  - Tag-Extraktion
  - Datenschutz-Validierung

### `chain-interface.js`

- **Zweck**: Verbindung zum Smart Contract auf Polygon
- **Features**:
  - Wallet-Management (seed-basiert)
  - Smart Contract Interaktion
  - State-Logging auf Blockchain
  - Kollektive Statistiken abrufen
  - Gas-Optimierung

### `insight-engine.js`

- **Zweck**: Proaktive Hinweise aus lokalen + kollektiven Mustern
- **Features**:
  - Lokale Muster analysieren
  - Kollektive Erkenntnisse einbeziehen
  - Kontextuelle Empfehlungen
  - Zeitbasierte Insights
  - Prioritäts-Ranking

### `index.js`

- **Zweck**: Hauptschnittstelle für das gesamte Hybrid-System
- **Features**:
  - Orchestrierung aller Module
  - Einheitliche API
  - Datenexport/-import
  - System-Status

## 🔧 Smart Contract

Der `ASIStateTracker.sol` Contract auf Polygon Mumbai:

```solidity
function logState(string key, uint256 value, string cid) external;
function getGlobalStats(string key) external view returns (uint256, uint256, uint256);
```

- **Speichert nur**: Zustand (0/1), CID, Timestamp
- **Keine PII**: Vollständig anonym
- **Gas-optimiert**: Minimaler Storage-Bedarf

## 🚀 Integration in UI

### NewReflectionModal Erweiterungen:

1. **Zustandsauswahl**: Checkboxes für tägliche Aktivitäten
2. **Stimmungserfassung**: Vorher/Nachher Bewertung
3. **Anonymisierungs-Optionen**:
   - "Anonym teilen" für Blockchain
   - "Öffentlich teilen" für traditionelle Uploads
4. **Privacy-Validation**: Automatische PII-Prüfung
5. **Insight-Display**: Proaktive Hinweise anzeigen

## 🔒 Datenschutz-Prinzipien

### Lokale Ebene

- **Vollständige Daten**: Unzensiert und privat
- **IndexedDB**: Browser-lokale Speicherung
- **Kein Cloud-Upload**: Standard-Speicherung bleibt lokal

### Dezentrale Ebene

- **Nur anonymisierte Daten**: Automatische PII-Entfernung
- **State-Codes**: `walked=1`, `meditated=0`, etc.
- **CID-Referenzen**: Links zu IPFS-gespeicherten anonymen Embeddings
- **Keine Rekonstruktion**: Ursprungstext nicht wiederherstellbar

## 🎯 Beispiel-Workflow

1. **Benutzer schreibt Reflexion**: "Heute war ich spazieren und fühle mich besser"

2. **State-Auswahl**: ✅ Spazieren (45 min, Stimmung: gestresst → ruhig)

3. **Anonymisierung**:

   ```
   Lokal: "Heute war ich spazieren und fühle mich besser"
   Anonym: embedding=[0.1, 0.3, ...], sentiment=positive, time_of_day=evening
   ```

4. **Speicherung**:

   - **Lokal**: Volltext + Kontext in IndexedDB
   - **Blockchain**: `walked=1` + CID zu anonymen Daten

5. **Insights**:
   - Lokal: "Du warst 5 Tage in Folge spazieren!"
   - Kollektiv: "89% der Nutzer fühlen sich nach dem Spazieren besser"

## 🛠️ Setup & Installation

### 1. Module initialisieren

```javascript
import HybridModel from "./src/modules/hybrid-model/index.js";

const hybridModel = new HybridModel();
await hybridModel.initialize();
```

### 2. Smart Contract deployen

```bash
cd contracts
npm install ethers
PRIVATE_KEY=your_key node deploy-contract.js
```

### 3. Frontend Integration

```javascript
// Reflexion verarbeiten
const result = await hybridModel.processReflection(
  title,
  content,
  selectedStates,
  shareAnonymously
);

// Insights abrufen
const insights = await hybridModel.getInsights();
```

## 📊 Datenstrukturen

### State Entry (Lokal)

```javascript
{
  state_key: "walked",
  value: 1,
  context: {
    duration: 45,
    mood_before: "stressed",
    mood_after: "calm"
  },
  timestamp: 1693834567890,
  local_only: true
}
```

### Anonymized Data (Dezentral)

```javascript
{
  embedding: [0.1, 0.3, -0.2, ...], // 384-dimensional
  tags: ["#movement", "#outdoor"],
  sentiment: { label: "positive", score: 0.8 },
  timeOfDay: "evening",
  textLength: 45,
  hashedContent: "a7b8c9d..."
}
```

### Blockchain Entry

```javascript
{
  key: "walked",
  value: 1,
  cid: "bafybei...",
  timestamp: 1693834567
}
```

## 🔄 System-Status

```javascript
const status = await hybridModel.getSystemStatus();
// {
//   hybridModel: true,
//   stateTracker: true,
//   chainInterface: true,
//   walletConnected: true,
//   localReflections: 25,
//   errors: []
// }
```

## 🚧 Entwicklung & Testing

### Unit Tests

```bash
npm test
```

### Lokale Blockchain

```bash
# Hardhat local node für Testing
npx hardhat node
```

### Privacy Validation

```javascript
const validation = await hybridModel.validatePrivacy(text);
// { isClean: false, piiFound: [...], recommendations: [...] }
```

## 🌟 Zukunftspläne

- [ ] **KI-Integration**: Lokale LLM für bessere Insights
- [ ] **Verschlüsselung**: E2E-Verschlüsselung für IPFS-Daten
- [ ] **Multi-Chain**: Support für andere Blockchains
- [ ] **Erweiterte Anonymisierung**: Differential Privacy
- [ ] **Social Features**: Anonyme Peer-Vergleiche
- [ ] **Export/Import**: Vollständige Datenportabilität

---

**Philosophie**: _Maximale Privatsphäre bei maximaler Lernfähigkeit durch clevere Trennung von lokalen und kollektiven Daten._
