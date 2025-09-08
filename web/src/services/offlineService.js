// Offline-first Service für ASI Core
// Fallback-Funktionen wenn kein Backend verfügbar ist

export class OfflineService {
  static isOnline() {
    return navigator.onLine;
  }

  static async fallbackSearch(query, localData = []) {
    console.log("🔍 Offline-Suche aktiviert für:", query);

    if (!localData || localData.length === 0) {
      return {
        results: [],
        query,
        source: "offline",
        message:
          "Keine lokalen Daten verfügbar. Erstelle deine ersten Reflexionen!",
      };
    }

    const searchTerms = query.toLowerCase().split(" ");
    const results = localData.filter((item) => {
      const content = item.content?.toLowerCase() || "";
      const tags = item.tags?.join(" ").toLowerCase() || "";

      return searchTerms.some(
        (term) => content.includes(term) || tags.includes(term)
      );
    });

    return {
      results: results.slice(0, 10),
      query,
      source: "offline",
      message:
        results.length > 0
          ? `${results.length} lokale Ergebnisse gefunden`
          : "Keine passenden lokalen Ergebnisse",
    };
  }

  static extractSimpleTags(content) {
    // Einfache Tag-Extraktion für Offline-Modus
    const commonWords = [
      "der",
      "die",
      "das",
      "und",
      "oder",
      "aber",
      "ich",
      "du",
      "er",
      "sie",
      "es",
    ];
    const words = content
      .toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((word) => word.length > 3 && !commonWords.includes(word));

    // Häufigste Wörter als Tags
    const wordCount = {};
    words.forEach((word) => {
      wordCount[word] = (wordCount[word] || 0) + 1;
    });

    return Object.entries(wordCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([word]) => word);
  }

  static generateOfflineInsights(reflections = []) {
    if (reflections.length === 0) {
      return {
        totalReflections: 0,
        patterns: [],
        suggestions: ["Beginne mit deiner ersten Reflexion!"],
        trends: [],
      };
    }

    const totalReflections = reflections.length;
    const recentReflections = reflections.filter(
      (r) =>
        new Date(r.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    ).length;

    const allTags = reflections.flatMap((r) => r.tags || []);
    const tagCounts = {};
    allTags.forEach((tag) => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });

    const topTags = Object.entries(tagCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([tag, count]) => ({ tag, count }));

    return {
      totalReflections,
      recentReflections,
      patterns: [
        `Du hast ${totalReflections} Reflexionen gesammelt`,
        `${recentReflections} davon in den letzten 7 Tagen`,
      ],
      suggestions: [
        "Exportiere deine Daten regelmäßig",
        "Nutze vielfältige Tags für bessere Organisation",
        "Reflektiere regelmäßig über deine Erkenntnisse",
      ],
      topTags,
      trends:
        topTags.length > 0
          ? [`Häufigstes Thema: ${topTags[0].tag}`]
          : ["Erstelle Tags um Trends zu erkennen"],
    };
  }
}

export default OfflineService;
