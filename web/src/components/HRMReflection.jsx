import React, { useState, useEffect } from 'react';
import './HRMReflection.css';

const HRMReflection = () => {
  const [reflection, setReflection] = useState('');
  const [tags, setTags] = useState('');
  const [privacyLevel, setPrivacyLevel] = useState('private');
  const [isProcessing, setIsProcessing] = useState(false);
  const [hrmInsights, setHrmInsights] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!reflection.trim()) {
      setError('Bitte gib deine Reflexion ein.');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setHrmInsights(null);

    try {
      const tagsArray = tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
      
      const response = await fetch('/api/reflection/hrm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: reflection,
          tags: tagsArray,
          privacy_level: privacyLevel,
          timestamp: new Date().toISOString(),
          hrm_enabled: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setHrmInsights(result);
      
      // Scroll to insights
      setTimeout(() => {
        const insightsElement = document.getElementById('hrm-insights');
        if (insightsElement) {
          insightsElement.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);

    } catch (error) {
      console.error('HRM-Analyse Fehler:', error);
      setError(`Fehler bei der HRM-Analyse: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'Sehr hoch';
    if (confidence >= 0.6) return 'Hoch';
    if (confidence >= 0.4) return 'Mittel';
    if (confidence >= 0.2) return 'Niedrig';
    return 'Sehr niedrig';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#27ae60';
    if (confidence >= 0.6) return '#2ecc71';
    if (confidence >= 0.4) return '#f39c12';
    if (confidence >= 0.2) return '#e67e22';
    return '#e74c3c';
  };

  return (
    <div className="hrm-reflection-container">
      <div className="hero-section">
        <div className="container">
          <h1 className="hero-title">
            <span className="brain-icon">🧠</span>
            HRM-Erweiterte Reflexion
          </h1>
          <p className="hero-subtitle">
            Hierarchical Reasoning Model für intelligente Selbstreflexion
          </p>
        </div>
      </div>

      <div className="container main-content">
        <div className="reflection-card">
          <div className="card-header">
            <h2>Deine Reflexion</h2>
            <p>Teile deine Gedanken und erhalte intelligente Einsichten</p>
          </div>

          <form onSubmit={handleSubmit} className="reflection-form">
            <div className="form-group">
              <label htmlFor="reflection-content" className="form-label">
                <i className="fas fa-pen-fancy"></i> Deine Reflexion
              </label>
              <textarea
                id="reflection-content"
                value={reflection}
                onChange={(e) => setReflection(e.target.value)}
                placeholder="Teile deine Gedanken, Gefühle und Erfahrungen...

Beispiele:
• Wie war dein Tag? Was ist dir wichtig gewesen?
• Welche Herausforderungen hattest du?
• Was hast du gelernt oder erkannt?
• Wie fühlst du dich gerade?"
                rows="6"
                className="form-control reflection-textarea"
                disabled={isProcessing}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="reflection-tags" className="form-label">
                  <i className="fas fa-tags"></i> Tags (optional)
                </label>
                <input
                  type="text"
                  id="reflection-tags"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="arbeit, gesundheit, beziehungen, lernen..."
                  className="form-control"
                  disabled={isProcessing}
                />
                <small className="form-hint">Durch Kommas getrennt</small>
              </div>

              <div className="form-group">
                <label htmlFor="privacy-level" className="form-label">
                  <i className="fas fa-shield-alt"></i> Privacy Level
                </label>
                <select
                  id="privacy-level"
                  value={privacyLevel}
                  onChange={(e) => setPrivacyLevel(e.target.value)}
                  className="form-control"
                  disabled={isProcessing}
                >
                  <option value="private">🔒 Privat (nur lokal)</option>
                  <option value="anonymous">👤 Anonym (anonymisiert)</option>
                  <option value="public">🌐 Öffentlich</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={isProcessing || !reflection.trim()}
              className={`submit-button ${isProcessing ? 'processing' : ''}`}
            >
              {isProcessing ? (
                <>
                  <div className="spinner"></div>
                  HRM analysiert...
                </>
              ) : (
                <>
                  <i className="fas fa-brain"></i>
                  Mit HRM analysieren
                </>
              )}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}
        </div>

        {isProcessing && (
          <div className="processing-card">
            <div className="processing-content">
              <div className="processing-spinner"></div>
              <h3>🧠 HRM analysiert deine Reflexion...</h3>
              <p>High-Level Mustererkennung und Low-Level Aktionsplanung</p>
              <div className="processing-steps">
                <div className="step active">Mustererkennung</div>
                <div className="step active">Abstrakte Planung</div>
                <div className="step active">Konkrete Aktionen</div>
                <div className="step">Empfehlungen generieren</div>
              </div>
            </div>
          </div>
        )}

        {hrmInsights && hrmInsights.structured_data?.hrm && (
          <div id="hrm-insights" className="insights-section">
            <h2 className="insights-title">
              <i className="fas fa-lightbulb"></i>
              HRM-Insights
              <span className="insights-subtitle">Intelligente Analyse deiner Reflexion</span>
            </h2>

            <HRMInsightsDisplay insights={hrmInsights.structured_data.hrm} />
          </div>
        )}
      </div>
    </div>
  );
};

const HRMInsightsDisplay = ({ insights }) => {
  const confidence = insights.confidence || 0.5;
  const abstractPlan = insights.abstract_plan || {};
  const concreteAction = insights.concrete_action || {};
  const recommendations = insights.recommendations || [];

  return (
    <div className="insights-grid">
      {/* Confidence Score */}
      <div className="insight-card confidence-card">
        <div className="card-header">
          <h3><i className="fas fa-chart-line"></i> Analyse-Konfidenz</h3>
        </div>
        <div className="card-content">
          <div className="confidence-display">
            <div className="confidence-circle" style={{
              background: `conic-gradient(${getConfidenceColor(confidence)} ${confidence * 360}deg, #e0e0e0 0deg)`
            }}>
              <div className="confidence-value">
                {Math.round(confidence * 100)}%
              </div>
            </div>
            <div className="confidence-label">
              {getConfidenceLabel(confidence)}
            </div>
          </div>
        </div>
      </div>

      {/* Abstract Plan */}
      <div className="insight-card abstract-plan-card">
        <div className="card-header">
          <h3><i className="fas fa-sitemap"></i> Abstrakte Planung</h3>
        </div>
        <div className="card-content">
          {abstractPlan.patterns && abstractPlan.patterns.length > 0 && (
            <div className="patterns-section">
              <h4>Erkannte Muster:</h4>
              <div className="patterns-container">
                {abstractPlan.patterns.slice(0, 5).map((pattern, index) => (
                  <span key={index} className="pattern-badge">
                    {pattern.type}: {pattern.tag || pattern.theme || 'Unbekannt'}
                  </span>
                ))}
              </div>
            </div>
          )}

          {abstractPlan.suggested_goals && abstractPlan.suggested_goals.length > 0 && (
            <div className="goals-section">
              <h4><i className="fas fa-bullseye"></i> Empfohlene Ziele:</h4>
              <ul className="goals-list">
                {abstractPlan.suggested_goals.map((goal, index) => (
                  <li key={index}>{goal}</li>
                ))}
              </ul>
            </div>
          )}

          {abstractPlan.long_term_insights && abstractPlan.long_term_insights.length > 0 && (
            <div className="insights-section">
              <h4><i className="fas fa-telescope"></i> Langzeit-Einsichten:</h4>
              <ul className="insights-list">
                {abstractPlan.long_term_insights.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Concrete Action */}
      {concreteAction && Object.keys(concreteAction).length > 0 && (
        <div className="insight-card concrete-action-card">
          <div className="card-header">
            <h3><i className="fas fa-play-circle"></i> Konkrete Aktion</h3>
          </div>
          <div className="card-content">
            <div className="action-header">
              <h4>
                <i className="fas fa-cog"></i>
                {concreteAction.type || 'Allgemein'}
                <span className="priority-badge priority-{concreteAction.priority || 'medium'}">
                  {concreteAction.priority || 'Medium'} Priorität
                </span>
              </h4>
            </div>

            {concreteAction.suggestion && (
              <div className="action-suggestion">
                <p>{concreteAction.suggestion}</p>
              </div>
            )}

            {concreteAction.implementation && concreteAction.implementation.length > 0 && (
              <div className="implementation-steps">
                <h5><i className="fas fa-list-ol"></i> Umsetzungsschritte:</h5>
                <ol>
                  {concreteAction.implementation.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Strategic Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="insight-card recommendations-card">
          <div className="card-header">
            <h3><i className="fas fa-chess"></i> Strategische Empfehlungen</h3>
          </div>
          <div className="card-content">
            <div className="recommendations-list">
              {recommendations.map((rec, index) => (
                <div key={index} className="recommendation-item">
                  <div className="recommendation-content">
                    {rec}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="insight-card actions-card">
        <div className="card-header">
          <h3><i className="fas fa-rocket"></i> Nächste Schritte</h3>
        </div>
        <div className="card-content">
          <div className="action-buttons">
            <button className="action-button implement" onClick={() => {
              alert('🚀 Aktion zur Umsetzung markiert! In einem vollständigen System würde dies in deinen Kalender oder Task-Manager integriert.');
            }}>
              <i className="fas fa-rocket"></i>
              Aktion umsetzen
            </button>
            <button className="action-button save" onClick={() => {
              alert('💾 Insights gespeichert! In einem vollständigen System würde dies in deiner persönlichen Wissensdatenbank gespeichert.');
            }}>
              <i className="fas fa-save"></i>
              Insights speichern
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions (move these outside component if used elsewhere)
const getConfidenceLabel = (confidence) => {
  if (confidence >= 0.8) return 'Sehr hoch';
  if (confidence >= 0.6) return 'Hoch';
  if (confidence >= 0.4) return 'Mittel';
  if (confidence >= 0.2) return 'Niedrig';
  return 'Sehr niedrig';
};

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#27ae60';
  if (confidence >= 0.6) return '#2ecc71';
  if (confidence >= 0.4) return '#f39c12';
  if (confidence >= 0.2) return '#e67e22';
  return '#e74c3c';
};

export default HRMReflection;
