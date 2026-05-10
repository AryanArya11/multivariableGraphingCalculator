import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Plotly is large; pre-bundle it so the first lazy load doesn’t stall the dev server optimizer.
  optimizeDeps: {
    include: ['plotly.js', 'react-plotly.js'],
  },
})
