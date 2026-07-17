from __future__ import annotations

from contextlib import nullcontext
from typing import Literal

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

from .models import Annotation, Curve, Dataset, Project, PlotSettings


LegendLabelMode = Literal["auto", "curve", "dataset", "dataset_curve"]


# -----------------------------------------------------------------------------
# Public plotting API
# -----------------------------------------------------------------------------

def plot_project(
    project: Project,
    ax: Axes | None = None,
    *,
    label_mode: LegendLabelMode = "auto",
    autoscale_if_no_limits: bool = True,
) -> tuple[Figure, Axes]:
    """
    Plot all visible curves in a ChromaPlot project.

    Parameters
    ----------
    project
        Project object containing datasets, curves, and plot settings.
    ax
        Optional matplotlib axis. If omitted, a new figure and axis are created.
    label_mode
        Controls how legend labels are generated:

        - "auto": use curve names for one dataset, dataset + curve for multiple datasets
        - "curve": use curve names only
        - "dataset_curve": always use dataset + curve

    autoscale_if_no_limits
        If True, calculate sensible limits from visible curves when xlim/ylim are
        not explicitly set in `project.plot_settings`.

    Returns
    -------
    fig, ax
        The matplotlib figure and axis.
    """
    fig, ax = _get_figure_and_axis(project.plot_settings, ax=ax)

    visible_items = list(iter_visible_curves(project))

    style_context = plt.xkcd() if project.plot_settings.plot_xkcd else nullcontext()

    with style_context:
        for dataset, curve in visible_items:
            label = make_curve_label(project, dataset, curve, mode=project.plot_settings.legend_label_mode)
            plot_curve(ax, curve, label=label)

        apply_plot_settings(
            ax,
            project.plot_settings,
            has_visible_curves=bool(visible_items),
            autoscale_limits=autoscale_visible_curves(project) if autoscale_if_no_limits else None,
        )

        plot_annotations(ax, project)

        for dataset in project.datasets:
            plot_dataset_fractions(ax, dataset)

    # fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.tight_layout()
    return fig, ax


def plot_curve(ax: Axes, curve: Curve, label: str | None = None) -> None:
    """
    Plot a single curve onto an existing matplotlib axis.

    The plotted data are the display/transformed data, not the raw imported
    values. Raw data remain stored unchanged in `curve.x` and `curve.y`.
    """
    x, y = curve.display_arrays()
    style = curve.style

    ax.plot(
        x,
        y,
        label=label or curve.name,
        color=style.color,
        linewidth=style.linewidth,
        linestyle=style.linestyle,
        alpha=style.alpha,
        marker=style.marker,
        markersize=style.markersize,
        zorder=style.zorder,
    )


def plot_dataset_fractions(ax: Axes, dataset: Dataset) -> None:
    settings = dataset.fraction_label_settings

    if not settings.visible or not dataset.fractions:
        return
    
    if settings.hide_when_dataset_hidden and not dataset.visible_curves():
        return

    ymin, ymax = ax.get_ylim()
    height = ymax - ymin
    line_top = ymin + height * settings.line_height_fraction
    label_y = ymin + height * (settings.line_height_fraction * settings.label_height_fraction)

    visible_fractions = [
        fraction for fraction in dataset.fractions
        if not (settings.hide_waste and fraction.kind == "waste")
    ]

    if settings.hide_first_fraction and visible_fractions:
        visible_fractions = visible_fractions[1:]

    for i, fraction in enumerate(visible_fractions, start=1):
        x_start = fraction.start_volume

        if fraction.end_volume is not None:
            x_label = (fraction.start_volume + fraction.end_volume) / 2
        elif i < len(visible_fractions):
            x_label = (fraction.start_volume + visible_fractions[i].start_volume) / 2
        else:
            x_label = fraction.start_volume

        x_boundary = x_start

        if settings.show_boundaries:
            ax.vlines(
                x_boundary,
                ymin,
                line_top,
                color=settings.line_color,
                linestyle=settings.line_style,
                linewidth=settings.line_width,
                alpha=settings.line_alpha,
                zorder=1,
            )

        if settings.show_labels:
            if settings.label_mode == "sequential":
                label = str(i)
            else:
                label = fraction.display_label or fraction.label

            ax.text(
                x_label,
                label_y,
                label,
                fontsize=settings.label_font_size,
                rotation=settings.label_rotation,
                ha="center",
                va="center",
                color=settings.label_color,
                alpha=settings.label_alpha,
                clip_on=True,
                zorder=2,
            )


# -----------------------------------------------------------------------------
# Iteration and labels
# -----------------------------------------------------------------------------

def iter_visible_curves(project: Project):
    """
    Yield `(dataset, curve)` pairs for all visible curves in plotting order.
    """
    for dataset in project.datasets:
        for curve in dataset.curves:
            if curve.visible:
                yield dataset, curve


def make_curve_label(
    project: Project,
    dataset: Dataset,
    curve: Curve,
    *,
    mode: LegendLabelMode = "auto",
) -> str:
    """
    Create a sensible legend label for a curve.

    For a single dataset, `UV` is usually enough. For multiple datasets, labels
    like `Run 1 — UV` avoid ambiguity.
    """
    if mode == "curve":
        return curve.name
    
    if mode == "dataset":
        return dataset.name

    if mode == "dataset_curve":
        return f"{dataset.name} — {curve.name}"

    if mode == "auto":
        if len(project.datasets) <= 1:
            return curve.name
        return f"{dataset.name} — {curve.name}"

    raise ValueError(f"Unknown label mode: {mode}")


# -----------------------------------------------------------------------------
# Plot settings
# -----------------------------------------------------------------------------

def apply_plot_settings(
    ax: Axes,
    settings: PlotSettings,
    *,
    has_visible_curves: bool = True,
    autoscale_limits: tuple[tuple[float, float], tuple[float, float]] | None = None,
) -> None:
    """
    Apply project-level plot settings to an axis.
    """
    font_family = "Comic Sans MS" if settings.plot_xkcd else settings.font_family

    ax.set_title(
        settings.title,
        fontsize=settings.font_sizes.title,
        fontfamily=font_family,
    )
    ax.set_xlabel(
        settings.x_label,
        fontsize=settings.font_sizes.axis_label,
        fontfamily=font_family,
    )
    ax.set_ylabel(
        settings.y_label,
        fontsize=settings.font_sizes.axis_label,
        fontfamily=font_family,
    )

    if settings.xlim is not None:
        ax.set_xlim(*settings.xlim)
    elif autoscale_limits is not None:
        ax.set_xlim(*autoscale_limits[0])

    if settings.ylim is not None:
        ax.set_ylim(*settings.ylim)
    elif autoscale_limits is not None:
        ax.set_ylim(*autoscale_limits[1])

    ticks = settings.tick_settings

    # Tick spacing
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    x_major_spacing = _safe_locator_spacing(
        ticks.x_major_spacing,
        xlim,
        MAX_MAJOR_TICKS,
    )

    x_minor_spacing = _safe_locator_spacing(
        ticks.x_minor_spacing,
        xlim,
        MAX_MINOR_TICKS,
    )

    y_major_spacing = _safe_locator_spacing(
        ticks.y_major_spacing,
        ylim,
        MAX_MAJOR_TICKS,
    )

    y_minor_spacing = _safe_locator_spacing(
        ticks.y_minor_spacing,
        ylim,
        MAX_MINOR_TICKS,
    )

    if x_major_spacing is not None:
        ax.xaxis.set_major_locator(
            MultipleLocator(x_major_spacing)
        )

    if x_minor_spacing is not None:
        ax.xaxis.set_minor_locator(
            MultipleLocator(x_minor_spacing)
        )

    if y_major_spacing is not None:
        ax.yaxis.set_major_locator(
            MultipleLocator(y_major_spacing)
        )

    if y_minor_spacing is not None:
        ax.yaxis.set_minor_locator(
            MultipleLocator(y_minor_spacing)
        )

    # Major ticks
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=settings.font_sizes.tick_label,
        direction=ticks.tick_direction,
        length=ticks.major_tick_length if ticks.major_ticks else 0,
    )

    # Minor ticks
    if ticks.minor_ticks:
        if not ticks.x_minor_spacing and not ticks.y_minor_spacing:
            ax.minorticks_on()

        ax.tick_params(
            axis="both",
            which="minor",
            direction=ticks.tick_direction,
            length=ticks.minor_tick_length,
        )
    else:
        ax.minorticks_off()

    # Font family for tick labels
    for tick_label in ax.get_xticklabels() + ax.get_yticklabels():
        tick_label.set_fontfamily(font_family)

    ax.grid(settings.grid)

    if settings.clean_plot:
        apply_clean_plot_style(ax)

    if settings.plot_xkcd:
        apply_xkcd_style(ax)

    if settings.show_legend and has_visible_curves:

        legend_prop = {
            "family": font_family,
            "size": settings.font_sizes.legend,
        }

        if settings.legend_location == "outside top":
            legend = ax.legend(
                loc="upper center",
                bbox_to_anchor=(settings.legend_bbox_x, settings.legend_bbox_y),
                frameon=not settings.clean_plot,
                ncol=settings.legend_columns,
                prop=legend_prop,
            )

        else:
            legend = ax.legend(
                loc=settings.legend_location,
                frameon=not settings.clean_plot,
                prop=legend_prop,
            )
        if legend is not None:
            legend.set_draggable(False)

MAX_MAJOR_TICKS = 50
MAX_MINOR_TICKS = 200

def _safe_locator_spacing(
    spacing: float | None,
    limits: tuple[float, float],
    maximum_ticks: int,
) -> float | None:
    if spacing is None or spacing <= 0:
        return None

    span = abs(float(limits[1]) - float(limits[0]))

    if span <= 0:
        return float(spacing)

    minimum_spacing = _nice_spacing_at_least(
        span / maximum_ticks
    )

    return max(float(spacing), minimum_spacing)

def _nice_spacing_at_least(value: float) -> float:
    if value <= 0:
        return 1.0

    exponent = math.floor(math.log10(value))
    magnitude = 10 ** exponent
    normalised = value / magnitude

    if normalised <= 1:
        nice_value = 1
    elif normalised <= 2:
        nice_value = 2
    elif normalised <= 5:
        nice_value = 5
    else:
        nice_value = 10

    return nice_value * magnitude

def apply_clean_plot_style(ax: Axes) -> None:
    """
    Apply a simple presentation/publication-style clean plot mode.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def apply_xkcd_style(ax: Axes) -> None:
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_sketch_params(scale=1.5, length=100, randomness=6)
    for line in ax.xaxis.get_ticklines() + ax.yaxis.get_ticklines():
        line.set_markeredgewidth(1.5)
        line.set_sketch_params(scale=5, length=100, randomness=10)

# -----------------------------------------------------------------------------
# Autoscaling
# -----------------------------------------------------------------------------

def autoscale_visible_curves(
    project: Project,
    *,
    x_padding_fraction: float = 0.01,
    y_padding_fraction: float = 0.03,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """
    Calculate axis limits from all visible curves.

    Returns
    -------
    ((xmin, xmax), (ymin, ymax)) or None
        Returns None when there are no visible curves with finite data.
    """
    x_chunks: list[np.ndarray] = []
    y_chunks: list[np.ndarray] = []

    for _, curve in iter_visible_curves(project):
        x, y = curve.display_arrays()
        mask = np.isfinite(x) & np.isfinite(y)
        if np.any(mask):
            x_chunks.append(x[mask])
            y_chunks.append(y[mask])

    if not x_chunks or not y_chunks:
        return None

    x_all = np.concatenate(x_chunks)
    y_all = np.concatenate(y_chunks)

    xmin, xmax = float(np.min(x_all)), float(np.max(x_all))
    ymin, ymax = float(np.min(y_all)), float(np.max(y_all))

    xmin, xmax = _pad_limits(xmin, xmax, x_padding_fraction)
    ymin, ymax = _pad_limits(ymin, ymax, y_padding_fraction)

    return (xmin, xmax), (ymin, ymax)


def _pad_limits(vmin: float, vmax: float, padding_fraction: float) -> tuple[float, float]:
    """Pad numeric limits by a fraction of their span."""
    if not np.isfinite(vmin) or not np.isfinite(vmax):
        return 0.0, 1.0

    if vmin == vmax:
        pad = abs(vmin) * padding_fraction
        if pad == 0:
            pad = 1.0
        return vmin - pad, vmax + pad

    span = vmax - vmin
    pad = span * padding_fraction
    return vmin - pad, vmax + pad


# -----------------------------------------------------------------------------
# Figure/axis helpers
# -----------------------------------------------------------------------------

def _get_figure_and_axis(settings: PlotSettings, ax: Axes | None = None) -> tuple[Figure, Axes]:
    """Return `(fig, ax)`, creating a new figure if needed."""
    if ax is not None:
        return ax.figure, ax

    fig, ax = plt.subplots(figsize=(settings.figure_width, settings.figure_height))
    return fig, ax


# -----------------------------------------------------------------------------
# Annotations
# -----------------------------------------------------------------------------

def plot_annotations(ax: Axes, project: Project) -> None:
    for annotation in project.annotations:
        if not annotation.visible:
            continue

        if annotation.type == "shaded_region":
            plot_shaded_region(ax, annotation, project)

def plot_shaded_region(
    ax: Axes,
    annotation: Annotation,
    project: Project,
) -> None:
    data = annotation.data
    style = annotation.style

    curve_id = data.get("curve_id")
    curve = project.get_curve(curve_id)

    if curve is None:
        return

    try:
        x_start = float(data.get("x_start"))
        x_end = float(data.get("x_end"))
    except (TypeError, ValueError):
        return

    xmin, xmax = sorted((x_start, x_end))

    x, y = curve.display_arrays()

    mask = (x >= xmin) & (x <= xmax)

    if not np.any(mask):
        return

    ymin, ymax = ax.get_ylim()

    ax.fill_between(
        x[mask],
        y[mask],
        y2=ymin,
        color=style.get("color", curve.style.color),
        alpha=float(style.get("alpha", 0.25)),
        zorder=0,
    )