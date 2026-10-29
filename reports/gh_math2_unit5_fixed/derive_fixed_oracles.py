"""Independent oracle for Unit 5 進階題12 (semicircle, A1-A4 on the diameter, B1-B6 on the arc).

The 10 points are read from the authoritative PDF vectors (page 16), labelled by position, and every pair / triple is enumerated with an
exact collinearity test on the PDF coordinates.  The counts are cross-checked against the closed forms C(10,2)-C(4,2)+1 and C(10,3)-C(4,3).
Also records the figure's vector bounds used for the fixed crop.

    python reports/gh_math2_unit5_fixed/derive_fixed_oracles.py
"""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
import fitz  # noqa: E402

from core.textbook_pdf_visual import build_page_index, union_bbox  # noqa: E402

PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/e24c72f89309_單元05-組合.pdf"
PDF_SHA = "e24c72f893099354886c288daef25eab59cd315facc778f7ffa96d4e242ec166"
PAGE = 16
SEARCH = [420.0, 580.0, 530.0, 660.0]  # page-16 area right of the stem of 進階題12; every ink object inside is the figure


def inside(outer, b, tol=0.5):
    return b[0] >= outer[0] - tol and b[1] >= outer[1] - tol and b[2] <= outer[2] + tol and b[3] <= outer[3] + tol


def main():
    assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA
    with fitz.open(str(PDF)) as doc:
        page = build_page_index(doc)[PAGE - 1]
    ink = [d for d in page["drawings"] + page["small_drawings"] if inside(SEARCH, d["bbox"])]
    arc = [d for d in ink if d["area"] > 1000]
    assert len(arc) == 1, "exactly one arc+diameter path"
    ax0, ay0, ax1, ay1 = arc[0]["bbox"]
    # Dots are the ~5.8x4.5pt filled paths (area ~26); label glyphs are larger letters or thin subscripts.
    dots = [d for d in ink if 20 <= d["area"] <= 30 and 5 <= d["bbox"][2] - d["bbox"][0] <= 7]
    centres = [((d["bbox"][0] + d["bbox"][2]) / 2, (d["bbox"][1] + d["bbox"][3]) / 2) for d in dots]
    assert len(centres) == 10, len(centres)
    diameter_y = ay1
    on_diameter = sorted([c for c in centres if abs(c[1] - diameter_y) <= 3.0])
    on_arc = [c for c in centres if abs(c[1] - diameter_y) > 3.0]
    assert len(on_diameter) == 4 and len(on_arc) == 6
    cx, cy, radius = (ax0 + ax1) / 2, diameter_y, (ax1 - ax0) / 2
    arc_residual = max(abs(math.hypot(x - cx, y - cy) - radius) for x, y in on_arc)
    assert arc_residual < 2.5, arc_residual
    assert all(ax0 < x < ax1 for x, _ in on_diameter), "A points are interior to the diameter"
    on_arc.sort(key=lambda p: -math.atan2(cy - p[1], p[0] - cx))  # B1 at the left end, counter-clockwise order reversed
    points = {f"A{i + 1}": p for i, p in enumerate(on_diameter)} | {f"B{i + 1}": p for i, p in enumerate(on_arc)}

    def area2(p, q, r):
        return abs((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]))

    names = sorted(points)
    tol = 1.5 * 10  # twice-area tolerance (pt^2) for "collinear"; reported below against the smallest non-collinear triple
    triples = list(itertools.combinations(names, 3))
    collinear = [t for t in triples if area2(*(points[n] for n in t)) <= tol]
    non_collinear_min = min(area2(*(points[n] for n in t)) for t in triples if t not in collinear)
    lines = set()
    for a, b in itertools.combinations(names, 2):
        members = frozenset([a, b] + [c for c in names if c not in (a, b) and area2(points[a], points[b], points[c]) <= tol])
        lines.add(members)
    n_lines, n_triangles = len(lines), len(triples) - len(collinear)
    assert n_lines == math.comb(10, 2) - math.comb(4, 2) + 1 == 40
    assert n_triangles == math.comb(10, 3) - math.comb(4, 3) == 116
    assert sorted(collinear) == sorted(itertools.combinations(["A1", "A2", "A3", "A4"], 3))

    figure_bounds = union_bbox([d["bbox"] for d in ink])
    choices = [{"label": "①", "text": "24"}, {"label": "②", "text": "36"}, {"label": "③", "text": "40"},
               {"label": "④", "text": "45"}, {"label": "⑤", "text": "48"}]
    oracle = {
        "anchor_id": "general_2_section_advanced_exercise_012_037",
        "method": "PDF vector dots (page 16) labelled by position; all 45 pairs / 120 triples enumerated; closed forms cross-checked",
        "pdf_sha256": PDF_SHA, "page": PAGE,
        "figure_vector_bounds": [round(v, 1) for v in figure_bounds],
        "figure_ink_objects": len(ink),
        "points_pt": {k: [round(v[0], 2), round(v[1], 2)] for k, v in points.items()},
        "arc_radius_pt": round(radius, 2), "arc_max_residual_pt": round(arc_residual, 2),
        "collinear_triples": [list(t) for t in collinear], "collinear_tolerance_twice_area_pt2": tol,
        "smallest_non_collinear_twice_area_pt2": round(non_collinear_min, 1),
        "part_1": {"lines": n_lines, "closed_form": "C(10,2)-C(4,2)+1 = 45-6+1 = 40", "choice": "③", "choices": choices},
        "part_2": {"triangles": n_triangles, "closed_form": "C(10,3)-C(4,3) = 120-4 = 116"},
        "script": "reports/gh_math2_unit5_fixed/derive_fixed_oracles.py",
    }
    (HERE / "fixed_oracles.json").write_text(json.dumps(oracle, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: oracle[k] for k in ("figure_vector_bounds", "figure_ink_objects", "arc_max_residual_pt",
                                             "smallest_non_collinear_twice_area_pt2", "part_1", "part_2")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
