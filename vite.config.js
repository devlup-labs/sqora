// Vite configuration file for React application
// This configures Vite to use the React plugin for JSX transformation
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  root: 'Frontend',
  plugins: [react()],
  resolve: {
    alias: {
      'hls.js': 'hls.js/dist/hls.js',
    },
  },
  build: {
    chunkSizeWarningLimit: 1600, // Increases the limit to 1.6MB
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    watch: {
      ignored: ['**/Unmute/**', '**/node_modules/**', '**/.git/**'],
    },
  },
})