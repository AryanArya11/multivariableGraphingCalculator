"""
Application entry: create FastAPI app, CORS for the Vite dev server, mount routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import plot

app = FastAPI(title="Multivariable graphing API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes from plot.router are mounted under /api → POST /plot becomes POST /api/plot.
app.include_router(plot.router, prefix="/api")
