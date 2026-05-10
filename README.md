# Multivariable 3D graphing calculator

Monorepo with a **FastAPI** backend that evaluates \(z = f(x, y)\) from a text expression (SymPy + NumPy) and a **Vite + React + TypeScript** frontend that plots surfaces with Plotly. The browser never evaluates user math; only the backend does.

## Documentation

- **[Architecture diagrams](docs/architecture.md)** — Mermaid diagrams for system context, frontend/backend structure, and request flow.

## Repository layout

```text
multivariableGraphingCalculator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router mount (/api)
│   │   ├── routers/
│   │   │   └── plot.py          # POST /plot → PlotResponse
│   │   ├── schemas/
│   │   │   └── plot.py          # Pydantic request/response models
│   │   └── services/
│   │       └── surface_plot.py # SymPy parse, lambdify, meshgrid → JSON lists
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── public/
│   └── src/
│       ├── main.tsx             # React entry (mounts <App />)
│       ├── App.tsx               # Expression input, fetch /api/plot, Suspense
│       ├── SurfacePlot.tsx       # Lazy-loaded Plotly surface + error boundary
│       ├── App.css
│       ├── index.css
│       └── vite-env.d.ts       # Types for import.meta.env (e.g. VITE_API_BASE)
├── docs/
│   └── architecture.md          # Mermaid architecture diagrams
├── .gitignore
└── README.md
```

## Prerequisites

- **Python 3.12+** (recommended) with a virtual environment at `.venv` or similar  
- **Node.js** and **npm** (for the frontend)

## Backend

Create or activate a venv, install dependencies, run Uvicorn from the **repository root** so imports resolve:

```powershell
cd path\to\multivariableGraphingCalculator
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --app-dir backend
```

- API docs: `http://127.0.0.1:8000/docs`  
- Plot endpoint: **`POST /api/plot`** with JSON body  
  `{ "expression": "x^2 + y^2", "x_min": -5, "x_max": 5, "y_min": -5, "y_max": 5, "resolution": 50 }`  
  (bounds and resolution are optional; defaults match `schemas/plot.py`.)

If PowerShell blocks `Activate.ps1`, using `.\.venv\Scripts\python.exe -m uvicorn ...` avoids changing the execution policy.

## Frontend

```powershell
cd path\to\multivariableGraphingCalculator\frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). The UI posts to **`http://127.0.0.1:8000/api/plot`** by default. Override with a root `.env` file in `frontend/`:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

Production build:

```powershell
npm run build
```

Output is written to `frontend/dist/`.

## Development notes

- **CORS** allows the Vite dev origin (`http://localhost:5173`) from `backend/app/main.py`.  
- Plotly is **lazy-loaded** in `SurfacePlot.tsx` to keep the initial bundle smaller.  
- **`react-plotly.js`** is CommonJS; `SurfacePlot.tsx` normalizes the default export for Vite.
