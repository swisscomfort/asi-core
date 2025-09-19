# 🧹 ASI-Core Bereinigungsscripts

Diese Scripts helfen dabei, Ihr ASI-Core Projekt von unnötigen Dateien zu bereinigen und für Production zu optimieren.

## 📋 Verfügbare Scripts

### 1. `quick-cleanup.sh` - Schnelle Bereinigung ⚡
**Empfohlen für tägliche Verwendung**

```bash
./quick-cleanup.sh
```

**Entfernt:**
- Python Cache (`__pycache__`, `*.pyc`)
- IDE Dateien (`.vscode`, `.idea`)
- Temporäre Dateien (`*.tmp`, `*.bak`, `*.log`)
- Test Artefakte (`.pytest_cache`, `.coverage`)
- Build Dateien (`build/`, `dist/`)
- Leere Verzeichnisse

**Sicher:** Entfernt nur eindeutig unnötige Dateien

### 2. `cleanup.sh` - Umfassende Bereinigung 🔄
**Für gründliche Aufräumarbeiten**

```bash
./cleanup.sh
```

**Zusätzlich zu Quick-Cleanup:**
- Web Build Artefakte
- Große Dateien Analyse
- Detaillierte Statistiken
- CMake Build Files

### 3. `analyze-project.sh` - Projekt-Analyse 🔍
**Für Diagnose und Optimierung**

```bash
./analyze-project.sh
```

**Analysiert:**
- Duplikate und ähnliche Dateien
- Dateien mit vielen Imports
- Große Python-Dateien (>500 Zeilen)
- TODO/FIXME Kommentare
- Leere oder minimale Dateien

### 4. `prepare-production.sh` - Production Deployment 🚀
**NUR für finale Production-Bereitstellung**

```bash
./prepare-production.sh
```

**⚠️ ACHTUNG:** Entfernt ALLE Entwicklungs-Dateien!
- Test-Dateien und -Verzeichnisse
- GitHub Actions
- Entwicklungs-Configs
- Example-Dateien
- **Erstellt automatisch Backup!**

## 📊 Bereinigungsergebnisse

Nach der Quick-Cleanup:
- **Entfernte Dateien:** 14.595
- **Größenreduktion:** 8.3GB → 8.0GB (300MB gespart)
- **Behalten:** Alle wichtigen Core-Dateien

## 🎯 Empfohlener Workflow

### Tägliche Entwicklung:
```bash
./quick-cleanup.sh
```

### Vor Git Commits:
```bash
./cleanup.sh
```

### Projekt-Optimierung:
```bash
./analyze-project.sh
./cleanup.sh
```

### Production Deployment:
```bash
./prepare-production.sh
```

## 🔒 Sicherheitshinweise

- **Backup:** `prepare-production.sh` erstellt automatisch Backups
- **Git Status:** Prüfen Sie `git status` vor Production-Bereinigung
- **Core Files:** Alle Scripts behalten wichtige Projektdateien
- **Wiederherstellung:** Entwicklungs-Dependencies mit `pip install -r requirements.txt` wiederherstellen

## 📁 Behalten vs. Entfernen

### ✅ Wird IMMER behalten:
- `src/` - Core Code
- `asi_core/` - Hauptmodule  
- `main.py` - Eingangsscript
- `requirements.txt` - Dependencies
- `config/` - Konfiguration
- `data/` - Datenverzeichnis (bereinigt)
- `contracts/` - Smart Contracts
- `start.sh` - Start-Script

### ❌ Wird entfernt:
- `__pycache__/` - Python Cache
- `tests/` - Test-Dateien (nur bei Production)
- `.vscode/`, `.idea/` - IDE Configs
- `build/`, `dist/` - Build Artefakte
- `web/node_modules/` - NPM Cache
- `*.pyc`, `*.tmp`, `*.log` - Temporäre Dateien

## 💡 Ein-Zeilen-Bereinigung

Für schnelle manuelle Bereinigung:

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; find . -name "*.pyc" -delete; rm -rf .pytest_cache build dist
```

## 🚀 Nach der Bereinigung

Das bereinigte Projekt ist optimal für:
- **Git Repositories** - Kleinere Clone-Zeiten
- **Docker Images** - Reduzierte Image-Größe
- **Production Deployment** - Schnellere Startzeiten
- **Code Reviews** - Fokus auf wichtigen Code

---

**Hinweis:** Diese Scripts sind speziell für ASI-Core optimiert und respektieren die Projektstruktur.