# ASI Smart Contract Integration

## 🎯 Überblick

Diese Implementierung erweitert das ASI (Autonomous Self-Improvement) System um Smart Contract-Funktionalität auf der Polygon-Blockchain. Reflexionen können nun dezentral indexiert und durchsuchbar gemacht werden.

## 🏗️ Smart Contract (ASIIndex.sol)

### Features

- **Dezentrale Indexierung**: Metadaten von Reflexionen werden on-chain gespeichert
- **Content-Referenzierung**: IPFS/Arweave CIDs für dezentrale Content-Speicherung
- **Tag-System**: Kategorisierung und Filterung nach Tags
- **AI-Embeddings**: Speicherung von Embeddings für semantische Suche
- **Access Control**: Owner-basierte Zugriffskontrolle
- **Events**: Automatische Event-Emission für externe Services

### Entry-Struktur

```solidity
struct Entry {
    uint256 entryId;        // Eindeutige ID
    string cid;             // IPFS/Arweave Content Identifier
    string[] tags;          // Tags für Kategorisierung
    bytes embedding;        // AI-Embedding für Suche
    uint256 timestamp;      // Erstellungszeitpunkt
    address owner;          // Ersteller-Adresse
    bool isActive;          // Aktiv-Status
}
```

### Hauptfunktionen

- `registerEntry()` - Registriert neue Reflexion
- `updateEntry()` - Aktualisiert bestehende Reflexion
- `getEntry()` - Holt Entry-Details
- `getEntriesByOwner()` - Entries eines Besitzers
- `getEntriesByTag()` - Entries nach Tag

## 🐍 Python-Integration

### ASIBlockchainClient

```python
from asi_core.blockchain import ASIBlockchainClient

client = ASIBlockchainClient(
    rpc_url="https://rpc-mumbai.maticvigil.com/",
    private_key="your_private_key",
    contract_address="0x..."
)

tx_hash = client.register_entry_on_chain(
    cid="QmYourIPFSHash...",
    tags=["persönlichkeit", "ziele"],
    embedding=ai_embedding_bytes,
    timestamp=int(time.time())
)
```

### Backend-Integration

- Automatische Integration in `process_reflection_workflow()`
- Environment-Variable basierte Konfiguration
- Fehlerbehandlung und Logging
- Optionale Aktivierung über `ENABLE_BLOCKCHAIN`

## 🚀 Setup und Deployment

### 1. Dependencies installieren

```bash
# Python Dependencies
pip install web3 python-dotenv

# Hardhat Dependencies
cd web/contracts
npm install
```

### 2. Konfiguration

```bash
# .env Datei erstellen
cp .env.example .env

# Konfiguration ausfüllen:
# - MUMBAI_RPC_URL / POLYGON_RPC_URL
# - PRIVATE_KEY (ohne 0x)
# - ASI_CONTRACT_ADDRESS (nach Deployment)
# - ENABLE_BLOCKCHAIN=true
```

### 3. Smart Contract deployen

```bash
cd web/contracts

# Kompilieren
npx hardhat compile

# Mumbai Testnet
npx hardhat run scripts/deployASIIndex.js --network mumbai

# Polygon Mainnet
npx hardhat run scripts/deployASIIndex.js --network polygon
```

### 4. Contract-Adresse konfigurieren

```bash
# Contract-Adresse aus Deployment-Output in .env eintragen
ASI_CONTRACT_ADDRESS=0x1234567890...
```

## 🧪 Testing

### Lokaler Test

```bash
# Integration-Test ausführen
python test_blockchain_integration.py

# Vollständige Demonstration
python demo_complete_integration.py
```

### Mit lokalem Hardhat-Node

```bash
# Terminal 1: Lokalen Node starten
cd web/contracts
npx hardhat node

# Terminal 2: Contract deployen
npx hardhat run scripts/deployASIIndex.js --network localhost

# Terminal 3: Python-Tests
python test_blockchain_integration.py
```

## 🔄 Workflow-Integration

### Automatische Registrierung

Bei aktiviertem `AUTO_REGISTER_ON_CHAIN=true` werden Reflexionen automatisch auf der Blockchain registriert:

1. **Reflexion erstellen** → `main.py`
2. **AI-Verarbeitung** → Anonymisierung, Embedding
3. **Lokale Speicherung** → SQLite Database
4. **Dezentrale Speicherung** → IPFS/Arweave Upload
5. **Blockchain-Registrierung** → Smart Contract Call
6. **Event-Emission** → On-chain Indexierung

### Manuelle Registrierung

```python
from asi_core.blockchain import ASIBlockchainClient

client = ASIBlockchainClient.from_config(config)
tx_hash = client.register_entry_on_chain(...)
```

## 🛡️ Sicherheit

### Best Practices

- ✅ Private Keys niemals in Code speichern
- ✅ .env Dateien in .gitignore
- ✅ Sichere RPC-Endpunkte verwenden
- ✅ Gas-Limits überwachen
- ✅ Extensive Tests auf Testnet
- ✅ Smart Contract Auditing für Produktion

### Zugriffskontrollen

- Entry-Updates nur durch Owner
- Validierung aller Eingaben
- Reentrancy-Schutz implementiert
- Event-basierte Transparenz

## 📊 Monitoring

### Events

```solidity
event EntryRegistered(uint256 indexed entryId, string indexed cid, address indexed owner, uint256 timestamp);
event EntryUpdated(uint256 indexed entryId, string indexed cid, uint256 timestamp);
event EntryDeactivated(uint256 indexed entryId, uint256 timestamp);
```

### Query-Möglichkeiten

- Entries nach Owner
- Entries nach Tag
- Alle Entries mit Pagination
- Entry-Status und Details

## 🎯 Nächste Schritte

### Kurzfristig

- [ ] Mumbai Testnet Deployment
- [ ] End-to-End Tests mit echten Reflexionen
- [ ] Frontend-Integration
- [ ] Monitoring Dashboard

### Mittelfristig

- [ ] L2-Integration (Polygon PoS → zkEVM)
- [ ] Gas-Optimierungen
- [ ] Batch-Operations
- [ ] IPFS-Pinning Service

### Langfristig

- [ ] Cross-Chain-Kompatibilität
- [ ] Governance-Token
- [ ] Dezentrale Suchfunktionen
- [ ] Community-Features

## 📁 Dateistruktur

```
asi-core/
├── asi_core/
│   └── blockchain.py              # Python-Web3 Integration
├── web/contracts/
│   ├── contracts/
│   │   └── ASIIndex.sol          # Smart Contract
│   ├── scripts/
│   │   └── deployASIIndex.js     # Deployment Script
│   ├── deployments/              # Deployment Artefakte
│   ├── hardhat.config.js         # Hardhat Konfiguration
│   └── package.json              # Dependencies
├── main.py                       # Erweitert um Blockchain
├── .env.example                  # Konfigurationsvorlage
├── test_blockchain_integration.py # Test Suite
└── demo_complete_integration.py   # Demo Script
```

## 🤝 Contribution

1. Fork das Repository
2. Feature Branch erstellen
3. Änderungen committen
4. Tests ausführen
5. Pull Request erstellen

## 📜 Lizenz

Siehe LICENSE Datei für Details.

---

**✅ Smart Contract Logik vollständig implementiert und bereit für Deployment!**
