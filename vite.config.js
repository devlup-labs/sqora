// Vite configuration file for React application
// This configures Vite to use the React plugin for JSX transformation
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
