"""Payload contracts for the periodic-pattern operations of sequence.progression (普高數學2 Unit 1).

* ``figure_path_pattern`` draws the numbered path with the shared ``coordinate_plane`` renderer (points + arrows, no axes): the
  main picture and the four option pictures come from the same ``path_points`` walk that produced the answer.
* ``finger_counting_cycle`` reuses the reviewed textbook hand picture (``reuse_textbook_image`` — the practice route attaches the
  stored, manually verified crop); nothing is drawn.
"""

from __future__ import annotations

from typing import Any

from .sequence_progression_adapter import _RATIONAL, _choice_part, _parts_payload, _part, _t
from .sequence_progression_patterns import FINGER_NAMES, _cycle, path_points

_WORD = {"U": "向上", "R": "向右", "D": "向下", "L": "向左"}
_COLOR = {"U": "#c62828", "D": "#2e7d32", "R": "#111827", "L": "#111827"}
_CIRCLED = "①②③④⑤"
_TIMES = "\\times "
_STEP = {"U": (0, 1), "R": (1, 0), "D": (0, -1), "L": (-1, 0)}
_GAP = 0.3
_BASE = 20  # keeps (0, 0) outside the view: the picture is drawn without axes or grid


def _rule_words(cycle: tuple[str, ...]) -> str:
    words = [_WORD[d] for d in cycle]
    return "先" + "、".join(words[:-1]) + "、再" + words[-1]


def _arrows(points: list[tuple[int, tuple[int, int]]], cycle_dirs: list[str], ox: float, oy: float, scale: float):
    pts = [{"x": _BASE + ox + scale * x, "y": _BASE + oy + scale * y, "label": str(n)} for n, (x, y) in points]
    arrows = []
    for (p, q), d in zip(zip(pts, pts[1:]), cycle_dirs):  # stop short of both numbers so arrows never run through a label
        dx, dy = _STEP[d]
        arrows.append({"from": [p["x"] + _GAP * dx, p["y"] + _GAP * dy], "to": [q["x"] - _GAP * dx, q["y"] - _GAP * dy], "color": _COLOR[d], "lineWidth": 2.4})
    return pts, arrows


def _figure(cycle: tuple[str, ...], start: int, t: int, options: list[dict[str, Any]]) -> dict[str, Any]:
    main_count = 3 * len(cycle)
    main = path_points(cycle, start, start, main_count)
    dirs = [cycle[i % len(cycle)] for i in range(main_count - 1)]
    points, arrows = _arrows(main, dirs, 0, 4.6, 2)
    points.append({"x": _BASE - 1.5, "y": _BASE + 4.6, "label": "開始"})
    for k, option in enumerate(options):
        ox = 3.9 * k + 0.6
        moves = list(option["pair"])
        shape = [(0, 0)]
        for d in moves:
            dx, dy = _STEP[d]
            shape.append((shape[-1][0] + dx, shape[-1][1] + dy))
        miny = min(p[1] for p in shape)
        numbered = [(t + i, (px, py - miny)) for i, (px, py) in enumerate(shape)]
        pts, arr = _arrows(numbered, moves, ox, 0, 2)
        points += pts
        arrows += arr
        points.append({"x": _BASE + ox, "y": _BASE + 3.3, "label": _CIRCLED[k]})
    # The shared renderer only treats a spec as drawable when it has a line or curve; the numbered path is all arrows, so a
    # zero-length anchor segment (invisible) at the 開始 mark makes the spec renderable without touching static/js.
    anchor = [_BASE - 1.5, _BASE + 4.6]
    return {"kind": "coordinate_plane", "points": points, "arrows": arrows, "lines": [{"through_points": [anchor, anchor], "extend": False}], "show_grid": False,
            "hide_unlabeled_points": True, "x_range": [_BASE - 2.4, _BASE + 15.4], "y_range": [_BASE - 1.0, _BASE + 7.2],
            "render_required": True}


def figure_path_pattern_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    cycle = _cycle(g)
    start, t, T = int(g["start"]), int(g["t"]), int(g["T"])
    choices = [{"label": o["label"], "value": _CIRCLED[k]} for k, o in enumerate(a["options"])]
    question = (f"從 {_t(str(start))} 開始，依照{_rule_words(cycle)}的規律，將所有正整數依序排列如下圖所示。\n"
                f"(1)選出由 {_t(str(t))} 經 {_t(str(t + 1))} 到 {_t(str(t + 2))} 的圖形。（單選）\n"
                f"(2)已知從 {_t(str(start))} 排到 {_t(str(T))} 共經過 $n$ 次向上，求 $n$ 的值。")
    parts = [{**_choice_part(1, a["correct_option"], choices), "label": "(1) 圖形", "prompt": "(1) 圖形"}, _part(2, str(a["n_ups"]), *_RATIONAL, label="(2) n", prompt="(2) n")]
    period = a["period"]
    pos = (t - start) % period
    idx = [o["label"] for o in a["options"]].index(a["correct_option"])
    moves = "、".join(_WORD[d] for d in a["options"][idx]["pair"])
    ups = sum(1 for d in cycle if d == "U")
    rem = start + pos
    steps = [f"(1) 規律每 {period} 個數字重複一次，{t}={_t(str((t - start) // period) + _TIMES + str(period) + '+' + str(rem))}，所以 {t} 的位置相對關係與 {rem} 相同；"
             f"從 {t} 到 {t + 1}、再到 {t + 2} 的方向是{moves}，故選{_CIRCLED[idx]}。",
             f"(2) 從 {start} 排到 {T} 共走 {T - start} 步，每 {period} 步含 {ups} 次向上；逐步點算，向上共 {a['n_ups']} 次，即 $n={a['n_ups']}$。"]
    payload = _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){_CIRCLED[idx]}　(2)n={a['n_ups']}",
                             explanation_steps=steps, shape="figure_path")
    payload["visual_spec"] = _figure(cycle, start, t, a["options"])
    payload["visual_backed"] = True
    return payload


def finger_counting_cycle_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    ks, N, period = [int(k) for k in g["ks"]], int(g["N"]), a["period"]
    names = "、".join(_t(f"a_{{{k}}}") for k in ks)
    question = ("伸出左手，從大拇指開始，按照右圖的方式依序數數字：\n$1, 2, 3, 4, 5, 6, 7, 8, 9, 10,\\ldots$。\n"
                "設 $a_{n}$ 是第 $n$ 次對應到大拇指時所數到的數字。\n"
                f"(1)數數看：寫出 {names} 的值。\n(2)數到 {_t(str(N))} 時，所對應的是哪根手指頭？（單選）")
    choices = [{"label": "ABCDE"[i], "value": _CIRCLED[i] + name} for i, name in enumerate(FINGER_NAMES)]
    parts = [_part(i + 1, a["terms"][i], *_RATIONAL, label=f"(1) a{k}", prompt=f"(1) a{k}") for i, k in enumerate(ks)]
    parts.append({**_choice_part(len(ks) + 1, a["choice"], choices), "label": "(2) 手指", "prompt": "(2) 手指"})
    r = (N - 1) % period + 1
    steps = [f"(1) 依圖，從大拇指數到小指再折返回大拇指，每 {period} 個數字為一輪，所以 $a_{{n}}=1+{period}(n-1)$，"
             + "、".join(f"$a_{{{k}}}={a['terms'][i]}$" for i, k in enumerate(ks)) + "。",
             f"(2) {_t(str(N) + '=' + str((N - 1) // period) + _TIMES + str(period) + '+' + str(r))}，數到 {N} 與數到 {r} 落在同一根手指：{a['finger']}。"]
    payload = _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(f"a{k}={a['terms'][i]}" for i, k in enumerate(ks)) + f"；{a['finger']}",
                             explanation_steps=steps, shape="finger_cycle")
    payload["reuse_textbook_image"] = True
    return payload
