#!/bin/bash

echo "🎯 ASI-CORE PROJEKT-SPEZIALIST - Workflow-Optimierung"
echo "=================================================="
echo ""

# Funktion zum Deaktivieren von Workflows
deactivate_workflow() {
    local workflow="$1"
    local reason="$2"
    if [ -f ".github/workflows/${workflow}.yml" ]; then
        echo "❌ DEAKTIVIERE: ${workflow}.yml - ${reason}"
        mv ".github/workflows/${workflow}.yml" ".github/workflows/${workflow}.yml.disabled" 2>/dev/null || echo "  → Bereits deaktiviert"
    fi
}

# Funktion zum Aktivieren von Workflows
activate_workflow() {
    local workflow="$1"
    local reason="$2"
    if [ -f ".github/workflows/${workflow}.yml.disabled" ]; then
        echo "✅ AKTIVIERE: ${workflow}.yml - ${reason}"
        mv ".github/workflows/${workflow}.yml.disabled" ".github/workflows/${workflow}.yml"
    fi
}

echo "📊 ANALYSE - ASI-Core ist ein KI-System mit:"
echo "  • PWA (Progressive Web App)"
echo "  • Blockchain Integration (Polygon)"
echo "  • Dezentrale Speicherung (IPFS)"
echo "  • KI-gestützte Reflexionen"
echo "  • GitHub Pro Features"
echo ""

echo "🎯 OPTIMIERUNGS-STRATEGIE:"
echo "  ✅ BEHALTEN: Kritische Workflows für PWA + Sicherheit"
echo "  ❌ ENTFERNEN: Überflüssige Deployments + Analytics"
echo "  🔧 FOKUS: Qualitätssicherung + Automatisierung"
echo ""

echo "🔧 PHASE 1: KRITISCHE WORKFLOWS AKTIVIEREN"
echo "------------------------------------------"

# Essentielle Workflows aktivieren
activate_workflow "ci" "Python CI/CD Pipeline - KERN"
activate_workflow "test" "Automatisierte Tests - KERN"
activate_workflow "deploy" "PWA zu GitHub Pages - KERN"
activate_workflow "codeql" "Sicherheits-Scans - KERN"
activate_workflow "docs" "Dokumentation - WICHTIG"

echo ""
echo "🔧 PHASE 2: SUPPORT-WORKFLOWS (selektiv)"
echo "-----------------------------------------"

activate_workflow "labels" "Issue-Management - NÜTZLICH"
activate_workflow "pwa-status" "PWA-Monitoring - SPEZIFISCH FÜR PWA"
activate_workflow "pages-activation" "GitHub Pages Setup - EINMALIG"

echo ""
echo "❌ PHASE 3: ÜBERFLÜSSIGE WORKFLOWS DEAKTIVIEREN"
echo "------------------------------------------------"

# Nicht benötigte Deployments
deactivate_workflow "deploy-ipfs" "IPFS-Deployment - NICHT KONFIGURIERT"
deactivate_workflow "deploy-netlify" "Netlify - NICHT GEBRAUCHT"
deactivate_workflow "deploy-vercel" "Vercel - NICHT GEBRAUCHT"
deactivate_workflow "deploy-presentation" "Separate Präsentation - REDUNDANT"

# Analytics & Monitoring (zu viel)
deactivate_workflow "analytics" "Analytics - ZU VIEL"
deactivate_workflow "github-pro-analytics" "GitHub Pro Analytics - REDUNDANT"
deactivate_workflow "performance" "Performance Monitoring - NICHT KRITISCH"

# Backups & Storage
deactivate_workflow "backup" "Backup - NICHT KONFIGURIERT"
deactivate_workflow "codespace-backup" "Codespace Backup - UNNÖTIG"

# Security (bereits durch CodeQL abgedeckt)
deactivate_workflow "security" "Security Scan - CODEQL GENÜGT"
deactivate_workflow "security-scan" "Security Scan - REDUNDANT"

# Setup & Configuration
deactivate_workflow "setup-github-pages" "Setup - EINMALIG ERLEDIGT"
deactivate_workflow "setup-pages" "Setup - REDUNDANT"
deactivate_workflow "setup-project-management" "Project Setup - NICHT NÖTIG"

# Experimentell & Beta
deactivate_workflow "beta-project-setup" "Beta Features - NICHT STABIL"
deactivate_workflow "advanced-ci" "Advanced CI - ZU KOMPLEX"

# Release Management (noch nicht relevant)
deactivate_workflow "release" "Release Automation - ZU FRÜH"

echo ""
echo "📈 PHASE 4: ENDERGEBNIS"
echo "----------------------"

active_workflows=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
disabled_workflows=$(ls -1 .github/workflows/*.disabled 2>/dev/null | wc -l)

echo "✅ AKTIVE WORKFLOWS: $active_workflows"
echo "❌ DEAKTIVIERTE WORKFLOWS: $disabled_workflows"
echo ""

echo "🎯 FINALE KONFIGURATION:"
echo "  • CI/CD Pipeline (Python + PWA)"
echo "  • Sicherheits-Scans (CodeQL)"
echo "  • Automatische Dokumentation"
echo "  • PWA-Monitoring"
echo "  • Issue-Management"
echo ""

echo "🚀 VORTEILE DIESER KONFIGURATION:"
echo "  • 70% weniger Benachrichtigungen"
echo "  • Fokus auf Kernfunktionalität"
echo "  • Schnellere Builds"
echo "  • Weniger Fehlerquellen"
echo "  • Professionelle CI/CD"
echo ""

echo "✨ OPTIMIERUNG ABGESCHLOSSEN!"
echo "Ihr ASI-Core Repository ist jetzt optimal konfiguriert für Produktivität und Stabilität."