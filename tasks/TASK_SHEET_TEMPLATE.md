# ASI Core Task Sheet Template

## YAML Schema für Task-Sheets

Dieses Template definiert die Struktur für alle ASI Core Tasks. Jeder Task muss diese Felder enthalten:

```yaml
task_id: "M{milestone}-T{number}"      # Format: M1-T001, M2-T005, etc.
title: "Kurze, klare Beschreibung"     # 3-7 Wörter, actionsorientiert
version: "1.0"                         # Versionierung für Updates
status: "open"                         # open|claimed|submitted|approved|paid

# Wirtschaftliche Parameter
bounty:
  token: "ASI"                         # Token-Symbol
  amount: 2500                         # Bounty-Höhe  
  currency_equivalent: "~25 USD"       # Orientierungshilfe

# Zeitrahmen
created: "2025-09-16"                  # Erstellungsdatum
deadline: "2025-10-15"                 # Späteste Abgabe
estimated_hours: 8                     # Geschätzte Arbeitszeit

# Task-Hierarchie  
dependencies: 
  - "M0-T001"                          # Abhängige Tasks (müssen completed sein)
  - "M0-T002"
blocks:                                # Tasks die von diesem abhängen
  - "M1-T005"
  - "M1-T006"

# Arbeitsanforderungen
deliverables:
  - "GitHub PR mit funktionierendem Code"
  - "README mit Installations-/Nutzungsanleitung" 
  - "Tests mit ≥80% Coverage für neue Module"
  - "IPFS-Upload aller Artefakte"

# Objektive Abnahmekriterien
definition_of_done:
  - "CI Pipeline: build+lint+test erfolgreich"
  - "Lighthouse PWA Score ≥ 90"
  - "Security Scan ohne Critical/High Findings"
  - "Peer Review von mindestens 2 Reviewern"
  - "Deployment im Staging-Environment erfolgreich"

# Verifikation & Reviews
reviewers:
  - "0xReviewer1Address..."            # Ethereum-Adressen
  - "0xReviewer2Address..."
  
auto_verifier:
  github:
    repo: "swisscomfort/asi-core"
    branch: "main"
    required_checks: 
      - "build"
      - "test"  
      - "lint"
      - "security-scan"
  content_checks:
    must_include:                      # Dateien die existieren müssen
      - "README.md"
      - "package.json"
    must_not_include:                  # Verbotene Inhalte
      - "hardcoded-secrets"
      - "TODO.*FIXME"

# Metadaten
category: "frontend"                   # frontend|backend|contracts|docs|infra
difficulty: "intermediate"             # beginner|intermediate|advanced
skills_required:
  - "JavaScript/TypeScript"
  - "React/Next.js"
  - "PWA Development"

# Compliance
license: "AGPL-3.0"                   # Open Source Lizenz
contributor_agreement: "required"      # CLA erforderlich
privacy_impact: "low"                 # low|medium|high

# Evidence & Artefakte (wird von Contributor ausgefüllt)
evidence:
  github_pr: ""                       # URL zum PR
  ipfs_cids: []                       # Liste von IPFS-Hashes
  demo_url: ""                        # Live-Demo falls applicable
  documentation: ""                   # Zusätzliche Dokumentation

# Zusätzliche Informationen
notes: |
  Zusätzliche Kontext-Informationen, Tipps oder wichtige Hinweise
  für Contributors. Kann Markdown enthalten.
  
  **Wichtig**: UX soll schlicht bleiben, Fokus auf Funktionalität.

# Belohnungs-Mechanismen
rewards:
  referral_bonus: 5                   # % Bonus für Referrer
  early_completion_bonus: 10          # % Bonus bei Abgabe vor Deadline
  quality_bonus: 15                   # % Bonus bei außergewöhnlicher Qualität

# Governance (optional)
voting_required: false                # Erfordert DAO-Abstimmung
dispute_process: "standard"           # standard|expedited|dao-only
```

## Validierungs-Regeln

1. **task_id** muss unique sein und Format M{zahl}-T{zahl} folgen
2. **bounty.amount** muss > 0 sein  
3. **deadline** muss in der Zukunft liegen
4. **dependencies** Tasks müssen existieren
5. **reviewers** müssen gültige Ethereum-Adressen sein
6. **deliverables** und **definition_of_done** müssen mindestens 1 Item haben

## Status-Transitions

```
open → claimed → submitted → approved → paid
  ↓       ↓         ↓          ↓
  ↓       ↓         ↓          ↓
timeout  timeout   rejected   disputed
  ↓       ↓         ↓          ↓  
 open    open     claimed     dao-vote
```

## IPFS Integration

Jeder Task wird als YAML-Datei auf IPFS gepinnt:
- Task-CID wird im Smart Contract registriert
- Evidence-CIDs werden bei Submission hinzugefügt
- Verifier-Reports werden als JSON mit Signaturen gepinnt