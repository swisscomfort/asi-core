/**
 * Storacha Service - Professioneller dezentraler Speicher-Client
 * Basiert auf dem offiziellen @storacha/client
 */

class StorachaService {
  constructor() {
    this.client = null;
    this.spaceDid = "did:key:z6Mkee4LjNKaS6Yh25y5w1R97ib7tabTUp5TzW9JnkJcbKsc";
    this.isInitialized = false;
  }

  /**
   * Initialisiere den Storacha Client
   */
  async initialize() {
    if (this.isInitialized) return this.client;

    try {
      // Dynamischer Import für bessere Bundle-Größe
      const { create } = await import("@storacha/client");

      this.client = await create();
      this.isInitialized = true;

      console.log("Storacha Client initialisiert");
      return this.client;
    } catch (error) {
      console.error("Fehler bei Storacha-Initialisierung:", error);
      throw new Error(
        `Storacha-Initialisierung fehlgeschlagen: ${error.message}`
      );
    }
  }

  /**
   * Upload einer Reflexion als JSON-Datei
   * @param {Object} reflection - Die Reflexionsdaten
   * @returns {Promise<string>} - Der CID der gespeicherten Datei
   */
  async uploadReflection(reflection) {
    try {
      await this.initialize();

      // JSON-Datei erstellen
      const jsonContent = JSON.stringify(reflection, null, 2);
      const timestamp = reflection.timestamp || new Date().toISOString();
      const filename = `reflection_${timestamp.replace(/[:.]/g, "-")}.json`;

      // Blob und File erstellen
      const blob = new Blob([jsonContent], { type: "application/json" });
      const file = new File([blob], filename, { type: "application/json" });

      // Upload zu Storacha mit Space-DID
      const result = await this.client.upload(file, {
        space: this.spaceDid,
      });

      const cid = result.toString();
      console.log(`✅ Storacha Upload erfolgreich:`, {
        filename,
        cid,
        url: `https://w3s.link/ipfs/${cid}`,
        size: blob.size,
      });

      return cid;
    } catch (error) {
      console.error("❌ Storacha Upload fehlgeschlagen:", error);
      throw new Error(`Upload fehlgeschlagen: ${error.message}`);
    }
  }

  /**
   * Upload beliebiger Dateien
   * @param {File} file - Die hochzuladende Datei
   * @returns {Promise<string>} - Der CID der gespeicherten Datei
   */
  async uploadFile(file) {
    try {
      await this.initialize();

      const result = await this.client.upload(file, {
        space: this.spaceDid,
      });

      const cid = result.toString();
      console.log(`✅ Datei Upload erfolgreich:`, {
        filename: file.name,
        cid,
        url: `https://w3s.link/ipfs/${cid}`,
        size: file.size,
      });

      return cid;
    } catch (error) {
      console.error("❌ Datei Upload fehlgeschlagen:", error);
      throw new Error(`Upload fehlgeschlagen: ${error.message}`);
    }
  }

  /**
   * Generiere eine öffentliche URL für einen CID
   * @param {string} cid - Content Identifier
   * @returns {string} - Öffentliche IPFS URL
   */
  getPublicUrl(cid) {
    return `https://w3s.link/ipfs/${cid}`;
  }

  /**
   * Prüfe ob der Service verfügbar ist
   * @returns {Promise<boolean>}
   */
  async isAvailable() {
    try {
      await this.initialize();
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Singleton-Instanz exportieren
export default new StorachaService();
