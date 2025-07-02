import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    open: true,
    https: true  // 🔥 Added HTTPS for Facebook authentication
  },
  css: {
    postcss: './postcss.config.js'
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})