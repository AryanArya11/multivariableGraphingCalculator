# Architecture (current)

## System context

```mermaid
flowchart LR
  subgraph client [Browser]
    UI[React UI Vite]
  end
  subgraph server [Python]
    API[FastAPI Uvicorn]
  end
  UI -->|"POST /api/plot JSON"| API
  API -->|"JSON x y z meta"| UI
```

## Frontend (Vite + React + TypeScript)

```mermaid
flowchart TB
  subgraph entry [Entry]
    HTML[index.html]
    MAIN[main.tsx]
  end
  subgraph app [App]
    APP[App.tsx]
    SUSP[Suspense]
    SP[SurfacePlot.tsx lazy]
    PLOT[Plot react-plotly.js]
  end
  HTML --> MAIN
  MAIN --> APP
  APP -->|"fetch VITE_API_BASE /api/plot"| API_LAYER[Backend]
  APP --> SUSP
  SUSP --> SP
  SP --> PLOT
```

## Backend (FastAPI)

```mermaid
flowchart TB
  subgraph fastapi [FastAPI app]
    MAIN_PY[app/main.py]
    CORS[CORSMiddleware]
    R[routers/plot.py]
    MAIN_PY --> CORS
    MAIN_PY --> R
  end
  subgraph layer [Request flow]
    SCH[schemas/plot.py Pydantic]
    SVC[services/surface_plot.py]
    R -->|"validate PlotRequest"| SCH
    R -->|"generate_surface_grid"| SVC
  end
  subgraph math [Math stack]
    SYM[SymPy parse_expr lambdify]
    NP[NumPy meshgrid]
    SVC --> SYM
    SVC --> NP
  end
```

## End-to-end request path

```mermaid
sequenceDiagram
  participant User
  participant App as App.tsx
  participant API as FastAPI /api/plot
  participant Sch as schemas/plot.py
  participant Svc as surface_plot.py
  participant SY as SymPy NumPy

  User->>App: Enter expression click Plot
  App->>API: POST JSON expression optional bounds
  API->>Sch: Parse body into PlotRequest
  Sch-->>API: Validated model
  API->>Svc: generate_surface_grid(...)
  Svc->>SY: parse lambdify sample grid
  SY-->>Svc: x y z arrays lists
  Svc-->>API: grids normalized string
  API-->>App: PlotResponse data meta
  App->>User: Surface chart Plotly chunk
```

## Notes

- Math strings are evaluated **only** on the server (`surface_plot.py`); the browser never parses user expressions as code.
- Plotly loads in a **lazy** chunk (`SurfacePlot.tsx`) after a successful API response.
- API routes are mounted under **`/api`** (`main.py`: `include_router(..., prefix="/api")`), so the plot endpoint is **`POST /api/plot`**.
