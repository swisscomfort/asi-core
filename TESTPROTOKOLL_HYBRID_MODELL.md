# ASI-Core Hybrid-Modell Testprotokoll

## Vorbereitung

### System-Setup

1. Workspace-Pfad: `/workspaces/asi-core`
2. Python-Environment konfigurieren
3. Node.js Dependencies installieren: `cd web && npm install`
4. Seed generieren: `python -c "import secrets; print(secrets.token_hex(32))"`
5. Environment Variables setzen (.env Datei)

### Test-Datensets

```json
{
  "reflexion_minimal": {
    "title": "Kurze Reflexion",
    "content": "Heute war ein guter Tag.",
    "states": [{ "key": "spazieren", "value": 1 }],
    "tags": ["#alltag"]
  },
  "reflexion_pii": {
    "title": "PII Test",
    "content": "Heute habe ich mit Michael Schmidt in München über meine Probleme gesprochen. Meine E-Mail: test@example.com",
    "states": [{ "key": "gespräch", "value": 1 }],
    "tags": ["#persönlich"]
  },
  "reflexion_komplex": {
    "title": "Komplexe Zustandsreflexion",
    "content": "Nach 30 Minuten Spaziergang fühle ich mich von gestresst zu entspannt. Die frische Luft hat geholfen.",
    "states": [
      {
        "key": "spazieren",
        "value": 1,
        "duration": "30",
        "moodBefore": "stressed",
        "moodAfter": "calm"
      }
    ],
    "tags": ["#gesundheit", "#natur"]
  }
}
```

## Testkategorien

### 1. Lokale Funktionalität

#### Test 1.1: IndexedDB Speicherung

| Test-ID                 | T1.1.001                                                     |
| ----------------------- | ------------------------------------------------------------ |
| **Beschreibung**        | Erfolgreiche Speicherung einer Reflexion in IndexedDB        |
| **Eingabe**             | `reflexion_minimal`                                          |
| **Erwartetes Ergebnis** | Reflexion in Browser IndexedDB gespeichert, ID zurückgegeben |
| **Validierung**         | Browser DevTools > Application > IndexedDB > ASI_Reflections |
| **Status**              | ⏳                                                           |

#### Test 1.2: Zustandserkennung und -speicherung

| Test-ID                 | T1.2.001                                       |
| ----------------------- | ---------------------------------------------- |
| **Beschreibung**        | Erkennung "spazieren = 1" Zustand              |
| **Eingabe**             | `reflexion_minimal` mit state "spazieren"      |
| **Erwartetes Ergebnis** | State in IndexedDB > ASI_StateTracker > states |
| **Validierung**         | `stateTracker.getStateHistory("spazieren", 1)` |
| **Status**              | ⏳                                             |

#### Test 1.3: Mustererkennung über Zeit

| Test-ID                 | T1.3.001                                    |
| ----------------------- | ------------------------------------------- |
| **Beschreibung**        | 5-Tage Spaziergang-Streak Erkennung         |
| **Eingabe**             | 5x täglich "spazieren" State                |
| **Erwartetes Ergebnis** | Pattern mit `consecutive_days: 5`           |
| **Validierung**         | `stateTracker.analyzePatterns("spazieren")` |
| **Status**              | ⏳                                          |

#### Test 1.4: HRM Integration

| Test-ID                 | T1.4.001                                                |
| ----------------------- | ------------------------------------------------------- |
| **Beschreibung**        | HRM Analyse-Workflow                                    |
| **Eingabe**             | Reflexionstext über `/api/hrm/analyze`                  |
| **Erwartetes Ergebnis** | JSON mit `confidence`, `abstract_plan`, `insights`      |
| **Validierung**         | HTTP Response Status 200, Content-Type application/json |
| **Status**              | ⏳                                                      |

### 2. Anonymisierung

#### Test 2.1: PII-Erkennung Namen

| Test-ID                 | T2.1.001                                         |
| ----------------------- | ------------------------------------------------ |
| **Beschreibung**        | Erkennung deutscher Vornamen                     |
| **Eingabe**             | "Michael Schmidt war heute da"                   |
| **Erwartetes Ergebnis** | "[NAME] Schmidt war heute da"                    |
| **Validierung**         | `anonymizer.anonymizeText(input).anonymizedText` |
| **Status**              | ⏳                                               |

#### Test 2.2: PII-Erkennung Orte

| Test-ID                 | T2.2.001                             |
| ----------------------- | ------------------------------------ |
| **Beschreibung**        | Erkennung deutscher Städte           |
| **Eingabe**             | "In München war es schön"            |
| **Erwartetes Ergebnis** | "In [CITY] war es schön"             |
| **Validierung**         | Anonymisierter Text enthält "[CITY]" |
| **Status**              | ⏳                                   |

#### Test 2.3: E-Mail Anonymisierung

| Test-ID                 | T2.3.001                            |
| ----------------------- | ----------------------------------- |
| **Beschreibung**        | E-Mail-Adressen entfernen           |
| **Eingabe**             | "test@example.com schrieb mir"      |
| **Erwartetes Ergebnis** | "[EMAIL] schrieb mir"               |
| **Validierung**         | Keine E-Mail im anonymisierten Text |
| **Status**              | ⏳                                  |

#### Test 2.4: Embedding-Generierung

| Test-ID                 | T2.4.001                                    |
| ----------------------- | ------------------------------------------- |
| **Beschreibung**        | 384-dimensionales Embedding erstellen       |
| **Eingabe**             | Anonymisierter Text                         |
| **Erwartetes Ergebnis** | Array mit 384 Float-Werten, normalisiert    |
| **Validierung**         | `embedding.length === 384`, Magnitude ≈ 1.0 |
| **Status**              | ⏳                                          |

### 3. Dezentrale Integration

#### Test 3.1: Storacha Upload

| Test-ID                 | T3.1.001                              |
| ----------------------- | ------------------------------------- |
| **Beschreibung**        | Erfolgreicher Upload zu Storacha/IPFS |
| **Eingabe**             | Reflexions-JSON mit `isPublic: true`  |
| **Erwartetes Ergebnis** | CID zurückgegeben (Qm... Format)      |
| **Validierung**         | CID über IPFS Gateway abrufbar        |
| **Status**              | ⏳                                    |

#### Test 3.2: Polygon Smart Contract

| Test-ID                 | T3.2.001                             |
| ----------------------- | ------------------------------------ |
| **Beschreibung**        | Zustandsregistrierung auf Polygon    |
| **Eingabe**             | CID, State-Key, Embedding-Hash       |
| **Erwartetes Ergebnis** | Transaction Hash, Block-Bestätigung  |
| **Validierung**         | `polygonscan.com` Transaction-Status |
| **Status**              | ⏳                                   |

#### Test 3.3: Kollektive Statistiken

| Test-ID                 | T3.3.001                                         |
| ----------------------- | ------------------------------------------------ |
| **Beschreibung**        | Aggregation aller "spazieren"-States             |
| **Eingabe**             | Query nach State "spazieren"                     |
| **Erwartetes Ergebnis** | Anzahl, Durchschnitt, Zeitverteilung             |
| **Validierung**         | Smart Contract `getStateStatistics("spazieren")` |
| **Status**              | ⏳                                               |

### 4. UI/UX Tests

#### Test 4.1: Zustandsauswahl Modal

| Test-ID                 | T4.1.001                             |
| ----------------------- | ------------------------------------ |
| **Beschreibung**        | State-Selector im NewReflectionModal |
| **Eingabe**             | Klick auf "Zustand hinzufügen"       |
| **Erwartetes Ergebnis** | Dropdown mit verfügbaren States      |
| **Validierung**         | `predefinedStates` Array im DOM      |
| **Status**              | ⏳                                   |

#### Test 4.2: Persönliche Streaks

| Test-ID                 | T4.2.001                           |
| ----------------------- | ---------------------------------- |
| **Beschreibung**        | Anzeige von Streak-Informationen   |
| **Eingabe**             | Dashboard-Aufruf mit 3+ Tage Daten |
| **Erwartetes Ergebnis** | "X Tage in Folge" Anzeige          |
| **Validierung**         | DOM Element mit Streak-Count       |
| **Status**              | ⏳                                 |

#### Test 4.3: Kollektive Erkenntnisse

| Test-ID                 | T4.3.001                     |
| ----------------------- | ---------------------------- |
| **Beschreibung**        | Community Insights Dashboard |
| **Eingabe**             | Insights-Tab öffnen          |
| **Erwartetes Ergebnis** | Aggregierte Daten ohne PII   |
| **Validierung**         | Keine Namen/Orte in Insights |
| **Status**              | ⏳                           |

## Validierungsmethoden

### Anonymitätstest

```javascript
// Test: Kann Person aus geteilten Daten identifiziert werden?
const anonymized = await anonymizer.anonymize(reflexion_pii);
const piiDetected = anonymized.detectedPII;

// Validierung: Alle PII-Typen erkannt
assert(piiDetected.some((item) => item.type === "name"));
assert(piiDetected.some((item) => item.type === "email"));
assert(!anonymized.anonymizedText.includes("Michael"));
```

### Verifizierbarkeitstest

```javascript
// Test: Blockchain-Zustand beweisbar
const txHash = await chainInterface.logState("spazieren", 1, cid);
const verification = await contract.verifyState(txHash);

assert(verification.valid === true);
assert(verification.stateKey === "spazieren");
```

### Integritätstest

```bash
# Test: Daten überleben Systemneustart
# 1. Reflexion erstellen
python asi_hybrid_cli.py add-state "Test Reflexion" --state 1

# 2. System neu starten
pkill -f "python.*asi"
sleep 5

# 3. Daten prüfen
python asi_hybrid_cli.py stats
# Erwartung: Reflexion noch vorhanden
```

### Seed-Wiederherstellungstest

```javascript
// Test: Wallet-Wiederherstellung funktioniert
const originalSeed = "0x1234...";
const wallet1 = new ethers.Wallet(originalSeed);

// System zurücksetzen, Seed erneut eingeben
const wallet2 = new ethers.Wallet(originalSeed);

assert(wallet1.address === wallet2.address);
```

## Benchmarking-Metriken

### Speicherplatzverbrauch

```bash
# Lokale IndexedDB Größe messen
du -sh ~/.config/vscode-browser/User/IndexedDB/
# Ziel: < 100MB nach 30 Tagen

# Dezentrale Speicher-Kosten
# Storacha: ~$0.15/GB/Monat
# Polygon Gas: ~0.001 ETH pro State-Log
```

### Upload-Geschwindigkeit

```javascript
const startTime = Date.now();
const cid = await StorachaService.uploadReflection(data);
const uploadTime = Date.now() - startTime;

// Zielwerte:
// Storacha: < 5 Sekunden
// IPFS: < 10 Sekunden
// Arweave: < 30 Sekunden
```

### Mustererkennungsgenauigkeit

```javascript
// Streak-Erkennung Genauigkeit
const realStreaks = [5, 3, 7, 2]; // Manuell verifiziert
const detectedStreaks = patterns.map((p) => p.consecutive_days);
const accuracy = calculateAccuracy(realStreaks, detectedStreaks);

// Ziel: > 95% Genauigkeit
assert(accuracy > 0.95);
```

### Seed-Wiederherstellungszeit

```javascript
const startTime = Date.now();
await hybridModel.restoreFromSeed(seedPhrase);
const restoreTime = Date.now() - startTime;

// Ziel: < 30 Sekunden
assert(restoreTime < 30000);
```

## Testdurchführung

### Phase 1: Lokale Tests

```bash
# 1. Environment vorbereiten
cp config/secrets.example.json config/secrets.json
python configure_python_environment.py

# 2. IndexedDB Tests
cd web && npm test -- --grep "IndexedDB"

# 3. State Tracking Tests
node -e "
const StateTracker = require('./src/modules/hybrid-model/state-tracker.js');
const tracker = new StateTracker();
// Testausführung hier
"

# 4. HRM Integration
python -m pytest tests/ -k "test_hrm"
```

### Phase 2: Anonymisierungstests

```bash
# 1. PII-Erkennung
node tests/test-anonymizer.js

# 2. Embedding-Generierung
python tests/test_embeddings.py

# 3. Vergleichstest Roh vs. Anonymisiert
node tests/test-pii-comparison.js
```

### Phase 3: Dezentrale Tests

```bash
# 1. Storacha Setup prüfen
node scripts/test-storacha-connection.js

# 2. Polygon Connection
python scripts/test-polygon-connection.py

# 3. End-to-End Upload
node tests/test-full-upload-workflow.js
```

### Phase 4: UI-Tests

```bash
# 1. Modal-Funktionalität
cd web && npm run test:ui

# 2. Dashboard-Integration
npm run test:dashboard

# 3. Insights-Darstellung
npm run test:insights
```

## Ergebnisverifikation

### Erfolgreiche Tests

- [ ] T1.1.001: IndexedDB Speicherung
- [ ] T1.2.001: Zustandserkennung
- [ ] T1.3.001: Mustererkennung
- [ ] T1.4.001: HRM Integration
- [ ] T2.1.001: PII-Erkennung Namen
- [ ] T2.2.001: PII-Erkennung Orte
- [ ] T2.3.001: E-Mail Anonymisierung
- [ ] T2.4.001: Embedding-Generierung
- [ ] T3.1.001: Storacha Upload
- [ ] T3.2.001: Polygon Smart Contract
- [ ] T3.3.001: Kollektive Statistiken
- [ ] T4.1.001: Zustandsauswahl Modal
- [ ] T4.2.001: Persönliche Streaks
- [ ] T4.3.001: Kollektive Erkenntnisse

### Fehlerbehandlung

#### Typische Fehler und Lösungen

**IndexedDB Quota Exceeded**

```javascript
// Fehler: QuotaExceededError
// Lösung: Automatische Datenbereinigung
await stateTracker.clearOldData(30); // 30 Tage behalten
```

**Storacha Upload Failed**

```javascript
// Fehler: Network timeout
// Lösung: Retry mit exponential backoff
const result = await retryWithBackoff(
  () => StorachaService.uploadReflection(data),
  3
);
```

**Smart Contract Gas Estimation Failed**

```javascript
// Fehler: Gas estimation failed
// Lösung: Manuelle Gas-Limits
const gasLimit = 300000; // Feste Gas-Grenze
const tx = await contract.logState(state, { gasLimit });
```

**PII Detection False Positives**

```javascript
// Fehler: "August" als Name erkannt
// Lösung: Context-aware Patterns
const isMonth =
  /\b(januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)\b/i.test(
    text
  );
```

## Testbericht-Template

### Test-Ausführung

```
Datum: [YYYY-MM-DD]
Tester: [Name]
Version: [Git Commit Hash]
Environment: [Browser/Node Version]

Ergebnisse:
- Erfolgreich: [X]/[Total] Tests
- Fehlgeschlagen: [Y]/[Total] Tests
- Übersprungen: [Z]/[Total] Tests

Performance:
- Durchschnittliche Upload-Zeit: [X]s
- IndexedDB Größe: [X]MB
- Mustererkennungsgenauigkeit: [X]%

Kritische Fehler: [Liste]
Empfehlungen: [Liste]
```

### Einzeltest-Bericht

```
Test-ID: [TX.Y.ZZZ]
Status: ✅ BESTANDEN / ❌ FEHLGESCHLAGEN / ⏳ AUSSTEHEND

Eingabedaten:
[Konkrete Testdaten]

Erwartetes Ergebnis:
[Spezifische Erwartung]

Tatsächliches Ergebnis:
[Actual Output]

Ausführungszeit: [X]ms
Fehlerdetails: [Falls fehlgeschlagen]
Logs: [Relevante Log-Ausgaben]
```

## Kontinuierliche Integration

### GitHub Actions Workflow

```yaml
name: ASI-Core Hybrid Model Tests
on: [push, pull_request]

jobs:
  test-local:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
      - name: Install dependencies
        run: cd web && npm ci
      - name: Run local tests
        run: npm run test:local

  test-anonymization:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test PII detection
        run: node tests/test-anonymizer.js
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: anonymization-results
          path: test-results/

  test-integration:
    runs-on: ubuntu-latest
    env:
      MUMBAI_RPC_URL: ${{ secrets.MUMBAI_RPC_URL }}
      PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
    steps:
      - uses: actions/checkout@v3
      - name: Test blockchain integration
        run: python tests/test_blockchain_integration.py
```

### Monitoring & Alerting

```javascript
// Performance Monitoring
const performanceThresholds = {
  uploadTime: 5000, // 5s max
  embeddingGeneration: 1000, // 1s max
  patternAnalysis: 2000, // 2s max
  dbQuery: 500, // 500ms max
};

// Automated Health Checks
setInterval(async () => {
  const health = await runHealthChecks();
  if (health.issues.length > 0) {
    await alertDevelopers(health.issues);
  }
}, 300000); // Alle 5 Minuten
```
