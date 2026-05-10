import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// StrictMode is omitted: in development it double-mounts children, which breaks Plotly’s
// WebGL lifecycle (react-plotly.js). Production builds were already single-mount.
createRoot(document.getElementById('root')!).render(<App />)
