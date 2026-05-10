"""
HTTP layer for plotting: validate axis ranges, delegate math to the service, map errors to status codes.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.plot import PlotData, PlotMeta, PlotRequest, PlotResponse
from app.services.surface_plot import SurfacePlotError, generate_surface_grid

# Router is a bundle of routes; main.py will include_router(...) with optional prefix.
router = APIRouter(tags=["plot"])


@router.post("/plot", response_model=PlotResponse)
def plot_surface(body: PlotRequest) -> PlotResponse:
    # Cross-field rules: Pydantic validated each field alone; empty or inverted ranges need explicit checks.
    if body.x_min >= body.x_max or body.y_min >= body.y_max:
        raise HTTPException(
            status_code=400,
            detail="Each axis needs min < max (x_min < x_max and y_min < y_max).",
        )

    try:
        x, y, z, normalized = generate_surface_grid(
            body.expression,
            body.x_min,
            body.x_max,
            body.y_min,
            body.y_max,
            body.resolution,
        )
    except SurfacePlotError as e:
        # Service signals expected user errors; 400 = client sent something we refuse to plot.
        raise HTTPException(status_code=400, detail=e.message) from e

    return PlotResponse(
        data=PlotData(x=x, y=y, z=z),
        meta=PlotMeta(expression_normalized=normalized),
    )
