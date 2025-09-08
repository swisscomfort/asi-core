// API Health Check Service
export class ApiHealthService {
  static isApiAvailable = false;
  static lastCheckTime = 0;
  static checkInterval = 30000; // 30 Sekunden

  static async checkApiHealth() {
    const now = Date.now();

    // Cache für 30 Sekunden
    if (now - this.lastCheckTime < this.checkInterval) {
      return this.isApiAvailable;
    }

    try {
      const apiUrl =
        process.env.NODE_ENV === "production"
          ? "https://swisscomfort.github.io/asi-core"
          : "http://localhost:8000";

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${apiUrl}/api/health`, {
        method: "GET",
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
        },
      });

      clearTimeout(timeoutId);
      this.isApiAvailable = response.ok;
      this.lastCheckTime = now;

      return this.isApiAvailable;
    } catch (error) {
      console.log("API nicht verfügbar:", error.message);
      this.isApiAvailable = false;
      this.lastCheckTime = now;

      return false;
    }
  }

  static async withFallback(apiCall, fallbackCall) {
    const isOnline = await this.checkApiHealth();

    if (!isOnline) {
      console.log("🔄 API nicht verfügbar - verwende Offline-Modus");
      return await fallbackCall();
    }

    try {
      return await apiCall();
    } catch (error) {
      console.log("🔄 API-Fehler - fallback zu Offline-Modus");
      this.isApiAvailable = false;
      return await fallbackCall();
    }
  }
}

export default ApiHealthService;
