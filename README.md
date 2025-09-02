# ASI Core - Autonomous Self-Improvement System 🧠

Ein Open-Source-System für persönliche Reflexion, Anonymisierung und dezentrale Speicherung.

## 🌟 Vision

ASI Core ermöglicht es dir, deine Gedanken und Reflexionen sicher zu erfassen, zu strukturieren und für dein persönliches Wachstum zu nutzen - während deine Privatsphäre geschützt bleibt.

## ✨ Features

### Core-Funktionen

- **📝 Reflexions-Eingabe**: Geführte und freie Reflexions-Erfassung
- **🔒 Anonymisierung**: Automatische Entfernung persönlicher Daten
- **🧠 KI-Analyse**: Lokale Sentiment- und Themen-Analyse
- **🔍 Semantische Suche**: Intelligente Suche in deinen Reflexionen

### Speicher-Optionen

- **💾 Lokale Datenbank**: SQLite für temporäre Daten
- **🌐 IPFS-Integration**: Dezentrale Speicherung
- **⛓️ Arweave-Speicherung**: Permanente Blockchain-Speicherung
- **� Storacha-Integration**: Moderne dezentrale Speicherung mit automatisierten Uploads
- **�🔐 Blockchain-Verifikation**: Smart Contract-basierte Integrität

### Privacy & Sicherheit

- **3 Privacy-Level**: Private, Anonyme und Öffentliche Reflexionen
- **🔐 Wallet-Integration**: Sichere Signierung und Verifikation
- **🛡️ Lokale KI**: Keine externen API-Aufrufe für sensible Daten

## 🚀 Schnellstart

### Installation

```bash
# Repository klonen
git clone https://github.com/swisscomfort/asi-core.git
cd asi-core

# Python-Abhängigkeiten installieren
pip install -r requirements.txt

# React Frontend installieren (optional)
cd web
npm install
cd ..

# Konfiguration erstellen
cp config/secrets.example.json config/secrets.json
```

### Erste Schritte

```bash
# Hauptsystem starten (CLI)
python main.py

# Web-Interface starten (Flask - Port 8000)
python src/web/app.py

# React Frontend starten (Port 5173)
cd web && npm run dev

# Oder direkt eine Reflexion verarbeiten
python main.py process "Heute war ein besonderer Tag..."

# Suche in Reflexionen
python main.py search "Arbeit und Stress"

# Statistiken anzeigen
python main.py stats
```

## 📂 Projektstruktur

```
asi-core/
├── src/
│   ├── core/              # Kern-Module
│   │   ├── input.py       # Reflexions-Eingabe
│   │   ├── processor.py   # Verarbeitung & Anonymisierung
│   │   ├── enhanced_processor.py # Erweiterte Verarbeitung
│   │   └── output.py      # Ausgabe & Hinweise
│   ├── storage/           # Speicher-Module
│   │   ├── local_db.py    # SQLite-Datenbank
│   │   ├── ipfs_client.py # IPFS-Integration
│   │   ├── arweave_client.py # Arweave-Speicherung
│   │   └── storacha_client_clean.py # Storacha-Integration
│   ├── ai/                # KI-Module
│   │   ├── embedding.py   # Vektor-Embeddings
│   │   └── search.py      # Semantische Suche
│   ├── blockchain/        # Blockchain-Module
│   │   ├── contract.py    # Smart Contract-Interface
│   │   └── wallet.py      # Wallet-Management
│   └── web/               # Web-Interface
│       ├── app.py         # Flask-Server
│       └── templates/     # HTML-Templates
├── web/                   # React Frontend
│   ├── src/               # React Komponenten
│   ├── package.json       # Node.js Dependencies
│   └── vite.config.js     # Build-Konfiguration
├── scripts/               # Utility Scripts
├── data/                  # Daten-Verzeichnis
├── config/                # Konfiguration
└── main.py               # Hauptanwendung
```

## 🔧 Konfiguration

Kopiere `config/secrets.example.json` zu `config/secrets.json` und passe die Einstellungen an:

```json
{
  "ipfs_api_url": "http://localhost:5001/api/v0",
  "arweave_gateway": "https://arweave.net",
  "storacha_enabled": false,
  "blockchain_rpc_url": "http://localhost:8545",
  "privacy_default": "private",
  "auto_upload_ipfs": false,
  "auto_upload_arweave": false,
  "web_port": 8000
}
```

## 🔒 Privacy-Level

- **Private**: Nur lokal gespeichert, nicht geteilt
- **Anonymous**: Anonymisiert, kann auf IPFS gespeichert werden
- **Public**: Vollständig öffentlich, permanent auf Arweave

## 💡 Verwendung

### Reflexion erfassen

```python
from src.core.input import InputHandler

handler = InputHandler()
reflection = handler.capture_reflection(
    "Meine Gedanken heute...",
    tags=["persönlich", "wachstum"]
)
```

### Semantische Suche

```python
from src.ai.search import SemanticSearchEngine

results = search_engine.search_by_text("Arbeit und Stress")
for result in results:
    print(f"{result.similarity_score:.3f}: {result.content_preview}")
```

### Storacha-Integration

```python
from src.storage.storacha_client_clean import StorachaUploader

uploader = StorachaUploader()
result = uploader.upload_reflection_data(processed_data)
print(f"Storacha Upload: {result['status']}")
```

### Dezentrale Speicherung

```python
from src.storage.ipfs_client import IPFSClient

ipfs = IPFSClient()
hash = ipfs.upload_reflection(processed_data)
print(f"IPFS Hash: {hash}")
```

## 🤝 Beitragen

Wir freuen uns über Beiträge! Siehe [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) für Community-Richtlinien.

### Entwicklung

```bash
# Tests ausführen
pytest

# Code-Formatierung
black src/

# Linting
flake8 src/

# React Frontend entwickeln
cd web
npm run dev      # Development Server
npm run build    # Production Build
npm run lint     # ESLint
```

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

## 🚀 Implementierungsfortschritt

### ✅ Vollständig implementiert

- **Kern-System**: Alle Core-Module (input, processor, enhanced_processor, output)
- **KI-Pipeline**: Lokale Embeddings und semantische Suche
- **Speicher-Backends**: SQLite, IPFS-Client, Arweave-Client, Storacha-Integration
- **Blockchain-Integration**: Smart Contract Interface, Wallet-Management
- **Web-Interface**: Flask-Server mit Bootstrap-Frontend
- **React Frontend**: Moderne Web-UI mit Vite und Tailwind CSS
- **CLI-Tools**: Vollständige Kommandozeilen-Integration
- **Upload Scripts**: Automatisierte Storacha-Uploads

### 🧪 Erfolgreich getestet

- ✅ Reflexions-Workflow komplett funktional
- ✅ Web-Interface responsive und einsatzbereit
- ✅ React Frontend mit modernem UI/UX
- ✅ Simulation-Modi für IPFS und Arweave
- ✅ Storacha-Upload-Funktionalität
- ✅ Lokale Datenbank mit allen Features
- ✅ KI-Analyse und Suche vollständig implementiert

### 🔴 Live-System verfügbar

Das ASI Core System ist **produktionsbereit** und kann sofort verwendet werden:

```bash
# Hauptsystem starten (CLI)
python main.py

# Web-Interface (Flask - Port 8000)
python src/web/app.py

# React Frontend (Port 5173)
cd web && npm run dev
```

**Status**: ✅ Vollständig funktionsfähig und getestet!

## 🎯 Roadmap

- [x] **Web-Interface** ✅ Implementiert (Flask + Bootstrap)
- [x] **React Frontend** ✅ Implementiert (Vite + Tailwind CSS)
- [x] **Storacha-Integration** ✅ Implementiert
- [ ] Mobile App (React Native)
- [ ] Erweiterte KI-Modelle (lokale LLMs)
- [ ] Gruppen-Reflexionen
- [ ] Export-Funktionen (PDF, CSV)
- [x] **Dezentrale Speicherung** ✅ Implementiert

## 🙏 Danksagungen

- OpenAI für KI-Inspiration
- IPFS & Protocol Labs für dezentrale Technologie
- Arweave für permanente Speicherung
- Storacha für moderne dezentrale Speicherlösungen
- Ethereum-Community für Blockchain-Standards
- React & Vite Community für moderne Web-Entwicklung

---

**ASI Core** - Dein persönlicher Begleiter für Selbstreflexion und Wachstum 🌱  
A decentralized, anonymous, lifelong digital twin – built in silence
