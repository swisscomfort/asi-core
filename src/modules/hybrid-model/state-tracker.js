import { openDB } from "idb";

class StateTracker {
  constructor() {
    this.dbName = "ASI_StateTracker";
    this.dbVersion = 1;
    this.db = null;
    this.states = new Map();
    this.initDB();
  }

  async initDB() {
    this.db = await openDB(this.dbName, this.dbVersion, {
      upgrade(db) {
        if (!db.objectStoreNames.contains("states")) {
          const stateStore = db.createObjectStore("states", {
            keyPath: "id",
            autoIncrement: true,
          });
          stateStore.createIndex("timestamp", "timestamp");
          stateStore.createIndex("state_key", "state_key");
          stateStore.createIndex("date", "date");
        }

        if (!db.objectStoreNames.contains("patterns")) {
          const patternStore = db.createObjectStore("patterns", {
            keyPath: "id",
            autoIncrement: true,
          });
          patternStore.createIndex("pattern_type", "pattern_type");
          patternStore.createIndex("confidence", "confidence");
        }
      },
    });
  }

  async setLocalState(key, value, context = {}) {
    const timestamp = Date.now();
    const date = new Date().toISOString().split("T")[0];

    const stateEntry = {
      state_key: key,
      value: value,
      context: context,
      timestamp: timestamp,
      date: date,
      mood_before: context.mood_before || null,
      mood_after: context.mood_after || null,
      duration: context.duration || null,
      time_of_day: new Date().getHours(),
      local_only: true,
    };

    if (this.db) {
      const tx = this.db.transaction("states", "readwrite");
      await tx.objectStore("states").add(stateEntry);
      await tx.done;
    }

    this.states.set(`${key}_${timestamp}`, stateEntry);

    // Trigger pattern analysis
    this.analyzePatterns(key);

    return stateEntry;
  }

  async getStateHistory(key, days = 7) {
    if (!this.db) await this.initDB();

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    const cutoffTimestamp = cutoffDate.getTime();

    const tx = this.db.transaction("states", "readonly");
    const store = tx.objectStore("states");
    const index = store.index("state_key");

    const allEntries = await index.getAll(key);
    return allEntries.filter((entry) => entry.timestamp >= cutoffTimestamp);
  }

  async getAllStatesForDay(date) {
    if (!this.db) await this.initDB();

    const tx = this.db.transaction("states", "readonly");
    const store = tx.objectStore("states");
    const index = store.index("date");

    return await index.getAll(date);
  }

  async analyzePatterns(stateKey) {
    const history = await this.getStateHistory(stateKey, 14);
    if (history.length < 3) return null;

    // Streak analysis
    const recentStates = history.slice(-7);
    const consecutiveDays = this.calculateStreak(recentStates);

    // Time pattern analysis
    const timePatterns = this.analyzeTimePatterns(history);

    // Mood correlation analysis
    const moodCorrelations = this.analyzeMoodCorrelations(history);

    const pattern = {
      state_key: stateKey,
      pattern_type: "behavior_analysis",
      consecutive_days: consecutiveDays,
      time_patterns: timePatterns,
      mood_correlations: moodCorrelations,
      confidence: this.calculateConfidence(history),
      analyzed_at: Date.now(),
      sample_size: history.length,
    };

    // Store pattern
    if (this.db) {
      const tx = this.db.transaction("patterns", "readwrite");
      await tx.objectStore("patterns").add(pattern);
      await tx.done;
    }

    return pattern;
  }

  calculateStreak(states) {
    const dates = [...new Set(states.map((s) => s.date))].sort();
    let streak = 0;
    let currentDate = new Date();

    for (let i = dates.length - 1; i >= 0; i--) {
      const stateDate = new Date(dates[i]);
      const dayDiff = Math.floor(
        (currentDate - stateDate) / (1000 * 60 * 60 * 24)
      );

      if (dayDiff === streak) {
        streak++;
      } else {
        break;
      }
    }

    return streak;
  }

  analyzeTimePatterns(history) {
    const timeGroups = {
      morning: [], // 6-12
      afternoon: [], // 12-18
      evening: [], // 18-22
      night: [], // 22-6
    };

    history.forEach((state) => {
      const hour = state.time_of_day;
      if (hour >= 6 && hour < 12) timeGroups.morning.push(state);
      else if (hour >= 12 && hour < 18) timeGroups.afternoon.push(state);
      else if (hour >= 18 && hour < 22) timeGroups.evening.push(state);
      else timeGroups.night.push(state);
    });

    return {
      most_active_time: Object.keys(timeGroups).reduce((a, b) =>
        timeGroups[a].length > timeGroups[b].length ? a : b
      ),
      distribution: Object.fromEntries(
        Object.entries(timeGroups).map(([key, value]) => [key, value.length])
      ),
    };
  }

  analyzeMoodCorrelations(history) {
    const moodChanges = history.filter((s) => s.mood_before && s.mood_after);
    if (moodChanges.length === 0) return null;

    const improvements = moodChanges.filter(
      (s) => this.getMoodScore(s.mood_after) > this.getMoodScore(s.mood_before)
    );

    return {
      total_mood_entries: moodChanges.length,
      improvements: improvements.length,
      improvement_rate: improvements.length / moodChanges.length,
      common_before_moods: this.getFrequencyMap(
        moodChanges.map((s) => s.mood_before)
      ),
      common_after_moods: this.getFrequencyMap(
        moodChanges.map((s) => s.mood_after)
      ),
    };
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

  getFrequencyMap(items) {
    return items.reduce((acc, item) => {
      acc[item] = (acc[item] || 0) + 1;
      return acc;
    }, {});
  }

  calculateConfidence(history) {
    if (history.length < 3) return 0.1;
    if (history.length < 7) return 0.5;
    if (history.length < 14) return 0.7;
    return 0.9;
  }

  async getLocalInsights(days = 7) {
    if (!this.db) await this.initDB();

    const tx = this.db.transaction("patterns", "readonly");
    const patterns = await tx.objectStore("patterns").getAll();

    const insights = [];

    for (const pattern of patterns) {
      const history = await this.getStateHistory(pattern.state_key, days);

      if (pattern.consecutive_days > 2) {
        insights.push({
          type: "streak",
          message: `Du hast in den letzten ${pattern.consecutive_days} Tagen kontinuierlich "${pattern.state_key}" praktiziert.`,
          confidence: pattern.confidence,
          state_key: pattern.state_key,
        });
      }

      if (
        pattern.mood_correlations &&
        pattern.mood_correlations.improvement_rate > 0.7
      ) {
        insights.push({
          type: "mood_improvement",
          message: `"${
            pattern.state_key
          }" verbessert deine Stimmung in ${Math.round(
            pattern.mood_correlations.improvement_rate * 100
          )}% der Fälle.`,
          confidence: pattern.confidence,
          state_key: pattern.state_key,
        });
      }

      if (pattern.time_patterns.most_active_time) {
        insights.push({
          type: "time_pattern",
          message: `Du praktizierst "${pattern.state_key}" meist am ${pattern.time_patterns.most_active_time}.`,
          confidence: pattern.confidence * 0.8,
          state_key: pattern.state_key,
        });
      }
    }

    return insights.sort((a, b) => b.confidence - a.confidence).slice(0, 5);
  }

  async exportAnonymizedData() {
    if (!this.db) await this.initDB();

    const tx = this.db.transaction("states", "readonly");
    const allStates = await tx.objectStore("states").getAll();

    const anonymized = allStates.map((state) => ({
      state_key: state.state_key,
      value: state.value,
      time_of_day: state.time_of_day,
      day_of_week: new Date(state.timestamp).getDay(),
      duration: state.duration,
      mood_improvement:
        state.mood_before && state.mood_after
          ? this.getMoodScore(state.mood_after) -
            this.getMoodScore(state.mood_before)
          : null,
      // No timestamps, dates, or personal context
    }));

    return anonymized;
  }

  async clearOldData(daysToKeep = 90) {
    if (!this.db) await this.initDB();

    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    const cutoffTimestamp = cutoffDate.getTime();

    const tx = this.db.transaction(["states", "patterns"], "readwrite");

    const stateStore = tx.objectStore("states");
    const stateIndex = stateStore.index("timestamp");
    const stateCursor = await stateIndex.openCursor(
      IDBKeyRange.upperBound(cutoffTimestamp)
    );

    while (stateCursor) {
      await stateCursor.delete();
      await stateCursor.continue();
    }

    await tx.done;
  }
}

export default StateTracker;
