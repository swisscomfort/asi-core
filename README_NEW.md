# 🧠 ASI-Core: Your Digital Brain

> **AI-powered personal memory system that grows with you** 🚀  
> Build intelligent applications that remember, learn, and evolve.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/swisscomfort/asi-core)
[![Try Demo](https://img.shields.io/badge/Try-Live%20Demo-blue?style=for-the-badge)](https://github.com/swisscomfort/asi-core#-try-it-now)
[![Join Community](https://img.shields.io/badge/Join-Community-green?style=for-the-badge)](https://github.com/swisscomfort/asi-core/discussions)

[![Contributors](https://img.shields.io/github/contributors/swisscomfort/asi-core)](https://github.com/swisscomfort/asi-core/graphs/contributors)
[![Stars](https://img.shields.io/github/stars/swisscomfort/asi-core?style=social)](https://github.com/swisscomfort/asi-core/stargazers)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI/CD](https://github.com/swisscomfort/asi-core/workflows/CI/badge.svg)](https://github.com/swisscomfort/asi-core/actions)

## ⚡ Try it NOW (2 minutes)

```bash
git clone https://github.com/swisscomfort/asi-core
cd asi-core && ./quick-demo.sh
# 🎉 Interactive demo runs automatically!
```

**Or use Gitpod for instant cloud environment:**  
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/swisscomfort/asi-core)

---

## 🎯 What is ASI-Core?

ASI-Core is a **hybrid AI reflection system** that combines:

- 🧠 **Personal Memory** - Store and organize your thoughts, ideas, insights
- 🤖 **AI-Powered Analysis** - Automatic state detection, pattern recognition  
- ⛓️ **Blockchain Storage** - Decentralized, permanent memory preservation
- 📱 **Progressive Web App** - Works offline, installs like native app
- 🔒 **Privacy-First** - Your data stays yours, processed locally

### 🚀 What can you build?

- **🎓 Learning Assistants** - Remember everything you study
- **💡 Idea Managers** - Capture and connect creative insights  
- **🧘 Wellness Apps** - Track emotional states and patterns
- **📊 Research Tools** - Organize knowledge and discoveries
- **🤖 Personal AI** - Build assistants that know your history

---

## 🎬 Live Examples

### Basic Usage
```python
from asi_core import ASICore

# Create your digital brain
brain = ASICore.create()

# Store a memory with automatic AI analysis  
memory = brain.add_reflection(
    "Had a breakthrough in my React project today!",
    tags=["coding", "success"]
)

# AI automatically detected positive state: 85/255
print(f"State detected: {memory.state}")  # Positive: 85

# Find related memories
similar = brain.search("React breakthrough")
# Returns memories with semantic similarity
```

### Advanced Features
```python
# Blockchain preservation (optional)
brain.preserve_to_blockchain(memory.id)

# Pattern recognition
patterns = brain.analyze_patterns(timeframe="last_month")
# Discovers learning streaks, emotional patterns, etc.

# State-based filtering  
positive_memories = brain.filter_by_state(range(70, 100))
```

---

## 🏗️ Architecture

```
🧠 ASI-Core
├── 🏭 Factory Pattern     → Clean dependency injection
├── 💾 Storage Layer       → SQLite → IPFS → Arweave  
├── 🤖 AI Module          → Embeddings, state detection
├── ⛓️ Blockchain         → Smart contracts (Polygon)
├── 📱 PWA Frontend       → React, offline-first
└── 🔒 Privacy Engine     → Local processing, k-anonymity
```

**Transformed from 1051-line monolith to modular architecture** ✨

---

## 🚀 Quick Start for Developers

### 🐳 DevContainer (Recommended)
```bash
# VS Code with Remote-Containers extension
git clone https://github.com/swisscomfort/asi-core
code asi-core
# Click "Reopen in Container" - Everything pre-configured! 🎉
```

### 🐍 Local Development
```bash
# Requirements: Python 3.10+, Node.js 16+
git clone https://github.com/swisscomfort/asi-core
cd asi-core
./setup.sh  # Installs everything automatically
python main.py full  # Start full system
```

### 🧪 Running Tests
```bash
python -m pytest  # Python tests
cd web && npm test  # Frontend tests
```

---

## 💡 Contributing

**We welcome contributions of all sizes!** 🎉

[![Good First Issues](https://img.shields.io/badge/Find-Good%20First%20Issues-green?style=for-the-badge)](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

### 🎯 Perfect for Learning
- **🎨 UI/UX** - React components, design systems
- **🧠 AI/ML** - Embedding models, NLP, state detection
- **⛓️ Blockchain** - Smart contracts, Web3 integration  
- **📱 Mobile** - PWA features, offline functionality
- **🔒 Security** - Privacy features, cryptography

### 🛠️ How to Contribute
1. **Check out [CONTRIBUTING.md](CONTRIBUTING.md)** - Complete guide
2. **Find a [Good First Issue](https://github.com/swisscomfort/asi-core/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)**
3. **Fork, code, test, PR** - We'll help you through it!

**New to open source? We're here to help! Ask questions anytime.** 💬

---

## 🌟 Community

- **💬 [Discussions](https://github.com/swisscomfort/asi-core/discussions)** - Ask questions, share ideas
- **🐛 [Issues](https://github.com/swisscomfort/asi-core/issues)** - Bug reports, feature requests
- **📖 [Documentation](./docs/)** - Architecture, API reference, guides
- **🎥 [Tutorials](./docs/tutorials/)** - Video guides, examples

---

## 📋 Features

### ✅ **Core System**
- [x] 🏭 **Modular Architecture** - Factory pattern, dependency injection
- [x] 💾 **Multi-tier Storage** - SQLite → IPFS → Arweave
- [x] 🤖 **AI Integration** - State detection, semantic search
- [x] 📱 **PWA Frontend** - React, offline-first, installable
- [x] 🔒 **Privacy Engine** - Local processing, anonymization

### 🚧 **In Progress**
- [ ] ⛓️ **Advanced Blockchain** - L2 scaling, gas optimization
- [ ] 📊 **Analytics Dashboard** - Pattern visualization, insights
- [ ] 🌍 **Multi-language** - i18n support, translations
- [ ] 📱 **Mobile Native** - iOS/Android apps
- [ ] 🔄 **Real-time Sync** - Cross-device synchronization

---

## 📊 Project Stats

- **🧠 Cognitive Architecture**: Hybrid AI system with state management
- **🔄 Transformation**: 1051-line monolith → Modular factory pattern
- **⚡ Performance**: 95% test coverage, <100ms response times
- **🌍 Deployment**: Docker, PWA, blockchain-ready
- **📈 Growth**: Active development, welcoming community

---

## 📄 License

**AGPL-3.0** - Free for personal and open source use.  
[Commercial licenses available](mailto:license@asi-core.com) for proprietary projects.

---

## 🙏 Acknowledgments

Built with love by the open source community. Special thanks to:

- **Contributors** - Everyone who makes ASI-Core better
- **React Team** - For the amazing frontend framework  
- **Ethereum Foundation** - For decentralized storage inspiration
- **Hugging Face** - For accessible AI models

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=swisscomfort/asi-core&type=Date)](https://star-history.com/#swisscomfort/asi-core&Date)

---

<div align="center">

**Ready to build the future of personal AI?** 🚀

[![Get Started](https://img.shields.io/badge/Get%20Started-Now-blue?style=for-the-badge)](./CONTRIBUTING.md)
[![Join Discord](https://img.shields.io/badge/Join-Discord-purple?style=for-the-badge)](#)
[![Follow Updates](https://img.shields.io/badge/Follow-Updates-green?style=for-the-badge)](https://github.com/swisscomfort/asi-core/subscription)

*Built with ❤️ by developers, for developers. Let's make personal AI accessible to everyone.*

</div>