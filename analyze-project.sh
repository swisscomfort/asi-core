#!/usr/bin/env bash

# Analysiert das Projekt und identifiziert unnötige Dateien

echo "🔍 ASI-Core Projekt-Analyse"
echo "============================"

# Finde duplicate/ähnliche Dateien
echo ""
echo "📄 Potenzielle Duplikate:"
find . -type f -name "*.py" -exec basename {} \; | sort | uniq -d

# Ungenutzte Imports finden
echo ""
echo "📦 Dateien mit vielen Imports (potenzielle Bloat):"
find . -name "*.py" -exec grep -l "^import\|^from" {} \; | while read file; do
    count=$(grep "^import\|^from" "$file" | wc -l)
    if [ $count -gt 10 ]; then
        echo "  $file: $count imports"
    fi
done

# Große Funktionen/Klassen
echo ""
echo "📏 Große Python-Dateien (>500 Zeilen):"
find . -name "*.py" -exec wc -l {} \; | awk '$1 > 500 {print $2 ": " $1 " Zeilen"}'

# TODO und FIXME Comments
echo ""
echo "🚧 TODO/FIXME Kommentare:"
grep -r "TODO\|FIXME" --include="*.py" . 2>/dev/null | wc -l

# Leere oder fast leere Dateien
echo ""
echo "📭 Leere oder minimale Dateien (<5 Zeilen):"
find . -name "*.py" -exec wc -l {} \; | awk '$1 < 5 {print $2}'