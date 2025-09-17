#!/usr/bin/env python3
"""
ASI Core - State Management Tests
Unit Tests für das State Management System
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import der zu testenden Module
import sys
sys.path.append(str(Path(__file__).parent.parent))

from asi_core.state_management import ASIStateManager


class TestASIStateManager:
    """Test Suite für ASI State Manager."""
    
    @pytest.fixture
    def temp_db_file(self):
        """Erstellt temporäre Datenbankdatei für Tests."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            yield f.name
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def state_manager(self, temp_db_file):
        """Erstellt State Manager Instanz für Tests."""
        return ASIStateManager(db_file=temp_db_file)
    
    def test_create_state_reflection_basic(self, state_manager):
        """Test: Grundlegende State Reflection Erstellung."""
        reflection_data = {
            'content': 'Heute war ein produktiver Tag.',
            'privacy': 'private',
            'timestamp': datetime.now().isoformat()
        }
        
        result = state_manager.create_state_reflection(reflection_data)
        
        assert result is not None
        assert 'state_value' in result
        assert 'reflection_id' in result
        assert 'asi_analysis' in result
        assert 0 <= result['state_value'] <= 255
    
    def test_create_state_reflection_empty_content(self, state_manager):
        """Test: State Reflection mit leerem Content."""
        reflection_data = {
            'content': '',
            'privacy': 'private'
        }
        
        result = state_manager.create_state_reflection(reflection_data)
        
        # Sollte trotzdem funktionieren, aber mit niedrigerem Confidence Score
        assert result is not None
        assert result['asi_analysis']['confidence_score'] < 0.5
    
    def test_create_state_reflection_with_themes(self, state_manager):
        """Test: State Reflection mit expliziten Themes."""
        reflection_data = {
            'content': 'Arbeit war stressig, aber ich habe viel gelernt.',
            'themes': ['work', 'stress', 'learning'],
            'privacy': 'private'
        }
        
        result = state_manager.create_state_reflection(reflection_data)
        
        assert result is not None
        assert 'themes' in result['asi_analysis']
        assert any(theme in result['asi_analysis']['themes'] for theme in ['work', 'stress', 'learning'])
    
    def test_suggest_state_from_text_positive(self, state_manager):
        """Test: State Suggestion für positiven Text."""
        positive_text = "Ich bin so glücklich und dankbar für diesen wunderbaren Tag!"
        
        suggestion = state_manager.suggest_state_from_text(positive_text)
        
        assert suggestion is not None
        assert 'suggested_state' in suggestion
        assert 'confidence' in suggestion
        assert 'reasoning' in suggestion
        # Positive Texte sollten höhere State Values haben
        assert suggestion['suggested_state'] > 128
    
    def test_suggest_state_from_text_negative(self, state_manager):
        """Test: State Suggestion für negativen Text."""
        negative_text = "Ich bin frustriert und müde. Alles geht schief heute."
        
        suggestion = state_manager.suggest_state_from_text(negative_text)
        
        assert suggestion is not None
        # Negative Texte sollten niedrigere State Values haben
        assert suggestion['suggested_state'] < 128
    
    def test_suggest_state_from_text_neutral(self, state_manager):
        """Test: State Suggestion für neutralen Text."""
        neutral_text = "Heute ist ein normaler Tag. Nichts besonderes passiert."
        
        suggestion = state_manager.suggest_state_from_text(neutral_text)
        
        assert suggestion is not None
        # Neutrale Texte sollten mittlere State Values haben
        assert 100 <= suggestion['suggested_state'] <= 155
    
    def test_state_transitions_basic(self, state_manager):
        """Test: Grundlegende State Transitions."""
        # Erstelle mehrere Reflections um Transitions zu testen
        reflections = [
            {'content': 'Guter Start in den Tag!', 'privacy': 'private'},
            {'content': 'Mittag wird stressig.', 'privacy': 'private'},
            {'content': 'Abend ist entspannt.', 'privacy': 'private'}
        ]
        
        results = []
        for reflection in reflections:
            result = state_manager.create_state_reflection(reflection)
            results.append(result)
        
        # Analysiere Transitions
        transitions = state_manager.analyze_state_transitions()
        
        assert transitions is not None
        assert 'transition_count' in transitions
        assert transitions['transition_count'] >= 0
    
    def test_analyze_state_transitions_with_history(self, state_manager):
        """Test: State Transition Analyse mit Historie."""
        # Erstelle mehrere States mit bekannten Patterns
        test_states = [
            {'content': 'Sehr glücklich heute!', 'expected_range': (200, 255)},
            {'content': 'Etwas müde aber okay.', 'expected_range': (100, 150)},
            {'content': 'Frustriert mit der Arbeit.', 'expected_range': (50, 100)},
            {'content': 'Wieder bessere Laune!', 'expected_range': (150, 200)}
        ]
        
        created_states = []
        for state_data in test_states:
            result = state_manager.create_state_reflection({
                'content': state_data['content'],
                'privacy': 'private'
            })
            created_states.append(result)
        
        # Analysiere Transitions
        transitions = state_manager.analyze_state_transitions()
        
        assert 'patterns' in transitions
        assert 'volatility' in transitions
        assert 'trend' in transitions
    
    def test_export_state_data_basic(self, state_manager):
        """Test: Grundlegender State Data Export."""
        # Erstelle einige Test-Reflections
        for i in range(3):
            state_manager.create_state_reflection({
                'content': f'Test reflection {i}',
                'privacy': 'private'
            })
        
        # Exportiere State Data
        exported_data = state_manager.export_state_data()
        
        assert exported_data is not None
        assert 'reflections' in exported_data
        assert 'statistics' in exported_data
        assert 'export_metadata' in exported_data
        assert len(exported_data['reflections']) >= 3
    
    def test_export_state_data_empty_database(self, state_manager):
        """Test: Export mit leerer Datenbank."""
        exported_data = state_manager.export_state_data()
        
        assert exported_data is not None
        assert exported_data['reflections'] == []
        assert exported_data['statistics']['total_reflections'] == 0
    
    def test_export_state_data_with_filters(self, state_manager):
        """Test: Export mit Filtern."""
        # Erstelle Test-Reflections mit verschiedenen Timestamps
        reflections = []
        for i in range(5):
            result = state_manager.create_state_reflection({
                'content': f'Filtered reflection {i}',
                'privacy': 'private'
            })
            reflections.append(result)
        
        # Export mit Limit
        exported_data = state_manager.export_state_data(limit=3)
        
        assert len(exported_data['reflections']) <= 3
    
    def test_state_value_consistency(self, state_manager):
        """Test: Konsistenz der State Values."""
        same_content = "Ich fühle mich heute sehr gut und produktiv."
        
        # Erstelle mehrmals dieselbe Reflection
        results = []
        for _ in range(3):
            result = state_manager.create_state_reflection({
                'content': same_content,
                'privacy': 'private'
            })
            results.append(result['state_value'])
        
        # State Values sollten ähnlich sein (deterministisches System)
        assert all(abs(results[0] - result) <= 10 for result in results[1:])
    
    def test_state_distribution_coverage(self, state_manager):
        """Test: State Distribution deckt verschiedene Bereiche ab."""
        test_texts = [
            "Extrem glücklich und euphoric!",  # Sehr hoch
            "Ziemlich gut heute.",             # Hoch
            "Ganz okay, nichts besonderes.",   # Mittel
            "Etwas müde und gestresst.",       # Niedrig
            "Sehr deprimiert und hoffnungslos." # Sehr niedrig
        ]
        
        state_values = []
        for text in test_texts:
            result = state_manager.create_state_reflection({
                'content': text,
                'privacy': 'private'
            })
            state_values.append(result['state_value'])
        
        # Sollte verschiedene State-Bereiche abdecken
        assert max(state_values) - min(state_values) > 50
    
    def test_error_handling_invalid_input(self, state_manager):
        """Test: Error Handling für ungültige Inputs."""
        # None Input
        result = state_manager.create_state_reflection(None)
        assert result is None or 'error' in result
        
        # Invalid Type
        result = state_manager.create_state_reflection("not a dict")
        assert result is None or 'error' in result
    
    def test_thread_safety_basic(self, state_manager):
        """Test: Grundlegende Thread Safety."""
        import threading
        
        results = []
        errors = []
        
        def create_reflection(index):
            try:
                result = state_manager.create_state_reflection({
                    'content': f'Thread reflection {index}',
                    'privacy': 'private'
                })
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Starte mehrere Threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_reflection, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Warte auf alle Threads
        for thread in threads:
            thread.join()
        
        # Alle sollten erfolgreich sein
        assert len(errors) == 0
        assert len(results) == 5
    
    @patch('asi_core.state_management.sqlite3')
    def test_database_connection_error(self, mock_sqlite, temp_db_file):
        """Test: Handling von Datenbankverbindungsfehlern."""
        mock_sqlite.connect.side_effect = Exception("Database connection failed")
        
        state_manager = ASIStateManager(db_file=temp_db_file)
        result = state_manager.create_state_reflection({
            'content': 'Test with DB error',
            'privacy': 'private'
        })
        
        # Sollte graceful handling haben
        assert result is None or 'error' in result


class TestStateAnalysis:
    """Test Suite für State Analysis Funktionen."""
    
    @pytest.fixture
    def state_manager(self):
        """State Manager mit temporärer Datenbank."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_file = f.name
        
        manager = ASIStateManager(db_file=db_file)
        yield manager
        
        Path(db_file).unlink(missing_ok=True)
    
    def test_sentiment_analysis_positive(self, state_manager):
        """Test: Sentiment Analysis für positive Texte."""
        positive_texts = [
            "Ich bin so glücklich!",
            "Fantastischer Tag heute!",
            "Alles läuft perfekt!"
        ]
        
        for text in positive_texts:
            suggestion = state_manager.suggest_state_from_text(text)
            assert suggestion['suggested_state'] > 128  # Über Mitte
    
    def test_sentiment_analysis_negative(self, state_manager):
        """Test: Sentiment Analysis für negative Texte."""
        negative_texts = [
            "Ich bin sehr traurig.",
            "Alles geht schief heute.",
            "Frustriert und müde."
        ]
        
        for text in negative_texts:
            suggestion = state_manager.suggest_state_from_text(text)
            assert suggestion['suggested_state'] < 128  # Unter Mitte
    
    def test_theme_extraction(self, state_manager):
        """Test: Theme Extraction aus Text."""
        text_with_themes = "Heute war die Arbeit stressig, aber ich habe viel über Teamwork gelernt."
        
        result = state_manager.create_state_reflection({
            'content': text_with_themes,
            'privacy': 'private'
        })
        
        themes = result['asi_analysis']['themes']
        assert any('work' in theme.lower() for theme in themes)


class TestStateValidation:
    """Test Suite für State Validation."""
    
    def test_state_value_range(self):
        """Test: State Values sind im gültigen Bereich."""
        from asi_core.state_management import ASIStateManager
        
        # Test verschiedene Texte
        test_cases = [
            "Extrem positiv und glücklich!",
            "Neutral und ausgeglichen.",
            "Sehr negativ und traurig."
        ]
        
        for text in test_cases:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                manager = ASIStateManager(db_file=f.name)
                suggestion = manager.suggest_state_from_text(text)
                
                # State Value muss im gültigen Bereich sein
                assert 0 <= suggestion['suggested_state'] <= 255
                
                Path(f.name).unlink(missing_ok=True)
    
    def test_confidence_score_range(self):
        """Test: Confidence Scores sind im gültigen Bereich."""
        from asi_core.state_management import ASIStateManager
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            manager = ASIStateManager(db_file=f.name)
            
            result = manager.create_state_reflection({
                'content': 'Test für Confidence Score',
                'privacy': 'private'
            })
            
            confidence = result['asi_analysis']['confidence_score']
            assert 0.0 <= confidence <= 1.0
            
            Path(f.name).unlink(missing_ok=True)


# Integration Tests
class TestStateIntegration:
    """Integration Tests für State Management."""
    
    def test_full_workflow(self):
        """Test: Vollständiger State Management Workflow."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_file = f.name
        
        try:
            manager = ASIStateManager(db_file=db_file)
            
            # 1. Erstelle Reflection
            reflection_data = {
                'content': 'Integration Test Reflection',
                'privacy': 'private',
                'themes': ['test', 'integration']
            }
            
            result = manager.create_state_reflection(reflection_data)
            assert result is not None
            
            # 2. Analysiere State Transitions
            transitions = manager.analyze_state_transitions()
            assert transitions is not None
            
            # 3. Exportiere Daten
            exported = manager.export_state_data()
            assert len(exported['reflections']) >= 1
            
            # 4. Suggest State
            suggestion = manager.suggest_state_from_text("Neuer Test Text")
            assert suggestion is not None
            
        finally:
            Path(db_file).unlink(missing_ok=True)


# Performance Tests
class TestStatePerformance:
    """Performance Tests für State Management."""
    
    def test_bulk_creation_performance(self):
        """Test: Performance bei Bulk Creation."""
        import time
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_file = f.name
        
        try:
            manager = ASIStateManager(db_file=db_file)
            
            start_time = time.time()
            
            # Erstelle 50 Reflections
            for i in range(50):
                manager.create_state_reflection({
                    'content': f'Performance test reflection {i}',
                    'privacy': 'private'
                })
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Sollte unter 10 Sekunden sein
            assert elapsed < 10.0
            print(f"Bulk creation took {elapsed:.2f} seconds for 50 reflections")
            
        finally:
            Path(db_file).unlink(missing_ok=True)


if __name__ == '__main__':
    # Führe Tests aus wenn direkt ausgeführt
    pytest.main([__file__, '-v'])
