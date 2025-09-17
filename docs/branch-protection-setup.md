# 🛡️ ASI-Core Branch Protection Setup

## 🎯 Ziel
Professioneller Branch-Schutz für das `main` Branch mit Enterprise-Standards.

## 📋 Voraussetzungen
- ✅ Alle Links funktionieren (getestet mit `./link_checker.sh`)
- ✅ GitHub Pro Account aktiv
- ✅ Repository Owner oder Admin-Rechte

## 🚀 Schritt-für-Schritt Setup

### 1. Repository Settings öffnen
```
GitHub.com → Dein Repository → Settings → Branches
```

### 2. Branch Protection Rule erstellen
```
Branch name pattern: main
```

### 3. Require Pull Requests aktivieren
```yaml
✅ Require a pull request before merging
✅ Require approvals (Empfohlen: 1-2)
✅ Dismiss stale pull request approvals when new commits are pushed
✅ Require review from Code Owners (Optional)
✅ Restrict who can dismiss pull request reviews (Optional)
```

### 4. Status Checks aktivieren
```yaml
✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging

Status checks:
- continuous-integration/github-actions
- security-scan
- codeql-analysis
- test-results
```

### 5. Branch Restrictions aktivieren
```yaml
✅ Include administrators
✅ Restrict pushes that create matching branches
✅ Allow force pushes: ❌ DEAKTIVIERT
✅ Allow deletions: ❌ DEAKTIVIERT
```

### 6. Lineare History erzwingen (Optional)
```yaml
✅ Require linear history
```

## 🔧 Erweiterte Konfiguration

### Code Owners Setup
Erstelle `.github/CODEOWNERS`:
```
# Global Owners
* @swisscomfort

# Spezifische Dateien
*.md @swisscomfort
src/ @swisscomfort
web/ @swisscomfort
```

### Auto-Merge aktivieren
```
Repository Settings → General → Pull Requests
✅ Allow auto-merge
✅ Automatically delete head branches
```

## 📊 Branch Protection Status

### Aktuelle Konfiguration prüfen:
```bash
# Branch Protection Status
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/swisscomfort/asi-core/branches/main/protection
```

### Erforderliche Workflows:
- ✅ CI/CD Pipeline (`.github/workflows/ci.yml`)
- ✅ Security Scan (`.github/workflows/security-scan.yml`)
- ✅ CodeQL Analysis (`.github/workflows/codeql.yml`)

## 🧪 Test der Konfiguration

### 1. Test-Pull Request erstellen
```bash
# Neuen Branch erstellen
git checkout -b test-branch-protection

# Änderung vornehmen
echo "Test" >> test.txt

# Commit und Push
git add test.txt
git commit -m "Test Branch Protection"
git push origin test-branch-protection
```

### 2. Pull Request erstellen
- Gehe zu: https://github.com/swisscomfort/asi-core/pulls
- "New Pull Request" → Branch auswählen
- Prüfe, ob alle Checks durchlaufen

### 3. Branch Protection testen
- Versuche direkt auf `main` zu pushen (sollte fehlschlagen)
- Versuche Force Push (sollte fehlschlagen)
- Versuche Branch zu löschen (sollte fehlschlagen)

## 🚨 Troubleshooting

### Problem: "Required status check" fehlt
**Lösung:** Stelle sicher, dass alle Workflows korrekt benannt sind
```yaml
# In Workflow-Dateien
name: "continuous-integration/github-actions"
```

### Problem: Admin kann nicht pushen
**Lösung:** Deaktiviere "Include administrators" oder füge Admin als Code Owner hinzu

### Problem: Branch kann nicht gemergt werden
**Lösung:** Prüfe alle erforderlichen Approvals und Status Checks

## 📈 Monitoring & Wartung

### Regelmäßige Checks:
```bash
# Monatlich: Branch Protection überprüfen
# Bei Workflow-Änderungen: Status Checks aktualisieren
# Bei Team-Änderungen: Code Owners aktualisieren
```

### Metriken tracken:
- ✅ Merge Success Rate
- ✅ Time to Merge
- ✅ Failed CI/CD Runs
- ✅ Security Vulnerabilities

## 🎉 Erfolgreich eingerichtet!

Nach dem Setup:
- ✅ `main` Branch ist geschützt
- ✅ Alle Pushes erfordern PRs
- ✅ Code Reviews sind mandatory
- ✅ CI/CD läuft automatisch
- ✅ Security Scans sind aktiv

## 📞 Support

Bei Problemen:
1. GitHub Docs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
2. Repository Issues: https://github.com/swisscomfort/asi-core/issues
3. Community Support: GitHub Discussions

---

*Branch Protection gewährleistet Code-Qualität und Sicherheit* 🛡️