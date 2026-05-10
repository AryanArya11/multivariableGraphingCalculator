"""
Pydantic models: the "shape" of JSON the API accepts and returns.

FastAPI reads the request body into PlotRequest, runs your route, then turns
PlotResponse back into JSON for the client. You don't parse JSON by hand.
"""

from pydantic import BaseModel, Field


class PlotRequest(BaseModel):
    """What the client sends in POST /plot (the JSON body)."""

    expression: str
    x_min: float = -5.0
    x_max: float = 5.0
    y_min: float = -5.0
    y_max: float = 5.0
    # ge = "greater or equal", le = "less or equal" — Pydantic rejects bad values before your code runs.
    resolution: int = Field(default=50, ge=2, le=300)


class PlotData(BaseModel):
    """The three 2D grids Plotly needs for a surface: same nested-list shape for x, y, z."""

    x: list[list[float]]
    y: list[list[float]]
    z: list[list[float]]


class PlotMeta(BaseModel):
    """Extra info for the UI (e.g. show the normalized expression after ^ → **)."""

    expression_normalized: str


class PlotResponse(BaseModel):
    """What the client gets back: grids under data, metadata under meta."""

    data: PlotData
    meta: PlotMeta
