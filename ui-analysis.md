# ASI Core - UI/Frontend Analyse

## Suche nach vorhandenen UI-Komponenten

```bash
# Suche nach Frontend/UI-relevanten Dateien
find /workspaces/asi-core -type f \( -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" -o -name "*.html" -o -name "*.css" -o -name "*.scss" \) 2>/dev/null
```

```bash
# Suche nach UI-Frameworks und Dependencies
find /workspaces/asi-core -name "package.json" -exec grep -l "react\|vue\|angular\|svelte" {} \; 2>/dev/null
```

```bash
# Suche nach UI-relevanten Verzeichnissen
find /workspaces/asi-core -type d \( -name "*ui*" -o -name "*frontend*" -o -name "*web*" -o -name "*app*" -o -name "*client*" \) 2>/dev/null
```

```bash
# Suche nach Desktop-App-Frameworks
find /workspaces/asi-core -name "*.toml" -o -name "Cargo.toml" | xargs grep -l "tauri\|electron" 2>/dev/null
```

```bash
# Suche nach Dokumentation über UI
find /workspaces/asi-core -name "*.md" | xargs grep -l -i "ui\|interface\|frontend\|gui" 2>/dev/null
```