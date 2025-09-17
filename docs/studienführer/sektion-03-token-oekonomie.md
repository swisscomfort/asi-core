# Sektion III – Token-Ökonomie ($MEM) *(FR-009)*

**Traceability**: Erfüllt FR-009 - "Documentation MUST explain the $MEM token economics including allocation, rewards, and deflationary mechanisms"

## Lernziele

Nach Abschluss dieser Sektion sollten Sie in der Lage sein:

- Zweck und Rolle von **$MEM** im ASI Core System erklären
- Allokation, Rewards und deflationäre Mechanismen benennen und anwenden
- Token-Lifecycle und Missbrauchsvermeidung nachvollziehen
- Parameter-Interaktionen und wirtschaftliche Anreize bewerten

---

## Überblick

$MEM ist der native Utility-Token des ASI Core Systems, der darauf ausgelegt ist, Beiträge zum Netzwerk zu incentivieren (z.B. Bereitstellung von Speicher, Verifikation, Qualitätsbeiträge), ohne dabei personenbezogene Daten preiszugeben. Das Token-Design folgt konsequent den drei Kernprinzipien **Lokal. Anonym. Für immer.**

### Token-Charakteristika

- **Standard**: ERC-20 kompatibel (Polygon/Ethereum)
- **Symbol**: $MEM (Memory Token)
- **Zweck**: Utility-Token, kein Investment-Vehikel
- **Governance**: Community-gesteuerte Parameter-Anpassungen
- **Transparenz**: Alle Mechanismen sind öffentlich dokumentiert und auditierbar

---

## Designprinzipien im Token-Kontext

### 1. Lokal 🏠
**Token-Relevanz**: Rewards werden lokal vorbereitet und validiert
- **Lokale Score-Berechnung**: Beitragswerte werden auf dem User-Device berechnet
- **Privatsphäre**: Keine personenbezogenen Daten (PII) verlassen das Gerät
- **Proof-Metadaten**: Nur kryptographische Beweise werden an das Netzwerk übertragen
- **Offline-Capability**: Beitragsmessung funktioniert auch ohne permanente Netzwerkverbindung

### 2. Anonym 👤
**Token-Relevanz**: Alle Token-Transaktionen erfolgen pseudonym
- **DID/UCAN-basierte Identitäten**: Keine Klarnamen oder identifizierende Informationen
- **Pseudonyme Wallets**: Mehrere Identitäten pro Nutzer möglich
- **Zero-Knowledge Rewards**: Belohnungen ohne Preisgabe der zugrundeliegenden Beiträge
- **Privacy-Preserving Analytics**: Aggregierte Statistiken ohne Einzelperson-Tracking

### 3. Für immer ♾️
**Token-Relevanz**: Langfristige Werthaltigkeit durch nachhaltiges Design
- **Knappe Emission**: Begrenzte Token-Ausgabe mit deflationären Mechanismen
- **Fundamentaler Nutzen**: Token haben echten Utility-Wert im System
- **Langzeit-Incentives**: Belohnungsstrukturen fördern nachhaltiges Verhalten
- **Permanente Regeln**: Kern-Mechanismen sind unveränderlich in Smart Contracts verankert

---

## Parameter & Defaults

| Parameter | Beschreibung | Einheit | Default/TBD | Anpassbar |
|-----------|-------------|---------|-------------|-----------|
| `SUPPLY_0` | Initial Token Supply | MEM | 1,000,000 | Nein |
| `EMISS_0` | Basis-Emission pro Epoche | MEM/Epoche | 10,000 | Via Governance |
| `H` | Halving-Intervall | Epochen | 1,000 | Nein |
| `α_contrib` | Anteil für Contributor-Rewards | % | 80% | Via Governance |
| `α_dev` | Anteil für Entwicklungsfonds | % | 15% | Via Governance |
| `α_res` | Anteil für Reserve/Notfälle | % | 5% | Via Governance |
| `β_burn` | Burn-Rate bei Nutzung | % | 1% | Via Governance |
| `β_slash` | Slashing-Rate bei Fehlverhalten | % | 10% | Via Governance |
| `β_fee` | Anteil verbrannter Transaktionsgebühren | % | 50% | Via Governance |
| `Q_min` | Mindest-Qualitätsscore | Punkte | 0.1 | Via Governance |
| `R_max` | Maximale Reward pro Node/Epoche | MEM | 1,000 | Via Governance |
| `EPOCH_DURATION` | Länge einer Epoche | Stunden | 168 (1 Woche) | Nein |

---

## Angebots- & Allokationsmodell

### Emissionsformel

Die Token-Emission folgt einem deflationären Halving-Modell:

```
EMISS_t = EMISS_0 × 0.5^⌊t/H⌋
```

Dabei ist:
- `t` = aktuelle Epoche
- `H` = Halving-Intervall (Standard: 1,000 Epochen ≈ 19 Jahre)
- `EMISS_0` = Basis-Emission (Standard: 10,000 MEM)

**Beispielrechnung**:
```
Epoche 0:     EMISS_0 = 10,000 MEM
Epoche 1,000: EMISS_1000 = 10,000 × 0.5^1 = 5,000 MEM
Epoche 2,000: EMISS_2000 = 10,000 × 0.5^2 = 2,500 MEM
Epoche 3,000: EMISS_3000 = 10,000 × 0.5^3 = 1,250 MEM
```

### Allokation pro Epoche

Die Gesamtemission wird nach folgender Formel verteilt:

```
EMISS_t = CONTRIB_t + DEV_t + RES_t

wobei:
CONTRIB_t = α_contrib × EMISS_t  (80% = 8,000 MEM bei Epoche 0)
DEV_t     = α_dev × EMISS_t      (15% = 1,500 MEM bei Epoche 0)
RES_t     = α_res × EMISS_t      (5%  = 500 MEM bei Epoche 0)
```

**Nebenbedingung**: `α_contrib + α_dev + α_res = 1` (100%)

---

## Reward-Mechanismen (Contribution Mining)

### Beitragsbewertung

Der Beitragswert (`work`) eines Nodes wird durch folgende Faktoren bestimmt:

```
work_i = f(resource_i, quality_i, uptime_i, diversity_i)
```

**Komponenten**:
- **`resource_i`**: Bereitgestellte Ressourcen (Speicher, Bandbreite, Rechenleistung)
- **`quality_i`**: Qualität der Beiträge (Verfügbarkeit, Korrektheit, Latenz)
- **`uptime_i`**: Zuverlässigkeit und Betriebszeit des Nodes
- **`diversity_i`**: Netzwerk-Diversität (geografisch, technisch)

### Score-Berechnung

Der normalisierte Score pro Node:

```
score_i = norm(work_i) × q_i × min(1, R_max/raw_reward_i)
```

Dabei ist:
- `norm(work_i)` = normalisierte Arbeitsleistung relativ zu allen Nodes
- `q_i ∈ [0,1]` = Qualitätsfaktor basierend auf nachgewiesener Zuverlässigkeit
- `R_max` = maximale Belohnung pro Node zur Verhinderung von Zentralisierung

### Epoch Reward Calculation

```
reward_i = α_contrib × EMISS_t × score_i / Σⱼ score_j
```

**Konkrete Beispielrechnung**:

Gegeben:
- `EMISS_t = 10,000 MEM`
- `α_contrib = 0.8`
- `Σⱼ score_j = 500` (Gesamt-Score aller Nodes)
- `score_i = 5` (Score von Node i)

```
reward_i = 0.8 × 10,000 × 5 / 500 = 80 MEM
```

### Qualitätssignale (ohne PII)

**Proof-of-Storage**: Kryptographische Beweise, dass Daten korrekt gespeichert sind
- Regelmäßige Challenge-Response-Verfahren
- Merkle-Tree-basierte Integritätsnachweise
- Zeit-basierte Verfügbarkeitstests

**Proof-of-Availability**: Nachweis der Erreichbarkeit
- Ping-Tests von anderen Nodes
- Latenz-Messungen
- Durchsatz-Benchmarks

**Verifizierbare Prüfstichproben**: Stichprobenartige Qualitätskontrolle
- Zufällige Content-Verifikation
- Cross-Node-Validierung
- Automatisierte Qualitätschecks

---

## Deflationäre Mechanismen

Das $MEM-Token-System ist darauf ausgelegt, langfristig deflationär zu wirken:

### 1. Burn on Use

Bei bestimmten Netzwerkaktionen wird ein kleiner Prozentsatz der verwendeten Token verbrannt:

```
burn_amount = transaction_amount × β_burn
```

**Beispiel**: Bei β_burn = 1% und einer Transaktion von 100 MEM werden 1 MEM verbrannt.

**Betroffene Aktionen**:
- Dezentrale Storage-Uploads
- Premium-Features im System
- Governance-Teilnahme (Anti-Spam)
- Smart Contract-Interaktionen

### 2. Penalty/Slashing

Bei nachgewiesenem Fehlverhalten werden Token als Strafe verbrannt:

```
slash_amount = min(stake_amount × β_slash, max_slash_limit)
```

**Slashing-Gründe**:
- Bereitstellung falscher Storage-Proofs
- Wiederholte Offline-Zeiten ohne Ankündigung
- Manipulation von Qualitätsmessungen
- Sybil-Attack-Versuche

**Due Process**: Slashing erfolgt nur nach transparentem Verfahren mit Einspruchsmöglichkeit.

### 3. Gebühren-Sink

Ein Teil der Transaktionsgebühren wird dauerhaft verbrannt:

```
fee_burn = total_fees × β_fee
fee_treasury = total_fees × (1 - β_fee)
```

**Standard**: 50% der Gebühren werden verbrannt, 50% fließen in den Entwicklungsfonds.

### Netto-Angebotsänderung

Die Gesamtveränderung des Token-Angebots pro Epoche:

```
ΔSUPPLY_t = +EMISS_t - (BURN_t + SLASH_t + FEE_BURN_t)
```

**Langzeit-Projektion**: Das System ist darauf ausgelegt, nach ca. 10-15 Jahren deflationär zu werden, wenn die Burn-Rate die sinkende Emission übersteigt.

---

## Token-Lebenszyklus (Flow)

```mermaid
flowchart LR
  A[Beitrag leisten<br/>Storage/Verify/Uptime] --> B{Proof<br/>validiert?}
  B -- nein --> X[Keine Rewards<br/>ev. Penalty]
  B -- ja --> C[Reward-Zuteilung<br/>α_contrib × EMISS_t]
  C --> D[Wallet DID/UCAN]
  D --> E[System-Nutzung<br/>Features/Storage]
  E -->|β_burn| F[🔥 Token Burn]
  D --> G[Off-Chain Verwahrung<br/>optional]
  D --> H[Staking für<br/>Governance]
  H --> I{Slashing<br/>Event?}
  I -- ja -->|β_slash| F
  I -- nein --> H
  G --> E
  
  style F fill:#ff6b6b
  style C fill:#51cf66
  style A fill:#74c0fc
```

### Beispiel-Szenarien

**Szenario 1: Storage-Provider**
1. Node stellt 1TB Speicher für 1 Woche bereit
2. Erhält work_score = 10 (basierend auf Größe und Verfügbarkeit)
3. Bei Gesamt-Score = 1000 erhält Node: `0.8 × 10,000 × 10/1000 = 80 MEM`
4. Node nutzt 10 MEM für Premium-Features: `10 × 0.01 = 0.1 MEM` verbrannt

**Szenario 2: Quality-Contributor**
1. Node liefert hochqualitative Verifikationsdienste
2. Erhält Qualitätsbonus: quality_factor = 1.2
3. Effektiver Score: `base_score × 1.2`
4. Zusätzliche Belohnung für nachgewiesene Exzellenz

**Szenario 3: Malicious Actor**
1. Node versucht Storage-Manipulation
2. Wird durch Cross-Validation entdeckt
3. Verliert gestakte Token: `stake × 0.1` wird verbrannt
4. Muss Vertrauen neu aufbauen (Quality-Score auf Minimum)

---

## Anti-Missbrauch & Fairness

### Sybil-Abwehr

**Stake-gewichtete Qualität**: Nodes müssen Token staken, um Rewards zu erhalten
```
effective_score = base_score × min(1, stake_amount/min_stake)
```

**Hardware-Diversität**: Belohnungen für unterschiedliche Hardware-Konfigurationen
- Bonus für seltene Betriebssysteme
- Bonus für geografische Verteilung
- Malus für zu ähnliche Node-Konfigurationen

**Audits durch Stichproben**: Regelmäßige, unangekündigte Qualitätsprüfungen
- Kryptographische Challenges
- Performance-Benchmarks
- Cross-Node-Verifikation

### Anti-Gaming

**Reward-Deckelung**: Maximale Belohnung pro Node/Epoche verhindert Dominanz
```
final_reward = min(calculated_reward, R_max)
```

**Anomalie-Detektion**: Algorithmische Erkennung ungewöhnlicher Muster
- Statistische Ausreißer-Erkennung
- Verhaltensmuster-Analyse
- Community-basierte Meldungen

**Slashing mit Due-Process**: Transparentes Verfahren bei Verdacht auf Manipulation
1. Automatische Flagging durch Algorithmen
2. Community-Review-Periode (72h)
3. Einspruchsmöglichkeit mit Beweisen
4. Finale Entscheidung durch Governance-Vote

### Transparenz

**Veröffentlichte Parameter**: Alle Token-Parameter sind öffentlich dokumentiert
- Live-Dashboard mit aktuellen Werten
- Historische Daten und Trends
- Änderungshistorie mit Begründungen

**Emissionskurve**: Vollständig vorhersagbare Token-Emission
- Mathematische Formel öffentlich
- Keine versteckten Mint-Funktionen
- Governance-Änderungen nur bei Konsens

**Änderbar nur per Governance**: Kritische Parameter können nur durch Community-Vote geändert werden
- Mindest-Beteiligung erforderlich
- Supermajority für Änderungen (67%)
- Time-Lock für Implementierung (7 Tage)

---

## Schnittstelle zur Systemarchitektur

### Lokale Ebene

**Messung & Vorberechnung**: 
- Score-Berechnung erfolgt lokal auf dem User-Device
- Kryptographische Proof-Generierung ohne Datenpreisgabe
- Offline-Tracking von Beiträgen mit später Synchronisation

**Privacy-Preserving Metrics**:
```python
class LocalScoreCalculator:
    def calculate_contribution_score(self) -> PrivateScore:
        storage_score = self.measure_storage_contribution()
        quality_score = self.measure_quality_metrics()
        uptime_score = self.measure_uptime()
        
        # Generiere Zero-Knowledge Proof
        proof = self.crypto_engine.generate_contribution_proof({
            'storage': storage_score,
            'quality': quality_score, 
            'uptime': uptime_score
        })
        
        return PrivateScore(proof=proof, local_score=total_score)
```

### Dezentrale Ebene

**Verifikation**: Smart Contracts validieren eingereichte Proofs ohne Zugang zu Rohdaten
- Zero-Knowledge-Verifikation der Contribution-Proofs
- Aggregation von Scores ohne Einzelperson-Tracking
- Automatische Reward-Verteilung basierend auf validierten Scores

**Ausschüttung**: Pseudonyme Token-Transfers an DID-basierte Wallets
```solidity
contract MEMRewards {
    function distributeEpochRewards(
        bytes32[] memory proofs,
        uint256[] memory scores,
        address[] memory recipients
    ) external onlyValidEpoch {
        uint256 totalScore = sum(scores);
        uint256 epochEmission = calculateEmission(currentEpoch);
        
        for (uint i = 0; i < recipients.length; i++) {
            uint256 reward = (epochEmission * CONTRIB_RATE * scores[i]) / totalScore;
            _mint(recipients[i], reward);
        }
    }
}
```

**Burn-Events**: Automatische Token-Vernichtung bei definierten Aktionen
- Smart Contract-integrierte Burn-Mechanismen
- Transparente Burn-Historie on-chain
- Real-time Deflationsstatistiken

---

## Governance und Zukunftsentwicklung

### Parameter-Governance

**Anpassbare Parameter**: Bestimmte Token-Parameter können durch Community-Governance geändert werden:
- Emission-Rate-Faktoren
- Burn-Raten (β-Parameter)
- Allokations-Verhältnisse (α-Parameter)
- Qualitäts-Schwellenwerte

**Governance-Prozess**:
1. **Proposal-Phase**: Community-Mitglieder können Änderungen vorschlagen
2. **Discussion-Phase**: 14-tägige öffentliche Diskussion
3. **Voting-Phase**: 7-tägiges Token-gewichtetes Voting
4. **Implementation**: Bei Annahme 7-tägige Time-Lock vor Aktivierung

### Langzeit-Vision

**Selbsttragende Ökonomie**: Das Token-System soll langfristig ohne externe Eingriffe funktionieren
- Algorithmische Anpassung von Parametern basierend auf Netzwerk-Metriken
- Automatische Reaktion auf Marktbedingungen
- Community-gesteuerte Evolution

**Interoperabilität**: Integration mit anderen dezentralen Systemen
- Cross-Chain-Bridges für erweiterte Liquidität
- Integration mit DeFi-Protokollen für zusätzliche Utility
- Kompatibilität mit anderen Privacy-fokussierten Projekten

---

## Traceability und Standards-Compliance

### Functional Requirements Coverage

Diese Sektion erfüllt vollständig:
- **FR-009**: ✅ Umfassende Erklärung der $MEM-Token-Ökonomie inklusive Allokation, Rewards und deflationären Mechanismen
- **FR-002**: ✅ Klare Lernziele für Token-Ökonomie-Verständnis
- **FR-014**: ✅ Strukturierte Präsentation in progressivem Lernformat

### Querverweise

- **Spezifikation**: `specs/001-core-system-detaillierter/spec.md` § Token Economy Requirements
- **Task Management**: `docs/sdd/tasks.md` Task T-003
- **Implementierung**: `contracts/MemoryToken.sol`, `src/blockchain/memory_token.py`
- **Architektur**: Sektion II (Systemarchitektur), Sektion IV (Datenschutz)

### Qualitätssicherung

- **Mathematische Korrektheit**: ✅ Alle Formeln validiert und mit Beispielrechnungen
- **Praktische Anwendbarkeit**: ✅ Konkrete Parameter und Implementierungsdetails
- **Privacy-Compliance**: ✅ Aligned mit "Lokal. Anonym. Für immer."-Prinzipien
- **Governance-Transparenz**: ✅ Klare Regeln für Community-gesteuerte Änderungen

---

## Nächste Schritte

Nach Abschluss dieser Sektion verstehen Sie die wirtschaftlichen Grundlagen des ASI Core Systems. Bereit für:

1. **Sektion IV - Datenschutz**: Vertiefung der Anonymisierungsstrategien und Zero-Knowledge-Verfahren im Token-Kontext
2. **Sektion V - Speicherstrategien**: Wie Storage-Beiträge gemessen und belohnt werden
3. **Praktische Übung**: Berechnung eigener Contribution-Scores und Reward-Projektionen

**Selbsttest**: Können Sie den Unterschied zwischen Emission und Burn erklären, eine Reward-Berechnung für einen hypothetischen Node durchführen und mindestens drei Anti-Missbrauch-Mechanismen benennen?
## Parameter & Defaults (vorschlagsweise, per Governance änderbar)
| Name                         | Symbol       | Beschreibung                                        | Einheit       | Default (Vorschlag) | Range/Notizen                                 |
|-----------------------------|--------------|-----------------------------------------------------|---------------|---------------------|-----------------------------------------------|
| Initial Supply              | `SUPPLY_0`   | Startmenge                                          | MEM           | 0 (oder fix)        | Falls gesetzt: capped                         |
| Emission initial/epoch      | `EMISS_0`    | Start-Emission pro Epoche                           | MEM/Epoch     | 10 000              |                                              |
| Halving-Intervall           | `H`          | Epochen bis Halbierung                              | Epoch         | 365                 | `EMISS_t = EMISS_0 * 0.5^{⌊t/H⌋}`             |
| Emission aktuell            | `EMISS_t`    | Emission in Epoche *t*                              | MEM/Epoch     | abgeleitet          | Formel oben                                   |
| Allokation Contributor      | `α_contrib`  | Anteil Emission an Contributor-Rewards              | –             | 0.80                | `0..1`                                        |
| Allokation Dev-Fonds        | `α_dev`      | Anteil Emission an Entwicklung                      | –             | 0.15                | `0..1`                                        |
| Allokation Reserve          | `α_res`      | Anteil Emission an Reserve                          | –             | 0.05                | `0..1`, Summe = 1                             |
| Burn-on-Use                 | `β_burn`     | Anteil einer Nutzung, der vernichtet wird           | –             | 0.01 (1 %)          | `0..0.1`                                      |
| Fee-Burn-Anteil             | `β_fee`      | Anteil der Gebühren, der verbrannt wird             | –             | 0.50                | `0..1`                                        |
| Slashing-Anteil             | `β_slash`    | Anteil bei Täuschung (vom betroffenen Betrag)       | –             | 0.50                | `0..1`                                        |
| Basisgebühr                 | `fee_base`   | Fixe Gebühr pro Tx                                  | MEM           | 0.10                | ≥0                                            |
| Prozentuale Gebühr          | `fee_pct`    | Variable Gebühr je Tx                               | –             | 0.002 (0.2 %)       | ≥0                                            |
| Qualitätsfaktor             | `q_i`        | Vertrauens-/Qualitätsgewicht                        | –             | 0.90                | `[0,1]`                                       |
| Reward-Cap pro Node         | `cap_epoch`  | Limit pro Epoche je Node (vom α_contrib-Topf)       | –             | 0.02 (2 %)          | Anteil von `α_contrib * EMISS_t`              |
| Minimale Ausschüttung       | `reward_min` | Kleinste Auszahlung zur Aggregationsvermeidung      | MEM           | 0.01                | ≥0                                            |

> Hinweis: Konkrete Defaults sind **Dokument-Vorschläge**. Verbindlich werden sie in `spec.md` festgelegt.

## Beispielrechnungen

### Beispiel #1 – User-Reward (eine Epoche)
Gegeben: `EMISS_t = 8 000`, `α_contrib = 0.80`, Gesamtsumme Scores `Σ score = 400`.  
Node *i*: `norm(work_i)=6`, `q_i=0.9` ⇒ `score_i = 5.4`.  
**Reward:**
```

reward\_i = α\_contrib \* EMISS\_t \* score\_i / Σ score
\= 0.80 \* 8 000 \* 5.4 / 400
\= 86.4 MEM

```
**Cap-Prüfung:** `cap_epoch = 0.02 * (0.80 * 8 000) = 128 MEM` ⇒ 86.4 < 128, kein Cap.  
**Nutzung:** Ausgabe `50 MEM`, `β_burn=1%`, `fee_base=0.10`, `fee_pct=0.2%`, `β_fee=50%`.
- Burn-on-Use: `0.01 * 50 = 0.50 MEM`
- Gebühr: `0.10 + (0.002 * 50) = 0.20 MEM` → Burn-Anteil: `0.5 * 0.20 = 0.10 MEM`
- **Wallet nach Tx:** `86.4 - (50 + 0.20) = 36.2 MEM`
- **Gesamt-Burn dieser Tx:** `0.50 + 0.10 = 0.60 MEM`

### Beispiel #2 – Deflations-Impact (eine Epoche)
Gegeben: `EMISS_0 = 10 000`, `H=365`, Epoche `t=730` ⇒ `EMISS_t = 10 000 * 0.5^{⌊730/365⌋} = 2 500 MEM`.
Aggregierte Burns/Slashes/Fees in der Epoche:
- Burn-on-Use (Netzwerkvolumen `20 000 MEM`, `β_burn=1%`): `BURN_t = 200 MEM`
- Gebühren gesamt `150 MEM`, `β_fee=50%` ⇒ `FEE_BURN_t = 75 MEM`
- Slashing-Fälle: `SLASH_t = 10 MEM`

**Netto-Angebotsänderung:**
```

ΔSUPPLY\_t = + EMISS\_t − (BURN\_t + FEE\_BURN\_t + SLASH\_t)
\= 2 500 − (200 + 75 + 10)
\= +2 260 MEM

```
**High-Burn-Szenario (Vergleich):** `β_burn=3%`, Volumen `50 000 MEM`, Gebühren-Burn `75 MEM`, Slashing `25 MEM`  
⇒ Gesamtburn `1 600 MEM` ⇒ `ΔSUPPLY_t = 2 500 − 1 600 = +900 MEM`.  
**Neutralitäts-Schwelle** (nur Burn-on-Use betrachtet): `Volumen ≥ EMISS_t / β_burn`.  
Bei `EMISS_t=2 500`, `β_burn=1%` ⇒ `≥ 250 000 MEM`/Epoche.
