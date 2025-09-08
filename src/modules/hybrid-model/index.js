import StateTracker from "./state-tracker.js";
import Anonymizer from "./anonymizer.js";
import ChainInterface from "./chain-interface.js";
import InsightEngine from "./insight-engine.js";

class HybridModel {
  constructor() {
    this.stateTracker = new StateTracker();
    this.anonymizer = new Anonymizer();
    this.chainInterface = new ChainInterface();
    this.insightEngine = new InsightEngine();
    this.isInitialized = false;
  }

  async initialize() {
    try {
      await Promise.all([
        this.stateTracker.initDB(),
        this.chainInterface.initialize(),
        this.insightEngine.initialize(),
      ]);
      this.isInitialized = true;
      return true;
    } catch (error) {
      console.error("Failed to initialize HybridModel:", error);
      return false;
    }
  }

  getAvailableStates() {
    return [
      { key: "walked", label: "Spaziergang/Gehen" },
      { key: "focused", label: "Fokussiert gearbeitet" },
      { key: "slept_well", label: "Gut geschlafen" },
      { key: "meditated", label: "Meditiert" },
      { key: "productive_morning", label: "Produktiver Morgen" },
      { key: "exercised", label: "Sport gemacht" },
      { key: "read", label: "Gelesen" },
      { key: "journaled", label: "Tagebuch geschrieben" },
      { key: "socialized", label: "Zeit mit anderen verbracht" },
      { key: "creative_work", label: "Kreativ tätig" },
    ];
  }

  getMoodOptions() {
    return [
      { value: "terrible", label: "😞 Schrecklich" },
      { value: "bad", label: "😔 Schlecht" },
      { value: "stressed", label: "😤 Gestresst" },
      { value: "neutral", label: "😐 Neutral" },
      { value: "okay", label: "🙂 Okay" },
      { value: "good", label: "😊 Gut" },
      { value: "calm", label: "😌 Ruhig" },
      { value: "great", label: "😄 Großartig" },
      { value: "excellent", label: "🤩 Exzellent" },
    ];
  }

  async validatePrivacy(content) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return await this.anonymizer.validatePrivacy(content);
  }

  async getInsights() {
    if (!this.isInitialized) {
      await this.initialize();
    }

    return await this.insightEngine.getPersonalInsights();
  }

  storeLocalReflection(reflection) {
    // Store in localStorage for now
    const reflections = JSON.parse(
      localStorage.getItem("asi_reflections") || "[]"
    );
    reflections.push(reflection);
    localStorage.setItem("asi_reflections", JSON.stringify(reflections));
  }

  async processReflection(
    title,
    content,
    selectedStates = [],
    shareAnonymously = false
  ) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // Process reflection through anonymizer
    const processedReflection = await this.anonymizer.processReflection(
      content,
      title
    );

    // Store locally (full data)
    const localEntry = {
      id: Date.now().toString(),
      ...processedReflection.local,
      selectedStates: selectedStates,
      shareAnonymously: shareAnonymously,
    };

    // Store in local storage
    this.storeLocalReflection(localEntry);

    // Process states
    const stateResults = [];
    for (const state of selectedStates) {
      const stateResult = await this.stateTracker.setLocalState(
        state.key,
        state.value,
        {
          reflection_id: localEntry.id,
          mood_before: state.moodBefore,
          mood_after: state.moodAfter,
          duration: state.duration,
          notes: state.notes,
        }
      );
      stateResults.push(stateResult);
    }

    // Share anonymously if requested
    let blockchainResults = null;
    if (shareAnonymously) {
      blockchainResults = await this.shareAnonymously(
        processedReflection.decentralized,
        selectedStates
      );
    }

    // Generate insights
    const insights = await this.insightEngine.processReflectionForInsights(
      title,
      content,
      selectedStates
    );

    return {
      success: true,
      localEntry: localEntry,
      stateResults: stateResults,
      blockchainResults: blockchainResults,
      insights: insights,
      processedData: processedReflection,
    };
  }

  async shareAnonymously(anonymizedData, selectedStates) {
    const results = [];

    try {
      // Upload anonymized reflection to decentralized storage if content is substantial
      let cid = "";
      if (anonymizedData.textLength > 50) {
        // This would integrate with IPFS/Storacha
        // For now, we'll just generate a mock CID
        cid = this.generateMockCID(anonymizedData);
      }

      // Log states to blockchain
      for (const state of selectedStates) {
        const result = await this.chainInterface.logState(
          state.key,
          state.value,
          cid
        );
        results.push({
          stateKey: state.key,
          value: state.value,
          blockchain: result,
          cid: cid,
        });
      }

      return {
        success: true,
        results: results,
        cid: cid,
        anonymizedData: anonymizedData,
      };
    } catch (error) {
      console.error("Failed to share anonymously:", error);
      return {
        success: false,
        error: error.message,
        results: results,
      };
    }
  }

  generateMockCID(data) {
    // Generate a mock CID based on data hash
    const hash = this.anonymizer.simpleHash(JSON.stringify(data));
    return `bafybei${hash.toString(16).padStart(52, "0")}`;
  }

  storeLocalReflection(entry) {
    const reflections = this.getLocalReflections();
    reflections.push(entry);

    // Keep only last 1000 reflections to manage storage
    if (reflections.length > 1000) {
      reflections.splice(0, reflections.length - 1000);
    }

    localStorage.setItem("asi_local_reflections", JSON.stringify(reflections));
  }

  getLocalReflections(limit = 50) {
    try {
      const stored = localStorage.getItem("asi_local_reflections");
      const reflections = stored ? JSON.parse(stored) : [];
      return reflections.slice(-limit).reverse(); // Most recent first
    } catch (error) {
      console.error("Failed to get local reflections:", error);
      return [];
    }
  }

  async getStateHistory(stateKey, days = 7) {
    return await this.stateTracker.getStateHistory(stateKey, days);
  }

  async getInsights() {
    return await this.insightEngine.generateProactiveInsights();
  }

  async getCollectiveStats(stateKey) {
    return await this.chainInterface.getGlobalStats(stateKey);
  }

  async validatePrivacy(text) {
    return this.anonymizer.validateAnonymization(text);
  }

  async getWalletInfo() {
    return await this.chainInterface.getWalletInfo();
  }

  async estimateTransactionCost(stateKey, value) {
    return await this.chainInterface.estimateTransactionCost(stateKey, value);
  }

  getAvailableStates() {
    return [
      { key: "walked", label: "Spazieren/Laufen", category: "movement" },
      { key: "meditated", label: "Meditiert", category: "mindfulness" },
      { key: "exercised", label: "Sport gemacht", category: "movement" },
      {
        key: "focused",
        label: "Fokussiert gearbeitet",
        category: "productivity",
      },
      { key: "slept_well", label: "Gut geschlafen", category: "health" },
      { key: "ate_healthy", label: "Gesund gegessen", category: "health" },
      {
        key: "journaled",
        label: "Tagebuch geschrieben",
        category: "reflection",
      },
      { key: "called_friend", label: "Freund angerufen", category: "social" },
      { key: "read_book", label: "Buch gelesen", category: "learning" },
      { key: "listened_music", label: "Musik gehört", category: "wellness" },
      {
        key: "worked_on_hobby",
        label: "Hobby gepflegt",
        category: "creativity",
      },
      { key: "took_break", label: "Pause gemacht", category: "wellness" },
      { key: "organized_space", label: "Aufgeräumt", category: "productivity" },
      { key: "planned_day", label: "Tag geplant", category: "productivity" },
      {
        key: "practiced_gratitude",
        label: "Dankbarkeit praktiziert",
        category: "mindfulness",
      },
      { key: "helped_someone", label: "Jemandem geholfen", category: "social" },
      {
        key: "learned_something",
        label: "Etwas gelernt",
        category: "learning",
      },
      {
        key: "spent_time_nature",
        label: "Zeit in der Natur",
        category: "wellness",
      },
      {
        key: "connected_family",
        label: "Familie kontaktiert",
        category: "social",
      },
      {
        key: "creative_work",
        label: "Kreativ gearbeitet",
        category: "creativity",
      },
    ];
  }

  getMoodOptions() {
    return [
      { value: "terrible", label: "Schrecklich", score: 1 },
      { value: "bad", label: "Schlecht", score: 2 },
      { value: "stressed", label: "Gestresst", score: 3 },
      { value: "neutral", label: "Neutral", score: 4 },
      { value: "okay", label: "Okay", score: 5 },
      { value: "good", label: "Gut", score: 6 },
      { value: "calm", label: "Ruhig", score: 7 },
      { value: "great", label: "Großartig", score: 8 },
      { value: "excellent", label: "Exzellent", score: 9 },
    ];
  }

  async exportData() {
    const data = {
      localReflections: this.getLocalReflections(1000),
      stateHistory: await this.stateTracker.exportAnonymizedData(),
      insights: await this.insightEngine.getInsightSummary(),
      exportedAt: new Date().toISOString(),
      version: "1.0.0",
    };

    return data;
  }

  async importData(data) {
    try {
      if (data.localReflections) {
        localStorage.setItem(
          "asi_local_reflections",
          JSON.stringify(data.localReflections)
        );
      }

      // Note: State history would need to be imported into IndexedDB
      // This is a simplified version

      return { success: true, message: "Data imported successfully" };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async clearOldData(daysToKeep = 90) {
    // Clear old state data
    await this.stateTracker.clearOldData(daysToKeep);

    // Clear old reflections
    const reflections = this.getLocalReflections(1000);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const filteredReflections = reflections.filter((reflection) => {
      return new Date(reflection.timestamp) > cutoffDate;
    });

    localStorage.setItem(
      "asi_local_reflections",
      JSON.stringify(filteredReflections)
    );

    return {
      success: true,
      message: `Cleared data older than ${daysToKeep} days`,
      remainingReflections: filteredReflections.length,
    };
  }

  async getSystemStatus() {
    const status = {
      hybridModel: this.isInitialized,
      stateTracker: this.stateTracker.db !== null,
      chainInterface: this.chainInterface.isInitialized,
      walletConnected: false,
      localReflections: this.getLocalReflections().length,
      lastActivity: null,
      errors: [],
    };

    try {
      const walletInfo = await this.chainInterface.getWalletInfo();
      status.walletConnected = walletInfo !== null;
      status.walletAddress = walletInfo?.address;
      status.walletBalance = walletInfo?.balance;
    } catch (error) {
      status.errors.push(`Wallet: ${error.message}`);
    }

    try {
      const recentReflections = this.getLocalReflections(1);
      if (recentReflections.length > 0) {
        status.lastActivity = new Date(recentReflections[0].timestamp);
      }
    } catch (error) {
      status.errors.push(`Local data: ${error.message}`);
    }

    return status;
  }
}

export default HybridModel;
