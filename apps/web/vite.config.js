import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// See docs/NETWORK.md: bind to 0.0.0.0 so phones on the field Wi-Fi can reach the
// dev server, and proxy /api + /ws to Django so the browser only needs one origin.
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
