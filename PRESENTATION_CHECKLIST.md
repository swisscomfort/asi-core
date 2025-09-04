# Präsentations-Checklist

## Sofort erledigen (nächste 15 Minuten):

### 1. Build-Problem beheben

- [ ] Export-Syntax in allen React-Komponenten überprüfen
- [ ] Production Build zum Laufen bringen

### 2. Demo-Daten erstellen

- [ ] Einige Beispiel-Reflexionen hinzufügen
- [ ] config/secrets.json mit Demo-Werten erstellen

### 3. Präsentations-Script

- [ ] 3-Minuten Demo-Flow definieren
- [ ] Screenshots/Videos der UI erstellen

## Demo-Kommandos bereithalten:

```bash
# Backend starten
cd /workspaces/asi-core
python main.py

# Frontend starten (separates Terminal)
cd /workspaces/asi-core/web
npm run dev

# Demo-Reflexion verarbeiten
python main.py process "Heute habe ich über meine Karriereziele nachgedacht"

# HRM-Demo
python main.py hrm-test

# Suche demonstrieren
python main.py search "Karriere"
```

## Präsentations-Story (5 Minuten):

1. **Problem** (30s): Datenschutz bei persönlichen Reflexionen
2. **Lösung** (60s): ASI-Core Architektur erklären
3. **Demo** (180s): Live-Demonstration
4. **Ausblick** (30s): Roadmap und Vision

## Backup-Plan:

Falls Live-Demo fehlschlägt:

- Screenshots bereithalten
- Video-Recording als Fallback
- Architektur-Diagramm zeigen
