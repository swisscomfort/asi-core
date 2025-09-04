/**
 * Storacha Service - Dezentrale Speicherung mit Storacha Client
 */

import { create } from "@storacha/client";

class StorachaService {
  constructor() {
    this.client = null;
    this.isInitialized = false;
    this.spaceName = "asi-core";
    this.token = import.meta.env.VITE_STORACHA_TOKEN;
  }

  /**
   * Initialisiert den Storacha Client und lädt den Space
   */
  async initialize() {
    if (this.isInitialized && this.client) {
      return this.client;
    }

    try {
      // Client erstellen
      this.client = await create();

      // Wenn Token vorhanden, authentifizieren
      if (this.token) {
        await this.client.authorize(this.token);
      }

      // Space laden oder erstellen
      await this.ensureSpace();

      this.isInitialized = true;
      console.log("✅ Storacha Client initialisiert");
      return this.client;
    } catch (error) {
      console.error("❌ Storacha Initialisierung fehlgeschlagen:", error);
      throw new Error(
        `Storacha Initialisierung fehlgeschlagen: ${error.message}`
      );
    }
  }

  /**
   * Stellt sicher, dass der asi-core Space existiert
   */
  async ensureSpace() {
    try {
      const spaces = await this.client.spaces();
      let space = spaces.find((s) => s.name === this.spaceName);

      if (!space) {
        space = await this.client.createSpace(this.spaceName);
        console.log("✅ Neuer Space erstellt:", this.spaceName);
      }

      await this.client.setCurrentSpace(space.did());
      console.log("✅ Space geladen:", this.spaceName);
      return space;
    } catch (error) {
      console.error("❌ Space-Setup fehlgeschlagen:", error);
      throw error;
    }
  }

  /**
   * Lädt eine Datei auf Storacha hoch
   * @param {File} file - Die hochzuladende Datei
   * @returns {Promise<string>} - Der CID der gespeicherten Datei
   */
  async uploadToStoracha(file) {
    try {
      // Offline-Check
      if (!navigator.onLine) {
        throw new Error("Keine Internetverbindung verfügbar");
      }

      // Client initialisieren
      await this.initialize();

      // Datei hochladen
      const result = await this.client.upload(file);
      const cid = result.toString();

      // CID lokal speichern
      this.saveCIDLocally(cid, file.name);

      console.log("✅ Upload erfolgreich:", {
        filename: file.name,
        cid,
        url: `https://${cid}.ipfs.w3s.link`,
      });

      return cid;
    } catch (error) {
      console.error("❌ Upload fehlgeschlagen:", error);

      // Spezifische Fehlermeldungen
      if (error.message.includes("authorization")) {
        throw new Error("Ungültige Storacha-Credentials");
      }
      if (
        error.message.includes("network") ||
        error.message.includes("fetch")
      ) {
        throw new Error("Netzwerkfehler - bitte später versuchen");
      }

      throw new Error(`Upload fehlgeschlagen: ${error.message}`);
    }
  }

  /**
   * Speichert CID im localStorage
   */
  saveCIDLocally(cid, filename) {
    try {
      const stored = JSON.parse(localStorage.getItem("storacha_cids") || "[]");
      stored.push({
        cid,
        filename,
        timestamp: new Date().toISOString(),
      });
      localStorage.setItem("storacha_cids", JSON.stringify(stored));
    } catch (error) {
      console.warn("⚠️ Konnte CID nicht lokal speichern:", error);
    }
  }

  /**
   * Gibt alle lokal gespeicherten CIDs zurück
   */
  getStoredCIDs() {
    try {
      return JSON.parse(localStorage.getItem("storacha_cids") || "[]");
    } catch (error) {
      console.warn("⚠️ Konnte CIDs nicht laden:", error);
      return [];
    }
  }

  /**
   * Prüft den Verbindungsstatus
   */
  async getConnectionStatus() {
    try {
      if (!navigator.onLine) {
        return { connected: false, reason: "Offline" };
      }

      await this.initialize();
      return { connected: true, spaceName: this.spaceName };
    } catch (error) {
      return {
        connected: false,
        reason: error.message.includes("authorization")
          ? "Ungültige Credentials"
          : "Verbindungsfehler",
      };
    }
  }

  /**
   * Erstellt eine JSON-Datei aus einem Reflexions-Objekt und lädt sie hoch
   */
  async uploadReflection(reflection) {
    try {
      // JSON-String erstellen
      const jsonContent = JSON.stringify(reflection, null, 2);

      // Dateiname generieren
      const timestamp = reflection.timestamp || new Date().toISOString();
      const filename = `reflection_${timestamp.replace(/[:.]/g, "-")}.json`;

      // File-Objekt erstellen
      const file = new File([jsonContent], filename, {
        type: "application/json",
      });

      // Upload
      return await this.uploadToStoracha(file);
    } catch (error) {
      console.error("❌ Reflexion-Upload fehlgeschlagen:", error);
      throw error;
    }
  }
}

// Singleton-Instanz exportieren
export default new StorachaService();
