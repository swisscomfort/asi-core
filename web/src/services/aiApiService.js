// API Service für ASI Core KI-Funktionen

const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://your-api-domain.com"
    : "http://localhost:8000";

class AIApiService {
  // Semantische Suche
  static async semanticSearch(query, options = {}) {
    console.log(`🔍 Semantische Suche gestartet: "${query}"`, {
      url: `${API_BASE_URL}/api/search`,
      options,
    });

    try {
      // Backend erwartet GET mit Query-Parametern
      const url = new URL(`${API_BASE_URL}/api/search`);
      url.searchParams.append("q", query);
      url.searchParams.append("limit", options.limit || 20);

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      console.log(`📡 API Response Status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error: ${response.status}`, errorText);
        throw new Error(`Search failed: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log(`✅ Suchergebnisse erhalten:`, result);
      return result;
    } catch (error) {
      console.error("❌ Semantic search error:", error);
      if (error.name === "TypeError" && error.message.includes("fetch")) {
        console.error(`🚨 Backend nicht erreichbar unter: ${API_BASE_URL}`);
      }
      throw error;
    }
  }

  // Inhaltanalyse für neue Reflexionen
  static async analyzeContent(content) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/analyze-content`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        throw new Error(`Content analysis failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Content analysis error:", error);
      // Fallback für lokale Analyse
      return {
        suggested_tags: this.extractLocalTags(content),
        suggestions: [],
      };
    }
  }

  // Mustererkennung
  static async recognizePatterns(reflection) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/patterns`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: reflection.content,
          tags: reflection.tags,
          timestamp: reflection.timestamp,
        }),
      });

      if (!response.ok) {
        throw new Error(`Pattern recognition failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Pattern recognition error:", error);
      return { patterns: [] };
    }
  }

  // KI-Insights generieren
  static async generateInsights(reflection) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai/insights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ reflection }),
      });

      if (!response.ok) {
        throw new Error(`Insights generation failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Insights generation error:", error);
      // Fallback für lokale Analyse
      return this.generateLocalInsights(reflection);
    }
  }

  // Lokale Fallback-Funktionen
  static extractLocalTags(content) {
    const words = content.toLowerCase().match(/\b\w{4,}\b/g) || [];
    const germanStopWords = [
      "dass",
      "sich",
      "wird",
      "sind",
      "nach",
      "wird",
      "seine",
      "seine",
    ];

    const filteredWords = words.filter(
      (word) => !germanStopWords.includes(word) && word.length > 3
    );

    const uniqueWords = [...new Set(filteredWords)];
    return uniqueWords.slice(0, 5);
  }

  static generateLocalInsights(reflection) {
    const content = reflection.content.toLowerCase();

    // Einfache Sentiment-Analyse
    const positiveWords = [
      "glücklich",
      "froh",
      "gut",
      "toll",
      "super",
      "liebe",
      "schön",
    ];
    const negativeWords = [
      "traurig",
      "schlecht",
      "müde",
      "stress",
      "angst",
      "problem",
    ];

    const positiveCount = positiveWords.reduce(
      (count, word) => count + (content.includes(word) ? 1 : 0),
      0
    );
    const negativeCount = negativeWords.reduce(
      (count, word) => count + (content.includes(word) ? 1 : 0),
      0
    );

    let sentiment = "neutral";
    let confidence = 0.5;

    if (positiveCount > negativeCount) {
      sentiment = "positive";
      confidence = Math.min(0.9, 0.6 + positiveCount * 0.1);
    } else if (negativeCount > positiveCount) {
      sentiment = "negative";
      confidence = Math.min(0.9, 0.6 + negativeCount * 0.1);
    }

    // Einfache Themen-Erkennung
    const themes = [];
    if (
      content.includes("arbeit") ||
      content.includes("job") ||
      content.includes("beruf")
    ) {
      themes.push("Beruf");
    }
    if (
      content.includes("familie") ||
      content.includes("eltern") ||
      content.includes("kind")
    ) {
      themes.push("Familie");
    }
    if (content.includes("freund") || content.includes("beziehung")) {
      themes.push("Beziehungen");
    }
    if (
      content.includes("gesundheit") ||
      content.includes("sport") ||
      content.includes("körper")
    ) {
      themes.push("Gesundheit");
    }

    return {
      sentiment: { label: sentiment, confidence },
      themes,
      recommendations: [
        "Versuche ähnliche Gedanken in der Zukunft zu verfolgen",
        "Reflektiere über die Muster in deinen Gedanken",
      ],
    };
  }

  // Reflexionen laden
  static async loadRecentReflections(limit = 20) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/reflections/recent?limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`Loading reflections failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Loading reflections error:", error);
      // Fallback: Lade aus localStorage
      return this.loadFromLocalStorage();
    }
  }

  // LocalStorage Fallback
  static loadFromLocalStorage() {
    try {
      const stored = localStorage.getItem("asi-reflections");
      if (stored) {
        const reflections = JSON.parse(stored);
        return { reflections: reflections.slice(0, 20) };
      }
    } catch (error) {
      console.error("LocalStorage loading error:", error);
    }
    return { reflections: [] };
  }

  static saveToLocalStorage(reflection) {
    try {
      const stored = localStorage.getItem("asi-reflections");
      const reflections = stored ? JSON.parse(stored) : [];

      // Füge neue Reflexion hinzu
      reflections.unshift({
        ...reflection,
        hash: this.generateHash(reflection.content + reflection.timestamp),
      });

      // Halte nur die letzten 100 Reflexionen
      const trimmed = reflections.slice(0, 100);

      localStorage.setItem("asi-reflections", JSON.stringify(trimmed));
    } catch (error) {
      console.error("LocalStorage saving error:", error);
    }
  }

  static generateHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }
}

export default AIApiService;
