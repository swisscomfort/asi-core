import StateTracker from "./state-tracker.js";
import Anonymizer from "./anonymizer.js";
import ChainInterface from "./chain-interface.js";

class InsightEngine {
  constructor() {
    this.stateTracker = new StateTracker();
    this.anonymizer = new Anonymizer();
    this.chainInterface = new ChainInterface();
    this.isInitialized = false;

    this.insightTemplates = {
      streak: {
        threshold: 3,
        message: (key, days) =>
          `Du hast "${key}" ${days} Tage in Folge praktiziert! Großartig!`,
        type: "achievement",
      },
      mood_improvement: {
        threshold: 0.7,
        message: (key, rate) =>
          `"${key}" verbessert deine Stimmung in ${Math.round(
            rate * 100
          )}% der Fälle.`,
        type: "correlation",
      },
      collective_validation: {
        threshold: 0.75,
        message: (key, rate, users) =>
          `${Math.round(
            rate * 100
          )}% von ${users} Nutzern berichten positive Ergebnisse mit "${key}".`,
        type: "collective",
      },
      recommendation: {
        message: (key, confidence) =>
          `Basierend auf deinen Mustern könnte "${key}" heute hilfreich sein.`,
        type: "suggestion",
      },
      timing_insight: {
        message: (key, time) =>
          `Du praktizierst "${key}" meist am ${time}. Das ist deine produktivste Zeit!`,
        type: "pattern",
      },
    };

    this.commonStates = [
      "walked",
      "meditated",
      "exercised",
      "focused",
      "slept_well",
      "ate_healthy",
      "journaled",
      "called_friend",
      "read_book",
      "listened_music",
      "worked_on_hobby",
      "took_break",
      "organized_space",
      "planned_day",
      "practiced_gratitude",
    ];
  }

  async initialize() {
    try {
      await this.stateTracker.initDB();
      await this.chainInterface.initialize();
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error("Failed to initialize InsightEngine:", error);
      return false;
    }
  }

  async generateProactiveInsights() {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const insights = [];

    // Get local insights
    const localInsights = await this.generateLocalInsights();
    insights.push(...localInsights);

    // Get collective insights (if connected to blockchain)
    try {
      const collectiveInsights = await this.generateCollectiveInsights();
      insights.push(...collectiveInsights);
    } catch (error) {
      console.warn("Could not fetch collective insights:", error.message);
    }

    // Generate contextual insights
    const contextualInsights = await this.generateContextualInsights();
    insights.push(...contextualInsights);

    // Sort by relevance and confidence
    return this.rankInsights(insights);
  }

  async generateLocalInsights() {
    const insights = [];
    const localInsights = await this.stateTracker.getLocalInsights(7);

    // Process local insights through templates
    for (const insight of localInsights) {
      const processedInsight = await this.processLocalInsight(insight);
      if (processedInsight) {
        insights.push(processedInsight);
      }
    }

    // Add missing activity suggestions
    const missingActivityInsights = await this.suggestMissingActivities();
    insights.push(...missingActivityInsights);

    return insights;
  }

  async processLocalInsight(insight) {
    const template = this.insightTemplates[insight.type];
    if (!template) return null;

    const processedInsight = {
      id: `local_${insight.type}_${insight.state_key}_${Date.now()}`,
      type: template.type,
      message: insight.message,
      confidence: insight.confidence,
      stateKey: insight.state_key,
      source: "local",
      priority: this.calculatePriority(insight),
      actionable: true,
      timestamp: Date.now(),
    };

    // Add specific actions based on insight type
    switch (insight.type) {
      case "streak":
        processedInsight.actions = [
          { type: "continue", label: `${insight.state_key} heute fortsetzen` },
          { type: "share", label: "Erfolg teilen (anonym)" },
        ];
        break;

      case "mood_improvement":
        processedInsight.actions = [
          { type: "schedule", label: `${insight.state_key} für heute planen` },
          { type: "reminder", label: "Erinnerung setzen" },
        ];
        break;

      case "time_pattern":
        processedInsight.actions = [
          { type: "optimize", label: "Optimale Zeit nutzen" },
          { type: "calendar", label: "Kalender-Eintrag erstellen" },
        ];
        break;
    }

    return processedInsight;
  }

  async generateCollectiveInsights() {
    const insights = [];

    // Get collective patterns for common states
    for (const stateKey of this.commonStates) {
      try {
        const stats = await this.chainInterface.getGlobalStats(stateKey);

        if (stats.totalEntries > 20) {
          const insight = {
            id: `collective_${stateKey}_${Date.now()}`,
            type: "collective",
            message: this.insightTemplates.collective_validation.message(
              stateKey,
              stats.positiveRate,
              stats.uniqueUsers
            ),
            confidence: Math.min(stats.totalEntries / 100, 0.9),
            stateKey: stateKey,
            source: "collective",
            priority: this.calculateCollectivePriority(stats),
            sampleSize: stats.totalEntries,
            uniqueUsers: stats.uniqueUsers,
            timestamp: Date.now(),
            actions: [
              { type: "try", label: `${stateKey} heute versuchen` },
              {
                type: "learn_more",
                label: "Mehr über diese Aktivität erfahren",
              },
            ],
          };

          insights.push(insight);
        }
      } catch (error) {
        console.warn(`Could not fetch stats for ${stateKey}:`, error.message);
      }
    }

    return insights;
  }

  async generateContextualInsights() {
    const insights = [];
    const now = new Date();
    const hour = now.getHours();
    const dayOfWeek = now.getDay();

    // Time-based insights
    if (hour >= 6 && hour < 9) {
      insights.push({
        id: `contextual_morning_${Date.now()}`,
        type: "contextual",
        message:
          "Guten Morgen! Wie wäre es mit einer kurzen Meditation oder einem Spaziergang?",
        confidence: 0.6,
        source: "contextual",
        priority: "medium",
        timeRelevant: true,
        actions: [
          { type: "quick_meditation", label: "5-Min Meditation" },
          { type: "morning_walk", label: "Kurzer Spaziergang" },
        ],
      });
    }

    if (hour >= 12 && hour < 14) {
      insights.push({
        id: `contextual_lunch_${Date.now()}`,
        type: "contextual",
        message:
          "Mittagszeit! Eine kurze Pause könnte deine Produktivität steigern.",
        confidence: 0.7,
        source: "contextual",
        priority: "medium",
        timeRelevant: true,
        actions: [
          { type: "take_break", label: "Pause machen" },
          { type: "mindful_eating", label: "Bewusst essen" },
        ],
      });
    }

    if (hour >= 18 && hour < 21) {
      insights.push({
        id: `contextual_evening_${Date.now()}`,
        type: "contextual",
        message: "Der Tag geht zu Ende. Zeit für Reflexion oder Entspannung?",
        confidence: 0.8,
        source: "contextual",
        priority: "high",
        timeRelevant: true,
        actions: [
          { type: "reflect", label: "Tag reflektieren" },
          { type: "unwind", label: "Entspannen" },
        ],
      });
    }

    // Day-based insights
    if (dayOfWeek === 1) {
      // Monday
      insights.push({
        id: `contextual_monday_${Date.now()}`,
        type: "contextual",
        message: "Neuer Wochenstart! Setze dir ein kleines, erreichbares Ziel.",
        confidence: 0.6,
        source: "contextual",
        priority: "medium",
        dayRelevant: true,
        actions: [
          { type: "set_goal", label: "Wochenziel setzen" },
          { type: "plan_week", label: "Woche planen" },
        ],
      });
    }

    if (dayOfWeek === 5) {
      // Friday
      insights.push({
        id: `contextual_friday_${Date.now()}`,
        type: "contextual",
        message:
          "Wochenende steht bevor! Was hat diese Woche gut funktioniert?",
        confidence: 0.7,
        source: "contextual",
        priority: "medium",
        dayRelevant: true,
        actions: [
          { type: "weekly_review", label: "Woche reflektieren" },
          { type: "celebrate", label: "Erfolge feiern" },
        ],
      });
    }

    return insights;
  }

  async suggestMissingActivities() {
    const insights = [];
    const recentStates = await this.stateTracker.getAllStatesForDay(
      new Date().toISOString().split("T")[0]
    );

    const todaysActivities = new Set(recentStates.map((s) => s.state_key));

    // Check for missing fundamental activities
    const fundamentalActivities = [
      "walked",
      "meditated",
      "focused",
      "took_break",
    ];

    for (const activity of fundamentalActivities) {
      if (!todaysActivities.has(activity)) {
        // Check historical performance
        const history = await this.stateTracker.getStateHistory(activity, 30);
        if (history.length > 3) {
          // Only suggest if they've done it before
          const avgBenefit =
            history.reduce((sum, entry) => {
              if (entry.mood_before && entry.mood_after) {
                return (
                  sum +
                  (this.getMoodScore(entry.mood_after) -
                    this.getMoodScore(entry.mood_before))
                );
              }
              return sum;
            }, 0) / history.length;

          if (avgBenefit > 0.5) {
            insights.push({
              id: `missing_${activity}_${Date.now()}`,
              type: "suggestion",
              message: `Du hast heute noch nicht "${activity}" praktiziert. Es hat dir bisher meist geholfen.`,
              confidence: Math.min(history.length / 10, 0.8),
              stateKey: activity,
              source: "local_analysis",
              priority: "medium",
              historicalBenefit: avgBenefit,
              actions: [
                { type: "do_now", label: `${activity} jetzt machen` },
                { type: "schedule_later", label: "Für später planen" },
              ],
            });
          }
        }
      }
    }

    return insights;
  }

  getMoodScore(mood) {
    const moodScores = {
      terrible: 1,
      bad: 2,
      stressed: 3,
      neutral: 4,
      okay: 5,
      good: 6,
      calm: 7,
      great: 8,
      excellent: 9,
    };
    return moodScores[mood] || 4;
  }

  calculatePriority(insight) {
    if (insight.confidence > 0.8) return "high";
    if (insight.confidence > 0.6) return "medium";
    return "low";
  }

  calculateCollectivePriority(stats) {
    if (stats.positiveRate > 0.8 && stats.uniqueUsers > 50) return "high";
    if (stats.positiveRate > 0.6 && stats.uniqueUsers > 20) return "medium";
    return "low";
  }

  rankInsights(insights) {
    return insights
      .sort((a, b) => {
        // Priority ranking
        const priorityScore = { high: 3, medium: 2, low: 1 };
        const aPriority = priorityScore[a.priority] || 1;
        const bPriority = priorityScore[b.priority] || 1;

        if (aPriority !== bPriority) {
          return bPriority - aPriority;
        }

        // Confidence ranking
        if (a.confidence !== b.confidence) {
          return b.confidence - a.confidence;
        }

        // Time relevance
        if (a.timeRelevant && !b.timeRelevant) return -1;
        if (!a.timeRelevant && b.timeRelevant) return 1;

        // Recency
        return b.timestamp - a.timestamp;
      })
      .slice(0, 8); // Limit to top 8 insights
  }

  async processReflectionForInsights(title, content, selectedStates = []) {
    // Process the reflection content
    const processedReflection = await this.anonymizer.processReflection(
      content,
      title
    );

    // Log selected states
    for (const state of selectedStates) {
      await this.stateTracker.setLocalState(state.key, state.value, {
        reflection_id: Date.now(),
        mood_before: state.moodBefore,
        mood_after: state.moodAfter,
        duration: state.duration,
        notes: state.notes,
      });
    }

    // Generate immediate insights based on new data
    const immediateInsights = await this.generateImmediateInsights(
      selectedStates,
      processedReflection
    );

    return {
      processedReflection,
      immediateInsights,
      recommendations: await this.generateRecommendations(selectedStates),
    };
  }

  async generateImmediateInsights(states, processedReflection) {
    const insights = [];

    // Analyze sentiment vs activities
    if (processedReflection.decentralized.sentiment.label === "positive") {
      for (const state of states.filter((s) => s.value === 1)) {
        insights.push({
          id: `immediate_positive_${state.key}_${Date.now()}`,
          type: "immediate",
          message: `"${state.key}" scheint heute einen positiven Einfluss zu haben!`,
          confidence: 0.7,
          stateKey: state.key,
          source: "immediate_analysis",
          priority: "medium",
        });
      }
    }

    // Detect patterns within the session
    const stateKeys = states.map((s) => s.key);
    const combinations = this.findStateCombinations(stateKeys);

    for (const combo of combinations) {
      insights.push({
        id: `immediate_combo_${combo.join("_")}_${Date.now()}`,
        type: "immediate",
        message: `Die Kombination aus ${combo.join(
          " und "
        )} funktioniert gut für dich!`,
        confidence: 0.6,
        stateKeys: combo,
        source: "immediate_analysis",
        priority: "low",
      });
    }

    return insights;
  }

  findStateCombinations(stateKeys) {
    const combinations = [];
    for (let i = 0; i < stateKeys.length; i++) {
      for (let j = i + 1; j < stateKeys.length; j++) {
        combinations.push([stateKeys[i], stateKeys[j]]);
      }
    }
    return combinations;
  }

  async generateRecommendations(currentStates) {
    const recommendations = [];
    const currentStateKeys = currentStates.map((s) => s.key);

    // Recommend complementary activities
    const complementaryMap = {
      walked: ["meditated", "focused"],
      meditated: ["focused", "journaled"],
      exercised: ["slept_well", "ate_healthy"],
      focused: ["took_break", "practiced_gratitude"],
      worked: ["took_break", "listened_music"],
    };

    for (const stateKey of currentStateKeys) {
      const complementary = complementaryMap[stateKey];
      if (complementary) {
        for (const suggestion of complementary) {
          if (!currentStateKeys.includes(suggestion)) {
            recommendations.push({
              type: "complementary",
              message: `Da du heute "${stateKey}" gemacht hast, könnte "${suggestion}" eine gute Ergänzung sein.`,
              stateKey: suggestion,
              confidence: 0.6,
            });
          }
        }
      }
    }

    return recommendations.slice(0, 3); // Limit to 3 recommendations
  }

  async getInsightSummary() {
    const insights = await this.generateProactiveInsights();

    const summary = {
      total: insights.length,
      byType: {},
      byPriority: { high: 0, medium: 0, low: 0 },
      bySource: {},
      mostConfident: insights[0] || null,
      actionable: insights.filter((i) => i.actions && i.actions.length > 0)
        .length,
    };

    insights.forEach((insight) => {
      summary.byType[insight.type] = (summary.byType[insight.type] || 0) + 1;
      summary.byPriority[insight.priority] =
        (summary.byPriority[insight.priority] || 0) + 1;
      summary.bySource[insight.source] =
        (summary.bySource[insight.source] || 0) + 1;
    });

    return summary;
  }
}

export default InsightEngine;
