from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

import numpy as np

from .styles import CurveStyle, default_curve_style
from .transforms import CurveTransform

CURRENT_SCHEMA_VERSION = 1

AnnotationType = Literal[
    "shaded_region",
    "vertical_marker",
    "text_label",
    "fraction_label",
]


# -----------------------------
# Utility helpers
# -----------------------------

def new_id(prefix: str) -> str:
    """Create a short unique ID with a readable prefix"""
    return f"{prefix}_{uuid4().hex[:12]}"

def now_iso() -> str:
    """Return current time in ISO format for metadata"""
    return datetime.now().isoformat(timespec="seconds")

def _array_to_list(values: list[float] | np.ndarray) -> list[float]:
    """Convert list/array-like numeric values to JSON-safe floats"""
    return np.asarray(values, dtype=float).tolist()


# -----------------------------
# Source metadata
# -----------------------------

@dataclass
class DataSource:
    """
    Metadata describing where a dataset originally came from

    Save project will not include raw data, so source path is only for
    traceability. Loading project will not require original file.
    """

    path: str | None = None
    importer: str = "unknown"
    imported_at: str = field(default_factory=now_iso)
    file_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DataSource | None":
        if data is None:
            return None
        return cls(
            path=data.get("path"),
            importer=str(data.get("importer", "unknown")),
            imported_at=str(data.get("imported_at", now_iso())),
            file_hash=data.get("file_hash"),            
        )


# -----------------------------
# Plot settings
# -----------------------------

@dataclass
class FontSettings:
    title: int = 14
    axis_label: int = 12
    tick_label: int = 10
    legend: int = 10

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "FontSettings":
        if data is None:
            return cls()
        return cls(
            title=int(data.get("title", 14)),
            axis_label=int(data.get("axis_label", 12)),
            tick_label=int(data.get("tick_label", 10)),
            legend=int(data.get("legend", 10)),            
        )


@dataclass
class TickSettings:
    major_ticks: bool = True
    minor_ticks: bool = True
    tick_direction: str = "out"

    x_major_spacing: float | None = None
    x_minor_spacing: float | None = None
    y_major_spacing: float | None = None
    y_minor_spacing: float | None = None

    major_tick_length: float = 6.0
    minor_tick_length: float = 3.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "TickSettings":
        if data is None:
            return cls()

        return cls(
            major_ticks=bool(data.get("major_ticks", True)),
            minor_ticks=bool(data.get("minor_ticks", True)),
            tick_direction=str(data.get("tick_direction", "out")),

            x_major_spacing=data.get("x_major_spacing"),
            x_minor_spacing=data.get("x_minor_spacing"),
            y_major_spacing=data.get("y_major_spacing"),
            y_minor_spacing=data.get("y_minor_spacing"),

            major_tick_length=float(data.get("major_tick_length", 6.0)),
            minor_tick_length=float(data.get("minor_tick_length", 3.0)),
        )


@dataclass
class PlotSettings:
    """Global settings for the full plot."""

    title: str = ""
    x_label: str = "Volume (mL)"
    y_label: str = "Absorbance (mAU)"
    xlim: tuple[float, float] | None = None
    ylim: tuple[float, float] | None = None
    show_legend: bool = True
    legend_location: str = "best"
    legend_bbox_x: float = 0.5
    legend_bbox_y: float = 1.12
    legend_columns: int = 5
    figure_width: float = 8.0
    figure_height: float = 5.0
    font_sizes: FontSettings = field(default_factory=FontSettings)
    font_family: str = "Helvetica"
    tick_settings: TickSettings = field(default_factory=TickSettings)
    grid: bool = False
    clean_plot: bool = False
    plot_xkcd: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "xlim": list(self.xlim) if self.xlim is not None else None,
            "ylim": list(self.ylim) if self.ylim is not None else None,
            "show_legend": self.show_legend,
            "legend_location": self.legend_location,
            "legend_bbox_x": self.legend_bbox_x,
            "legend_bbox_y": self.legend_bbox_y,
            "legend_columns": self.legend_columns,
            "figure_width": self.figure_width,
            "figure_height": self.figure_height,
            "font_sizes": self.font_sizes.to_dict(),
            "font_family": self.font_family,
            "tick_settings": self.tick_settings.to_dict(),
            "grid": self.grid,
            "clean_plot": self.clean_plot,
            "plot_xkcd": self.plot_xkcd,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PlotSettings":
        if data is None:
            return cls()

        xlim = data.get("xlim")
        ylim = data.get("ylim")

        return cls(
            title=str(data.get("title", "")),
            x_label=str(data.get("x_label", "Volume (mL)")),
            y_label=str(data.get("y_label", "Absorbance (mAU)")),
            xlim=tuple(xlim) if xlim is not None else None,
            ylim=tuple(ylim) if ylim is not None else None,
            show_legend=bool(data.get("show_legend", True)),
            legend_location=str(data.get("legend_location", "best")),
            figure_width=float(data.get("figure_width", 8.0)),
            figure_height=float(data.get("figure_height", 5.0)),
            font_sizes=FontSettings.from_dict(data.get("font_sizes")),
            font_family=str(data.get("font_family", "Helvetica")),
            tick_settings=TickSettings.from_dict(data.get("tick_settings")),
            grid=bool(data.get("grid", False)),
            clean_plot=bool(data.get("clean_plot", False)),
            legend_bbox_x=float(data.get("legend_bbox_x", 0.5)),
            legend_bbox_y=float(data.get("legend_bbox_y", 1.12)),
            legend_columns=int(data.get("legend_columns", 5)),
            plot_xkcd=bool(data.get("plot_xkcd", False)),
        )
    

# -----------------------------
# Curves and datasets
# -----------------------------

@dataclass
class Curve:
    """
    One plottable curve from a chromatography dataset. E.g. UV 280 nm, UV 260 nm, conductivity etc.
    """

    name: str
    x: list[float] | np.ndarray
    y: list[float] | np.ndarray
    id: str = field(default_factory=lambda: new_id("curve"))
    x_label: str = "Volume"
    y_label: str = "Signal"
    x_unit: str | None = "mL"
    y_unit: str | None = None
    visible: bool = True
    style: CurveStyle = field(default_factory=CurveStyle)
    transform: CurveTransform = field(default_factory=CurveTransform)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.x = _array_to_list(self.x)
        self.y = _array_to_list(self.y)
        if len(self.x) != len(self.y):
            raise ValueError(
                f"Curve '{self.name}' has mismatched x/y lengths: "
                f"{len(self.x)} and {len(self.y)}"
            )

    @property
    def label(self) -> str:
        """Label used for legends. Currently the same as name."""
        return self.name

    def raw_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        """Return raw x/y data as NumPy arrays."""
        return np.asarray(self.x, dtype=float), np.asarray(self.y, dtype=float)

    def display_arrays(self) -> tuple[np.ndarray, np.ndarray]:
        """Return transformed x/y arrays for plotting."""
        x, y = self.raw_arrays()
        return self.transform.apply(x, y)

    def set_visible(self, visible: bool) -> None:
        self.visible = bool(visible)

    def reset_transform(self) -> None:
        self.transform.reset()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "x": _array_to_list(self.x),
            "y": _array_to_list(self.y),
            "x_label": self.x_label,
            "y_label": self.y_label,
            "x_unit": self.x_unit,
            "y_unit": self.y_unit,
            "visible": self.visible,
            "style": self.style.to_dict(),
            "transform": self.transform.to_dict(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Curve":
        return cls(
            id=str(data.get("id", new_id("curve"))),
            name=str(data.get("name", "Untitled curve")),
            x=data.get("x", []),
            y=data.get("y", []),
            x_label=str(data.get("x_label", "Volume")),
            y_label=str(data.get("y_label", "Signal")),
            x_unit=data.get("x_unit", "mL"),
            y_unit=data.get("y_unit"),
            visible=bool(data.get("visible", True)),
            style=CurveStyle.from_dict(data.get("style")),
            transform=CurveTransform.from_dict(data.get("transform")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class Dataset:
    """
    One imported chromatography run/rile containing one or more curves
    """

    name: str
    curves: list[Curve] = field(default_factory=list)
    id: str = field(default_factory=lambda: new_id("dataset"))
    source: DataSource | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_curve(self, curve: Curve) -> None:
        self.curves.append(curve)

    def remove_curve(self, curve_id: str) -> None:
        self.curves = [curve for curve in self.curves if curve.id != curve_id]

    def get_curve(self, curve_id: str) -> Curve | None:
        for curve in self.curves:
            if curve.id == curve_id:
                return curve
        return None

    def visible_curves(self) -> list[Curve]:
        return [curve for curve in self.curves if curve.visible]

    def assign_default_styles(self) -> None:
        """Assign deterministic default styles to all curves in this dataset."""
        for i, curve in enumerate(self.curves):
            curve.style = default_curve_style(i)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source.to_dict() if self.source is not None else None,
            "metadata": self.metadata,
            "curves": [curve.to_dict() for curve in self.curves],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Dataset":
        return cls(
            id=str(data.get("id", new_id("dataset"))),
            name=str(data.get("name", "Untitled dataset")),
            source=DataSource.from_dict(data.get("source")),
            metadata=dict(data.get("metadata", {})),
            curves=[Curve.from_dict(curve_data) for curve_data in data.get("curves", [])],
        )


# -----------------------------
# Annotations
# -----------------------------

@dataclass
class Annotation:
    """
    Generic annotation object
    """

    type: AnnotationType
    data: dict[str, Any]
    id: str = field(default_factory=lambda: new_id("annotation"))
    visible: bool = True
    style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "visible": self.visible,
            "style": self.style,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Annotation":
        return cls(
            id=str(data.get("id", new_id("annotation"))),
            type=data.get("type", "text_label"),
            visible=bool(data.get("visible", True)),
            style=dict(data.get("style", {})),
            data=dict(data.get("data", {})),
        )


# -----------------------------
# Project
# -----------------------------

@dataclass
class Project:
    """Complete saveable ChromaPlot project."""

    name: str = "Untitled"
    datasets: list[Dataset] = field(default_factory=list)
    plot_settings: PlotSettings = field(default_factory=PlotSettings)
    annotations: list[Annotation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: int = CURRENT_SCHEMA_VERSION

    def add_dataset(self, dataset: Dataset) -> None:
        self.datasets.append(dataset)

    def remove_dataset(self, dataset_id: str) -> None:
        self.datasets = [dataset for dataset in self.datasets if dataset.id != dataset_id]

    def get_dataset(self, dataset_id: str) -> Dataset | None:
        for dataset in self.datasets:
            if dataset.id == dataset_id:
                return dataset
        return None

    def get_curve(self, curve_id: str) -> Curve | None:
        for dataset in self.datasets:
            curve = dataset.get_curve(curve_id)
            if curve is not None:
                return curve
        return None

    def visible_curves(self) -> list[Curve]:
        curves: list[Curve] = []
        for dataset in self.datasets:
            curves.extend(dataset.visible_curves())
        return curves

    def add_annotation(self, annotation: Annotation) -> None:
        self.annotations.append(annotation)

    def remove_annotation(self, annotation_id: str) -> None:
        self.annotations = [ann for ann in self.annotations if ann.id != annotation_id]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "project": {
                "name": self.name,
                "metadata": self.metadata,
                "datasets": [dataset.to_dict() for dataset in self.datasets],
                "plot_settings": self.plot_settings.to_dict(),
                "annotations": [ann.to_dict() for ann in self.annotations],
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        schema_version = int(data.get("schema_version", CURRENT_SCHEMA_VERSION))
        project_data = data.get("project", data)

        return cls(
            schema_version=schema_version,
            name=str(project_data.get("name", "Untitled")),
            metadata=dict(project_data.get("metadata", {})),
            datasets=[
                Dataset.from_dict(dataset_data)
                for dataset_data in project_data.get("datasets", [])
            ],
            plot_settings=PlotSettings.from_dict(project_data.get("plot_settings")),
            annotations=[
                Annotation.from_dict(annotation_data)
                for annotation_data in project_data.get("annotations", [])
            ],
        )


def create_empty_project(name: str = "Untitled") -> Project:
    """Convenience factory for a new empty project."""
    return Project(name=name)
