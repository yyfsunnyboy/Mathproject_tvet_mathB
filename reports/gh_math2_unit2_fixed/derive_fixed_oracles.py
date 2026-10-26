"""Independent derivation of the reference answers for the four Unit 2 rows that have no dynamic generator (read-only).

* 12719 / 12727: the areas are measured from the VECTOR drawing of the paired PDF itself (the paths of the printed figure), scaled by the
  length the stem fixes (square side 2 / AB = 1).  Nothing is read off by eye and no candidate value is assumed.
* 12731 / 12735: the induction step is verified symbolically (sympy) and numerically; the base case and the first terms are enumerated.

Prints the evidence and writes ``fixed_oracles.json`` next to this file.
"""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import fitz
import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/9d32c092de77_單元02-級數.pdf"
PDF_SHA = "9d32c092de7712d26cb4d4076da4c98340c66368c00ecd9094d017b8ced0c964"
assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA
doc = fitz.open(PDF)


def polygons(page: int, window: tuple, filled: bool | None) -> list[list[tuple[float, float]]]:
    """Closed three-segment paths (triangles) of the page inside ``window``."""
    out = []
    rect = fitz.Rect(*window)
    for dr in doc[page - 1].get_drawings():
        r = dr["rect"]
        if not rect.contains(r) or r.width > 120:
            continue
        if filled is True and dr.get("fill") is None:
            continue
        if filled is False and dr.get("fill") is not None:
            continue
        pts = []
        for it in dr["items"]:
            if it[0] == "l":
                pts += [(round(it[1].x, 2), round(it[1].y, 2)), (round(it[2].x, 2), round(it[2].y, 2))]
        uniq = []
        for p in pts:
            if not any(abs(p[0] - q[0]) < 0.05 and abs(p[1] - q[1]) < 0.05 for q in uniq):
                uniq.append(p)
        if len(uniq) == 3 and len(dr["items"]) == 3:
            out.append(uniq)
    return out


def area(tri):
    (x1, y1), (x2, y2), (x3, y3) = tri
    return abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2


def is_isosceles_right(tri, tol=0.03):
    d = sorted(((tri[i][0] - tri[j][0]) ** 2 + (tri[i][1] - tri[j][1]) ** 2) for i, j in ((0, 1), (1, 2), (0, 2)))
    return abs(d[0] - d[1]) / d[1] < tol and abs(d[2] - 2 * d[1]) / d[2] < tol


def rationalise(x: float) -> Fraction:
    """Snap a measured area ratio (PDF coordinates are printed to 0.01) to the simplest dyadic fraction k / 2^m that fits within 1.5 %.

    Isosceles right triangles built on each other's legs / hypotenuses have areas that differ by powers of 2, so a dyadic value is the
    expected shape; the fit tolerance guards against accepting a wrong snap.
    """
    for m in range(0, 11):
        k = round(x * 2 ** m)
        if k > 0 and abs(k / 2 ** m - x) <= 0.015 * x:
            return Fraction(k, 2 ** m)
    raise AssertionError(f"no dyadic fit for {x}")


result = {"pdf_sha256": PDF_SHA}

# --- 12719: square ABCD (side 2), five filled black isosceles right triangles ---------------------------------------------------------
window = (422, 567, 511, 661)
square = next(dr["rect"] for dr in doc[7].get_drawings() if dr.get("fill") is None and fitz.Rect(*window).contains(dr["rect"]) and abs(dr["rect"].width - dr["rect"].height) < 0.1 and dr["rect"].width > 60)
side_pt = square.width
black = polygons(8, window, filled=True)
black = [t for t in black if is_isosceles_right(t)]
assert len(black) == 5, len(black)
scale = Fraction(2) / rationalise(side_pt)  # the stem fixes the square side = 2
areas = sorted((rationalise(area(t) / side_pt ** 2 * 4) for t in black), reverse=True)  # area in units where the side is 2
total = sum(areas)
print("12719 triangles (area, side 2):", [str(a) for a in areas], "total", total)
# nesting check: the triangles must not overlap (their areas must add up to the area of their union, tested on a fine grid)
xs = [p[0] for t in black for p in t]
ys = [p[1] for t in black for p in t]


def inside(t, x, y):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = sign((x, y), t[0], t[1]), sign((x, y), t[1], t[2]), sign((x, y), t[2], t[0])
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


n, overlap, covered = 400, 0, 0
for i in range(n):
    for j in range(n):
        x, y = min(xs) + (max(xs) - min(xs)) * (i + 0.5) / n, min(ys) + (max(ys) - min(ys)) * (j + 0.5) / n
        c = sum(inside(t, x, y) for t in black)
        overlap += c > 1
        covered += c > 0
print("12719 overlapping grid cells:", overlap, "of", covered, "covered cells")
assert overlap < covered * 0.003
result["12719"] = {"answer": str(total), "areas": [str(a) for a in areas], "method": "areas of the five filled triangles measured from the PDF page-8 vector paths, scaled by square side = 2; no overlap",
                   "page": 8, "bbox": list(window)}

# --- 12727: five stroked isosceles right triangles, AB = 1 -------------------------------------------------------------------------
window = (429, 445, 515, 548)
tris = [t for t in polygons(16, window, filled=False) if is_isosceles_right(t)]
assert len(tris) == 5, len(tris)
ab = min(area(t) ** 0.5 * (2 ** 0.5) for t in tris)  # the smallest triangle (T1) has legs AB = 1 by the stem
areas = sorted(((rationalise(area(t) / ab ** 2) for t in tris)), reverse=True)  # area in units where AB = 1 (T1 leg)
total = sum(areas)
print("12727 triangles (area, AB=1):", [str(a) for a in areas], "total", total)
result["12727"] = {"answer": str(total), "areas": [str(a) for a in areas], "method": "areas of the five stroked isosceles right triangles from the PDF page-16 vector paths, scaled by AB = 1 (the shortest leg, T1)",
                   "page": 16, "bbox": list(window)}

# --- 12731 / 12735: induction ----------------------------------------------------------------------------------------------------------
k, n_ = sp.symbols("k n", integer=True, positive=True)
sq = lambda m: m * (m + 1) * (2 * m + 1) / 6  # noqa: E731
cu = lambda m: (m * (m + 1) / 2) ** 2  # noqa: E731
assert sp.simplify(sq(k) + (k + 1) ** 2 - sq(k + 1)) == 0
assert sp.simplify(cu(k) + (k + 1) ** 3 - cu(k + 1)) == 0
assert sq(1) == 1 == 1 ** 2 and cu(1) == 1 == 1 ** 3
assert all(sum(i ** 2 for i in range(1, m + 1)) == sq(m) and sum(i ** 3 for i in range(1, m + 1)) == cu(m) for m in range(1, 40))
# the factorisations printed in the reference proofs
assert sp.expand(k * (2 * k + 1) + 6 * (k + 1)) == sp.expand((k + 2) * (2 * k + 3))
assert sp.simplify(k ** 2 / 4 + (k + 1) - (k + 2) ** 2 / 4) == 0
print("12731 / 12735: inductive steps verified symbolically and for n = 1..39")
result["12731"] = {"verified": "induction step (k -> k+1) symbolic + n=1..39 numeric"}
result["12735"] = {"verified": "induction step (k -> k+1) symbolic + n=1..39 numeric"}
(HERE / "fixed_oracles.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
