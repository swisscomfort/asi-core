#!/usr/bin/env bash

# ASI-Core Bereinigungsmanager
# Vereint alle Bereinigungsoptionen in einem Tool

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

show_help() {
    echo "🧹 ASI-Core Bereinigungsmanager"
    echo "==============================="
    echo ""
    echo "Verwendung: $0 [OPTION]"
    echo ""
    echo "Optionen:"
    echo "  quick       Schnelle Bereinigung (empfohlen für täglich)"
    echo "  full        Umfassende Bereinigung"
    echo "  analyze     Projekt-Analyse durchführen"
    echo "  production  Production-Vorbereitung (VORSICHT!)"
    echo "  help        Diese Hilfe anzeigen"
    echo ""
    echo "Beispiele:"
    echo "  $0 quick      # Schnelle tägliche Bereinigung"
    echo "  $0 full       # Vor Git Commit"
    echo "  $0 analyze    # Projekt analysieren"
    echo ""
    echo "Für Details siehe: CLEANUP_README.md"
}

run_quick() {
    echo "🚀 Führe schnelle Bereinigung aus..."
    if [ -f "$SCRIPT_DIR/quick-cleanup.sh" ]; then
        "$SCRIPT_DIR/quick-cleanup.sh"
    else
        echo "❌ quick-cleanup.sh nicht gefunden!"
        exit 1
    fi
}

run_full() {
    echo "🔄 Führe umfassende Bereinigung aus..."
    if [ -f "$SCRIPT_DIR/cleanup.sh" ]; then
        "$SCRIPT_DIR/cleanup.sh"
    else
        echo "❌ cleanup.sh nicht gefunden!"
        exit 1
    fi
}

run_analyze() {
    echo "🔍 Führe Projekt-Analyse aus..."
    if [ -f "$SCRIPT_DIR/analyze-project.sh" ]; then
        "$SCRIPT_DIR/analyze-project.sh"
    else
        echo "❌ analyze-project.sh nicht gefunden!"
        exit 1
    fi
}

run_production() {
    echo "🚀 WARNUNG: Production-Vorbereitung entfernt Entwicklungs-Dateien!"
    echo ""
    read -p "Sind Sie sicher? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "$SCRIPT_DIR/prepare-production.sh" ]; then
            "$SCRIPT_DIR/prepare-production.sh"
        else
            echo "❌ prepare-production.sh nicht gefunden!"
            exit 1
        fi
    else
        echo "Abgebrochen."
    fi
}

# Hauptlogik
case "${1:-help}" in
    quick)
        run_quick
        ;;
    full)
        run_full
        ;;
    analyze)
        run_analyze
        ;;
    production)
        run_production
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unbekannte Option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac