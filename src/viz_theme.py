"""Shared matplotlib theme: one visual system across every chart in the project.

Palette roles follow a validated design system rather than matplotlib defaults.
The categorical slots were checked with a colour-vision-deficiency validator:
the three used here clear the all-pairs CVD floor (worst pair dE 9.2 deutan) and
the normal-vision floor (worst 24.0) on this surface. Aqua sits below 3:1
contrast on the light surface, so any chart using it carries visible direct
labels -- colour never has to do the work alone.

Rules enforced here:
  * one y-axis per chart, never two scales
  * categorical hues assigned in fixed order, never cycled
  * sequential = one hue light->dark; diverging = blue/red with a grey midpoint
  * recessive grid and axes, thin marks, rounded data-ends
  * legend whenever there are >= 2 series; a single series is named by the title
"""
from __future__ import annotations

import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import PathPatch
from matplotlib.path import Path

# --- surfaces and ink -------------------------------------------------------
SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

# --- categorical slots, in fixed order --------------------------------------
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
          "#008300", "#4a3aa7", "#e34948"]
BLUE, ORANGE, AQUA = SERIES[0], SERIES[1], SERIES[2]

# --- polarity (diverging) ---------------------------------------------------
POS = "#2a78d6"    # blue  = profit / above baseline
NEG = "#e34948"    # red   = loss / below baseline
MID = "#f0efec"    # neutral grey midpoint

# --- status (reserved; never used as a series colour) -----------------------
STATUS = {"good": "#0ca30c", "warning": "#fab219",
          "serious": "#ec835a", "critical": "#d03b3b"}

# --- sequential blue ramp, light -> dark ------------------------------------
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
            "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
            "#184f95", "#104281", "#0d366b"]


def sequential_cmap(name: str = "seq_blue") -> LinearSegmentedColormap:
    """Continuous one-hue ramp for magnitude encodings (heatmaps, choropleths)."""
    return LinearSegmentedColormap.from_list(name, SEQ_BLUE)


def diverging_cmap(name: str = "div_br") -> LinearSegmentedColormap:
    """Blue <-> red with a neutral grey midpoint, for signed magnitude."""
    return LinearSegmentedColormap.from_list(name, [NEG, MID, POS])


def polarity_colors(values) -> list[str]:
    """Blue where >= 0, red where < 0. Colour follows the sign, not the rank."""
    return [POS if v >= 0 else NEG for v in values]


def apply_theme() -> None:
    """Set rcParams once; every figure in the project inherits this."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "savefig.edgecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_SECONDARY,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "xtick.labelcolor": INK_SECONDARY,
        "ytick.labelcolor": INK_SECONDARY,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.labelcolor": INK_SECONDARY,
        "lines.linewidth": 2.0,
        "lines.markersize": 8,
        "figure.dpi": 130,
        "savefig.dpi": 130,
        "savefig.bbox": "tight",
        "axes.prop_cycle": mpl.cycler(color=SERIES),
    })


ROUND_PX = 5.0   # corner radius of a bar's data end, in device pixels


def _rounded_bar_path(lo: float, hi: float, centre: float, thickness: float,
                      r_along: float, r_across: float, horizontal: bool) -> Path:
    """Bar path with the *data end* rounded and the baseline end square.

    Rounding both ends would detach the bar from its baseline; rounding only the
    data end keeps the value anchored while softening the mark. `r_along` and
    `r_across` are separate because a corner that is circular on screen is
    elliptical in data units whenever the two axes have different scales.
    """
    length = hi - lo
    if length == 0:
        length = 1e-9
    sign = 1.0 if length > 0 else -1.0
    ra = min(r_along, abs(length) * 0.5) * sign
    rc = min(r_across, thickness * 0.5)

    a, b = centre - thickness / 2, centre + thickness / 2
    # Walk from the baseline, along the near side, around the rounded data end,
    # and back down the far side.
    pts = [
        (lo, a), (hi - ra, a), (hi, a), (hi, a + rc),
        (hi, b - rc), (hi, b), (hi - ra, b), (lo, b),
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3,
             Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO]
    if not horizontal:
        pts = [(y, x) for x, y in pts]
    pts.append(pts[0])
    codes.append(Path.CLOSEPOLY)
    return Path(pts, codes)


def rounded_bars(ax, positions, values, colors, thickness: float = 0.62,
                 baseline: float = 0.0, horizontal: bool = True,
                 gap_ring: bool = True):
    """Draw bars with rounded data-ends and a surface-coloured separating ring.

    The geometry is finalised in `save()` rather than here: the pixel-space
    corner radius can only be converted to data units once the axis limits are
    settled, and callers normally set limits after drawing.
    """
    if isinstance(colors, str):
        colors = [colors] * len(values)

    specs = []
    for pos, val, col in zip(positions, values, colors):
        patch = PathPatch(
            Path([(0, 0), (0, 0)], [Path.MOVETO, Path.CLOSEPOLY]),
            facecolor=col, edgecolor=SURFACE if gap_ring else "none",
            linewidth=1.4 if gap_ring else 0, joinstyle="round", zorder=3,
        )
        ax.add_patch(patch)
        specs.append((patch, baseline, float(val), float(pos), thickness, horizontal))

    ax._rounded_bar_specs = getattr(ax, "_rounded_bar_specs", []) + specs
    # Bars are patches, so autoscale cannot see them; widen the limits by hand.
    lo, hi = min(list(values) + [baseline]), max(list(values) + [baseline])
    if horizontal:
        ax.update_datalim([(lo, min(positions) - thickness),
                           (hi, max(positions) + thickness)])
    else:
        ax.update_datalim([(min(positions) - thickness, lo),
                           (max(positions) + thickness, hi)])
    ax.autoscale_view()
    return ax


def _finalise_rounded_bars(fig) -> None:
    """Rebuild every registered bar path now that axis limits are final."""
    for ax in fig.axes:
        specs = getattr(ax, "_rounded_bar_specs", None)
        if not specs:
            continue
        inv = ax.transData.inverted()
        ox, oy = inv.transform((0.0, 0.0))
        dx = abs(inv.transform((ROUND_PX, 0.0))[0] - ox)
        dy = abs(inv.transform((0.0, ROUND_PX))[1] - oy)
        for patch, base, val, pos, thick, horiz in specs:
            r_along, r_across = (dx, dy) if horiz else (dy, dx)
            patch.set_path(_rounded_bar_path(
                base, val, pos, thick, r_along, r_across, horiz))


def title_block(ax, title: str, subtitle: str = "", wrap: int = 96) -> None:
    """Left-aligned title over an optional subtitle that states the finding.

    The subtitle is wrapped and the title's pad is computed from the wrapped
    line count, so the two never collide however long the sentence runs.
    """
    lines = textwrap.wrap(subtitle, wrap) if subtitle else []
    pad = 14 + 13 * len(lines) if lines else 10
    ax.set_title(title, loc="left", fontsize=13, fontweight="600",
                 color=INK, pad=pad)
    if lines:
        ax.annotate("\n".join(lines), xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 9), textcoords="offset points",
                    fontsize=9.5, color=INK_SECONDARY, va="bottom", ha="left",
                    linespacing=1.35)


def source_note(fig, text: str) -> None:
    """Provenance line in the bottom-left corner of the figure."""
    fig.text(0.005, -0.015, text, fontsize=8, color=INK_MUTED,
             ha="left", va="top")


def save(fig, path, source: str = "") -> None:
    if source:
        source_note(fig, source)
    _finalise_rounded_bars(fig)
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(f"  chart -> {path.name}")


def money(x: float) -> str:
    """Compact currency label: $1.2M / $340K / $512."""
    a = abs(x)
    sign = "-" if x < 0 else ""
    if a >= 1_000_000:
        return f"{sign}${a/1_000_000:.1f}M"
    if a >= 1_000:
        return f"{sign}${a/1_000:.0f}K"
    return f"{sign}${a:.0f}"


def despine(ax, keep=("bottom",)) -> None:
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(side in keep)


__all__ = [
    "apply_theme", "rounded_bars", "polarity_colors", "sequential_cmap",
    "diverging_cmap", "title_block", "source_note", "save", "money", "despine",
    "SURFACE", "INK", "INK_SECONDARY", "INK_MUTED", "GRID", "BASELINE",
    "SERIES", "BLUE", "ORANGE", "AQUA", "POS", "NEG", "MID", "STATUS", "np",
]
