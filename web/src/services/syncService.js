import { localStorageService } from "./localStorage";

export class SyncService {
  constructor() {
    this.isOnline = navigator.onLine;
    this.setupEventListeners();
  }

  setupEventListeners() {
    window.addEventListener("online", () => {
      this.isOnline = true;
      this.performSync();
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
    });
  }

  async performSync() {
    if (!this.isOnline) return;

    try {
      const unsyncedReflections = await localStorage.getUnsyncedReflections();

      for (const reflection of unsyncedReflections) {
        try {
          // Here would be the actual upload to IPFS/Storacha
          // For now, just mark as synced after a delay
          await new Promise((resolve) => setTimeout(resolve, 1000));
          await localStorage.markReflectionSynced(reflection.id);

          console.log(`Synced reflection ${reflection.id}`);
        } catch (error) {
          console.error(`Failed to sync reflection ${reflection.id}:`, error);
        }
      }

      await localStorage.clearSyncQueue();
    } catch (error) {
      console.error("Sync failed:", error);
    }
  }

  async uploadToStoracha(reflection) {
    // Placeholder for Storacha upload
    // Implementation would use the existing Storacha client
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ cid: "mock-cid-" + Date.now() });
      }, 1000);
    });
  }

  getConnectionStatus() {
    return {
      online: this.isOnline,
      message: this.isOnline
        ? "Online - Änderungen werden synchronisiert"
        : "Offline - Änderungen werden synchronisiert, sobald du online bist",
    };
  }
}

export const syncService = new SyncService();
