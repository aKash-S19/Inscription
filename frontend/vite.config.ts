import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The backend runs on :8080 in dev. In production the Spring Boot jar serves
// the built frontend from /static, so all API calls are relative (/api/...).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
