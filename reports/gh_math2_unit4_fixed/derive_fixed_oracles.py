"""Independent derivation of the reference answer for the one Unit 4 row that has no dynamic generator (12801, read-only).

12801 shows an irregular street map ("下圖為一街道圖，從 A 取捷徑走到 B")：some street segments of the 5x4 lattice are missing, so the figure itself is
the problem and cannot be re-parameterised.  The answer is derived from the VECTOR drawing of the paired PDF (page 16, the paths of the printed
figure), not from the textbook solution (the row has none) and not by eye:

* every drawn line / rectangle side inside the verified figure region is snapped to the lattice (spacing 14.17 pt) and becomes street edges;
* the shortest routes are the monotone (right / up) paths on those edges, counted two ways: dynamic programming over the lattice and explicit
  depth-first listing of every path;
* the same street graph is read independently from the pixels of the stored PNG crop (the picture the student sees) and must be identical.

Writes ``fixed_oracles.json`` next to this file.
"""
import hashlib
import json
import sys
from pathlib import Path

import fitz
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/bf39d447345e_單元04-排列.pdf"
PDF_SHA = "bf39d447345e163ab4bab942337cd96ca9460eaf477f89953d284b7ed35025cb"
assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA
PNG_DIR = ROOT / "uploads/question_assets/general/longteng/數學2/ch_unknown_單元4_排列/sec_unknown_4排列"
PNG = next(PNG_DIR.glob("basic_exercise_4習題_基礎題6*_fig1.png"))
PAGE, WINDOW = 15, fitz.Rect(255, 398, 355, 486)  # page 16; the manually verified crop region of the figure (letters A / B excluded below)
SPACING = 14.17


def snap(v: float, origin: float) -> int:
    k = round((v - origin) / SPACING)
    assert abs(origin + k * SPACING - v) < 0.6, (v, origin)
    return k


def vector_edges() -> tuple[set, set, int, int]:
    segments = []
    for dr in fitz.open(PDF)[PAGE].get_drawings():
        r = dr["rect"]
        if not WINDOW.contains(r) or dr.get("fill") is not None:
            continue  # filled paths are the letters A and B
        for it in dr["items"]:
            if it[0] == "re":
                x0, y0, x1, y1 = it[1].x0, it[1].y0, it[1].x1, it[1].y1
                segments += [(x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)]
            elif it[0] == "l":
                segments.append((it[1].x, it[1].y, it[2].x, it[2].y))
    x_origin = min(min(s[0], s[2]) for s in segments)
    y_bottom = max(max(s[1], s[3]) for s in segments)  # PDF y grows downwards: the bottom street has the largest y
    horizontal, vertical = set(), set()
    for x0, y0, x1, y1 in segments:
        if abs(y0 - y1) < 0.01:  # a horizontal street line
            j = snap(y_bottom, y0)  # rows counted from the bottom
            a, b = sorted((snap(x0, x_origin), snap(x1, x_origin)))
            horizontal |= {(i, j) for i in range(a, b)}  # edge (i, j) -> (i + 1, j)
        else:
            i = snap(x0, x_origin)
            a, b = sorted((snap(y_bottom, y0), snap(y_bottom, y1)))
            vertical |= {(i, j) for j in range(a, b)}  # edge (i, j) -> (i, j + 1)
    width = max(i for i, _j in horizontal) + 1
    height = max(j for _i, j in vertical) + 1
    return horizontal, vertical, width, height


def pixel_edges() -> tuple[set, set, int, int]:
    im = Image.open(PNG).convert("RGB")
    w, h = im.size
    dark = lambda x, y: sum(im.getpixel((x, y))) < 250  # noqa: E731

    def lines(values, limit):
        out, cur = [], []
        for i, v in enumerate(values):
            if v > limit:
                cur.append(i)
            elif cur:
                out.append(sum(cur) / len(cur))
                cur = []
        if cur:
            out.append(sum(cur) / len(cur))
        return out

    xs = lines([sum(dark(x, y) for y in range(h)) for x in range(w)], h * 0.3)
    ys = list(reversed(lines([sum(dark(x, y) for x in range(w)) for y in range(h)], w * 0.3)))  # bottom first
    horizontal, vertical = set(), set()
    for j, y in enumerate(ys):
        for i in range(len(xs) - 1):
            pts = [(xs[i] + (xs[i + 1] - xs[i]) * t / 10, y) for t in range(2, 9)]
            if all(dark(round(px), round(py)) for px, py in pts):
                horizontal.add((i, j))
    for i, x in enumerate(xs):
        for j in range(len(ys) - 1):
            pts = [(x, ys[j] + (ys[j + 1] - ys[j]) * t / 10) for t in range(2, 9)]
            if all(dark(round(px), round(py)) for px, py in pts):
                vertical.add((i, j))
    return horizontal, vertical, len(xs) - 1, len(ys) - 1


def count_dp(horizontal: set, vertical: set, width: int, height: int) -> int:
    ways = {(0, 0): 1}
    for j in range(height + 1):
        for i in range(width + 1):
            if (i, j) == (0, 0):
                continue
            ways[(i, j)] = (ways.get((i - 1, j), 0) if (i - 1, j) in horizontal else 0) + (ways.get((i, j - 1), 0) if (i, j - 1) in vertical else 0)
    return ways[(width, height)]


def count_dfs(horizontal: set, vertical: set, width: int, height: int) -> tuple[int, list[str]]:
    routes: list[str] = []

    def go(i: int, j: int, trail: str) -> None:
        if (i, j) == (width, height):
            routes.append(trail)
            return
        if (i, j) in horizontal:
            go(i + 1, j, trail + "右")
        if (i, j) in vertical:
            go(i, j + 1, trail + "上")

    go(0, 0, "")
    return len(routes), routes


h1, v1, w1, hh1 = vector_edges()
h2, v2, w2, hh2 = pixel_edges()
assert (h1, v1, w1, hh1) == (h2, v2, w2, hh2), "the PDF vector street graph and the stored PNG crop disagree"
dp = count_dp(h1, v1, w1, hh1)
dfs, routes = count_dfs(h1, v1, w1, hh1)
assert dp == dfs and len(set(routes)) == len(routes) and all(r.count("右") == w1 and r.count("上") == hh1 for r in routes)
print("lattice", w1, "x", hh1, "| horizontal edges", len(h1), "| vertical edges", len(v1), "| shortest routes", dp)
result = {"12801": {"answer": str(dp), "width": w1, "height": hh1, "horizontal_edges": sorted(h1), "vertical_edges": sorted(v1),
                    "method": "PDF vector street graph (page 16) == PNG pixel graph; routes counted by DP and by explicit listing",
                    "pdf_sha256": PDF_SHA, "page": 16, "bbox": [261.0, 403.0, 348.0, 480.0]}}
(HERE / "fixed_oracles.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print("written", HERE / "fixed_oracles.json")

