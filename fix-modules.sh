#!/usr/bin/env bash
# Sofort-Fix für fehlende Module

echo "🔧 Fixing ASI-Core modules..."

# 1. Erstelle fehlende Verzeichnisse
mkdir -p asi_core
mkdir -p src/ai/hrm/high_level
mkdir -p src/ai/hrm/low_level

# 2. Erstelle pattern_recognition.py falls fehlt
if [ ! -f "src/ai/hrm/high_level/pattern_recognition.py" ]; then
cat > src/ai/hrm/high_level/pattern_recognition.py << 'EOF'
from typing import Dict, List, Any

class PatternRecognizer:
    def __init__(self, embedding_system, local_db):
        self.embedding_system = embedding_system
        self.local_db = local_db
        
    def analyze_patterns(self, user_context: Dict[str, Any]) -> List[Dict]:
        patterns = []
        content = user_context.get("content", "").lower()
        
        # Simple pattern detection
        if "stress" in content:
            patterns.append({
                "type": "temporal",
                "tag": "stress",
                "frequency": 3,
                "confidence": 0.7
            })
        
        if "fokus" in content or "focus" in content:
            patterns.append({
                "type": "similarity",
                "tags": ["fokus"],
                "similarity": 0.8
            })
            
        return patterns
EOF
fi

# 3. Erstelle detail_analysis.py falls fehlt
if [ ! -f "src/ai/hrm/low_level/detail_analysis.py" ]; then
cat > src/ai/hrm/low_level/detail_analysis.py << 'EOF'
from typing import Dict, Any

class DetailAnalyzer:
    def analyze_details(self, user_context: Dict[str, Any]) -> Dict:
        content = user_context.get("content", "")
        word_count = len(content.split())
        
        sentiment_score = 0.5  # Neutral default
        if any(word in content.lower() for word in ["gut", "super", "toll"]):
            sentiment_score = 0.8
        elif any(word in content.lower() for word in ["schlecht", "müde", "stress"]):
            sentiment_score = 0.3
            
        return {
            "word_count": word_count,
            "sentiment": sentiment_score,
            "confidence_score": 0.7,
            "key_topics": ["reflexion", "selbst"]
        }
EOF
fi

# 4. Erstelle ASI-Core Module
cat > asi_core/__init__.py << 'EOF'
from .blockchain import ASIBlockchainClient, ASIBlockchainError, create_blockchain_client_from_config
from .search import ASIEmbeddingGenerator, ASISemanticSearch
from .state_management import ASIStateManager, suggest_state_from_text

__all__ = [
    'ASIBlockchainClient',
    'ASIBlockchainError',
    'create_blockchain_client_from_config',
    'ASIEmbeddingGenerator',
    'ASISemanticSearch',
    'ASIStateManager',
    'suggest_state_from_text'
]
EOF

echo "✅ Modules fixed!"
