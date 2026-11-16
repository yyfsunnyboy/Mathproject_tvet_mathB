"""Grade 0–15 percentage bar charts (one PNG per subject) for statistics.univariate_descriptive.

The charts are drawn from the same percentage vectors the domain grades, and every chart is checked after layout:
no text may be clipped by the image border, value labels may not overlap each other or any bar, and a missing CJK
glyph is an error instead of a silently blank box.
"""

from __future__ import annotations

import base64
import io
import math
import warnings
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from typing import Any

CJK_FONTS = ("Microsoft JhengHei", "Noto Sans TC", "Noto Sans CJK TC", "PingFang TC", "Microsoft YaHei")
# Near-square so that, in the student scratchpad's two-image grid, the chart keeps ~0.6–0.75 of its natural size.
FIG_SIZE_IN = (5.0, 4.8)
DPI = 125
Y_LABEL = "人數百分比（%）"
BAR_COLOR = "#f59e0b"
BAR_EDGE = "#b45309"


@lru_cache(maxsize=1)
def _cjk_font() -> str:
    from matplotlib import font_manager

    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in CJK_FONTS:
        if name in names:
            return name
    raise RuntimeError("cjk_font_unavailable")


def _two_decimals(p: Fraction) -> str:
    return format(Decimal(p.numerator) / Decimal(p.denominator), ".2f")


def chart_y_max(series: list[list[Fraction]]) -> int:
    top = max(max(s) for s in series)
    return int(math.ceil(float(top * Fraction(118, 100) + 1) / 5) * 5)


def _overlap(a, b, tol: float = 0.5) -> bool:
    return a.x0 < b.x1 - tol and b.x0 < a.x1 - tol and a.y0 < b.y1 - tol and b.y0 < a.y1 - tol


def _check_layout(fig, renderer, ax, texts, value_labels, bars) -> None:
    width, height = fig.bbox.width, fig.bbox.height
    for t in texts:
        box = t.get_window_extent(renderer)
        if box.x0 < 0 or box.y0 < 0 or box.x1 > width or box.y1 > height:
            raise ValueError(f"chart_text_clipped:{t.get_text()}")
    boxes = [t.get_window_extent(renderer) for t in value_labels]
    bar_boxes = [b.get_window_extent(renderer) for b in bars]
    title = ax.title.get_window_extent(renderer)
    plot = ax.get_window_extent(renderer)
    for i, box in enumerate(boxes):
        if _overlap(box, title) or box.y1 > plot.y1 + 0.5:
            raise ValueError(f"chart_label_above_plot:{i}")
        for j in range(i + 1, len(boxes)):
            if _overlap(box, boxes[j]):
                raise ValueError(f"chart_labels_overlap:{i}:{j}")
        for j, bar in enumerate(bar_boxes):
            if _overlap(box, bar):
                raise ValueError(f"chart_label_hits_bar:{i}:{j}")


@lru_cache(maxsize=64)
def _render_panel(subject: str, pcts: tuple[str, ...], y_max: int) -> tuple[str, tuple[tuple[float, float], ...], tuple[int, int]]:
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    values = [Fraction(p) for p in pcts]
    with matplotlib.rc_context({"font.family": [_cjk_font()], "axes.unicode_minus": False}), warnings.catch_warnings():
        warnings.simplefilter("error")
        fig = Figure(figsize=FIG_SIZE_IN, dpi=DPI, facecolor="white")
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        bars = ax.bar(range(len(values)), [float(v) for v in values], width=0.62, color=BAR_COLOR, edgecolor=BAR_EDGE, linewidth=0.6)
        pad = y_max * 0.012
        # 16 two-decimal labels only fit a readable size when set vertically above each bar
        labels = [ax.text(g, float(v) + pad, _two_decimals(v), ha="center", va="bottom", rotation=90, fontsize=10, color="#111827")
                  for g, v in enumerate(values)]
        ax.set_xlim(-0.6, len(values) - 0.4)
        ax.set_ylim(0, y_max)
        ax.set_xticks(range(len(values)))
        ax.set_xticklabels([str(g) for g in range(len(values))], fontsize=11)
        step = 5 if y_max <= 40 else 10
        ax.set_yticks(range(0, y_max + 1, step))
        ax.tick_params(axis="y", labelsize=10)
        ax.yaxis.grid(True, color="#e5e7eb", linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_xlabel(f"{subject}級分", fontsize=12)
        ax.set_ylabel(Y_LABEL, fontsize=12)
        ax.set_title(f"{subject}級分人數百分比分布圖", fontsize=13, fontweight="bold")
        fig.tight_layout(pad=0.6)
        canvas.draw()
        renderer = canvas.get_renderer()
        texts = [ax.title, ax.xaxis.label, ax.yaxis.label, *labels, *ax.get_xticklabels(), *ax.get_yticklabels()]
        _check_layout(fig, renderer, ax, texts, labels, bars)
        extents = [b.get_window_extent(renderer) for b in bars]
        geometry = tuple((round(e.height, 3), round((e.x0 + e.x1) / 2, 3)) for e in extents)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=DPI, metadata={"Software": None})
        size = (int(round(fig.bbox.width)), int(round(fig.bbox.height)))
    return base64.b64encode(buf.getvalue()).decode("ascii"), geometry, size


def render_grade_charts(series: dict[str, list[Fraction]]) -> list[dict[str, Any]]:
    """One bar chart per subject on a shared percentage axis, so the spreads can be compared by eye as well."""
    y_max = chart_y_max(list(series.values()))
    out = []
    for subject, values in series.items():
        png, geometry, size = _render_panel(subject, tuple(str(v) for v in values), y_max)
        out.append({
            "subject": subject, "title": f"{subject}級分人數百分比分布圖", "x_label": f"{subject}級分", "y_label": Y_LABEL,
            "grades": list(range(len(values))), "percent": [_two_decimals(v) for v in values], "y_max": y_max,
            "bar_heights_px": [h for h, _x in geometry], "bar_centers_px": [x for _h, x in geometry],
            "size_px": list(size), "png_base64": png,
        })
    return out
