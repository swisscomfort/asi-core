# ASI-Core Hybrid-Modell Integration

## Vollständige Integration des Hybrid-Modells in ASI-Core

Diese Integration erweitert das ASI-Core-System um ein vollständiges Hybrid-Modell mit lokaler Zustandsverfolgung, Anonymisierung und dezentraler Speicherung.

## Implementierte Komponenten

### 1. **NewReflectionModal_complete.jsx** ✅

- Erweitert um Zustandsauswahl mit vordefinierten Aktivitäten
- Checkboxen für: `walked`, `focused`, `slept_well`, `meditated`, `productive_morning`, etc.
- Stimmungserfassung vor/nach Aktivitäten
- Zeiterfassung und Notizen für jede Aktivität
- Automatische Anonymisierung bei geteilten Reflexionen
- Privacy-Validierung mit Empfehlungen

### 2. **PersonalInsights.jsx** ✅

- Zeigt persönliche Streaks an
- Stimmungsverbesserungs-Erkenntnisse
- Zeitbasierte Muster
- Vertrauensbewertungen für alle Insights
- Automatische Aktualisierung

### 3. **Dashboard.jsx** ✅

- Persönliche Streaks Sektion
- Kollektive Erfolgsquoten aller Benutzer
- Proaktive Empfehlungen basierend auf:
  - Tageszeit (morgens → Spaziergang/Meditation)
  - Mustern (Streak-Fortsetzung)
- Integration der PersonalInsights Komponente

### 4. **Smart Contract (ASIStateTracker.sol)** ✅

```solidity
function logState(string memory key, uint256 value, string memory cid)
function getAggregateState(string memory key) returns (uint256, uint256)
function getMultipleAggregateStates(string[] memory keys)
```

### 5. **Flask API Endpunkte (main.py)** ✅

```python
GET  /api/states?days=7           # Benutzerzustände
GET  /api/insights?days=7         # Persönliche Erkenntnisse
GET  /api/states/aggregate        # Kollektive Daten
POST /api/states/log              # Neuen Zustand loggen
GET  /api/recommendations         # Proaktive Empfehlungen
```

### 6. **Hybrid-Model Module** ✅

- **state-tracker.js**: Lokale Zustandsspeicherung mit IndexedDB
- **anonymizer.js**: PII-Erkennung und Entfernung
- **chain-interface.js**: Blockchain/IPFS Integration
- **insight-engine.js**: Mustererkennung und Insights
- **index.js**: Zentrale Orchestrierung

## Wichtige Features

### ✅ **Lokale Funktionalität**

- Vollständige Offline-Fähigkeit
- Keine Cloud-KI-Abhängigkeiten
- IndexedDB für persistente lokale Speicherung
- Seed-basierte Wiederherstellung möglich

### ✅ **Datenschutz & Anonymisierung**

- Automatische PII-Erkennung (E-Mail, Namen, Adressen)
- Privacy-Validierung mit Warnungen
- Vollständige Anonymisierung vor dezentraler Speicherung
- Nur Verhaltensmuster werden geteilt, keine persönlichen Daten

### ✅ **Dezentrale Speicherung**

- IPFS für anonymisierte Daten
- Smart Contract für Aggregationsdaten
- Lokale Speicherung für vollständige Daten
- Optional: Storacha für verschlüsselte Backups

### ✅ **Insight-Engine**

- Streak-Erkennung (3+ aufeinanderfolgende Tage)
- Stimmungskorrelationen (70%+ Verbesserung)
- Zeitbasierte Muster (produktivste Tageszeiten)
- Kollektive Validierung (75%+ Erfolgsrate)
- Proaktive Empfehlungen

### ✅ **Smart Contract Integration**

```solidity
// Anonyme Zustandsaggregation
mapping(string => uint256) public stateSums;
mapping(string => uint256) public stateCounts;
mapping(string => AggregateData) public aggregateStates;
```

## Verwendung

### Frontend Integration

```jsx
import HybridModel from "../src/modules/hybrid-model/index.js";

const hybridModel = new HybridModel();
await hybridModel.initialize();

// Zustand loggen
await hybridModel.stateTracker.setLocalState("walked", 1, {
  mood_before: "neutral",
  mood_after: "good",
  duration: 30,
});

// Insights abrufen
const insights = await hybridModel.getInsights();
```

### API Integration

```javascript
// Zustände abrufen
const response = await fetch("/api/states?days=7");
const states = await response.json();

// Empfehlungen abrufen
const recommendations = await fetch("/api/recommendations");
const recs = await recommendations.json();
```

## Datenfluss

1. **Lokale Erfassung**: Benutzer wählt Aktivitäten in NewReflectionModal
2. **Verarbeitung**: HybridModel anonymisiert und analysiert
3. **Lokale Speicherung**: IndexedDB speichert vollständige Daten
4. **Dezentrale Teilung**: Nur anonymisierte Muster bei opt-in
5. **Insight-Generierung**: Muster werden lokal analysiert
6. **Dashboard-Anzeige**: Persönliche und kollektive Insights

## Sicherheit & Privacy

- **Zero-Knowledge**: Persönliche Daten verlassen niemals das lokale System
- **Opt-in Sharing**: Benutzer entscheidet bewusst über anonyme Teilung
- **PII-Schutz**: Automatische Erkennung und Entfernung persönlicher Daten
- **Seed Recovery**: Komplett lokale Wiederherstellung möglich

Diese Integration stellt ein vollständiges, datenschutzfreundliches System für persönliche Entwicklung mit kollektiven Erkenntnissen bereit.
