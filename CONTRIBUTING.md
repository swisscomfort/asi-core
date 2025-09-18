# Contributing to ASI-Core

> **🎯 Your journey to building the future of personal AI starts here!**

[![Contributors](https://img.shields.io/github/contributors/swisscomfort/asi-core)](https://github.com/swisscomfort/asi-core/graphs/contributors)
[![Good First Issues](https://img.shields.io/github/issues/swisscomfort/asi-core/good%20first%20issue)](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
[![Help Wanted](https://img.shields.io/github/issues/swisscomfort/asi-core/help%20wanted)](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)

## 🚀 Quick Start - See it in Action!

**🌐 LIVE DEMO:** [**swisscomfort.github.io/asi-core**](https://swisscomfort.github.io/asi-core/)

Experience ASI-Core immediately in your browser! The PWA is fully functional, installable, and works offline.

### Local Development Setup (15 minutes):

```bash
# 1. Clone & Demo
git clone https://github.com/swisscomfort/asi-core.git
cd asi-core
./quick-demo.sh      # 2-minute interactive demo

# 2. Full Setup
./setup.sh           # Installs dependencies, creates configs
python main.py       # Start main system
```

---

## 🎯 Perfekte erste Contributions

### 👶 **Good First Issues** (1-2 Stunden)
[![Good First Issues](https://img.shields.io/badge/Finde-Good%20First%20Issues-green?style=for-the-badge)](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

- 🎨 **UI Verbesserungen** - React Components verschönern
- 📖 **Documentation** - README Übersetzungen, Typos fixen
- 🧪 **Tests schreiben** - Coverage erhöhen ist immer welcome!
- 🐛 **Bugs fixen** - Kleine Issues, große Wirkung
- 💡 **Examples erweitern** - Mehr Playground-Code

### 🛠️ **Intermediate** (halber Tag)
- 🚀 **Features implementieren** - Neue Module entwickeln
- 🔐 **Security verbessern** - Audit-Findings beheben
- ⚡ **Performance optimieren** - Bottlenecks beseitigen
- 🤖 **KI-Features** - Embedding-Models integrieren

### 🏆 **Advanced** (mehrere Tage)
- 🏗️ **Architektur** - Core-System Erweiterungen
- ⛓️ **Blockchain** - Smart Contract Development
- 📱 **Mobile** - PWA Features für iOS/Android
- 🔄 **CI/CD** - Workflow Optimierungen

---

## 🛠️ Development Environment

### 🐳 **Option 1: DevContainer (Empfohlen)**
```bash
# VS Code öffnen
code .
# "Reopen in Container" klicken - FERTIG! ✨
```

### 🐍 **Option 2: Lokale Installation**
```bash
# Python 3.10+ erforderlich
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 🧪 **Tests ausführen**
```bash
# Alle Tests
python -m pytest

# Spezifische Tests  
python -m pytest tests/test_state_management.py

# Coverage Report
python -m pytest --cov=asi_core --cov-report=html
```

---

## 📋 Contribution Workflow

### 1. **🍴 Fork & Branch**
```bash
# Fork über GitHub UI, dann:
git clone https://github.com/YOUR_USERNAME/asi-core.git
cd asi-core
git checkout -b feature/amazing-new-feature
```

### 2. **🔨 Develop & Test**
```bash
# Änderungen machen
# Tests schreiben/aktualisieren
python -m pytest
# Alles funktioniert? ✅
```

### 3. **📝 Commit & Push**
```bash
git add .
git commit -m "feat: add amazing new feature"
git push origin feature/amazing-new-feature
```

### 4. **🎯 Pull Request erstellen**
- [PR Template](/.github/pull_request_template.md) nutzen
- Screenshots bei UI-Änderungen
- Tests und Docs erwähnen

---

## 📚 Code Style & Standards

### 🐍 **Python**
```python
# Black formatter (automatisch via pre-commit)
black asi_core/

# Type hints verwenden
def process_reflection(content: str, state: int) -> Dict[str, Any]:
    """Process user reflection with state analysis."""
    return {"content": content, "state": state}
```

### ⚛️ **React/JavaScript**
```javascript
// Prettier formatting (automatisch)
// TypeScript preferiert
export interface ReflectionData {
  id: string;
  content: string;
  state: number;
  timestamp: Date;
}
```

### 📖 **Documentation**
```markdown
# Jede neue Funktion dokumentieren
# Examples bei API-Änderungen hinzufügen
# Docstrings für alle public functions
```

---

## 🤝 Community Guidelines

### ✅ **Do's**
- **Freundlich sein** - Wir sind alle hier um zu lernen! 
- **Fragen stellen** - Besser nachfragen als raten
- **Tests schreiben** - Code ohne Tests ist unvollständig
- **Dokumentieren** - Future You wird es danken
- **Feedback geben** - Konstruktive Reviews helfen allen

### ❌ **Don'ts**  
- **Nicht: Breaking Changes** ohne Discussion
- **Nicht: Code ohne Tests** submitte
- **Nicht: Komplexe PRs** - lieber aufteilen
- **Nicht: Toxic Verhalten** - siehe [Code of Conduct](CODE_OF_CONDUCT.md)

---

## 🏆 Recognition & Rewards

### 🥇 **Contributor Levels**
- **👶 First Timer** - Erste Contribution → Badge + Mention
- **🛠️ Regular** - 5+ Contributions → Maintainer Consideration  
- **🚀 Core** - 20+ Contributions → Repository Rights
- **🏆 Maintainer** - Trusted with Review Powers

### 🎁 **Perks**
- **🎊 Shoutouts** auf Social Media
- **📜 LinkedIn Recommendations** für gute Contributors
- **🎓 Learning Credits** für Courses (bei größeren Contributions)
- **💼 Job References** - wir empfehlen gerne!

---

## 📞 Need Help?

### 💬 **Instant Help**
- **[GitHub Discussions](https://github.com/swisscomfort/asi-core/discussions)** - Fragen stellen
- **[Discord Server](#)** - Live Chat (bald verfügbar)
- **Issues kommentieren** - Mentors helfen gerne!

### 📧 **Direct Contact**
- **Maintainer**: [@swisscomfort](https://github.com/swisscomfort)
- **Email**: `asi-core@example.com` (für private Themen)

### 🔗 **Resources**
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Verstehe das System
- **[API Reference](docs/API-REFERENCE.md)** - Complete API docs
- **[Examples](examples/)** - Learning by example
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues

---

## 🎯 Current Focus Areas

### 🔥 **High Priority** (Help needed!)
- [ ] **Performance Optimization** - Memory usage, response times
- [ ] **Mobile PWA** - iOS/Android specific features  
- [ ] **Accessibility** - WCAG compliance, screen readers
- [ ] **Internationalization** - Multi-language support

### 📈 **Growth Areas**
- [ ] **AI Integration** - More embedding models, better state detection
- [ ] **Blockchain Features** - Advanced smart contracts, L2 support
- [ ] **Cloud Deployment** - Docker, Kubernetes, cloud providers
- [ ] **Monitoring** - Analytics, performance metrics, health checks

---

## 🌟 Thank You!

Jeder Beitrag macht ASI-Core besser für alle! Von einem Typo-Fix bis zur neuen Feature-Implementation - alles hilft beim Aufbau der Zukunft von Personal AI.

**Ready to start? Check out our [Good First Issues](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)!** 🚀

---

*Built with ❤️ by developers, for developers. Let's make personal AI accessible to everyone!*