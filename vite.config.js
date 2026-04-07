// Vite configuration file for React application
// This configures Vite to use the React plugin for JSX transformation
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  root: 'Frontend',
  envDir: '../../',
  plugins: [react()],
  resolve: {
    alias: {
      'hls.js': 'hls.js/dist/hls.js',
    },
  },
  build: {
    chunkSizeWarningLimit: 1600,
  },
  server: {
    proxy: {
      // SSE stream — must come before the generic /api rule
      '/api/chat/stream': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Disable response buffering so SSE tokens aren't held back
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq) => {
            proxyReq.setHeader('Accept', 'text/event-stream')
          })
        },
      },
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