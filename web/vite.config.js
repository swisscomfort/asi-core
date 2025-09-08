import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import { resolve } from "path";

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const isProduction = mode === 'production';
  
  return {
    base: isProduction ? "/asi-core/" : "/",
    
    // Advanced build optimizations
    build: {
      target: 'es2020',
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: !isProduction,
      minify: isProduction ? 'terser' : false,
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      } : {},
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            utils: ['ethers', 'axios'],
            ui: ['@heroicons/react'],
          },
        },
      },
      chunkSizeWarningLimit: 1000,
    },

    // Development server configuration
    server: {
      host: '0.0.0.0',
      port: 5173,
      strictPort: true,
      hmr: {
        overlay: true,
      },
    },

    // Preview server configuration
    preview: {
      host: '0.0.0.0',
      port: 4173,
      strictPort: true,
    },

    // Path resolution
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@services': resolve(__dirname, 'src/services'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@types': resolve(__dirname, 'src/types'),
      },
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(env.VITE_APP_VERSION || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    plugins: [
      react({
        // React plugin optimizations
        babel: {
          plugins: isProduction ? ['babel-plugin-dev-expression'] : [],
        },
      }),
      
      VitePWA({
        registerType: "autoUpdate",
        devOptions: {
          enabled: true,
        },
        
        workbox: {
          globPatterns: ["**/*.{js,css,html,ico,png,svg,json,woff2}"],
          maximumFileSizeToCacheInBytes: 5000000,
          
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
              handler: "CacheFirst",
              options: {
                cacheName: "google-fonts-cache",
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365,
                },
                cacheKeyWillBeUsed: async ({ request }) => request.url,
              },
            },
            {
              urlPattern: /^https:\/\/api\./i,
              handler: "NetworkFirst",
              options: {
                cacheName: "api-cache",
                expiration: {
                  maxEntries: 100,
                  maxAgeSeconds: 60 * 60, // 1 hour
                },
                networkTimeoutSeconds: 10,
              },
            },
          ],
        },
        
        includeAssets: [
          "icon-192.png", 
          "icon-512.png", 
          "apple-touch-icon.png",
          "favicon.ico"
        ],
        
        manifest: {
          name: env.VITE_PWA_NAME || "ASI-Core",
          short_name: env.VITE_PWA_SHORT_NAME || "ASI",
          description: env.VITE_APP_DESCRIPTION || "ASI Core - Artificial Self-Intelligence System",
          theme_color: env.VITE_PWA_THEME_COLOR || "#1e40af",
          background_color: env.VITE_PWA_BACKGROUND_COLOR || "#ffffff",
          display: "standalone",
          orientation: "portrait-primary",
          scope: "/asi-core/",
          start_url: "/asi-core/",
          
          icons: [
            {
              src: "icon-192.png",
              sizes: "192x192",
              type: "image/png",
              purpose: "any maskable",
            },
            {
              src: "icon-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "any maskable",
            },
          ],
          
          categories: ["productivity", "utilities", "lifestyle"],
          
          shortcuts: [
            {
              name: "Neue Reflexion",
              short_name: "Neu",
              description: "Erstelle eine neue Reflexion",
              url: "/asi-core/?action=new",
              icons: [{ src: "icon-192.png", sizes: "192x192" }],
            },
            {
              name: "Suchen",
              short_name: "Suche",
              description: "Durchsuche deine Reflexionen",
              url: "/asi-core/?action=search",
              icons: [{ src: "icon-192.png", sizes: "192x192" }],
            },
          ],
        },
      }),
    ],

    // Performance optimizations
    optimizeDeps: {
      include: ['react', 'react-dom', 'ethers'],
      exclude: ['@web3-storage/w3up-client'],
    },

    // CSS configuration
    css: {
      devSourcemap: !isProduction,
      modules: {
        localsConvention: 'camelCase',
      },
    },
  };
});
    }),
  ],
  build: {
    outDir: "dist",
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    hmr: {
      clientPort: 5173,
    },
  },
});
