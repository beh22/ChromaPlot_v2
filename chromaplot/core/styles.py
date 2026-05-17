from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

DEFAULT_COLOURS = [
    "#000000",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

VALID_LINESTYLES = {"-", "--", "-.", ":", "None", ""}

@dataclass
class CurveStyle:
    """Display style for a single curve"""

    color: str = "#000000"
    linewidth: float = 1.5
    linestyle: str = "-"
    alpha: float = 1.0
    marker: str | None = None
    markersize: float = 4.0
    zorder: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "CurveStyle":
        if data is None:
            return cls()
        return cls(
            color=str(data.get("color", "#000000")),
            linewidth=float(data.get("linewidth", 1.5)),
            linestyle=str(data.get("linestyle", "-")),
            alpha=float(data.get("alpha", 1.0)),
            marker=data.get("marker", None),
            markersize=float(data.get("markersize", 4.0)),
            zorder=int(data.get("zorder", 1)),
        )


def default_curve_style(index: int = 0) -> CurveStyle:
    color = DEFAULT_COLOURS[index % len(DEFAULT_COLOURS)]
    return CurveStyle(color=color)

def is_valid_linestyle(linestyle: str) -> bool:
    return linestyle in VALID_LINESTYLES