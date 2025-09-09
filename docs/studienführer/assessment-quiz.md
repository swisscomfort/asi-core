# Assessment – Quiz (FR-003, FR-004)

## Hinweise
- 10 Fragen, 20 Punkte gesamt (leicht 1, mittel 2, schwer 3).
- Beantworten Sie alle Fragen vollständig.
- Verwenden Sie bei schweren Fragen Begründungen und Trade-off-Analysen.

## Fragen

### L1 (Leicht - 1 Punkt)
**Frage**: Nennen Sie die drei Kernprinzipien des ASI Core Systems und erklären Sie kurz die Bedeutung von "Lokal".  
**Quelle**: Sektion I – Die drei Kernprinzipien: "Lokal. Anonym. Für immer."

### L2 (Leicht - 1 Punkt)
**Frage**: Was ist das Ziel der Zero-Knowledge-Verfahren im ASI Core System?  
**Quelle**: Sektion I – Kernprinzip "Anonym"

### L3 (Leicht - 1 Punkt)
**Frage**: Welche vier dezentralen Speichernetzwerke werden im ASI Core System für permanente Archivierung verwendet?  
**Quelle**: Sektion I – Kernprinzip "Für immer", Multi-Layer Storage-Strategie

### L4 (Leicht - 1 Punkt)
**Frage**: Was ist der Zweck des $MEM-Tokens und welchen Standard verwendet er?  
**Quelle**: Sektion III – Token-Charakteristika

### M1 (Mittel - 2 Punkte)
**Frage**: Beschreiben Sie den Standard-Datenfluss im ASI Core System, wenn ein Nutzer eine neue Reflexion erstellt. Erklären Sie die Rolle der lokalen und dezentralen Ebene.  
**Quelle**: Sektion II – Datenflüsse (Sequenz), Zwei-Ebenen-Modell

### M2 (Mittel - 2 Punkte)
**Frage**: Erklären Sie die Funktionen der Core Engine und warum sie für die Orchestrierung im System wichtig ist. Nennen Sie mindestens drei ihrer Hauptaufgaben.  
**Quelle**: Sektion II – Hauptkomponenten, Core Engine (Orchestrierung)

### M3 (Mittel - 2 Punkte)
**Frage**: Wie wird das Prinzip "Anonym" in der Token-Ökonomie umgesetzt? Beschreiben Sie mindestens zwei Mechanismen.  
**Quelle**: Sektion III – Designprinzipien im Token-Kontext, Anonym

### M4 (Mittel - 2 Punkte)
**Frage**: Was bedeutet "Privacy by Design" im Kontext der Hybrid-Architektur und wie wird es technisch umgesetzt?  
**Quelle**: Sektion II – Designprinzipien, Privacy by Design

### S1 (Schwer - 3 Punkte)
**Frage**: Analysieren Sie die Trade-offs der Hybrid-Architektur. Welche Vor- und Nachteile entstehen durch die Trennung von lokaler Verarbeitung und dezentraler Verifikation? Diskutieren Sie mindestens einen technischen und einen wirtschaftlichen Aspekt.  
**Quelle**: Sektion II – Architektur-Überblick, Zwei-Ebenen-Modell + Sektion III – Token-Designprinzipien

### S2 (Schwer - 3 Punkte)
**Frage**: Erläutern Sie, wie die deflationären Mechanismen des $MEM-Tokens (Halving, Burn-Rate, Slashing) das langfristige Werterhaltungsprinzip "Für immer" unterstützen. Welche Risiken könnten bei der Parameterjustierung entstehen und wie könnte das Governance-System diese abmildern?  
**Quelle**: Sektion I–III – Integration aller Kernprinzipien mit Token-Ökonomie

## Antwortschlüssel

### L1: Die drei Kernprinzipien + Lokal-Erklärung
**Antwort**: Die drei Kernprinzipien sind "Lokal. Anonym. Für immer." "Lokal" bedeutet, dass alle persönlichen Daten und sensiblen Verarbeitungen primär auf dem lokalen Gerät des Nutzers stattfinden, ohne Abhängigkeit von Cloud-Services.

### L2: Ziel der Zero-Knowledge-Verfahren
**Antwort**: Zero-Knowledge-Verfahren ermöglichen die Verifikation von Daten ohne Preisgabe der Inhalte. Das System kann beweisen, dass bestimmte Eigenschaften erfüllt sind (z.B. Mindestlänge einer Reflexion), ohne den tatsächlichen Inhalt preiszugeben.

### L3: Vier dezentrale Speichernetzwerke
**Antwort**: IPFS (dezentrale Replikation), Arweave (permanente Archivierung), Storacha (Community-gestützte Speicherung) und Polygon (Blockchain-basierte Metadaten).

### L4: $MEM-Token Zweck und Standard
**Antwort**: $MEM ist der native Utility-Token zur Incentivierung von Netzwerk-Beiträgen (Speicher, Verifikation, Qualitätsbeiträge). Er verwendet den ERC-20 Standard und ist auf Polygon/Ethereum deployt.

### M1: Standard-Datenfluss neue Reflexion
**Antwort**: 1) Nutzer erstellt Reflexion → 2) Core Engine leitet an LocalStore weiter für Validierung und lokale Speicherung → 3) CryptoEngine generiert Zero-Knowledge Proof → 4) NetworkSync sendet nur anonymisierte Beweise an dezentrale Netzwerke → 5) Lokale Daten sind sofort nutzbar, Netzwerk-Bestätigung erfolgt asynchron. Lokale Ebene: Verarbeitung und Speicherung. Dezentrale Ebene: Verifikation und Archivierung.

### M2: Core Engine Funktionen
**Antwort**: Die Core Engine orchestriert alle Systemkomponenten durch: 1) Request Routing (Weiterleitung an zuständige Module), 2) Policy Enforcement (Durchsetzung von Datenschutz-/Sicherheitsrichtlinien), 3) State Management (Synchronisation zwischen lokal/dezentral), 4) Event Coordination (System-Events koordinieren). Sie ist wichtig, weil sie die einheitliche Policy-Durchsetzung und koordinierte Interaktion aller Komponenten gewährleistet.

### M3: Anonymität in Token-Ökonomie
**Antwort**: 1) DID/UCAN-basierte pseudonyme Identitäten ohne Klarnamen, 2) Zero-Knowledge Rewards (Belohnungen ohne Preisgabe der zugrundeliegenden Beiträge), 3) Pseudonyme Wallets (mehrere Identitäten pro Nutzer möglich), 4) Privacy-Preserving Analytics (aggregierte Statistiken ohne Einzelperson-Tracking).

### M4: Privacy by Design in Hybrid-Architektur
**Antwort**: "Privacy by Design" bedeutet, dass persönliche Daten nie das lokale Gerät in unverschlüsselter Form verlassen. Technische Umsetzung: Alle sensiblen Operationen (NLP, Embedding, Search) erfolgen lokal, nur anonymisierte/verschlüsselte Daten werden übertragen, automatische Anonymisierung vor Netzwerk-Interaktionen, Minimal Data Exposure (nur notwendige Metadaten).

### S1: Trade-offs der Hybrid-Architektur
**Antwort**: **Vorteile**: Technisch: Vollständige Datenkontrolle, Offline-Fähigkeit, minimale Angriffsfläche. Wirtschaftlich: Keine Cloud-Kosten, Nutzer-Autonomie. **Nachteile**: Technisch: Komplexere Architektur, begrenzte lokale Ressourcen, Synchronisation-Herausforderungen. Wirtschaftlich: Höhere Hardware-Anforderungen für Nutzer, langsamere kollektive Intelligenz-Entwicklung. **Trade-off**: Maximale Privatsphäre vs. Skalierbarkeit - die Architektur priorisiert Nutzer-Kontrolle über Effizienz.

### S2: Deflationäre Mechanismen und "Für immer"
**Antwort**: **Unterstützung**: Halving reduziert Inflation langfristig, Burn-Rate bei Nutzung schafft Knappheit, Slashing bestraft Fehlverhalten und erhält Netzwerk-Qualität. Diese Mechanismen schaffen fundamentalen Utility-Wert statt spekulativen Wert. **Risiken**: Zu aggressive Deflation könnte Liquidität reduzieren, falsche Parameter könnten Teilnahme entmutigen. **Governance-Abmilderung**: Community-gesteuerte Anpassungen via Governance-Token, öffentliche Audits, schrittweise Parameteränderungen mit Observation-Perioden, Notfall-Reserve für kritische Situationen.

## Bewertung & Rubrik

### Punkteverteilung
- **Leicht (1 P)**: Korrekte Kernaussage oder Auflistung
- **Mittel (2 P)**: Korrekt + kurzer Bezug zum System (z.B. Datenfluss/Begründung)
- **Schwer (3 P)**: Korrekt + Trade-off-Analyse/Herleitung mit systemischem Verständnis

### Bewertungskriterien
- **Vollständigkeit**: Alle geforderten Aspekte behandelt
- **Fachliche Korrektheit**: Technische Details stimmen überein
- **Systemverständnis**: Zusammenhänge zwischen Komponenten erkannt
- **Quellenverwendung**: Bezug zu den angegebenen Sektionen

### Bestehensgrenze
- **Bestehen ab 14/20 Punkten (70%)**
- **Empfehlung**: Bei < 14 Punkten Wiederholung der entsprechenden Sektionen
- **Exzellenz**: 18+ Punkte zeigen tiefes Systemverständnis

### Lernhinweise
Bei schwachen Ergebnissen in bestimmten Bereichen:
- **L1-L4 schwach**: Sektion I nochmals durcharbeiten (Grundprinzipien)
- **M1-M4 schwach**: Sektion II vertiefen (Architektur-Details)
- **S1-S2 schwach**: Systemische Zusammenhänge zwischen allen Sektionen analysieren
