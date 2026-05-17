from __future__ import annotations

from typing import Literal

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

from .models import Curve, Dataset, Project, PlotSettings


LegendLabelMode = Literal["auto", "curve", "dataset_curve"]


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

    for dataset, curve in visible_items:
        label = make_curve_label(project, dataset, curve, mode=label_mode)
        plot_curve(ax, curve, label=label)

    apply_plot_settings(
        ax,
        project.plot_settings,
        has_visible_curves=bool(visible_items),
        autoscale_limits=autoscale_visible_curves(project) if autoscale_if_no_limits else None,
    )

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
    font_family = settings.font_family

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
    if ticks.x_major_spacing:
        ax.xaxis.set_major_locator(MultipleLocator(ticks.x_major_spacing))

    if ticks.x_minor_spacing:
        ax.xaxis.set_minor_locator(MultipleLocator(ticks.x_minor_spacing))

    if ticks.y_major_spacing:
        ax.yaxis.set_major_locator(MultipleLocator(ticks.y_major_spacing))

    if ticks.y_minor_spacing:
        ax.yaxis.set_minor_locator(MultipleLocator(ticks.y_minor_spacing))

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
        tick_label.set_fontfamily(settings.font_family)

    ax.grid(settings.grid)

    if settings.clean_plot:
        apply_clean_plot_style(ax)

    if settings.show_legend and has_visible_curves:

        if settings.legend_location == "outside top":
            legend = ax.legend(
                loc="upper center",
                bbox_to_anchor=(settings.legend_bbox_x, settings.legend_bbox_y),
                fontsize=settings.font_sizes.legend,
                frameon=not settings.clean_plot,
                ncol=5,
                prop={"family": font_family},
            )

        else:
            legend = ax.legend(
                loc=settings.legend_location,
                fontsize=settings.font_sizes.legend,
                frameon=not settings.clean_plot,
                prop={"family": font_family},
            )
        if legend is not None:
            legend.set_draggable(False)



def apply_clean_plot_style(ax: Axes) -> None:
    """
    Apply a simple presentation/publication-style clean plot mode.

    This can be expanded later, but for now it removes the top/right spines and
    avoids a boxed-in look.
    """
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# -----------------------------------------------------------------------------
# Autoscaling
# -----------------------------------------------------------------------------

def autoscale_visible_curves(
    project: Project,
    *,
    x_padding_fraction: float = 0.02,
    y_padding_fraction: float = 0.05,
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

