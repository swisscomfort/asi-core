# 🚀 ASI-Core Quick Start Guide

**Willkommen bei ASI-Core!** Der intelligenteste Weg zu starten ist mit unserer **Live PWA** ⚡

## 🌐 **SOFORT LOSLEGEN - Kein Setup nötig!**

### **🎯 Live PWA Demo (0 Minuten Setup):**
**Direkt öffnen:** [**swisscomfort.github.io/asi-core**](https://swisscomfort.github.io/asi-core/)

- 📱 **Installierbar** auf Mobile & Desktop
- 🔄 **Offline-fähig** - funktioniert ohne Internet
- ⚡ **Instant Loading** - Progressive Web App Technologie
- 🎯 **Sofort nutzbar** - keine Registrierung erforderlich

---

## ⚡ **ENTWICKLER-QUICKSTART (2 Minuten):**

### **1. Clone & Demo:**
```bash
git clone https://github.com/swisscomfort/asi-core.git
cd asi-core
./quick-demo.sh  # 🎯 Interaktive 2-Minuten Demo
```

### **2. Vollständiges Setup:**
```bash
./setup.sh      # Automatische Konfiguration
./start.sh      # Interaktives Starter-Menü
```

### **3. PWA Development:**
```bash
cd web
npm install
npm run dev     # Development Server (Port 5173)
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
