// API Service für ASI Core KI-Funktionen
import { ethers } from "ethers";

const API_BASE_URL =
  process.env.NODE_ENV === "production"
    ? "https://your-api-domain.com"
    : "http://localhost:8000";

const MEMORY_INDEX_ABI = [
  "function addMemory(string memory _cid, string[] memory _tags, int256[768] memory _embedding) external",
  "function getMemory(uint256 index) external view returns (string memory cid, string[] memory tags, int256[768] memory embedding, uint256 timestamp, address owner, bool shared)",
  "function getTotalMemories() external view returns (uint256)",
  "function getUserMemoryCount(address user) external view returns (uint256)",
  "event MemoryStored(address indexed owner, string cid, string[] tags)",
];

const MEMORY_INDEX_ADDRESS = "0x1234567890123456789012345678901234567890"; // Replace with deployed Mumbai address

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

  // Blockchain-Integration für Memory Index
  static async indexToBlockchain(cid, tags, embedding) {
    try {
      if (!window.ethereum) {
        console.warn("No wallet connected, skipping blockchain indexing");
        return null;
      }

      await window.ethereum.request({ method: "eth_requestAccounts" });

      const provider = new ethers.BrowserProvider(window.ethereum);
      const network = await provider.getNetwork();

      // Switch to Polygon Mumbai if not already
      if (network.chainId !== 80001n) {
        try {
          await window.ethereum.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: "0x13881" }], // Mumbai testnet
          });
        } catch (switchError) {
          if (switchError.code === 4902) {
            await window.ethereum.request({
              method: "wallet_addEthereumChain",
              params: [
                {
                  chainId: "0x13881",
                  chainName: "Polygon Mumbai",
                  nativeCurrency: {
                    name: "MATIC",
                    symbol: "MATIC",
                    decimals: 18,
                  },
                  rpcUrls: ["https://rpc-mumbai.maticvigil.com/"],
                  blockExplorerUrls: ["https://mumbai.polygonscan.com/"],
                },
              ],
            });
          } else {
            throw switchError;
          }
        }
      }

      const signer = await provider.getSigner();
      const contract = new ethers.Contract(
        MEMORY_INDEX_ADDRESS,
        MEMORY_INDEX_ABI,
        signer
      );

      // Convert embedding to int256 array
      const embeddingInt256 = embedding.map((val) => Math.round(val * 1000000));

      // Ensure exactly 768 dimensions
      while (embeddingInt256.length < 768) {
        embeddingInt256.push(0);
      }
      embeddingInt256.length = 768;

      const tx = await contract.addMemory(cid, tags, embeddingInt256);
      await tx.wait();

      console.log("Indexed:", tx.hash);
      return tx.hash;
    } catch (error) {
      console.error("Blockchain indexing error:", error);
      return null;
    }
  }

  // Storacha Upload mit Blockchain-Integration
  static async uploadToStorachaWithIndex(content, tags, embedding) {
    try {
      // Upload to Storacha first
      const storachaResponse = await this.uploadToStoracha(content);

      if (storachaResponse && storachaResponse.cid) {
        // Index to blockchain
        const txHash = await this.indexToBlockchain(
          storachaResponse.cid,
          tags,
          embedding
        );

        return {
          ...storachaResponse,
          txHash,
        };
      }

      return storachaResponse;
    } catch (error) {
      console.error("Upload with indexing error:", error);
      throw error;
    }
  }

  // Neue Reflexion erstellen
  static async createReflection(reflectionData) {
    try {
      console.log("📝 Erstelle neue Reflexion:", reflectionData);

      const response = await fetch(`${API_BASE_URL}/api/reflection/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          cid: reflectionData.cid,
          title: reflectionData.title,
          tags: reflectionData.tags || [],
          shared: reflectionData.shared || false,
          timestamp: reflectionData.timestamp,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ API Error: ${response.status}`, errorText);
        throw new Error(
          `Reflexion erstellen fehlgeschlagen: ${response.status} - ${errorText}`
        );
      }

      const result = await response.json();
      console.log("✅ Reflexion erstellt:", result);
      return result;
    } catch (error) {
      console.error("❌ Fehler beim Erstellen der Reflexion:", error);
      throw error;
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
