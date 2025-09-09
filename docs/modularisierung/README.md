# ASI-Core Modularisierungs-Plan

## Zielbild

Das ASI-Core System soll in klar abgegrenzte Module aufgeteilt werden, um:

- **Wartbarkeit** zu verbessern durch klare Verantwortlichkeiten
- **Testbarkeit** zu erhöhen durch isolierte Komponenten
- **Skalierbarkeit** zu ermöglichen durch loose gekoppelte Module
- **Wiederverwendbarkeit** zu fördern durch definierte APIs

## Vorgeschlagene Module

### 1. **core** - Kernfunktionalität

- **Zweck**: Zentrale ASI-Logik und Hauptschnittstellen
- **Verantwortung**: Orchestrierung, Konfiguration, Haupteinstiegspunkte
- **API**: `ASICore`, `ASIConfig`, Core-Interfaces

### 2. **domain** - Geschäftslogik

- **Zweck**: Fachliche Domänen-Logik ohne technische Abhängigkeiten
- **Verantwortung**: Reflexions-Modelle, State-Definitionen, Business Rules
- **API**: Domain Models, Value Objects, Business Services

### 3. **processing** - Datenverarbeitung

- **Zweck**: Semantic Search, NLP, Embedding-Generierung
- **Verantwortung**: Text-Processing, Vektor-Operationen, KI-Integration
- **API**: `ProcessingEngine`, `SemanticSearch`, `EmbeddingService`

### 4. **blockchain** - Blockchain-Integration

- **Zweck**: Dezentrale Speicherung und Smart Contract-Interaktion
- **Verantwortung**: Web3-Verbindungen, Contract-Calls, Wallet-Management
- **API**: `BlockchainClient`, `ContractManager`, `WalletService`

### 5. **storage** - Datenpersistierung

- **Zweck**: Lokale und dezentrale Datenspeicherung
- **Verantwortung**: Datenbank-Operations, IPFS/Arweave-Integration, Caching
- **API**: `StorageManager`, `DecentralizedStorage`, `CacheService`

### 6. **web** - Web-Interface

- **Zweck**: Frontend PWA und API-Endpunkte
- **Verantwortung**: UI-Komponenten, REST-API, WebSocket-Verbindungen
- **API**: React-Komponenten, API-Router, WebSocket-Handler

### 7. **io** - Ein-/Ausgabe

- **Zweck**: Externe Schnittstellen und Datenformate
- **Verantwortung**: Import/Export, File-Operations, Format-Konvertierung
- **API**: `FileManager`, `ImportExport`, Format-Adapter

### 8. **common** - Gemeinsame Utilities

- **Zweck**: Wiederverwendbare Hilfsfunktionen
- **Verantwortung**: Logging, Validation, Common Utils, Constants
- **API**: Logger, Validators, Helpers, Types

### 9. **platform** - Plattform-Spezifisches

- **Zweck**: Plattform-abhängige Implementierungen
- **Verantwortung**: OS-Integration, Hardware-Access, Native APIs
- **API**: Platform-Abstractions, Native-Wrappers

### 10. **tests** - Test-Infrastructure

- **Zweck**: Test-Utilities und Mocks
- **Verantwortung**: Test-Helpers, Fixtures, Mock-Services
- **API**: Test-Utilities, Mock-Factories, Fixtures

## API-Grenzen und Layering-Regeln

### Layer-Architektur (von unten nach oben):

```
┌─────────────────────────────────────────┐
│              web (UI Layer)             │
├─────────────────────────────────────────┤
│         core (Application Layer)        │
├─────────────────────────────────────────┤
│  processing │ blockchain │ io │ storage │
│            (Service Layer)              │
├─────────────────────────────────────────┤
│          domain (Business Layer)        │
├─────────────────────────────────────────┤
│   common │ platform (Infrastructure)   │
└─────────────────────────────────────────┘
```

### Abhängigkeitsregeln:

1. **Obere Layer** dürfen **untere Layer** nutzen, nicht umgekehrt
2. **Domain Layer** hat **keine technischen Abhängigkeiten**
3. **Service Layer** Komponenten sind **untereinander gleichberechtigt**
4. **Common/Platform** sind **reine Utility-Layer**

### Interface-Definitionen:

- Jedes Modul definiert **öffentliche Interfaces**
- **Implementation Details** bleiben modul-intern
- **Cross-cutting Concerns** über Dependency Injection
- **Event-basierte Kommunikation** für lose Kopplung

## Migrationsstrategie

### Phase 1: Strukturierung (Wochen 1-2)

- [ ] Modul-Ordner erstellen
- [ ] Interface-Definitionen entwerfen
- [ ] Abhängigkeits-Analyse verfeinern
- [ ] Build-System anpassen (CMake-Targets)

### Phase 2: Core-Module (Wochen 3-4)

- [ ] `common` und `domain` extrahieren
- [ ] `core` Orchestrierung implementieren
- [ ] Tests auf neue Struktur anpassen
- [ ] CI/CD Pipeline validieren

### Phase 3: Service-Module (Wochen 5-7)

- [ ] `processing`, `storage`, `blockchain` separieren
- [ ] Interface-basierte Kommunikation etablieren
- [ ] Integration-Tests erweitern
- [ ] Performance-Benchmarks

### Phase 4: UI-Trennung (Wochen 8-9)

- [ ] `web` Modul isolieren
- [ ] API-Grenzen definieren
- [ ] Frontend-Backend-Integration testen
- [ ] End-to-End Tests

### Phase 5: Finalisierung (Woche 10)

- [ ] `io` und `platform` Module
- [ ] Dokumentation vervollständigen
- [ ] Code-Review und Refactoring
- [ ] Release-Vorbereitung

## Erfolgskriterien

### Technische Metriken:

- **Zyklomatische Komplexität** < 10 pro Funktion
- **Kopplungsgrad** zwischen Modulen minimal
- **Test-Coverage** > 85% pro Modul
- **Build-Zeit** nicht verschlechtert

### Qualitätsmerkmale:

- **Single Responsibility** pro Modul
- **Open/Closed Principle** für Erweiterungen
- **Dependency Inversion** für Abstrakte
- **Interface Segregation** für APIs

## Risiken und Mitigation

### Risiko: Performance-Verschlechterung

- **Mitigation**: Benchmark-Tests vor/nach Migration
- **Monitoring**: Continuous Performance Testing

### Risiko: Breaking Changes

- **Mitigation**: Inkrementelle Migration mit Backward-Compatibility
- **Rollback**: Git-Feature-Branches für jede Phase

### Risiko: Komplexitäts-Zunahme

- **Mitigation**: Klare Interface-Dokumentation
- **Training**: Code-Reviews und Pair-Programming

## Tools und Standards

### Entwicklung:

- **Architektur**: Clean Architecture / Hexagonal Architecture
- **Patterns**: Repository, Factory, Observer, Strategy
- **Documentation**: PlantUML für Diagramme, Sphinx für API-Docs

### Build-System:

- **CMake**: Module als separate Targets
- **Testing**: Google Test / pytest mit Modul-Isolation
- **CI/CD**: Module-spezifische Pipeline-Stages

## Aktivierung

Das ASI-Modul-System kann optional über CMake-Schalter aktiviert werden:

### Standard-Konfiguration (Module deaktiviert)

```bash
cmake -S . -B build -G Ninja
cmake --build build
```

### Modul-Konfiguration (Module aktiviert)

```bash
cmake -S . -B build-mod -G Ninja -DASI_ENABLE_MODULES=ON
cmake --build build-mod
```

Mit `-DASI_ENABLE_MODULES=ON` werden 10 INTERFACE-Targets erstellt:

- **Infrastructure**: `asi::common`, `asi::platform`, `asi::tests`
- **Domain**: `asi::domain`
- **Services**: `asi::processing`, `asi::blockchain`, `asi::storage`, `asi::io`
- **Application**: `asi::core`
- **UI**: `asi::web`

Die Konfiguration ist erfolgreich, auch wenn noch keine C++-Implementierung vorhanden ist. Das System erstellt die Modul-Struktur ohne das bestehende Python-Build-System zu beeinträchtigen.

### Abhängigkeits-Validierung

```bash
cmake -S . -B build-mod -G Ninja -DASI_ENABLE_MODULES=ON --graphviz=deps.dot
dot -Tpng deps.dot -o module-deps.png
```

## Langzeit-Vision

Das modularisierte ASI-Core System soll als **Plattform** für:

- **Plugin-Entwicklung** durch Dritte
- **Microservice-Migration** bei Bedarf
- **Multi-Language-Support** (Python/C++/Rust)
- **Cloud-Native Deployment** mit Container-Orchestrierung

---

> **Status**: � **Implementierung Schritt 1** | **Version**: 1.0 | **Letzte Aktualisierung**: 2025-09-09
