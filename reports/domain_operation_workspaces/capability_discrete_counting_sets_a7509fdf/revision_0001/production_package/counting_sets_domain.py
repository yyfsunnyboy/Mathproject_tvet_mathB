"""Exact domain operations for general-high Mathematics 2, Unit 3 計數原理 (sets and propositions, addition / multiplication principle,
inclusion-exclusion, tree diagrams and figure-dependent counting).

Domain key ``discrete.sets_counting``.  Components pass the *stated data of the problem*; every answer is derived here with exact integer
arithmetic.  Each operation owns a validator that re-derives the answer a different way (point sampling against the set definition, brute-force
enumeration of the labelled objects, a Venn-region rebuild, truth-table lookup, subset-of-edges matching enumeration) and never calls the
construction a second time.  Numbers cross the JSON boundary as ints.
"""

from __future__ import annotations

import itertools
import math
import re
from fractions import Fraction
from typing import Any, Callable

import sympy as sp

DOMAIN_KEY = "discrete.sets_counting"
X = sp.Symbol("x", real=True)


def _require(givens: dict[str, Any], *keys: str) -> None:
    missing = [k for k in keys if k not in givens]
    if missing:
        raise ValueError(f"givens_required:{','.join(missing)}")


def _int(v: Any, name: str, low: int | None = None, high: int | None = None) -> int:
    if isinstance(v, bool):
        raise ValueError(f"not_an_integer:{name}")
    try:
        f = Fraction(str(v).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"not_an_integer:{name}") from None
    if f.denominator != 1:
        raise ValueError(f"not_an_integer:{name}")
    n = int(f)
    if (low is not None and n < low) or (high is not None and n > high):
        raise ValueError(f"out_of_range:{name}")
    return n


def _int_list(values: Any, name: str, min_len: int = 1) -> list[int]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"not_a_list:{name}")
    out = [_int(v, name) for v in values]
    if len(out) < min_len or len(set(out)) != len(out):
        raise ValueError(f"bad_member_list:{name}")
    return out


# --- 1. interval set operations over the reals ---------------------------------------------------------------------------------

INTERVAL_ITEMS = ("intersection", "union", "a_minus_b", "b_minus_a", "a_complement", "b_complement")


def _interval_spec(spec: dict[str, Any], name: str) -> tuple[int, int, bool, bool]:
    lo, hi = _int(spec["lo"], name), _int(spec["hi"], name)
    if lo >= hi:
        raise ValueError(f"empty_interval:{name}")
    return lo, hi, bool(spec.get("lc", True)), bool(spec.get("hc", True))


def _pieces(result: Any) -> list[list[Any]]:
    """Sympy set -> [[lo|None, lo_closed, hi|None, hi_closed], ...] (only genuine intervals are accepted)."""
    parts = [result] if isinstance(result, sp.Interval) else (list(result.args) if isinstance(result, sp.Union) else None)
    if not parts or not all(isinstance(p, sp.Interval) for p in parts):
        raise ValueError("degenerate_result")
    parts.sort(key=lambda p: (0, 0) if p.start == -sp.oo else (1, float(p.start)))
    return [[None if p.start == -sp.oo else int(p.start), not bool(p.left_open), None if p.end == sp.oo else int(p.end), not bool(p.right_open)] for p in parts]


def _piece_text(piece: list[Any]) -> str:
    lo, lc, hi, hc = piece
    if lo is None:
        return f"x{'<=' if hc else '<'}{hi}"
    if hi is None:
        return f"x{'>=' if lc else '>'}{lo}"
    return f"{lo}{'<=' if lc else '<'}x{'<=' if hc else '<'}{hi}"


def interval_set_operations(A: dict[str, Any], B: dict[str, Any], items: list[str], **_: Any) -> dict[str, Any]:
    a, b = _interval_spec(A, "A"), _interval_spec(B, "B")
    sa = sp.Interval(a[0], a[1], left_open=not a[2], right_open=not a[3])
    sb = sp.Interval(b[0], b[1], left_open=not b[2], right_open=not b[3])
    out = []
    for item in items:
        if item not in INTERVAL_ITEMS:
            raise ValueError(f"unsupported_item:{item}")
        result = {"intersection": lambda: sa.intersect(sb), "union": lambda: sa.union(sb), "a_minus_b": lambda: sa - sb, "b_minus_a": lambda: sb - sa,
                  "a_complement": lambda: sp.S.Reals - sa, "b_complement": lambda: sp.S.Reals - sb}[item]()
        pieces = _pieces(result)
        out.append({"item": item, "pieces": pieces, "canonical": " or ".join(_piece_text(p) for p in pieces)})
    return {"items": out}


_RE_BETWEEN = re.compile(r"^(-?\d+)(<=|<)x(<=|<)(-?\d+)$")
_RE_ONE_SIDED = re.compile(r"^x(<=|<|>=|>)(-?\d+)$")


def _predicate(text: str) -> Callable[[Fraction], bool]:
    tests: list[Callable[[Fraction], bool]] = []
    for part in text.split(" or "):
        m = _RE_BETWEEN.match(part)
        if m:
            lo, lop, hop, hi = int(m.group(1)), m.group(2), m.group(3), int(m.group(4))
            tests.append(lambda x, lo=lo, lop=lop, hop=hop, hi=hi: (x > lo or (lop == "<=" and x == lo)) and (x < hi or (hop == "<=" and x == hi)))
            continue
        m = _RE_ONE_SIDED.match(part)
        if not m:
            raise ValueError(f"unreadable_answer:{part}")
        op, v = m.group(1), int(m.group(2))
        tests.append({"<": lambda x, v=v: x < v, "<=": lambda x, v=v: x <= v, ">": lambda x, v=v: x > v, ">=": lambda x, v=v: x >= v}[op])
    return lambda x: any(t(x) for t in tests)


def _check_interval_set_operations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    def member(spec: dict[str, Any], x: Fraction) -> bool:
        lo, hi, lc, hc = int(spec["lo"]), int(spec["hi"]), bool(spec.get("lc", True)), bool(spec.get("hc", True))
        return (lo < x or (lc and x == lo)) and (x < hi or (hc and x == hi))

    ends = [int(givens[k][e]) for k in ("A", "B") for e in ("lo", "hi")]
    points = {Fraction(e) + Fraction(d, 4) for e in ends for d in range(-6, 7)} | {Fraction(-1000), Fraction(1000)}
    rules = {"intersection": lambda a, b: a and b, "union": lambda a, b: a or b, "a_minus_b": lambda a, b: a and not b,
             "b_minus_a": lambda a, b: b and not a, "a_complement": lambda a, b: not a, "b_complement": lambda a, b: not b}
    if len(answer["items"]) != len(givens["items"]):
        return False
    for item, got in zip(givens["items"], answer["items"]):
        if got["item"] != item:
            return False
        want = _predicate(got["canonical"])
        if any(want(x) != rules[item](member(givens["A"], x), member(givens["B"], x)) for x in points):
            return False
    return True


# --- 2. finite set operations ---------------------------------------------------------------------------------------------------

SET_ITEMS = ("intersection", "union", "a_minus_b", "b_minus_a", "a_complement", "b_complement")


def finite_set_operations(A: list[int], B: list[int], items: list[str], universe: list[int] | None = None, **_: Any) -> dict[str, Any]:
    sa, sb = set(_int_list(A, "A")), set(_int_list(B, "B"))
    su = set(_int_list(universe, "universe")) if universe is not None else None
    if su is not None and not (sa | sb) <= su:
        raise ValueError("sets_outside_universe")
    out = []
    for item in items:
        if item in ("a_complement", "b_complement") and su is None:
            raise ValueError("complement_needs_universe")
        result = {"intersection": lambda: sa & sb, "union": lambda: sa | sb, "a_minus_b": lambda: sa - sb, "b_minus_a": lambda: sb - sa,
                  "a_complement": lambda: su - sa, "b_complement": lambda: su - sb}[item]() if item in SET_ITEMS else None
        if result is None:
            raise ValueError(f"unsupported_item:{item}")
        if not result:
            raise ValueError(f"empty_result:{item}")
        out.append({"item": item, "members": sorted(result)})
    return {"items": out}


def _check_finite_set_operations(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    universe = givens.get("universe")
    elements = sorted(set(universe) if universe is not None else set(givens["A"]) | set(givens["B"]))
    bit = {e: 1 << i for i, e in enumerate(elements)}
    ma, mb = sum(bit[e] for e in givens["A"]), sum(bit[e] for e in givens["B"])
    full = (1 << len(elements)) - 1
    masks = {"intersection": ma & mb, "union": ma | mb, "a_minus_b": ma & ~mb & full, "b_minus_a": mb & ~ma & full,
             "a_complement": ~ma & full, "b_complement": ~mb & full}
    if len(answer["items"]) != len(givens["items"]):
        return False
    for item, got in zip(givens["items"], answer["items"]):
        if got["item"] != item or sum(bit[e] for e in got["members"]) != masks[item] or len(set(got["members"])) != len(got["members"]):
            return False
    return True


# --- 3. sets defined by an equation ---------------------------------------------------------------------------------------------

def _equation_set(spec: dict[str, Any], name: str) -> tuple[list[int], Callable[[int], int]]:
    kind = spec["kind"]
    if kind == "square":
        rhs = _int(spec["rhs"], name, 1)
        if math.isqrt(rhs) ** 2 != rhs:
            raise ValueError(f"roots_not_integers:{name}")
        poly = X ** 2 - rhs
    elif kind == "quad":
        b, c = _int(spec["b"], name), _int(spec["c"], name)
        poly = X ** 2 + b * X + c
    else:
        raise ValueError(f"unsupported_equation_kind:{kind}")
    roots = sp.solve(poly, X)
    if len(roots) != 2 or not all(r.is_Integer for r in roots):
        raise ValueError(f"roots_not_two_integers:{name}")
    return sorted(int(r) for r in roots), sp.lambdify(X, poly)


def equation_root_sets(A: dict[str, Any], B: dict[str, Any], items: list[str], **_: Any) -> dict[str, Any]:
    ra, _fa = _equation_set(A, "A")
    rb, _fb = _equation_set(B, "B")
    out = []
    for item in items:
        members = sorted(set(ra) & set(rb)) if item == "intersection" else sorted(set(ra) | set(rb)) if item == "union" else None
        if not members:
            raise ValueError(f"unsupported_or_empty:{item}")
        out.append({"item": item, "members": members})
    return {"A": ra, "B": rb, "items": out}


def _check_equation_root_sets(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    def holds(spec: dict[str, Any], x: int) -> bool:
        return x * x == int(spec["rhs"]) if spec["kind"] == "square" else x * x + int(spec["b"]) * x + int(spec["c"]) == 0

    scan = range(-60, 61)
    ra = [x for x in scan if holds(givens["A"], x)]
    rb = [x for x in scan if holds(givens["B"], x)]
    if ra != answer["A"] or rb != answer["B"] or len(ra) != 2 or len(rb) != 2:
        return False
    for item, got in zip(givens["items"], answer["items"]):
        want = [x for x in scan if (x in ra and x in rb if item == "intersection" else x in ra or x in rb)]
        if got["item"] != item or got["members"] != want:
            return False
    return len(givens["items"]) == len(answer["items"])


# --- 4. propositions: truth values, compounds, selection -----------------------------------------------------------------------

FACTS: dict[str, tuple[str, bool]] = {
    "rect_square": ("長方形都是正方形", False),
    "eq_tri_isos": ("正三角形都是等腰三角形", True),
    "square_rect": ("正方形都是長方形", True),
    "rhombus_square": ("菱形都是正方形", False),
    "para_rect": ("平行四邊形都是長方形", False),
    "square_rhombus": ("正方形都是菱形", True),
    "prime_odd": ("質數都是奇數", False),
    "even_div2": ("偶數都是 2 的倍數", True),
    "isos_equi": ("等腰三角形都是正三角形", False),
    "rect_diag": ("長方形的兩條對角線等長", True),
    "tri_angles": ("三角形的內角和為 180 度", True),
}
_COMPARE_OPS = (">", "<", ">=", "<=", "=")
_PROPS = ("prime", "even", "odd", "multiple_of")


def _atom_truth(atom: dict[str, Any]) -> bool:
    kind = atom["kind"]
    if kind == "compare":
        a, b, op = _int(atom["a"], "a"), _int(atom["b"], "b"), atom["op"]
        if op not in _COMPARE_OPS:
            raise ValueError(f"unsupported_compare:{op}")
        return {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b, "=": a == b}[op]
    if kind == "fact":
        if atom["id"] not in FACTS:
            raise ValueError(f"unknown_fact:{atom['id']}")
        return FACTS[atom["id"]][1]
    if kind == "prop":
        n, prop = _int(atom["n"], "n", 2), atom["prop"]
        if prop == "prime":
            return bool(sp.isprime(n))
        if prop == "even":
            return n % 2 == 0
        if prop == "odd":
            return n % 2 == 1
        if prop == "multiple_of":
            return n % _int(atom["k"], "k", 2) == 0
    raise ValueError(f"unsupported_atom:{kind}")


def _atom_truth_again(atom: dict[str, Any]) -> bool:
    """Second derivation: sign of a difference, trial division, last digit, repeated addition."""
    kind = atom["kind"]
    if kind == "compare":
        d = int(atom["a"]) - int(atom["b"])
        sign = (d > 0) - (d < 0)
        return {">": sign == 1, "<": sign == -1, ">=": sign >= 0, "<=": sign <= 0, "=": sign == 0}[atom["op"]]
    if kind == "fact":
        return FACTS[atom["id"]][1]
    n = int(atom["n"])
    if atom["prop"] == "prime":
        return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
    if atom["prop"] == "even":
        return str(n)[-1] in "02468"
    if atom["prop"] == "odd":
        return str(n)[-1] in "13579"
    k = int(atom["k"])
    return any(k * m == n for m in range(n // k + 2))


def _option_truth(option: list[Any], truths: list[bool]) -> bool:
    kind = option[0]
    if kind == "atom":
        return truths[option[1]]
    if kind == "and":
        return truths[option[1]] and truths[option[2]]
    if kind == "or":
        return truths[option[1]] or truths[option[2]]
    if kind == "not":
        return not truths[option[1]]
    raise ValueError(f"unsupported_option:{kind}")


def _check_option(option: list[Any], n_atoms: int) -> None:
    arity = {"atom": 1, "not": 1, "and": 2, "or": 2}.get(option[0])
    if arity is None or len(option) != arity + 1 or any((not isinstance(i, int)) or isinstance(i, bool) or not 0 <= i < n_atoms for i in option[1:]):
        raise ValueError(f"bad_option:{option}")


def proposition_truth(atoms: list[dict[str, Any]], options: list[list[Any]], mode: str, **_: Any) -> dict[str, Any]:
    if mode not in ("truth", "select_true"):
        raise ValueError(f"unsupported_mode:{mode}")
    for option in options:
        _check_option(option, len(atoms))
    atom_truths = [_atom_truth(a) for a in atoms]
    truths = [_option_truth(o, atom_truths) for o in options]
    selected = [i + 1 for i, t in enumerate(truths) if t]
    if mode == "truth" and len(options) != 1:
        raise ValueError("truth_mode_has_one_statement")
    if mode == "select_true" and not 1 <= len(selected) <= len(options) - 2:
        raise ValueError("selection_needs_one_to_n_minus_two_correct")
    return {"mode": mode, "atom_truths": atom_truths, "truths": truths, "selected": selected}


_AND = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 1}
_OR = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 1}


def _check_proposition_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    atoms, options = givens["atoms"], givens["options"]
    base = tuple(int(_atom_truth_again(a)) for a in atoms)
    if [bool(v) for v in base] != answer["atom_truths"]:
        return False
    table = {}  # a truth table over every assignment of the atoms; the row of the actual assignment is read back
    for row in itertools.product((0, 1), repeat=len(atoms)):
        table[row] = [{"atom": lambda o, r=row: r[o[1]], "not": lambda o, r=row: 1 - r[o[1]], "and": lambda o, r=row: _AND[(r[o[1]], r[o[2]])],
                       "or": lambda o, r=row: _OR[(r[o[1]], r[o[2]])]}[o[0]](o) for o in options]
    row = table[base]
    return [bool(v) for v in row] == answer["truths"] and answer["selected"] == [i + 1 for i, v in enumerate(row) if v] \
        and (answer["mode"] == givens["mode"])


# --- 5. universal implications over the reals ----------------------------------------------------------------------------------

def _f(**kw: Any) -> dict[str, Any]:
    return kw


CLAIMS: dict[str, dict[str, Any]] = {
    "ab0_and": _f(hyp="ab=0", concl="a=0且b=0", h=lambda a, b: a * b == 0, c=lambda a, b: a == 0 and b == 0),
    "ab0_or": _f(hyp="ab=0", concl="a=0或b=0", h=lambda a, b: a * b == 0, c=lambda a, b: a == 0 or b == 0),
    "ab0_a": _f(hyp="ab=0", concl="a=0", h=lambda a, b: a * b == 0, c=lambda a, b: a == 0),
    "sq_eq": _f(hyp="a^{2}=b^{2}", concl="a=b", h=lambda a, b: a * a == b * b, c=lambda a, b: a == b),
    "sq_pm": _f(hyp="a^{2}=b^{2}", concl="a=b或a=-b", h=lambda a, b: a * a == b * b, c=lambda a, b: a == b or a == -b),
    "prod_pos_both": _f(hyp="ab>0", concl="a>0且b>0", h=lambda a, b: a * b > 0, c=lambda a, b: a > 0 and b > 0),
    "sum_pos_or": _f(hyp="a+b>0", concl="a>0或b>0", h=lambda a, b: a + b > 0, c=lambda a, b: a > 0 or b > 0),
    "sum_pos_both": _f(hyp="a+b>0", concl="a>0且b>0", h=lambda a, b: a + b > 0, c=lambda a, b: a > 0 and b > 0),
    "both_pos_prod": _f(hyp="a>0且b>0", concl="ab>0", h=lambda a, b: a > 0 and b > 0, c=lambda a, b: a * b > 0),
    "sq_sum_zero": _f(hyp="a^{2}+b^{2}=0", concl="a=0且b=0", h=lambda a, b: a * a + b * b == 0, c=lambda a, b: a == 0 and b == 0),
    "prod_nonzero": _f(hyp="ab@neq 0", concl="a@neq 0且b@neq 0", h=lambda a, b: a * b != 0, c=lambda a, b: a != 0 and b != 0),
    "gt_sq": _f(hyp="a>b", concl="a^{2}>b^{2}", h=lambda a, b: a > b, c=lambda a, b: a * a > b * b),
    "eq_sq": _f(hyp="a=b", concl="a^{2}=b^{2}", h=lambda a, b: a == b, c=lambda a, b: a * a == b * b),
    "sum0_both": _f(hyp="a+b=0", concl="a=0且b=0", h=lambda a, b: a + b == 0, c=lambda a, b: a == 0 and b == 0),
}
_GRID_1 = [Fraction(k, 2) for k in range(-12, 13)]
_GRID_2 = [Fraction(k, 3) for k in range(-15, 16)] + [Fraction(1, 7), Fraction(-2, 7), Fraction(5, 4)]


def _counterexample(claim: dict[str, Any], grid: list[Fraction]) -> tuple[Fraction, Fraction] | None:
    """The simplest pair (integers first, then smallest |a|+|b|) that satisfies the hypothesis but not the conclusion."""
    bad = [(a, b) for a, b in itertools.product(grid, repeat=2) if claim["h"](a, b) and not claim["c"](a, b)]
    return min(bad, key=lambda p: (p[0].denominator > 1 or p[1].denominator > 1, abs(p[0]) + abs(p[1]), p)) if bad else None


def implication_truth(claim: str, **_: Any) -> dict[str, Any]:
    if claim not in CLAIMS:
        raise ValueError(f"unknown_claim:{claim}")
    witness = _counterexample(CLAIMS[claim], _GRID_1)
    return {"truth": witness is None, "counterexample": None if witness is None else [str(witness[0]), str(witness[1])]}


def _check_implication_truth(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    claim = CLAIMS[givens["claim"]]
    if answer["truth"]:
        return answer["counterexample"] is None and _counterexample(claim, _GRID_2) is None
    a, b = (Fraction(v) for v in answer["counterexample"])
    return bool(claim["h"](a, b)) and not claim["c"](a, b) and _counterexample(claim, _GRID_2) is not None


# --- 6. necessary / sufficient conditions on x ----------------------------------------------------------------------------------

CONDITION_KINDS = ("eq", "abs_eq", "sq_eq", "gt", "ge", "lt", "le")
RELATION_LABELS = {"sufficient": "充分", "necessary": "必要", "iff": "充要"}


def _condition_set(cond: dict[str, Any], name: str) -> sp.Set:
    kind, v = cond["kind"], _int(cond["c"], name)
    if kind == "eq":
        return sp.FiniteSet(v)
    if kind == "abs_eq":
        return sp.FiniteSet(v, -v) if v > 0 else sp.FiniteSet(v)
    if kind == "sq_eq":
        if v < 1 or math.isqrt(v) ** 2 != v:
            raise ValueError(f"not_a_perfect_square:{name}")
        return sp.FiniteSet(math.isqrt(v), -math.isqrt(v))
    return {"gt": sp.Interval.open(v, sp.oo), "ge": sp.Interval(v, sp.oo), "lt": sp.Interval.open(-sp.oo, v), "le": sp.Interval(-sp.oo, v)}[kind] if kind in CONDITION_KINDS else _bad(kind)


def _bad(kind: str) -> sp.Set:
    raise ValueError(f"unsupported_condition:{kind}")


def condition_relation(cond: dict[str, Any], target: dict[str, Any], **_: Any) -> dict[str, Any]:
    c, t = _condition_set(cond, "cond"), _condition_set(target, "target")
    forward, backward = c.is_subset(t), t.is_subset(c)  # cond => target ; target => cond
    if forward and backward:
        relation = "iff"
    elif forward:
        relation = "sufficient"
    elif backward:
        relation = "necessary"
    else:
        raise ValueError("neither_sufficient_nor_necessary")
    return {"relation": relation, "label": RELATION_LABELS[relation]}


def _check_condition_relation(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    def holds(spec: dict[str, Any], x: Fraction) -> bool:
        v = int(spec["c"])
        return {"eq": x == v, "abs_eq": abs(x) == v, "sq_eq": x * x == v, "gt": x > v, "ge": x >= v, "lt": x < v, "le": x <= v}[spec["kind"]]

    grid = [Fraction(k, 2) for k in range(-60, 61)]
    forward = all(holds(givens["target"], x) for x in grid if holds(givens["cond"], x))
    backward = all(holds(givens["cond"], x) for x in grid if holds(givens["target"], x))
    relation = "iff" if forward and backward else "sufficient" if forward else "necessary" if backward else None
    return relation == answer["relation"] and RELATION_LABELS.get(relation) == answer["label"]


# --- 7. multiplication principle -------------------------------------------------------------------------------------------------

def choice_product(groups: list[dict[str, Any]], **_: Any) -> dict[str, Any]:
    counts = [_int(g["count"], "count", 1) for g in groups]
    if len(counts) < 2:
        raise ValueError("needs_two_steps")
    return {"counts": counts, "total": math.prod(counts)}


def _check_choice_product(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    counts = [int(g["count"]) for g in givens["groups"]]
    return sum(1 for _ in itertools.product(*[range(c) for c in counts])) == answer["total"] and answer["counts"] == counts


def grade_selection(grades: list[int], **_: Any) -> dict[str, Any]:
    sizes = [_int(g, "grade", 1) for g in grades]
    if len(sizes) < 3:
        raise ValueError("needs_three_grades")
    pairs = sum(sizes[i] * sizes[j] for i in range(len(sizes)) for j in range(i + 1, len(sizes)))
    return {"sizes": sizes, "one_each": math.prod(sizes), "different_pairs": pairs}


def _check_grade_selection(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    students = [(g, k) for g, size in enumerate(givens["grades"]) for k in range(int(size))]
    different = sum(1 for p, q in itertools.combinations(students, 2) if p[0] != q[0])
    one_each = sum(1 for combo in itertools.product(*[[(g, k) for k in range(int(s))] for g, s in enumerate(givens["grades"])]))
    return different == answer["different_pairs"] and one_each == answer["one_each"]


# --- 8. divisors -----------------------------------------------------------------------------------------------------------------

def _multiples_among_divisors(n: int, t: int) -> int:
    """Number of divisors of n that are multiples of t."""
    if n % t:
        return 0
    return math.prod(e - sp.multiplicity(p, t) + 1 for p, e in sp.factorint(n).items())


multiples_among_divisors = _multiples_among_divisors


def divisor_counting(n: int, multiple_of: int | None = None, exclude_multiple_of: int | None = None, **_: Any) -> dict[str, Any]:
    n = _int(n, "n", 2, 100000)
    total = math.prod(e + 1 for e in sp.factorint(n).values())
    filtered = None
    if multiple_of is not None:
        m = _int(multiple_of, "multiple_of", 2)
        filtered = _multiples_among_divisors(n, m)
        if exclude_multiple_of is not None:
            k = _int(exclude_multiple_of, "exclude_multiple_of", 2)
            filtered -= _multiples_among_divisors(n, math.lcm(m, k))
        if filtered < 1:
            raise ValueError("no_divisor_matches")
    return {"factorization": {str(p): e for p, e in sp.factorint(n).items()}, "total": total, "filtered": filtered}


def _check_divisor_counting(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n = int(givens["n"])
    divisors = [d for d in range(1, n + 1) if n % d == 0]
    if len(divisors) != answer["total"]:
        return False
    m, k = givens.get("multiple_of"), givens.get("exclude_multiple_of")
    if m is None:
        return answer["filtered"] is None
    kept = [d for d in divisors if d % int(m) == 0 and (k is None or d % int(k) != 0)]
    return len(kept) == answer["filtered"]


# --- 9. addition principle with "at least one" -----------------------------------------------------------------------------------

def at_least_one_pairing(head: dict[str, Any], tail: dict[str, Any], **_: Any) -> dict[str, Any]:
    t1, v1, t2, v2 = (_int(head["total"], "head", 2), _int(head["vet"], "head_vet", 1), _int(tail["total"], "tail", 2), _int(tail["vet"], "tail_vet", 1))
    if v1 >= t1 or v2 >= t2:
        raise ValueError("each_group_needs_a_newcomer")
    cases = [v1 * (t2 - v2), (t1 - v1) * v2, v1 * v2]
    return {"cases": cases, "count": sum(cases)}


def _check_at_least_one_pairing(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    h, t = givens["head"], givens["tail"]
    count = sum(1 for i in range(int(h["total"])) for j in range(int(t["total"])) if i < int(h["vet"]) or j < int(t["vet"]))
    return count == answer["count"] == sum(answer["cases"])


def ordered_at_least_one(others: int, special: int, picks: int, **_: Any) -> dict[str, Any]:
    o, s, k = _int(others, "others", 1), _int(special, "special", 1), _int(picks, "picks", 2, 3)
    n = o + s
    if k > o:
        raise ValueError("too_many_picks")
    ordered_all, ordered_plain = math.perm(n, k), math.perm(o, k)
    return {"all": ordered_all, "without_special": ordered_plain, "count": ordered_all - ordered_plain}


def _check_ordered_at_least_one(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    o, s, k = int(givens["others"]), int(givens["special"]), int(givens["picks"])
    people = ["o%d" % i for i in range(o)] + ["s%d" % i for i in range(s)]
    count = sum(1 for seq in itertools.permutations(people, k) if any(p[0] == "s" for p in seq))
    return count == answer["count"]


# --- 10. inclusion-exclusion with two sets ---------------------------------------------------------------------------------------

TWO_SET_KINDS = ("union_and_none", "union", "missing_set", "intersection_range")


def two_set_counting(kind: str, **g: Any) -> dict[str, Any]:
    if kind == "union_and_none" or kind == "union":
        _require(g, "U", "A", "B", "AB")
        u, a, b, ab = _int(g["U"], "U", 1), _int(g["A"], "A", 1), _int(g["B"], "B", 1), _int(g["AB"], "AB", 0)
        if ab > min(a, b) or a + b - ab > u:
            raise ValueError("inconsistent_counts")
        union = a + b - ab
        return {"kind": kind, "union": union, "none": u - union}
    if kind == "missing_set":
        _require(g, "union", "A", "AB")
        union, a, ab = _int(g["union"], "union", 1), _int(g["A"], "A", 1), _int(g["AB"], "AB", 1)
        b = union - a + ab
        if ab > min(a, b) or b < 1 or a > union:
            raise ValueError("inconsistent_counts")
        return {"kind": kind, "missing": b}
    if kind == "intersection_range":
        _require(g, "U", "A", "B")
        u, a, b = _int(g["U"], "U", 1), _int(g["A"], "A", 1), _int(g["B"], "B", 1)
        if a > u or b > u or a + b <= u:
            raise ValueError("range_is_trivial")
        return {"kind": kind, "max": min(a, b), "min": a + b - u}
    raise ValueError(f"unsupported_kind:{kind}")


def _overlap_union(a: int, b: int, overlap: int) -> int:
    first = set(range(a))
    second = set(range(a - overlap, a - overlap + b))
    return len(first | second)


def _check_two_set_counting(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    kind = givens["kind"]
    if kind in ("union_and_none", "union"):
        u, a, b, ab = int(givens["U"]), int(givens["A"]), int(givens["B"]), int(givens["AB"])
        return _overlap_union(a, b, ab) == answer["union"] and answer["none"] == u - answer["union"] >= 0
    if kind == "missing_set":
        union, a, ab = int(givens["union"]), int(givens["A"]), int(givens["AB"])
        return _overlap_union(a, answer["missing"], ab) == union
    u, a, b = int(givens["U"]), int(givens["A"]), int(givens["B"])
    feasible = [k for k in range(0, min(a, b) + 1) if a + b - k <= u and _overlap_union(a, b, k) <= u]
    return min(feasible) == answer["min"] and max(feasible) == answer["max"]


# --- 11. inclusion-exclusion with three sets ------------------------------------------------------------------------------------

THREE_SET_KINDS = ("union_and_none", "union")


def three_set_counting(kind: str, A: int, B: int, C: int, AB: int, BC: int, CA: int, ABC: int, U: int | None = None, **_: Any) -> dict[str, Any]:
    if kind not in THREE_SET_KINDS:
        raise ValueError(f"unsupported_kind:{kind}")
    a, b, c, ab, bc, ca, abc = (_int(v, n, 0) for v, n in ((A, "A"), (B, "B"), (C, "C"), (AB, "AB"), (BC, "BC"), (CA, "CA"), (ABC, "ABC")))
    if min(ab - abc, bc - abc, ca - abc, a - (ab - abc) - (ca - abc) - abc, b - (ab - abc) - (bc - abc) - abc, c - (bc - abc) - (ca - abc) - abc) < 0:
        raise ValueError("impossible_venn_diagram")
    union = a + b + c - ab - bc - ca + abc
    if kind == "union_and_none":
        u = _int(U, "U", 1)
        if union > u:
            raise ValueError("union_exceeds_total")
        return {"kind": kind, "union": union, "none": u - union}
    return {"kind": kind, "union": union}


def _venn_regions(g: dict[str, Any]) -> dict[str, int]:
    a, b, c, ab, bc, ca, abc = (int(g[k]) for k in ("A", "B", "C", "AB", "BC", "CA", "ABC"))
    ab_only, bc_only, ca_only = ab - abc, bc - abc, ca - abc
    return {"abc": abc, "ab": ab_only, "bc": bc_only, "ca": ca_only, "a": a - ab_only - ca_only - abc,
            "b": b - ab_only - bc_only - abc, "c": c - bc_only - ca_only - abc}


def _check_three_set_counting(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    regions = _venn_regions(givens)
    if min(regions.values()) < 0:
        return False
    union = sum(regions.values())
    if union != answer["union"]:
        return False
    return givens["kind"] == "union" or answer["none"] == int(givens["U"]) - union >= 0


# --- 12. multiples of several numbers ----------------------------------------------------------------------------------------------

def multiples_counting(limit: int, divisors: list[int], **_: Any) -> dict[str, Any]:
    n = _int(limit, "limit", 10, 10000)
    ds = _int_list(divisors, "divisors", 2)
    if min(ds) < 2:
        raise ValueError("divisors_start_at_two")
    any_multiple = 0
    for r in range(1, len(ds) + 1):
        for subset in itertools.combinations(ds, r):
            any_multiple += (-1) ** (r + 1) * (n // math.lcm(*subset))
    return {"any": any_multiple, "none": n - any_multiple}


def _check_multiples_counting(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, ds = int(givens["limit"]), [int(d) for d in givens["divisors"]]
    hit = sum(1 for v in range(1, n + 1) if any(v % d == 0 for d in ds))
    return hit == answer["any"] and n - hit == answer["none"]


# --- 13. coin payments -------------------------------------------------------------------------------------------------------------

def coin_payment(coins: list[int], total: int, **_: Any) -> dict[str, Any]:
    c1, c2 = _int_list(coins, "coins", 2)
    t = _int(total, "total", 1)
    if c1 >= c2:
        raise ValueError("coins_ascending")
    combos = [[(t - b * c2) // c1, b] for b in range(t // c2 + 1) if (t - b * c2) % c1 == 0]
    if len(combos) < 2:
        raise ValueError("needs_two_or_more_ways")
    return {"ways": len(combos), "combos": combos}


def _check_coin_payment(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    c1, c2, t = int(givens["coins"][0]), int(givens["coins"][1]), int(givens["total"])
    ways = [[a, b] for a in range(t // c1 + 1) for b in range(t // c2 + 1) if a * c1 + b * c2 == t]
    return sorted(ways) == sorted(answer["combos"]) and len(ways) == answer["ways"]


# --- 14. two dice ---------------------------------------------------------------------------------------------------------------------

def dice_sum_multiples(modulus: int, sides: int = 6, **_: Any) -> dict[str, Any]:
    k, s = _int(modulus, "modulus", 3, 11), _int(sides, "sides", 4, 12)
    freq: dict[int, int] = {}
    for total in range(2, 2 * s + 1):
        freq[total] = min(total - 1, 2 * s + 1 - total)
    sums = [t for t in freq if t % k == 0]
    if not sums:
        raise ValueError("no_such_sum")
    return {"sums": sums, "count": sum(freq[t] for t in sums)}


def _check_dice_sum_multiples(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    k, s = int(givens["modulus"]), int(givens.get("sides", 6))
    count = sum(1 for a in range(1, s + 1) for b in range(1, s + 1) if (a + b) % k == 0)
    return count == answer["count"]


# --- 15. first to win n games --------------------------------------------------------------------------------------------------------

def race_outcomes(wins_needed: int, winner: str = "甲", **_: Any) -> dict[str, Any]:
    n = _int(wins_needed, "wins_needed", 2, 5)
    if winner not in ("甲", "乙"):
        raise ValueError("winner_is_one_of_the_two_players")
    per_winner = sum(math.comb(n - 1 + lost, lost) for lost in range(n))
    return {"total": 2 * per_winner, "winner_wins": per_winner}


def _check_race_outcomes(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n = int(givens["wins_needed"])
    finished: list[str] = []

    def play(seq: str) -> None:
        if seq.count("a") == n or seq.count("b") == n:
            finished.append(seq)
            return
        play(seq + "a")
        play(seq + "b")

    play("")
    a_wins = sum(1 for s in finished if s.count("a") == n)
    return len(finished) == answer["total"] and a_wins == answer["winner_wins"] and len(finished) - a_wins == a_wins


# --- 16. simple paths in a graph ------------------------------------------------------------------------------------------------------

def graph_paths(vertices: list[str], edges: list[list[str]], start: str, end: str, **_: Any) -> dict[str, Any]:
    if start == end or start not in vertices or end not in vertices or len(set(vertices)) != len(vertices):
        raise ValueError("bad_endpoints")
    adjacency: dict[str, set[str]] = {v: set() for v in vertices}
    for p, q in edges:
        if p == q or p not in adjacency or q not in adjacency:
            raise ValueError("bad_edge")
        adjacency[p].add(q)
        adjacency[q].add(p)
    paths: list[str] = []

    def walk(path: list[str]) -> None:
        last = path[-1]
        if last == end:
            paths.append("".join(path))
            return
        for nxt in sorted(adjacency[last]):
            if nxt not in path:
                walk(path + [nxt])

    walk([start])
    if not paths:
        raise ValueError("no_path")
    return {"count": len(paths), "paths": paths}


def _check_graph_paths(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    vertices, start, end = list(givens["vertices"]), givens["start"], givens["end"]
    edge_set = {frozenset(e) for e in givens["edges"]}
    inner = [v for v in vertices if v not in (start, end)]
    found = []
    for r in range(len(inner) + 1):
        for middle in itertools.permutations(inner, r):
            chain = (start, *middle, end)
            if all(frozenset(pair) in edge_set for pair in zip(chain, chain[1:])):
                found.append("".join(chain))
    return sorted(found) == sorted(answer["paths"]) and len(found) == answer["count"]


# --- 17. coin tosses with early stop -----------------------------------------------------------------------------------------------

def coin_toss_sequences(max_tosses: int, run: int = 2, **_: Any) -> dict[str, Any]:
    n, r = _int(max_tosses, "max_tosses", 2, 8), _int(run, "run", 2, 3)
    if n < r:
        raise ValueError("fewer_tosses_than_the_run")
    live = {("H", 1): 1, ("T", 1): 1}
    ended = 0
    for length in range(2, n + 1):
        nxt: dict[tuple[str, int], int] = {}
        for (face, streak), count in live.items():
            for new in "HT":
                streak2 = streak + 1 if new == face else 1
                if streak2 == r or length == n:
                    ended += count
                else:
                    nxt[(new, streak2)] = nxt.get((new, streak2), 0) + count
        live = nxt
    return {"count": ended}


def _check_coin_toss_sequences(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    n, r = int(givens["max_tosses"]), int(givens.get("run", 2))
    done: list[str] = []

    def toss(seq: str) -> None:
        if len(seq) >= r and len(set(seq[-r:])) == 1 or len(seq) == n:
            done.append(seq)
            return
        toss(seq + "H")
        toss(seq + "T")

    toss("")
    return len(done) == answer["count"] and len(set(done)) == len(done)


# --- 18. tilings with 1x1 and 1x2 tiles -----------------------------------------------------------------------------------------------

def _cells(cells: Any) -> list[tuple[int, int]]:
    out = sorted((_int(c[0], "x"), _int(c[1], "y")) for c in cells)
    if len(set(out)) != len(out) or not 2 <= len(out) <= 12:
        raise ValueError("bad_region")
    return out


def tiling_count(cells: list[list[int]], ask: dict[str, Any], **_: Any) -> dict[str, Any]:
    region = _cells(cells)
    free = set(region)
    distribution: dict[int, int] = {}

    def cover(used: int) -> None:
        todo = [c for c in region if c in free]
        if not todo:
            distribution[used] = distribution.get(used, 0) + 1
            return
        x, y = todo[0]
        free.discard((x, y))
        cover(used)  # a 1x1 tile
        for other in ((x + 1, y), (x, y + 1)):  # a 1x2 tile, horizontal or vertical (the cell is the lowest-left free one)
            if other in free:
                free.discard(other)
                cover(used + 1)
                free.add(other)
        free.add((x, y))

    cover(0)
    kind, k = ask["kind"], ask.get("k")
    if kind == "total":
        value = sum(distribution.values())
    elif kind == "exactly":
        value = distribution.get(_int(k, "k", 0), 0)
    elif kind == "at_least":
        value = sum(v for used, v in distribution.items() if used >= _int(k, "k", 1))
    else:
        raise ValueError(f"unsupported_ask:{kind}")
    if value < 1:
        raise ValueError("nothing_to_count")
    return {"distribution": {str(u): v for u, v in sorted(distribution.items())}, "value": value}


def _check_tiling_count(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    region = _cells(givens["cells"])
    index = {c: i for i, c in enumerate(region)}
    edges = [(index[(x, y)], index[(x + dx, y + dy)]) for (x, y) in region for dx, dy in ((1, 0), (0, 1)) if (x + dx, y + dy) in index]
    if len(edges) > 20:
        return False
    by_size: dict[int, int] = {}
    for mask in range(1 << len(edges)):
        used: set[int] = set()
        ok, size = True, 0
        for i, (p, q) in enumerate(edges):
            if mask >> i & 1:
                if p in used or q in used:
                    ok = False
                    break
                used.update((p, q))
                size += 1
        if ok:
            by_size[size] = by_size.get(size, 0) + 1
    if {str(u): v for u, v in sorted(by_size.items())} != answer["distribution"]:
        return False
    kind, k = givens["ask"]["kind"], givens["ask"].get("k")
    want = sum(by_size.values()) if kind == "total" else by_size.get(int(k), 0) if kind == "exactly" else sum(v for u, v in by_size.items() if u >= int(k))
    return want == answer["value"]


# --- 19. a counting claim to mark true or false ---------------------------------------------------------------------------------------

def region_pairs_claim(south: int, north: int, claimed: int, relation: str = "same_region", **_: Any) -> dict[str, Any]:
    s, n, claim = _int(south, "south", 2), _int(north, "north", 2), _int(claimed, "claimed", 1)
    if relation == "same_region":
        actual = math.comb(s, 2) + math.comb(n, 2)
    elif relation == "different_regions":
        actual = s * n
    else:
        raise ValueError(f"unsupported_relation:{relation}")
    return {"actual": actual, "truth": claim == actual}


def _check_region_pairs_claim(givens: dict[str, Any], answer: dict[str, Any]) -> bool:
    teams = [("S", i) for i in range(int(givens["south"]))] + [("N", i) for i in range(int(givens["north"]))]
    same = givens.get("relation", "same_region") == "same_region"
    actual = sum(1 for p, q in itertools.combinations(teams, 2) if (p[0] == q[0]) == same)
    return actual == answer["actual"] and (int(givens["claimed"]) == actual) == answer["truth"]


# --- registry / entrypoint ---------------------------------------------------------------------------------------------------------------

_OPERATIONS: dict[str, tuple[Callable[..., dict[str, Any]], Callable[[dict[str, Any], dict[str, Any]], bool], tuple[str, ...]]] = {
    "interval_set_operations": (interval_set_operations, _check_interval_set_operations, ("A", "B", "items")),
    "finite_set_operations": (finite_set_operations, _check_finite_set_operations, ("A", "B", "items")),
    "equation_root_sets": (equation_root_sets, _check_equation_root_sets, ("A", "B", "items")),
    "proposition_truth": (proposition_truth, _check_proposition_truth, ("atoms", "options", "mode")),
    "implication_truth": (implication_truth, _check_implication_truth, ("claim",)),
    "condition_relation": (condition_relation, _check_condition_relation, ("cond", "target")),
    "choice_product": (choice_product, _check_choice_product, ("groups",)),
    "grade_selection": (grade_selection, _check_grade_selection, ("grades",)),
    "divisor_counting": (divisor_counting, _check_divisor_counting, ("n",)),
    "at_least_one_pairing": (at_least_one_pairing, _check_at_least_one_pairing, ("head", "tail")),
    "ordered_at_least_one": (ordered_at_least_one, _check_ordered_at_least_one, ("others", "special", "picks")),
    "two_set_counting": (two_set_counting, _check_two_set_counting, ("kind",)),
    "three_set_counting": (three_set_counting, _check_three_set_counting, ("kind", "A", "B", "C", "AB", "BC", "CA", "ABC")),
    "multiples_counting": (multiples_counting, _check_multiples_counting, ("limit", "divisors")),
    "coin_payment": (coin_payment, _check_coin_payment, ("coins", "total")),
    "dice_sum_multiples": (dice_sum_multiples, _check_dice_sum_multiples, ("modulus",)),
    "race_outcomes": (race_outcomes, _check_race_outcomes, ("wins_needed",)),
    "graph_paths": (graph_paths, _check_graph_paths, ("vertices", "edges", "start", "end")),
    "coin_toss_sequences": (coin_toss_sequences, _check_coin_toss_sequences, ("max_tosses",)),
    "tiling_count": (tiling_count, _check_tiling_count, ("cells", "ask")),
    "region_pairs_claim": (region_pairs_claim, _check_region_pairs_claim, ("south", "north", "claimed")),
}
OPERATIONS = tuple(_OPERATIONS)


def build_counting_sets_matrix(
    *, domain_operation: str | None = None, seed: int | None = None, constraints: dict[str, Any] | None = None, **_: Any
) -> dict[str, Any]:
    operation = str(domain_operation or "").strip()
    if operation not in _OPERATIONS:
        raise ValueError(f"unsupported_counting_sets_operation:{operation}")
    solve, _check, required = _OPERATIONS[operation]
    givens = {k: v for k, v in (constraints or {}).items() if k not in ("skill_id",)}
    _require(givens, *required)
    answer = solve(**givens)
    return {
        "domain": DOMAIN_KEY,
        "domain_operation": operation,
        "givens": givens,
        "answer": answer,
        "validation_facts": {"domain_operation": operation, "seed": 0 if seed is None else int(seed)},
    }


def _make_validator(operation: str) -> Callable[[Any], bool]:
    check = _OPERATIONS[operation][1]

    def validate(matrix: Any) -> bool:
        try:
            facts = matrix.get("validation_facts") or {}
            if matrix.get("domain") != DOMAIN_KEY or matrix.get("domain_operation") != operation or facts.get("domain_operation") != operation:
                return False
            return bool(check(matrix["givens"], matrix["answer"]))
        except Exception:
            return False

    validate.__name__ = f"validate_{operation}_matrix"
    return validate


for _op in _OPERATIONS:
    globals()[f"validate_{_op}_matrix"] = _make_validator(_op)
