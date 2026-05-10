"""
Math engine: turn a user string z = f(x, y) into 2D arrays for a Plotly surface.

We never use eval() on the string. SymPy parses it into a safe expression tree,
then lambdify turns that into a NumPy-callable function for fast grid evaluation.
"""

from __future__ import annotations

import numpy as np
from sympy import lambdify, parse_expr, symbols

# These are the only symbols users may reference; we compare parsed expr.free_symbols to this set.
x_sym, y_sym = symbols("x y")
_ALLOWED = {x_sym, y_sym}


class SurfacePlotError(Exception):
    """Carries a message the HTTP layer can show as 400 Bad Request."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def normalize_expression(expression: str) -> str:
    """Calculator users type ^ for powers; Python and SymPy need **."""
    return expression.replace("^", "**").strip()


def generate_surface_grid(
    expression: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    resolution: int,
) -> tuple[list[list[float]], list[list[float]], list[list[float]], str]:
    """
    Returns (x_grid, y_grid, z_grid, normalized_expression).

    Each of x_grid, y_grid, z_grid is a nested list with shape (ny, nx) so FastAPI
    can JSON-encode them without custom serializers. That shape comes from
    numpy.meshgrid(..., indexing="xy"), which matches Plotly surface conventions.
    """
    normalized = normalize_expression(expression)
    if not normalized:
        raise SurfacePlotError("Expression must not be empty.")

    # transformations="all" enables implicit multiplication etc.; still builds an AST, not arbitrary code.
    try:
        expr = parse_expr(normalized, transformations="all")
    except (SyntaxError, TypeError, ValueError) as e:
        raise SurfacePlotError(f"Could not parse expression: {e}") from e

    # Reject z, t, etc. early so lambdify never sees unexpected free variables.
    extra = expr.free_symbols - _ALLOWED
    if extra:
        names = ", ".join(sorted(s.name for s in extra))
        raise SurfacePlotError(f"Unknown variables: {names}. Only x and y are allowed.")

    # modules="numpy" makes sin, exp, etc. map to vectorized NumPy ufuncs on the whole grid.
    try:
        fn = lambdify((x_sym, y_sym), expr, modules="numpy")
    except Exception as e:
        raise SurfacePlotError(f"Could not compile expression: {e}") from e

    xs = np.linspace(x_min, x_max, resolution, dtype=np.float64)
    ys = np.linspace(y_min, y_max, resolution, dtype=np.float64)
    # indexing="xy": first axis is x-like, second is y-like; Plotly surface expects this pairing.
    xm, ym = np.meshgrid(xs, ys, indexing="xy")

    try:
        z = fn(xm, ym)
    except Exception as e:
        raise SurfacePlotError(f"Evaluation failed: {e}") from e

    if not isinstance(z, np.ndarray):
        z = np.asarray(z, dtype=np.float64)
    if z.shape != xm.shape:
        raise SurfacePlotError("Expression did not evaluate to a 2D grid over x and y.")

    if np.iscomplexobj(z):
        raise SurfacePlotError("Expression produced complex values in the sampled domain.")

    # JSON has no inf/nan; fail clearly instead of returning invalid JSON later.
    if not np.all(np.isfinite(z)):
        raise SurfacePlotError(
            "Expression produced non-finite values (e.g. overflow or division by zero) "
            "in the sampled domain."
        )

    return xm.tolist(), ym.tolist(), z.astype(np.float64).tolist(), normalized
