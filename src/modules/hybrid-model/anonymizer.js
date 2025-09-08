class Anonymizer {
  constructor() {
    this.piiPatterns = [
      // Names (common German first names)
      /\b(Michael|Andreas|Thomas|Stefan|Markus|Christian|Matthias|Alexander|Daniel|Martin|Peter|Klaus|Wolfgang|Jürgen|Günther|Frank|Bernd|Rainer|Hans|Uwe|Dieter|Anna|Maria|Elisabeth|Ursula|Monika|Christa|Ingrid|Helga|Renate|Gisela|Barbara|Brigitte|Andrea|Sabine|Petra|Gabriele|Claudia|Angelika|Susanne|Birgit|Karin|Julia|Sandra|Nicole|Stefanie|Christina|Katrin|Silke|Martina|Jennifer|Lisa|Nina|Melanie|Sarah|Laura|Katharina)\b/gi,

      // Email addresses
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,

      // Phone numbers (German format)
      /\b(?:\+49|0049|0)\s?(?:\(0\)|)\s?[1-9]\d{1,4}\s?\d{1,8}\b/g,

      // Dates (various formats)
      /\b(\d{1,2})[.\/\-](\d{1,2})[.\/\-](\d{2,4})\b/g,
      /\b(\d{2,4})[.\/\-](\d{1,2})[.\/\-](\d{1,2})\b/g,

      // German cities (major ones)
      /\b(Berlin|Hamburg|München|Köln|Frankfurt|Stuttgart|Düsseldorf|Dortmund|Essen|Leipzig|Bremen|Dresden|Hannover|Nürnberg|Duisburg|Bochum|Wuppertal|Bielefeld|Bonn|Münster|Karlsruhe|Mannheim|Augsburg|Wiesbaden|Gelsenkirchen|Mönchengladbach|Braunschweig|Chemnitz|Kiel|Aachen|Halle|Magdeburg|Freiburg|Krefeld|Lübeck|Oberhausen|Erfurt|Mainz|Rostock|Kassel|Hagen|Hamm|Saarbrücken|Mülheim|Potsdam|Ludwigshafen|Oldenburg|Leverkusen|Osnabrück|Solingen|Heidelberg|Herne|Neuss|Darmstadt|Paderborn|Regensburg|Ingolstadt|Würzburg|Fürth|Wolfsburg|Offenbach|Ulm|Heilbronn|Pforzheim|Göttingen|Bottrop|Trier|Recklinghausen|Reutlingen|Bremerhaven|Koblenz|Bergisch|Gladbach|Jena|Remscheid|Erlangen|Moers|Siegen|Hildesheim|Salzgitter)\b/gi,

      // Street addresses
      /\b\w+(?:straße|str\.|strasse|weg|platz|ring|allee|damm|chaussee|gasse)\s*\d+[a-z]?\b/gi,

      // Postal codes (German)
      /\b\d{5}\b/g,

      // Common personal identifiers
      /\bmein\w*\s+(name|partner|freund|freundin|mann|frau|kind|sohn|tochter|mutter|vater|oma|opa|chef|kollege|kollegin|arzt|ärztin|therapeut|therapeutin)\b/gi,

      // Work-related identifiers
      /\b(firma|unternehmen|arbeitgeber|company|ag|gmbh|kg|ohg)\s+\w+/gi,
    ];

    this.replacements = {
      names: "[NAME]",
      email: "[EMAIL]",
      phone: "[PHONE]",
      date: "[DATE]",
      city: "[CITY]",
      address: "[ADDRESS]",
      postal: "[PLZ]",
      personal: "[PERSON]",
      company: "[COMPANY]",
    };

    this.sentimentMap = {
      "sehr schlecht": -2,
      schlecht: -1,
      terrible: -2,
      bad: -1,
      stressed: -1,
      traurig: -1,
      wütend: -2,
      frustriert: -1,
      enttäuscht: -1,
      neutral: 0,
      okay: 0,
      normal: 0,
      gut: 1,
      good: 1,
      calm: 1,
      zufrieden: 1,
      entspannt: 1,
      "sehr gut": 2,
      great: 2,
      excellent: 2,
      fantastisch: 2,
      begeistert: 2,
    };
  }

  anonymizeText(text) {
    if (!text) return "";

    let anonymized = text;
    const detectedPII = [];

    // Replace names
    anonymized = anonymized.replace(this.piiPatterns[0], (match) => {
      detectedPII.push({ type: "name", original: match });
      return this.replacements.names;
    });

    // Replace email addresses
    anonymized = anonymized.replace(this.piiPatterns[1], (match) => {
      detectedPII.push({ type: "email", original: match });
      return this.replacements.email;
    });

    // Replace phone numbers
    anonymized = anonymized.replace(this.piiPatterns[2], (match) => {
      detectedPII.push({ type: "phone", original: match });
      return this.replacements.phone;
    });

    // Replace dates
    anonymized = anonymized.replace(this.piiPatterns[3], (match) => {
      detectedPII.push({ type: "date", original: match });
      return this.replacements.date;
    });

    anonymized = anonymized.replace(this.piiPatterns[4], (match) => {
      detectedPII.push({ type: "date", original: match });
      return this.replacements.date;
    });

    // Replace cities
    anonymized = anonymized.replace(this.piiPatterns[5], (match) => {
      detectedPII.push({ type: "city", original: match });
      return this.replacements.city;
    });

    // Replace addresses
    anonymized = anonymized.replace(this.piiPatterns[6], (match) => {
      detectedPII.push({ type: "address", original: match });
      return this.replacements.address;
    });

    // Replace postal codes
    anonymized = anonymized.replace(this.piiPatterns[7], (match) => {
      detectedPII.push({ type: "postal", original: match });
      return this.replacements.postal;
    });

    // Replace personal identifiers
    anonymized = anonymized.replace(this.piiPatterns[8], (match) => {
      detectedPII.push({ type: "personal", original: match });
      return this.replacements.personal;
    });

    // Replace company names
    anonymized = anonymized.replace(this.piiPatterns[9], (match) => {
      detectedPII.push({ type: "company", original: match });
      return this.replacements.company;
    });

    return {
      anonymizedText: anonymized,
      detectedPII: detectedPII,
      originalLength: text.length,
      anonymizedLength: anonymized.length,
    };
  }

  async generateEmbedding(text) {
    // Use a simple local embedding generation (bag of words with TF-IDF like approach)
    const words = text
      .toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((word) => word.length > 2);

    const uniqueWords = [...new Set(words)];
    const embedding = new Array(384).fill(0); // Simulate 384-dimensional embedding

    uniqueWords.forEach((word, index) => {
      const wordFreq = words.filter((w) => w === word).length / words.length;
      const hash = this.simpleHash(word);

      for (let i = 0; i < 384; i++) {
        embedding[i] += Math.sin(hash * (i + 1)) * wordFreq;
      }
    });

    // Normalize
    const magnitude = Math.sqrt(
      embedding.reduce((sum, val) => sum + val * val, 0)
    );
    if (magnitude > 0) {
      for (let i = 0; i < embedding.length; i++) {
        embedding[i] = embedding[i] / magnitude;
      }
    }

    return embedding;
  }

  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  extractTags(text) {
    const tags = [];

    // Explicit hashtags
    const hashtags = text.match(/#\w+/g);
    if (hashtags) {
      tags.push(...hashtags);
    }

    // Common activity keywords
    const activityKeywords = [
      "spazieren",
      "walking",
      "laufen",
      "joggen",
      "sport",
      "training",
      "meditation",
      "meditiert",
      "yoga",
      "entspannung",
      "arbeit",
      "work",
      "meeting",
      "projekt",
      "büro",
      "familie",
      "freunde",
      "partner",
      "kinder",
      "lernen",
      "lesen",
      "studieren",
      "kurs",
      "musik",
      "film",
      "series",
      "hobby",
      "essen",
      "kochen",
      "restaurant",
      "café",
      "reisen",
      "urlaub",
      "ausflug",
      "wandern",
    ];

    const lowerText = text.toLowerCase();
    activityKeywords.forEach((keyword) => {
      if (lowerText.includes(keyword)) {
        tags.push(`#${keyword}`);
      }
    });

    return [...new Set(tags)]; // Remove duplicates
  }

  extractSentiment(text) {
    const lowerText = text.toLowerCase();
    let sentimentScore = 0;
    let sentimentCount = 0;

    Object.entries(this.sentimentMap).forEach(([word, score]) => {
      if (lowerText.includes(word)) {
        sentimentScore += score;
        sentimentCount++;
      }
    });

    if (sentimentCount === 0) {
      // Fallback: simple positive/negative word detection
      const positiveWords = [
        "gut",
        "toll",
        "schön",
        "super",
        "great",
        "good",
        "happy",
        "zufrieden",
        "erfolgreich",
      ];
      const negativeWords = [
        "schlecht",
        "schlimm",
        "terrible",
        "bad",
        "sad",
        "angry",
        "frustrated",
        "müde",
      ];

      positiveWords.forEach((word) => {
        if (lowerText.includes(word)) {
          sentimentScore += 1;
          sentimentCount++;
        }
      });

      negativeWords.forEach((word) => {
        if (lowerText.includes(word)) {
          sentimentScore -= 1;
          sentimentCount++;
        }
      });
    }

    const averageSentiment =
      sentimentCount > 0 ? sentimentScore / sentimentCount : 0;

    let sentimentLabel = "neutral";
    if (averageSentiment > 0.5) sentimentLabel = "positive";
    else if (averageSentiment < -0.5) sentimentLabel = "negative";

    return {
      score: averageSentiment,
      label: sentimentLabel,
      confidence: Math.min(sentimentCount * 0.2, 1.0),
    };
  }

  async processReflection(text, title = "") {
    const fullText = `${title} ${text}`.trim();

    // Anonymize the text
    const anonymizationResult = this.anonymizeText(fullText);

    // Generate embedding from anonymized text
    const embedding = await this.generateEmbedding(
      anonymizationResult.anonymizedText
    );

    // Extract features
    const tags = this.extractTags(fullText); // Use original text for better tag extraction
    const sentiment = this.extractSentiment(fullText);

    const timeOfDay = new Date().getHours();
    let timeOfDayLabel = "night";
    if (timeOfDay >= 6 && timeOfDay < 12) timeOfDayLabel = "morning";
    else if (timeOfDay >= 12 && timeOfDay < 18) timeOfDayLabel = "afternoon";
    else if (timeOfDay >= 18 && timeOfDay < 22) timeOfDayLabel = "evening";

    return {
      // For local storage (full data)
      local: {
        originalText: fullText,
        title: title,
        content: text,
        timestamp: Date.now(),
        piiDetected: anonymizationResult.detectedPII,
      },

      // For decentralized sharing (anonymized)
      decentralized: {
        embedding: embedding,
        tags: tags,
        sentiment: sentiment,
        timeOfDay: timeOfDayLabel,
        textLength: fullText.length,
        hashedContent: this.simpleHash(anonymizationResult.anonymizedText),
        languageDetected: this.detectLanguage(fullText),
        wordCount: fullText.split(/\s+/).length,
        anonymizationMetrics: {
          originalLength: anonymizationResult.originalLength,
          anonymizedLength: anonymizationResult.anonymizedLength,
          piiCount: anonymizationResult.detectedPII.length,
          piiTypes: [
            ...new Set(anonymizationResult.detectedPII.map((p) => p.type)),
          ],
        },
      },
    };
  }

  detectLanguage(text) {
    // Simple German/English detection
    const germanWords = [
      "und",
      "der",
      "die",
      "das",
      "ich",
      "ist",
      "mit",
      "auf",
      "für",
      "von",
      "zu",
      "im",
      "am",
      "haben",
      "sein",
    ];
    const englishWords = [
      "and",
      "the",
      "of",
      "to",
      "in",
      "is",
      "it",
      "you",
      "that",
      "he",
      "was",
      "for",
      "on",
      "are",
      "as",
    ];

    const lowerText = text.toLowerCase();
    let germanCount = 0;
    let englishCount = 0;

    germanWords.forEach((word) => {
      if (
        lowerText.includes(` ${word} `) ||
        lowerText.startsWith(`${word} `) ||
        lowerText.endsWith(` ${word}`)
      ) {
        germanCount++;
      }
    });

    englishWords.forEach((word) => {
      if (
        lowerText.includes(` ${word} `) ||
        lowerText.startsWith(`${word} `) ||
        lowerText.endsWith(` ${word}`)
      ) {
        englishCount++;
      }
    });

    if (germanCount > englishCount) return "de";
    if (englishCount > germanCount) return "en";
    return "unknown";
  }

  validateAnonymization(text) {
    const anonymizationResult = this.anonymizeText(text);

    return {
      isClean: anonymizationResult.detectedPII.length === 0,
      piiFound: anonymizationResult.detectedPII,
      recommendations: this.getAnonymizationRecommendations(
        anonymizationResult.detectedPII
      ),
      riskLevel: this.calculatePrivacyRisk(anonymizationResult.detectedPII),
    };
  }

  getAnonymizationRecommendations(piiList) {
    const recommendations = [];

    if (piiList.some((p) => p.type === "name")) {
      recommendations.push(
        "Verwende Initialen oder allgemeine Begriffe statt Namen."
      );
    }

    if (piiList.some((p) => p.type === "city")) {
      recommendations.push(
        'Verwende "Stadt" oder "Region" statt spezifische Ortsnamen.'
      );
    }

    if (piiList.some((p) => p.type === "date")) {
      recommendations.push(
        'Verwende relative Zeitangaben wie "gestern" oder "letzte Woche".'
      );
    }

    return recommendations;
  }

  calculatePrivacyRisk(piiList) {
    if (piiList.length === 0) return "low";
    if (piiList.length <= 2) return "medium";
    return "high";
  }
}

export default Anonymizer;
