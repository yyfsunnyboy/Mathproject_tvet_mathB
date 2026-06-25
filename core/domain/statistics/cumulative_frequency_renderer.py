"""Deterministic cumulative-frequency graph and table renderer (Agg backend)."""

from __future__ import annotations

import base64
import io
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _normalize_direction(direction: str) -> str:
    key = str(direction or "").strip().lower()
    if key in {"below", "less_than", "以下"}:
        return "less_than"
    if key in {"above", "greater_than", "以上"}:
        return "greater_than"
    raise ValueError(f"unsupported_cumulative_direction:{direction}")


def _extract_xy(point: dict[str, Any]) -> tuple[float, int]:
    x_raw = point.get("x", point.get("class_bound"))
    y_raw = point.get("y", point.get("cumulative_count"))
    if x_raw is None or y_raw is None:
        raise ValueError("graph_point_missing_xy")
    return float(x_raw), int(y_raw)


def encode_png_base64(png_bytes: bytes) -> str:
    """Encode raw PNG bytes as ASCII base64 (no data-URL prefix)."""
    return base64.b64encode(png_bytes).decode("ascii")


def render_cumulative_frequency_graph(
    *,
    data_points: list[dict[str, Any]],
    cumulative_direction: str = "less_than",
    title: str = "累積次數分配折線圖",
    x_label: str = "分數",
    y_label: str | None = None,
    x_ticks: list[float] | None = None,
    y_ticks: list[int] | None = None,
    show_point_labels: bool = True,
    figsize: tuple[float, float] = (6.5, 4.0),
    dpi: int = 120,
    seed: int | None = None,
) -> dict[str, Any]:
    """Render a cumulative-frequency polyline chart and return PNG base64 + visual_spec."""
    if seed is not None:
        # Fixed styling seed for reproducible figure metadata only.
        import random

        random.seed(seed)

    direction = _normalize_direction(cumulative_direction)
    if not data_points:
        raise ValueError("data_points_required")

    xs: list[float] = []
    ys: list[int] = []
    for point in data_points:
        x_val, y_val = _extract_xy(point)
        xs.append(x_val)
        ys.append(y_val)

    dir_label = "以下累積次數" if direction == "less_than" else "以上累積次數"
    y_axis_label = y_label or f"{dir_label}（人）"

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    try:
        ax.plot(xs, ys, marker="o", color="#2563eb", linewidth=2, markersize=6)
        if show_point_labels:
            for x_val, y_val in zip(xs, ys, strict=True):
                ax.annotate(
                    str(y_val),
                    (x_val, y_val),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=9,
                )

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_axis_label, fontsize=10)
        if x_ticks is not None:
            ax.set_xticks(x_ticks)
        else:
            ax.set_xticks(xs)
        if y_ticks is not None:
            ax.set_yticks(y_ticks)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        png_bytes = buf.getvalue()
        image_base64 = encode_png_base64(png_bytes)

        visual_spec: dict[str, Any] = {
            "type": "cumulative_frequency_graph",
            "cumulative_direction": direction,
            "title": title,
            "x_label": x_label,
            "y_label": y_axis_label,
            "x_axis_semantics": "upper_class_boundary",
            "y_axis_semantics": "cumulative_frequency",
            "data_points": [{"x": x_val, "y": y_val} for x_val, y_val in zip(xs, ys, strict=True)],
            "x_ticks": list(x_ticks) if x_ticks is not None else xs,
            "y_ticks": list(y_ticks) if y_ticks is not None else sorted(set(ys)),
        }
        return {
            "image_base64": image_base64,
            "visual_spec": visual_spec,
            "png_byte_length": len(png_bytes),
        }
    finally:
        plt.close(fig)


def render_cumulative_frequency_table(
    *,
    headers: list[str],
    rows: list[list[Any]],
    blank_cells: list[tuple[int, int]] | None = None,
    title: str = "累積次數分配表",
) -> dict[str, Any]:
    """Build HTML table_data for bidirectional cumulative-frequency tables."""
    blank_set = {tuple(cell) for cell in (blank_cells or [])}
    display_rows: list[list[Any]] = []
    for row_idx, row in enumerate(rows):
        display_row: list[Any] = []
        for col_idx, cell in enumerate(row):
            if (row_idx, col_idx) in blank_set:
                display_row.append("")
            else:
                display_row.append(cell)
        display_rows.append(display_row)

    html_parts = [
        f'<table class="cumulative-frequency-table"><caption>{title}</caption><thead><tr>'
    ]
    for header in headers:
        html_parts.append(f"<th>{header}</th>")
    html_parts.append("</tr></thead><tbody>")
    for row in display_rows:
        html_parts.append("<tr>")
        for cell in row:
            html_parts.append(f"<td>{cell}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody></table>")
    html = "".join(html_parts)

    return {
        "table_data": {
            "type": "cumulative_frequency_table",
            "title": title,
            "headers": headers,
            "rows": rows,
            "display_rows": display_rows,
            "blank_cells": [{"row": r, "col": c} for r, c in blank_set],
            "html": html,
        },
        "visual_spec": {
            "type": "cumulative_frequency_table",
            "title": title,
            "headers": headers,
            "rows": display_rows,
        },
    }
