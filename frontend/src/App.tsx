import { lazy, Suspense, useCallback, useState } from 'react'
import './App.css'

const SurfacePlot = lazy(() => import('./SurfacePlot.tsx'))

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

type PlotResponse = {
  data: { x: number[][]; y: number[][]; z: number[][] }
  meta: { expression_normalized: string }
}

function formatErrorDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === 'object' && item !== null && 'msg' in item
          ? String((item as { msg: string }).msg)
          : JSON.stringify(item),
      )
      .join('; ')
  }
  return JSON.stringify(detail)
}

export default function App() {
  const [expression, setExpression] = useState('x^2 + y^2')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PlotResponse | null>(null)

  const plot = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/plot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expression }),
      })
      const json: unknown = await res.json()
      if (!res.ok) {
        setResult(null)
        const body = json as { detail?: unknown }
        setError(formatErrorDetail(body.detail ?? json))
        return
      }
      setResult(json as PlotResponse)
    } catch (e) {
      setResult(null)
      setError(e instanceof Error ? e.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }, [expression])

  return (
    <div className="app">
      <header className="toolbar">
        <label className="expr-label">
          <span className="expr-caption">z = f(x, y)</span>
          <input
            className="expr-input"
            value={expression}
            onChange={(e) => setExpression(e.target.value)}
            spellCheck={false}
            autoComplete="off"
          />
        </label>
        <button type="button" className="plot-btn" onClick={plot} disabled={loading}>
          {loading ? 'Plotting…' : 'Plot'}
        </button>
      </header>

      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}

      {result ? (
        <>
          <p className="meta">
            Normalized:{' '}
            <code>{result.meta.expression_normalized}</code>
          </p>
          <div className="plot-wrap">
            <Suspense fallback={<p className="meta">Loading chart…</p>}>
              <SurfacePlot
                x={result.data.x}
                y={result.data.y}
                z={result.data.z}
                expressionNormalized={result.meta.expression_normalized}
              />
            </Suspense>
          </div>
        </>
      ) : null}
    </div>
  )
}
