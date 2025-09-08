# 🚀 ASI-Core Deployment Alternativen

Da GitHub Pages mit privaten Pro+ Repositories Probleme bereitet, hier sind die verfügbaren Alternativen:

## 🎯 **SOFORTIGE LÖSUNG: Lokaler Server**

```bash
./start-pwa.sh
```

**Ergebnis:**

- ✅ PWA läuft sofort unter `http://localhost:3000`
- ✅ Vollständige PWA-Funktionalität
- ✅ Installierbar
- ✅ Offline-fähig
- ✅ Alle Features verfügbar

## 🌐 **Option 1: Netlify (Empfohlen)**

### Setup:

1. **Netlify Account:** https://netlify.com
2. **Repository verknüpfen:** GitHub Integration
3. **Build Settings:**
   - Build command: `cd web && npm run build`
   - Publish directory: `web/dist`
4. **Secrets in GitHub hinzufügen:**
   - `NETLIFY_AUTH_TOKEN`
   - `NETLIFY_SITE_ID`

### Vorteile:

- ✅ Kostenlos für persönliche Projekte
- ✅ Automatische HTTPS
- ✅ Custom Domain möglich
- ✅ CDN weltweit
- ✅ Private Repository Support

## 🔷 **Option 2: Vercel**

### Setup:

1. **Vercel Account:** https://vercel.com
2. **GitHub Integration:** Import Repository
3. **Secrets in GitHub hinzufügen:**
   - `VERCEL_TOKEN`
   - `ORG_ID`
   - `PROJECT_ID`

### Vorteile:

- ✅ Hervorragende Performance
- ✅ Edge Functions Support
- ✅ Automatische Optimierung
- ✅ Private Repository Support

## 🏠 **Option 3: Codespace Port Forwarding**

### Aktuell verfügbar:

```bash
cd web && npm run dev
```

**URL:** Wird automatisch von Codespace bereitgestellt

- ✅ Sofortiger Zugriff
- ✅ Live-Reload während Entwicklung
- ✅ Alle PWA-Features in Dev-Modus

## 📊 **Empfehlung:**

1. **Für sofortigen Test:** `./start-pwa.sh`
2. **Für Production:** Netlify Setup
3. **Für Entwicklung:** `npm run dev` in Codespace

## 🔧 **Workflows bereit:**

- ✅ `deploy-netlify.yml` - Bereit für Netlify
- ✅ `deploy-vercel.yml` - Bereit für Vercel
- ✅ `start-pwa.sh` - Lokaler Server

**Alle Alternativen unterstützen private Repositories und GitHub Pro+ vollständig!**
