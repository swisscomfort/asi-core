import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  base: process.env.NODE_ENV === "production" ? "/asi-core/" : "/",
  
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg}"],
      },
      includeAssets: ["icon-192.png", "icon-512.png"],
      manifest: {
        name: "ASI-Core",
        short_name: "ASI",
        description: "ASI Core - Artificial Self-Intelligence System",
        theme_color: "#1e40af",
        background_color: "#ffffff",
        display: "standalone",
        scope: "/asi-core/",
        start_url: "/asi-core/",
        icons: [
          {
            src: "icon-192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "icon-512.png",
            sizes: "512x512",
            type: "image/png",
          },
        ],
      },
    }),
  ],
});
