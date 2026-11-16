"""Grade 0–15 percentage bar charts (one PNG per subject) for statistics.univariate_descriptive.

The charts are drawn from the same percentage vectors the domain grades, and every chart is checked after layout:
no text may be clipped by the image border, value labels may not overlap each other or any bar, every character must
exist in the CJK font file (checked against its cmap, never by turning warnings into errors), every text artist must
use that file, and every bar must be present in the rendered pixels that are shipped.

Thread safety (waitress serves requests from a thread pool): only per-call Figure / FigureCanvasAgg objects are used
(no pyplot), fonts are passed per text artist (rcParams are never changed) and the process-wide ``warnings`` filters
are never touched. Matplotlib caches FT2Font objects per thread id, so no lock is needed.
"""

from __future__ import annotations

import base64
import io
import math
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from typing import Any

CJK_FONTS = ("Microsoft JhengHei", "Noto Sans TC", "Noto Sans CJK TC", "PingFang TC", "Microsoft YaHei")
# Landscape so that both student scratchpad grids are width-bound: two columns (desktop, cell ≈ 345 px wide) and
# stacked rows on narrow screens (430 px: cell ≈ 352 × 218 px), i.e. the chart shows at ≈ 0.62 of its pixel size.
FIG_SIZE_IN = (4.48, 2.72)
DPI = 125
VALUE_PT = 10.5
TICK_PT = 11
AXIS_PT = 11
TITLE_PT = 12.5
Y_LABEL = "人數百分比（%）"
BAR_COLOR = "#f59e0b"
BAR_EDGE = "#b45309"
_BAR_RGB = ((0xF5, 0x9E, 0x0B), (0xB4, 0x53, 0x09))


@lru_cache(maxsize=1)
def _cjk_font() -> tuple[str, str]:
    """(regular, bold) font file paths of the first installed CJK family."""
    from matplotlib import font_manager

    names = {f.name for f in font_manager.fontManager.ttflist}
    for name in CJK_FONTS:
        if name in names:
            regular = font_manager.findfont(font_manager.FontProperties(family=name), fallback_to_default=False)
            bold = font_manager.findfont(font_manager.FontProperties(family=name, weight="bold"), fallback_to_default=False)
            return regular, bold
    raise RuntimeError("cjk_font_unavailable")


@lru_cache(maxsize=4)
def _charmap(path: str) -> frozenset[int]:
    from matplotlib.ft2font import FT2Font

    return frozenset(FT2Font(path).get_charmap())


def _require_glyphs(path: str, texts: list[str]) -> None:
    covered = _charmap(path)
    missing = sorted({ch for text in texts for ch in text if not ch.isspace() and ord(ch) not in covered})
    if missing:
        raise ValueError(f"chart_glyph_missing:{''.join(missing)}")


def _font(path: str, size: float):
    from matplotlib.font_manager import FontProperties

    return FontProperties(fname=path, size=size)


def _two_decimals(p: Fraction) -> str:
    return format(Decimal(p.numerator) / Decimal(p.denominator), ".2f")


def chart_y_max(series: list[list[Fraction]]) -> int:
    # headroom for a vertical two-decimal label above the tallest bar
    top = max(max(s) for s in series)
    return int(math.ceil(float(top * Fraction(132, 100) + 1) / 5) * 5)


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


def _check_fonts(fig, files: tuple[str, str]) -> None:
    from matplotlib.text import Text

    for t in fig.findobj(Text):
        if t.get_text().strip() and t.get_fontproperties().get_file() not in files:
            raise ValueError(f"chart_font_fallback:{t.get_text()}")


def _check_pixels(rgb, extents, height: int) -> None:
    """Every bar of at least 1 px must be painted in the bar colours in the shipped pixels."""
    for i, e in enumerate(extents):
        if e.height < 1:
            continue
        col = int(round((e.x0 + e.x1) / 2))
        top, bottom = int(math.floor(height - e.y1)), int(math.ceil(height - e.y0))
        if e.height > 4:
            top, bottom = top + 1, bottom - 1
        painted = sum(1 for r, g, b in rgb[top:bottom, col].tolist()
                      if any(abs(r - c[0]) + abs(g - c[1]) + abs(b - c[2]) < 60 for c in _BAR_RGB))
        if painted < (0.8 * (bottom - top) if e.height > 4 else 1):
            raise ValueError(f"chart_bar_not_rendered:{i}")


@lru_cache(maxsize=64)
def _render_panel(subject: str, pcts: tuple[str, ...], y_max: int) -> tuple[str, tuple[tuple[float, float], ...], tuple[int, int]]:
    import numpy as np
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from PIL import Image

    regular, bold = _cjk_font()
    values = [Fraction(p) for p in pcts]
    value_texts = [_two_decimals(v) for v in values]
    title, x_label = f"{subject}級分人數百分比分布圖", f"{subject}級分"
    step = 5 if y_max <= 40 else 10
    y_ticks = list(range(0, y_max + 1, step))
    _require_glyphs(regular, [x_label, Y_LABEL, *value_texts, *map(str, range(len(values))), *map(str, y_ticks)])
    _require_glyphs(bold, [title])

    fig = Figure(figsize=FIG_SIZE_IN, dpi=DPI, facecolor="white")
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    bars = ax.bar(range(len(values)), [float(v) for v in values], width=0.62, color=BAR_COLOR, edgecolor=BAR_EDGE, linewidth=0.6)
    pad = y_max * 0.012
    # 16 two-decimal labels only fit a readable size when set vertically above each bar
    labels = [ax.text(g, float(v) + pad, text, ha="center", va="bottom", rotation=90, color="#111827",
                      fontproperties=_font(regular, VALUE_PT))
              for g, (v, text) in enumerate(zip(values, value_texts))]
    ax.set_xlim(-0.6, len(values) - 0.4)
    ax.set_ylim(0, y_max)
    ax.set_xticks(range(len(values)), [str(g) for g in range(len(values))], fontproperties=_font(regular, TICK_PT))
    ax.set_yticks(y_ticks, [str(t) for t in y_ticks], fontproperties=_font(regular, VALUE_PT))
    ax.tick_params(axis="both", length=3, pad=2)
    ax.yaxis.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel(x_label, fontproperties=_font(regular, AXIS_PT), labelpad=1)
    ax.set_ylabel(Y_LABEL, fontproperties=_font(regular, AXIS_PT), labelpad=2)
    ax.set_title(title, fontproperties=_font(bold, TITLE_PT), pad=4)
    fig.tight_layout(pad=0.4)
    canvas.draw()
    renderer = canvas.get_renderer()
    texts = [ax.title, ax.xaxis.label, ax.yaxis.label, *labels, *ax.get_xticklabels(), *ax.get_yticklabels()]
    _check_layout(fig, renderer, ax, texts, labels, bars)
    _check_fonts(fig, (regular, bold))
    extents = [b.get_window_extent(renderer) for b in bars]
    rgb = np.asarray(canvas.buffer_rgba())[:, :, :3].copy()
    _check_pixels(rgb, extents, rgb.shape[0])
    geometry = tuple((round(e.height, 3), round((e.x0 + e.x1) / 2, 3)) for e in extents)
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, format="PNG", optimize=True)
    size = (rgb.shape[1], rgb.shape[0])
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
