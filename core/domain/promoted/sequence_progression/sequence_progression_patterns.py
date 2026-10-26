"""Periodic-pattern operations of ``sequence.progression`` (普高數學2 Unit 1, 依圖形規律歸納).

* ``figure_path_pattern`` — numbers 1, 2, 3, ... laid out along a path whose step direction repeats with a fixed period
  (textbook: 上 → 右 → 下 → 右).  Answers: which three-number path picture shows ``t, t+1, t+2`` and how many "up" steps
  lie between ``start`` and ``T``.
* ``finger_counting_cycle`` — counting on the fingers of one hand, the finger repeating with a fixed period
  (大拇指 → 食指 → 中指 → 無名指 → 小指 → 無名指 → 中指 → 食指).  Answers: the k-th numbers landing on the thumb and the
  finger that number N lands on.

Answers come from the period arithmetic; each validator re-walks the path / the count step by step instead of reusing the
closed form.  Nothing here draws: the figure data is built from ``path_points`` so the picture and the answer share one walk.
"""

from __future__ import annotations

from typing import Any

CYCLE_DEFAULT = ("U", "R", "D", "R")
_DELTA = {"U": (0, 1), "R": (1, 0), "D": (0, -1), "L": (-1, 0)}
FINGERS = ("大拇指", "食指", "中指", "無名指", "小指", "無名指", "中指", "食指")
FINGER_NAMES = ("大拇指", "食指", "中指", "無名指", "小指")
LABELS = ("A", "B", "C", "D")


def _cycle(g: dict[str, Any]) -> tuple[str, ...]:
    cycle = tuple(g.get("cycle") or CYCLE_DEFAULT)
    if not cycle or any(d not in _DELTA for d in cycle):
        raise ValueError("pattern_cycle_invalid")
    return cycle


def direction(cycle: tuple[str, ...], start: int, i: int) -> str:
    """Direction of the step from number ``i`` to ``i + 1``."""
    return cycle[(i - start) % len(cycle)]


def path_points(cycle: tuple[str, ...], start: int, first: int, count: int) -> list[tuple[int, tuple[int, int]]]:
    """``count`` consecutive numbers beginning at ``first``, as (number, (x, y)), first number at the origin."""
    x = y = 0
    out = [(first, (0, 0))]
    for i in range(first, first + count - 1):
        dx, dy = _DELTA[direction(cycle, start, i)]
        x, y = x + dx, y + dy
        out.append((i + 1, (x, y)))
    return out


def option_pairs(cycle: tuple[str, ...]) -> list[tuple[str, str]]:
    """The two-step direction pair of every phase of the period (pairs must differ, else options are ambiguous)."""
    pairs = [(cycle[p % len(cycle)], cycle[(p + 1) % len(cycle)]) for p in range(len(cycle))]
    if len(set(pairs)) != len(pairs):
        raise ValueError("pattern_option_pairs_ambiguous")
    return pairs


def figure_path_pattern(start: int, t: int, T: int, order: list[int], **g: Any) -> dict[str, Any]:
    cycle = _cycle(g)
    start, t, T = int(start), int(t), int(T)
    pairs = option_pairs(cycle)
    if len(cycle) != 4 or sorted(order) != list(range(4)):
        raise ValueError("pattern_order_invalid")
    if t < start or T <= start:
        raise ValueError("pattern_numbers_invalid")
    phase = (t - start) % len(cycle)
    correct = LABELS[[order[k] for k in range(4)].index(phase)]
    ups = sum(1 for i in range(start, T) if direction(cycle, start, i) == "U")  # steps start->start+1 ... T-1->T
    options = [{"label": LABELS[k], "pair": list(pairs[order[k]])} for k in range(4)]
    return {"correct_option": correct, "n_ups": ups, "options": options, "phase": phase, "period": len(cycle)}


def _check_figure_path_pattern(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    cycle = _cycle(givens)
    start, t, T, order = int(givens["start"]), int(givens["t"]), int(givens["T"]), list(givens["order"])
    # re-walk: draw numbers t..t+2 and read their moves off the coordinates, then compare with every option picture
    walk = path_points(cycle, start, t, 3)
    moves = []
    for (_n1, (x1, y1)), (_n2, (x2, y2)) in zip(walk, walk[1:]):
        moves.append({(0, 1): "U", (1, 0): "R", (0, -1): "D", (-1, 0): "L"}[(x2 - x1, y2 - y1)])
    matching = [o["label"] for o in answer["options"] if o["pair"] == moves]
    if matching != [answer["correct_option"]] or [o["label"] for o in answer["options"]] != list(LABELS):
        return False
    if len({tuple(o["pair"]) for o in answer["options"]}) != 4:
        return False
    # count the up steps by walking from `start` to T through the coordinates
    full = path_points(cycle, start, start, T - start + 1)
    ups = sum(1 for (_a, (_x1, y1)), (_b, (_x2, y2)) in zip(full, full[1:]) if y2 > y1)
    return ups == answer["n_ups"] and sorted(order) == list(range(4))


def finger_counting_cycle(ks: list[int], N: int, **g: Any) -> dict[str, Any]:
    cycle = tuple(g.get("fingers") or FINGERS)
    if cycle[0] != "大拇指" or cycle.count("大拇指") != 1:
        raise ValueError("finger_cycle_invalid")
    period = len(cycle)
    ks, N = [int(k) for k in ks], int(N)
    if not ks or min(ks) < 1 or N < 1:
        raise ValueError("finger_inputs_invalid")
    terms = [1 + (k - 1) * period for k in ks]  # k-th time the count lands on the thumb
    finger = cycle[(N - 1) % period]
    return {"terms": [str(a) for a in terms], "finger": finger, "choice": "ABCDE"[FINGER_NAMES.index(finger)], "period": period}


def _check_finger_counting_cycle(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    cycle = tuple(givens.get("fingers") or FINGERS)
    ks, N = [int(k) for k in givens["ks"]], int(givens["N"])
    top = max(max(ks) * len(cycle), N) + len(cycle)
    # count 1, 2, 3, ... on the hand: bounce thumb -> pinky -> back, writing down every number that lands on the thumb
    index, step = 0, 1
    ladder = ("大拇指", "食指", "中指", "無名指", "小指")
    on_thumb, landed = [], {}
    for number in range(1, top + 1):
        finger = ladder[index]
        landed[number] = finger
        if finger == "大拇指":
            on_thumb.append(number)
        if index == len(ladder) - 1:
            step = -1
        elif index == 0:
            step = 1
        index += step
    return (landed[N] == answer["finger"] and answer["choice"] == "ABCDE"[FINGER_NAMES.index(landed[N])]
            and [str(on_thumb[k - 1]) for k in ks] == list(answer["terms"]))
