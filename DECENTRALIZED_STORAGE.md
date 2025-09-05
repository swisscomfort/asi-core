# ASI-System Dezentrale Speicherung

## Übersicht

Das ASI-System wurde um dezentrale Speicherfunktionalität erweitert, die IPFS für die Datenspeicherung und Arweave für die Metadaten-Persistierung nutzt.

## Architektur

```
Reflexion Input
      ↓
process_reflection() (asi_core/processing.py)
      ↓
upload_to_ipfs() (asi_core/storage.py)
      ↓
persist_metadata_on_arweave() (asi_core/storage.py)
      ↓
Dezentral gespeicherte Daten
```

## Installation

### 1. Python-Dependencies

```bash
pip install -r requirements.txt
```

### 2. IPFS Installation

#### Option A: Lokaler IPFS-Daemon (Empfohlen für Entwicklung)

1. IPFS herunterladen und installieren: https://ipfs.io/
2. IPFS initialisieren:
   ```bash
   ipfs init
   ```
3. IPFS-Daemon starten:
   ```bash
   ipfs daemon
   ```

#### Option B: Pinning-Service (Für Produktion)

Konfigurieren Sie einen Pinning-Service wie:

- [Pinata](https://pinata.cloud/)
- [Infura IPFS](https://infura.io/product/ipfs)
- [Web3.Storage](https://web3.storage/)

## Verwendung

### Demo ausführen

```bash
python decentralized_storage_demo.py
```

### Programmmatische Verwendung

```python
from asi_core.processing import process_reflection
from asi_core.storage import upload_to_ipfs, persist_metadata_on_arweave, create_metadata

# 1. Reflexion verarbeiten
data = process_reflection("Meine Gedanken...")

# 2. Auf IPFS hochladen
cid = upload_to_ipfs(data)

# 3. Metadaten erstellen und auf Arweave speichern
metadata = create_metadata(cid, data)
success = persist_metadata_on_arweave(cid, metadata)
```

## Konfiguration

### IPFS-Verbindung anpassen

In `asi_core/storage.py` können Sie die IPFS-Verbindung anpassen:

```python
# Für lokalen Daemon
client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# Für Remote-API
client = ipfshttpclient.connect('/dns4/ipfs.infura.io/tcp/5001/https')
```

### Fehlerbehandlung

Das System behandelt verschiedene Fehlerfälle:

- **ConnectionError**: IPFS-Daemon nicht erreichbar
- **RuntimeError**: Allgemeine Upload-Fehler
- **ValueError**: Ungültige Datenformate

## API-Referenz

### `upload_to_ipfs(data: dict) -> str`

Lädt ein Dictionary als JSON auf IPFS hoch.

**Parameter:**

- `data`: Dictionary mit Reflexionsdaten

**Rückgabe:**

- `str`: IPFS Content Identifier (CID)

**Exceptions:**

- `ConnectionError`: IPFS-Daemon nicht erreichbar
- `RuntimeError`: Upload-Fehler

### `persist_metadata_on_arweave(cid: str, metadata: dict) -> bool`

Speichert Metadaten auf Arweave (derzeit simuliert).

**Parameter:**

- `cid`: IPFS Content Identifier
- `metadata`: Metadaten-Dictionary

**Rückgabe:**

- `bool`: True bei Erfolg

### `create_metadata(cid: str, original_data: dict) -> dict`

Erstellt strukturierte Metadaten für Arweave.

**Parameter:**

- `cid`: IPFS Content Identifier
- `original_data`: Ursprüngliche Reflexionsdaten

**Rückgabe:**

- `dict`: Strukturierte Metadaten

## Entwicklung

### Tests hinzufügen

Für die neue Funktionalität sollten Tests hinzugefügt werden:

```python
# tests/test_storage.py
import pytest
from asi_core.storage import create_metadata

def test_create_metadata():
    cid = "QmTest123"
    data = {"type": "reflection", "timestamp": "2023-01-01T00:00:00"}
    metadata = create_metadata(cid, data)

    assert metadata["ipfs_cid"] == cid
    assert metadata["data_type"] == "reflection"
```

### Arweave-Integration erweitern

Für die vollständige Arweave-Integration:

1. Arweave-Wallet konfigurieren
2. `arweave-python-client` installieren
3. Transaction-Logik implementieren

## Sicherheitshinweise

- **Private Keys**: Nie private Schlüssel in Code einbetten
- **Pinning**: Für Produktionsdaten Pinning-Services verwenden
- **Backup**: Regelmäßige Backups der wichtigen CIDs
- **Anonymisierung**: Vor Upload sicherstellen, dass Daten anonymisiert sind

## Roadmap

- [ ] Vollständige Arweave-Integration
- [ ] Automatisches Pinning
- [ ] Verschlüsselung vor Upload
- [ ] Batch-Upload-Funktionalität
- [ ] Web-Interface für Upload/Download
- [ ] Metadaten-Suche
