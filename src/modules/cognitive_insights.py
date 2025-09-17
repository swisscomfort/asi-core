#!/usr/bin/env python3
"""
ASI Core - Cognitive Insights Module
Flask Blueprint für kognitive Einsichten und Bias-Erkennung
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

# Flask Blueprint für kognitive Einsichten
cognitive_insights_bp = Blueprint('cognitive_insights', __name__)


class CognitiveBiasDetector:
    """
    Erkennt kognitive Verzerrungen in Reflexions-Texten.
    """
    
    def __init__(self):
        """Initialisiert den Bias-Detector mit bekannten Bias-Mustern."""
        self.bias_patterns = {
            'confirmation_bias': {
                'keywords': ['bestätigt', 'wie erwartet', 'natürlich', 'offensichtlich'],
                'patterns': [r'\bwie ich dachte\b', r'\bwar klar\b', r'\bnatürlich\b'],
                'description': 'Tendenz, Informationen zu bevorzugen, die bestehende Überzeugungen bestätigen'
            },
            'anchoring_bias': {
                'keywords': ['zuerst', 'anfangs', 'ursprünglich', 'initial'],
                'patterns': [r'\bzuerst dachte ich\b', r'\banfangs war\b'],
                'description': 'Übermäßiger Fokus auf erste Informationen bei Entscheidungen'
            },
            'availability_heuristic': {
                'keywords': ['kürzlich', 'letztens', 'neulich', 'erst'],
                'patterns': [r'\bkann mich erinnern\b', r'\bwar mal\b'],
                'description': 'Überschätzung der Wahrscheinlichkeit aufgrund leicht abrufbarer Beispiele'
            },
            'negativity_bias': {
                'keywords': ['aber', 'jedoch', 'trotzdem', 'leider', 'problem', 'schlecht'],
                'patterns': [r'\baber\b', r'\bjedoch\b', r'\btrotzdem\b'],
                'description': 'Tendenz, negative Informationen stärker zu gewichten als positive'
            },
            'optimism_bias': {
                'keywords': ['sicher', 'bestimmt', 'definitiv', 'natürlich schaffe'],
                'patterns': [r'\bsicher schaffe\b', r'\bwird schon\b'],
                'description': 'Überschätzung positiver Ausgänge bei eigenen Plänen'
            },
            'planning_fallacy': {
                'keywords': ['schnell', 'einfach', 'kurz', 'mal eben'],
                'patterns': [r'\bschnell mal\b', r'\beinfach nur\b', r'\bmal eben\b'],
                'description': 'Unterschätzung der Zeit und Ressourcen für Aufgaben'
            }
        }
    
    def detect_biases(self, text: str) -> List[Dict]:
        """
        Erkennt kognitive Verzerrungen im Text.
        
        Args:
            text: Zu analysierender Text
            
        Returns:
            Liste von erkannten Biases mit Positionen und Beschreibungen
        """
        detected_biases = []
        text_lower = text.lower()
        
        for bias_name, bias_info in self.bias_patterns.items():
            bias_score = 0
            found_keywords = []
            found_patterns = []
            
            # Prüfe Keywords
            for keyword in bias_info['keywords']:
                if keyword in text_lower:
                    bias_score += 1
                    found_keywords.append(keyword)
            
            # Prüfe Patterns
            for pattern in bias_info['patterns']:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    bias_score += 2  # Patterns gewichten schwerer
                    found_patterns.append({
                        'pattern': pattern,
                        'match': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
            
            # Füge Bias hinzu wenn Score hoch genug
            if bias_score > 0:
                confidence = min(bias_score / 5.0, 1.0)  # Normalisiere auf 0-1
                
                detected_biases.append({
                    'bias_type': bias_name,
                    'description': bias_info['description'],
                    'confidence': confidence,
                    'score': bias_score,
                    'evidence': {
                        'keywords': found_keywords,
                        'patterns': found_patterns
                    }
                })
        
        # Sortiere nach Confidence
        detected_biases.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detected_biases


class CognitiveSuggestionGenerator:
    """
    Generiert kognitive Verbesserungsvorschläge basierend auf Bias-Erkennung.
    """
    
    def __init__(self):
        """Initialisiert den Suggestion Generator."""
        self.suggestion_templates = {
            'confirmation_bias': [
                'Hinterfrage deine Annahmen: Welche Gegenargumente könntest du übersehen haben?',
                'Suche bewusst nach Informationen, die deiner aktuellen Sichtweise widersprechen.',
                'Frage dich: "Was würde meine Meinung ändern können?"'
            ],
            'anchoring_bias': [
                'Betrachte das Problem aus verschiedenen Ausgangspunkten.',
                'Ignoriere die erste Information und starte die Analyse neu.',
                'Sammle mehrere unabhängige Einschätzungen, bevor du entscheidest.'
            ],
            'availability_heuristic': [
                'Suche nach statistischen Daten statt persönlicher Anekdoten.',
                'Berücksichtige Beispiele, die dir nicht sofort einfallen.',
                'Frage dich: "Ist dieses Beispiel repräsentativ für die Gesamtsituation?"'
            ],
            'negativity_bias': [
                'Liste bewusst positive Aspekte der Situation auf.',
                'Gewichte positive und negative Informationen bewusst gleich.',
                'Frage dich: "Was läuft gut in dieser Situation?"'
            ],
            'optimism_bias': [
                'Plane für das schlechteste Szenario.',
                'Hole dir Feedback von anderen zu deinen Plänen.',
                'Betrachte, was in der Vergangenheit schiefgelaufen ist.'
            ],
            'planning_fallacy': [
                'Verdoppele deine Zeitschätzung als Sicherheitspuffer.',
                'Zerlege große Aufgaben in kleinere, messbare Schritte.',
                'Dokumentiere, wie lange ähnliche Aufgaben tatsächlich gedauert haben.'
            ]
        }
        
        self.general_questions = [
            'Welche Annahmen machst du, die du hinterfragen könntest?',
            'Welche alternativen Perspektiven gibt es zu dieser Situation?',
            'Was würde jemand mit einer anderen Meinung dazu sagen?',
            'Welche Informationen könnten noch wichtig sein?',
            'Wie würdest du die Situation in einem Jahr bewerten?'
        ]
    
    def generate_suggestions(self, detected_biases: List[Dict], text: str) -> Dict:
        """
        Generiert Verbesserungsvorschläge basierend auf erkannten Biases.
        
        Args:
            detected_biases: Liste erkannter kognitiver Verzerrungen
            text: Originaltext für Kontext
            
        Returns:
            Dictionary mit Alternativen und Fragen
        """
        alternatives = []
        questions = []
        
        # Spezifische Vorschläge für erkannte Biases
        for bias in detected_biases[:3]:  # Top 3 Biases
            bias_type = bias['bias_type']
            if bias_type in self.suggestion_templates:
                alternatives.extend(self.suggestion_templates[bias_type][:2])
        
        # Allgemeine Reflexionsfragen
        questions.extend(self.general_questions[:3])
        
        # Kontext-spezifische Vorschläge
        if 'entscheidung' in text.lower():
            questions.append('Welche Kriterien sind für diese Entscheidung wirklich wichtig?')
            alternatives.append('Erstelle eine Pro-und-Contra-Liste mit gewichteten Faktoren.')
        
        if 'problem' in text.lower():
            questions.append('Ist das wirklich das Kernproblem oder nur ein Symptom?')
            alternatives.append('Nutze die 5-Why-Methode, um zur Ursache zu gelangen.')
        
        if 'ziel' in text.lower() or 'plan' in text.lower():
            questions.append('Welche Hindernisse könntest du übersehen haben?')
            alternatives.append('Entwickle einen Plan B für den Fall, dass etwas schiefgeht.')
        
        return {
            'alternatives': list(set(alternatives)),  # Entferne Duplikate
            'questions': list(set(questions)),
            'meta_suggestions': self._generate_meta_suggestions(detected_biases)
        }
    
    def _generate_meta_suggestions(self, detected_biases: List[Dict]) -> List[str]:
        """Generiert Meta-Vorschläge basierend auf der Bias-Analyse."""
        meta_suggestions = []
        
        if len(detected_biases) > 3:
            meta_suggestions.append(
                'Du zeigst mehrere kognitive Verzerrungen - nimm dir bewusst Zeit für die Reflexion.'
            )
        
        high_confidence_biases = [b for b in detected_biases if b['confidence'] > 0.7]
        if high_confidence_biases:
            meta_suggestions.append(
                f'Besonders ausgeprägt: {high_confidence_biases[0]["bias_type"]} - '
                'achte in Zukunft besonders darauf.'
            )
        
        if not detected_biases:
            meta_suggestions.append(
                'Keine starken kognitiven Verzerrungen erkannt - '
                'trotzdem lohnt sich eine kritische Selbstreflexion.'
            )
        
        return meta_suggestions


# Flask Route Handlers
@cognitive_insights_bp.route('/api/cognitive/biases', methods=['POST'])
def analyze_biases():
    """
    Analysiert Text auf kognitive Verzerrungen.
    
    Expected JSON Input:
    {
        "text": "Zu analysierender Text"
    }
    
    Returns:
        JSON mit gefundenen Biases und deren Positionen
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Kein Text für Analyse bereitgestellt',
                'status': 'error'
            }), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({
                'error': 'Leerer Text kann nicht analysiert werden',
                'status': 'error'
            }), 400
        
        # Bias-Detektion durchführen
        detector = CognitiveBiasDetector()
        detected_biases = detector.detect_biases(text)
        
        # Statistiken berechnen
        total_biases = len(detected_biases)
        high_confidence_biases = len([b for b in detected_biases if b['confidence'] > 0.6])
        
        response = {
            'status': 'success',
            'analysis_timestamp': datetime.now().isoformat(),
            'text_length': len(text),
            'statistics': {
                'total_biases_detected': total_biases,
                'high_confidence_biases': high_confidence_biases,
                'bias_density': total_biases / max(len(text.split()), 1)
            },
            'detected_biases': detected_biases
        }
        
        logger.info(f"Bias-Analyse abgeschlossen: {total_biases} Biases erkannt")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Fehler bei Bias-Analyse: {e}")
        return jsonify({
            'error': f'Analyse fehlgeschlagen: {str(e)}',
            'status': 'error'
        }), 500


@cognitive_insights_bp.route('/api/cognitive/suggestions', methods=['POST'])
def generate_suggestions():
    """
    Generiert Verbesserungsvorschläge basierend auf Text-Analyse.
    
    Expected JSON Input:
    {
        "text": "Originaltext",
        "detected_biases": [] // Optional: bereits erkannte Biases
    }
    
    Returns:
        JSON mit Alternativen und Fragen
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Kein Text für Vorschläge bereitgestellt',
                'status': 'error'
            }), 400
        
        text = data['text']
        detected_biases = data.get('detected_biases', [])
        
        # Falls keine Biases bereitgestellt, erst Detektion durchführen
        if not detected_biases:
            detector = CognitiveBiasDetector()
            detected_biases = detector.detect_biases(text)
        
        # Vorschläge generieren
        generator = CognitiveSuggestionGenerator()
        suggestions = generator.generate_suggestions(detected_biases, text)
        
        response = {
            'status': 'success',
            'generation_timestamp': datetime.now().isoformat(),
            'based_on_biases': len(detected_biases),
            'suggestions': suggestions
        }
        
        logger.info(f"Vorschläge generiert: {len(suggestions['alternatives'])} Alternativen, {len(suggestions['questions'])} Fragen")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Fehler bei Vorschlagsgenerierung: {e}")
        return jsonify({
            'error': f'Vorschlagsgenerierung fehlgeschlagen: {str(e)}',
            'status': 'error'
        }), 500


@cognitive_insights_bp.route('/api/cognitive/complete-analysis', methods=['POST'])
def complete_analysis():
    """
    Führt eine vollständige kognitive Analyse durch (Biases + Vorschläge).
    
    Expected JSON Input:
    {
        "text": "Zu analysierender Text"
    }
    
    Returns:
        JSON mit vollständiger Analyse und Vorschlägen
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Kein Text für Analyse bereitgestellt',
                'status': 'error'
            }), 400
        
        text = data['text']
        
        # Bias-Detektion
        detector = CognitiveBiasDetector()
        detected_biases = detector.detect_biases(text)
        
        # Vorschlagsgenerierung
        generator = CognitiveSuggestionGenerator()
        suggestions = generator.generate_suggestions(detected_biases, text)
        
        # Kombinierte Response
        response = {
            'status': 'success',
            'analysis_timestamp': datetime.now().isoformat(),
            'text_analysis': {
                'length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len([s for s in text.split('.') if s.strip()])
            },
            'bias_analysis': {
                'total_detected': len(detected_biases),
                'biases': detected_biases
            },
            'suggestions': suggestions,
            'summary': {
                'cognitive_load': 'high' if len(detected_biases) > 3 else 'medium' if detected_biases else 'low',
                'recommended_action': _get_recommended_action(detected_biases),
                'reflection_quality': _assess_reflection_quality(text, detected_biases)
            }
        }
        
        logger.info(f"Vollständige kognitive Analyse abgeschlossen")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Fehler bei vollständiger Analyse: {e}")
        return jsonify({
            'error': f'Analyse fehlgeschlagen: {str(e)}',
            'status': 'error'
        }), 500


@cognitive_insights_bp.route('/api/cognitive/bias-types', methods=['GET'])
def get_bias_types():
    """
    Gibt Informationen über alle erkennbaren Bias-Typen zurück.
    
    Returns:
        JSON mit Bias-Typen und Beschreibungen
    """
    try:
        detector = CognitiveBiasDetector()
        
        bias_info = {}
        for bias_name, bias_data in detector.bias_patterns.items():
            bias_info[bias_name] = {
                'name': bias_name.replace('_', ' ').title(),
                'description': bias_data['description'],
                'keywords_count': len(bias_data['keywords']),
                'patterns_count': len(bias_data['patterns'])
            }
        
        response = {
            'status': 'success',
            'total_bias_types': len(bias_info),
            'bias_types': bias_info
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Bias-Typen: {e}")
        return jsonify({
            'error': f'Abruf fehlgeschlagen: {str(e)}',
            'status': 'error'
        }), 500


# Hilfsfunktionen
def _get_recommended_action(detected_biases: List[Dict]) -> str:
    """Empfiehlt Aktion basierend auf erkannten Biases."""
    if not detected_biases:
        return 'continue_reflection'
    elif len(detected_biases) > 3:
        return 'pause_and_reconsider'
    elif any(b['confidence'] > 0.8 for b in detected_biases):
        return 'critical_review'
    else:
        return 'mindful_proceeding'


def _assess_reflection_quality(text: str, detected_biases: List[Dict]) -> str:
    """Bewertet die Qualität der Reflexion."""
    word_count = len(text.split())
    bias_count = len(detected_biases)
    
    if word_count < 20:
        return 'brief'
    elif bias_count > 4:
        return 'needs_improvement'
    elif bias_count <= 1 and word_count > 50:
        return 'good'
    else:
        return 'moderate'


# Error Handler für Blueprint
@cognitive_insights_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint nicht gefunden',
        'status': 'error'
    }), 404


@cognitive_insights_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Interner Serverfehler',
        'status': 'error'
    }), 500
