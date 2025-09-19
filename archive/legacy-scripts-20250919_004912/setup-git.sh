#!/bin/bash

# Git-Konfiguration
git config --global user.name "DEIN_NAME"
git config --global user.email "DEINE_EMAIL@example.com"

# Repository initialisieren (falls noch nicht geschehen)
git init

# Remote hinzufügen (ersetze mit deiner GitHub URL)
git remote add origin https://github.com/DEIN_USERNAME/asi-core.git

# Erste Commits
git add .
git commit -m "🧠 Initial ASI-Core System Documentation"

# Branch-Schutz für main
git checkout -b develop
git push -u origin develop
git checkout main
git push -u origin main

echo "✅ Git-Konfiguration abgeschlossen"
echo "📋 Nächste Schritte:"
echo "1. GitHub Repository erstellen"
echo "2. Branch Protection Rules einrichten"
echo "3. Secrets für Actions konfigurieren"
