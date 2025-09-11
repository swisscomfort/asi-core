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
