# ASI Core PWA - GitHub Pages Deployment

Dieses Repository ist so konfiguriert, dass die PWA automatisch über GitHub Pages bereitgestellt wird.

## 🚀 Automatisches Deployment

Bei jedem Push auf den `main` Branch:

1. **Build-Prozess:** Die PWA wird automatisch gebaut
2. **Deployment:** Direkt zu GitHub Pages hochgeladen
3. **Live-URL:** Nach Aktivierung verfügbar unter `https://swisscomfort.github.io/asi-core/` (Repository: https://github.com/swisscomfort/asi-core)

## 📋 Setup-Schritte für GitHub Pages

### 1. Repository Settings

- Gehe zu Repository → Settings → Pages
- Source: "GitHub Actions" auswählen
- Der Workflow ist bereits konfiguriert

### 2. Push zum Deployment

```bash
git add .
git commit -m "Add PWA with GitHub Pages deployment"
git push origin main
```

### 3. Deployment Status

- Actions Tab → "Deploy PWA to GitHub Pages"
- Nach erfolgreichem Build ist die PWA live

## 🔧 Konfiguration

- **Base URL:** `/asi-core/` (für GitHub Pages)
- **PWA Manifest:** Automatisch angepasst
- **Service Worker:** Aktiviert für Offline-Betrieb
- **Icons:** 192x192 und 512x512 verfügbar

## 📱 Features der deployed PWA

✅ **Installierbar** als native App  
✅ **Offline-First** - funktioniert ohne Internet  
✅ **Progressive** - lädt schnell und cacht Ressourcen  
✅ **Responsive** - funktioniert auf allen Geräten  
✅ **Auto-Updates** - Service Worker aktualisiert automatisch

## 🌐 Live-Demo

Nach dem ersten Push: **Repository verfügbar unter https://github.com/swisscomfort/asi-core** (GitHub Pages Deployment folgt)

Die PWA kann dann direkt im Browser installiert werden!
