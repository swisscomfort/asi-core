# 🚀 ASI-Core Quick Start Guide

Willkommen bei ASI-Core! Dieser Guide hilft Ihnen beim schnellen Einstieg.

## ⚡ Schnellstart (3 Schritte)

### 1. Erstmalige Einrichtung
```bash
# Repository klonen (falls noch nicht geschehen)
git clone https://github.com/swisscomfort/asi-core.git
cd asi-core

# Automatisches Setup ausführen
./setup.sh
```

### 2. System starten
```bash
# Interaktives Starter-Menü
./start.sh
```

### 3. PWA-Version (Optional)
```bash
# Progressive Web App starten
python start-pwa.py --open
```

## 🎯 Verfügbare Modi

| Modus | Beschreibung | Befehl |
|-------|--------------|--------|
| **CLI** | Interaktive Kommandozeile | `python main.py` |
| **Web** | Browser-Interface | `python main.py serve` |
| **API** | Nur API-Server | `python api_server.py` |
| **PWA** | Progressive Web App | `python start-pwa.py` |

## 🔧 System-Check

```bash
# Gesundheitscheck durchführen
python health_check.py

# Detaillierte Diagnose
python health_check.py --verbose
```

## 📱 PWA Features

- **✅ Offline-fähig** - Funktioniert ohne Internet
- **📱 Installierbar** - Als App installieren
- **🔄 Auto-Sync** - Automatische Synchronisation
- **🔔 Push-Notifications** - Benachrichtigungen (optional)

## 🐳 Docker

```bash
# Mit Docker Compose starten
docker-compose up -d

# Nur ASI-Core Container
docker build -t asi-core .
docker run -p 5000:5000 -v $(pwd)/data:/app/data asi-core
```

## 🌐 URLs

- **Web Interface**: http://localhost:5000
- **API Dokumentation**: http://localhost:5000/api/docs
- **PWA**: http://localhost:8000
- **IPFS Gateway**: http://localhost:8080 (falls aktiviert)

## 📊 Monitoring

```bash
# Live-Status anzeigen
python health_check.py

# Logs verfolgen
tail -f logs/asi-core.log
```

## 🔒 Sicherheit

Wichtige Dateien **NIEMALS** committen:
- `.env` - Environment-Variablen
- `config/secrets.json` - API-Keys
- `data/local/wallet.json` - Private Keys

## 🆘 Problembehebung

### Problem: "Permission denied" beim Start
```bash
chmod +x start.sh setup.sh
```

### Problem: "Module not found"
```bash
# Virtual Environment aktivieren
source .venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Database locked"
```bash
# Database Reset (ACHTUNG: Datenverlust!)
rm data/asi_local.db
python main.py  # Erstellt neue DB
```

### Problem: Port bereits belegt
```bash
# Andere Ports verwenden
export ASI_PORT=5001
python main.py serve
```

## 📚 Weitere Dokumentation

- [Vollständiges README](README.md)
- [Deployment Guide](DEPLOYMENT_READY.md)
- [API Dokumentation](docs/api/)
- [Blockchain Integration](BLOCKCHAIN_README.md)

## 🎉 Los geht's!

1. **Ersten Start**: `./setup.sh` ausführen
2. **System starten**: `./start.sh` ausführen  
3. **Browser öffnen**: http://localhost:5000
4. **Erste Reflexion erstellen**: "Neue Reflexion" Button

**Happy reflecting! 🧠✨**
