from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Project

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

DATASET_COLOURS = [
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

DATASET_LINESTYLES = ["-", "--", "-.", ":"]

VALID_LINESTYLES = {"-", "--", "-.", ":", "None", ""}

CURVE_TYPE_LINESTYLES = {
    "uv": "-",
    "conductivity": "--",
    "gradient": "-.",
    "pressure": ":",
    "temperature": "-.",
    "ph": "--",
    "flow": ":",
}

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

def default_style_for_curve_type(curve_type: str, index: int = 0) -> CurveStyle:
    """Return the default style associated with a chromatography curve type"""
    if curve_type == "uv":
        return CurveStyle(color="#1f77b4", linewidth=1.5, linestyle="-")
    if curve_type == "uv_auxiliary":
        return CurveStyle(color="#1f77b4", linewidth=1.0, linestyle=":", alpha=0.6)
    if curve_type == "conductivity":
        return CurveStyle(color="#2ca02c", linewidth=1.2, linestyle="-")
    if curve_type == "gradient":
        return CurveStyle(color="#ff7f0e", linewidth=1.0, linestyle="-")
    if curve_type == "pressure":
        return CurveStyle(color="#d62728", linewidth=1.0, linestyle="")
    if curve_type == "temperature":
        return CurveStyle(color="#9467bd", linewidth=1.0, linestyle="-")
    if curve_type == "ph":
        return CurveStyle(color="#8c564b", linewidth=1.0, linestyle="-")
    if curve_type == "flow":
        return CurveStyle(color="#7f7f7f", linewidth=1.0, linestyle="-")

    return default_curve_style(index)

def default_style_for_dataset(
    dataset_index: int,
    curve_index: int,
    curve_type: str,
) -> CurveStyle:
    """
    Return an automatic style for a curve using dataset-based styling

    All curves within a dataset share a colour. Known curve types use consistent
    line styles, while unknown curve types cycle through the available line styles.
    """
    color = DATASET_COLOURS[dataset_index % len(DATASET_COLOURS)]

    if curve_type == "uv_auxiliary":
        return CurveStyle(
            color=color,
            linewidth=1.0,
            linestyle=":",
            alpha=0.6,
        )

    linestyle = CURVE_TYPE_LINESTYLES.get(curve_type, DATASET_LINESTYLES[curve_index % len(DATASET_LINESTYLES)]) 

    return CurveStyle(
        color=color,
        linewidth=1.5,
        linestyle=linestyle,
    )

def automatic_curve_style(
    *,
    mode: str,
    curve_type: str,
    dataset_index: int,
    curve_index: int,
) -> CurveStyle:
    """Return an automatic style according to the selected styling mode"""
    if mode == "curve_type":
        return default_style_for_curve_type(
            curve_type,
            curve_index,
        )

    if mode == "dataset":
        return default_style_for_dataset(
            dataset_index,
            curve_index,
            curve_type,
        )

    raise ValueError(f"Unknown curve style mode: {mode}")

def is_valid_linestyle(linestyle: str) -> bool:
    return linestyle in VALID_LINESTYLES

def apply_automatic_styles_to_dataset(
    project: "Project",
    dataset_index: int,
) -> None:
    """Apply the project's automatic styling mode to one dataset."""
    dataset = project.datasets[dataset_index]
    mode = project.plot_settings.curve_style_mode

    dataset.display_color = DATASET_COLOURS[
        dataset_index % len(DATASET_COLOURS)
    ]

    style_index = 0

    for curve in dataset.curves:
        curve_type = str(
            curve.metadata.get("curve_type", "unknown")
        )

        curve.style = automatic_curve_style(
            mode=mode,
            curve_type=curve_type,
            dataset_index=dataset_index,
            curve_index=style_index,
        )

        if curve_type != "uv_auxiliary":
            style_index += 1

def apply_automatic_styles(project: "Project") -> None:
    """
    Apply the project's automatic styling mode to all curves.
    
    Dataset mode assigns one colour per dataset and uses line styles to distinguish
    curve types. Curve-type mode assigns styles according to curve type
    """
    for dataset_index in range(len(project.datasets)):
        apply_automatic_styles_to_dataset(
            project,
            dataset_index,
        )