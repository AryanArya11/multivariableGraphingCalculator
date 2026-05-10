import { Component, type ComponentType, type ErrorInfo, type ReactNode } from 'react'
import PlotImport from 'react-plotly.js'
import type { PlotParams } from 'react-plotly.js'

// react-plotly.js is CommonJS; Vite may expose `default` as `{ default: Plot }`, which makes
// `<Plot />` render as an invalid element type ("got: object"). Normalize to the component.
const Plot = (
  typeof PlotImport === 'function'
    ? PlotImport
    : (PlotImport as unknown as { default: ComponentType<PlotParams> }).default
) as ComponentType<PlotParams>

type SurfacePlotProps = {
  x: number[][]
  y: number[][]
  z: number[][]
  expressionNormalized: string
}

/** Shows the real Plotly/React error instead of only React’s generic wrapper message. */
class PlotErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Plot error:', error.message, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <p className="error" role="alert">
          Chart error: {this.state.error.message}
        </p>
      )
    }
    return this.props.children
  }
}

function PlotInner({
  x,
  y,
  z,
  expressionNormalized,
}: SurfacePlotProps) {
  const nx = x[0]?.length ?? 0
  const ny = x.length
  // Remount Plot when the grid or expression changes so Plotly doesn’t reuse bad GL state.
  const plotKey = `${expressionNormalized}:${ny}x${nx}`

  return (
    <Plot
      key={plotKey}
      data={[{ type: 'surface', x, y, z }]}
      layout={{
        title: { text: `z = ${expressionNormalized}` },
        autosize: true,
        margin: { l: 0, r: 0, t: 48, b: 0 },
      }}
      style={{ width: '100%', height: '72vh' }}
      useResizeHandler
      config={{ responsive: true }}
    />
  )
}

/** Plotly is heavy; keep it in its own chunk loaded only after a successful /api/plot response. */
export default function SurfacePlot(props: SurfacePlotProps) {
  return (
    <PlotErrorBoundary>
      <PlotInner {...props} />
    </PlotErrorBoundary>
  )
}
