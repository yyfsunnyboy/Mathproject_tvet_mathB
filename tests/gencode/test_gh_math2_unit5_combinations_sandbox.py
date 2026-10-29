"""Sandbox gate for 普高數學2 Unit 5 (組合、二項式定理), skills gh_Combination / gh_BinomialTheorem.

Builds ``tmp/gh_math2_unit5_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived (and, where the textbook prints a solution, checked against it); the textbook rows are read from a private
snapshot of the Stage 1 database.  Every generated stem is also RE-SOLVED here from the text it prints (numbers, names, letters, the LaTeX
expression), by brute-force enumeration or sympy, so a varied question is proved to keep its mathematical meaning independently of the givens
that produced it.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import re
import sqlite3
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp

from agent_domains_candidate.combinations import build_sandbox as B
from agent_domains_candidate.combinations import combinations_domain as D
from agent_domains_candidate.combinations.combinations_specs import COMPONENTS, FIXED_ROWS, OP, SKILLS
from agent_domains_candidate.combinations.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.combinations.verification import grade, verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = B.isolated_db()
SEEDS = range(20)
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
FLOOR = {12829: 9}  # teachers 2-4 x students per group: a small family of genuinely different questions
UNIT_IDS = set(range(12812, 12849))
ZH = {"一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}
FIGURE_CUES = ("如圖", "右圖", "下圖", "在圖", "左圖", "上圖")


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u5_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


def _answers(payload: dict):
    ans = payload["correct_answer"]
    if isinstance(ans, dict):
        return [ans[k] for k in sorted(ans, key=lambda k: int(k.split("_")[1]))]
    return ans


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator, metadata = _load(cid, "generate.py"), _load(cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation
    surfaces = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == D.DOMAIN_KEY
        text = payload["question_text"]
        assert "$$" not in text and "承例題" not in text and "承上" not in text and "MATH_PARSE_FAILED" not in text
        assert not any(cue in text for cue in FIGURE_CUES)  # no dynamic question of this unit has a picture
        assert not payload.get("visual_spec") and not payload.get("image_assets") and not payload.get("reuse_textbook_image")
        assert not payload["answer_contract"].get("answer_format_example")  # nothing a student sees before submitting can name the answer
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= FLOOR.get(cid, 10), len(surfaces)


def test_coverage_and_fixed_items_are_explicit():
    assert set(COMPONENTS) | set(FIXED_ROWS) == UNIT_IDS and len(UNIT_IDS) == 37
    assert not set(COMPONENTS) & set(FIXED_ROWS)
    assert len(COMPONENTS) == 34 and set(FIXED_ROWS) == {12834, 12838, 12845}
    assert all(len(reason) > 20 for reason in FIXED_ROWS.values())
    per_skill = {skill: sum(1 for s in COMPONENTS.values() if SKILLS[s[0]] == skill) for skill in SKILLS.values()}
    assert per_skill == {"gh_Combination": 22, "gh_BinomialTheorem": 12}
    from agent_domains_candidate.combinations.combinations_specs import SKILL_OPERATIONS

    for key, ops in SKILL_OPERATIONS.items():  # every component's operation is allowed for its own skill
        assert {s[1] for s in COMPONENTS.values() if s[0] == key} <= set(ops)
    assert set(D.OPERATIONS) == set(OP) == {s[1] for s in COMPONENTS.values()}


def test_skill_bindings_and_stems_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: (r[1], r[2]) for r in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12812 and 12848")}
    finally:
        con.close()
    assert len(rows) == 37
    assert Counter(s for s, _t in rows.values()) == {"gh_Combination": 23, "gh_BinomialTheorem": 14}
    for cid in COMPONENTS:
        assert rows[cid][0] == _skill_of(cid), cid
    assert rows[12834][0] == "gh_Combination" and rows[12838][0] == rows[12845][0] == "gh_BinomialTheorem"
    digits = lambda t: set(re.findall(r"\d+", re.sub(r"\s", "", re.sub(r"\\[a-zA-Z]+", "", t))))  # noqa: E731
    for cid in COMPONENTS:  # variant 0 is the textbook question: every number the textbook stem prints appears in the generated stem
        source, stem = rows[cid][1], _gen(cid, 0)["question_text"]
        assert digits(source) <= digits(stem) | {"1", "2", "3"}, (cid, digits(source) - digits(stem))


# --- hand-derived source oracles ---------------------------------------------------------------------------------------------------------

SOURCE_ORACLES = {
    12812: ["45", "45", "1"], 12813: ["120", "56"], 12814: "54", 12815: "15", 12816: ["90", "15", "15"], 12817: ["210", "35", "120"],
    12818: ["21", "10"], 12819: "198", 12820: "90", 12821: ["35", "280"], 12822: ["1", "3", "4", "5"], 12823: "A", 12824: "B", 12825: "A",
    12826: "1770", 12827: "210", 12828: ["210", "460", "455"], 12829: "12", 12830: "36", 12831: "12", 12832: "66", 12833: "72",
    12835: "x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4+y^5", 12836: "16x^4-32x^3y+24x^2y^2-8xy^3+y^4", 12837: "160", 12839: "1024", 12840: "A",
    12841: "10", 12842: "x^4+4x^3y+6x^2y^2+4xy^3+y^4", 12843: ["-41", "29"], 12844: "60", 12846: "2036", 12847: "35", 12848: "-1",
}


def test_source_oracles_by_hand():
    assert set(SOURCE_ORACLES) == set(COMPONENTS)
    for cid, want in SOURCE_ORACLES.items():
        assert _answers(_gen(cid, 0)) == want, cid
    # a few of them by hand, written out (independent of every code path above)
    assert 10 * 9 // 2 == 45 and 2 * (8 * 7 // 2) == 56 and (3 * 2 + 3 * 1) * 6 == 54 and 15 * 1 == 15
    assert 15 * 6 * 1 == 90 and 90 // 6 == 15 and (15 * 2) // 2 == 15 and 7 * 6 // 2 == 21 and 5 * 4 // 2 == 10
    assert (2 * 3 * 4 + 2 * 3 + 1 * 3) * 6 == 198 and 70 // 2 == 35 and 56 * 10 // 2 == 280
    assert 60 * 59 // 2 == 1770 and 35 * 6 == 210 and 21 * 10 == 210 and 495 - 35 == 460 and 495 - 35 - 5 == 455
    assert 2 * 6 == 12 and 6 * 6 == 36 and 12 * 11 // 2 == 66 and 1 + 10 * 6 + 5 == 66 and 5 * 4 * 3 + 4 * 3 == 72
    assert 20 * 8 == 160 and 2 ** 10 == 1024 and 2 ** 10 - 1 == 1023 and 15 * 4 == 60 and 35 == 7 * 6 * 5 // 6 and 2 ** 11 - 1 - 11 == 2036
    assert 10 + 5 * (-1) == 5 and (-41) ** 2 - 2 * 29 ** 2 == (-1) ** 5  # a² − 2b² is the norm of (√2 − 1)^5, i.e. (1 − 2)^5


def test_oracles_agree_with_the_solutions_printed_in_the_textbook():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        solutions = {r[0]: r[1] or "" for r in con.execute("select id, detailed_solution from textbook_examples where id between 12812 and 12848")}
    finally:
        con.close()
    printed = {12812: ["45", "1"], 12813: ["120", "56"], 12814: ["54"], 12815: ["15"], 12816: ["90", "15"], 12837: ["160"], 12839: ["1024"]}
    for cid, numbers in printed.items():
        tokens = set(re.findall(r"\d+", re.sub(r"\\rm|[{} ]", "", solutions[cid])))
        assert set(numbers) <= tokens, (cid, numbers, tokens)
    for cid, coeffs in ((12835, ["5", "10"]), (12836, ["16", "32", "24", "8"])):  # the expanded polynomial printed in the solution
        assert set(coeffs) <= set(re.findall(r"\d+", solutions[cid]))


# --- every stem re-solved from its own text ---------------------------------------------------------------------------------------------------------

def _nums(text: str) -> list[int]:
    return [int(v) for v in re.findall(r"\$([+-]?\d+)\$", text)]


def _comb_count(n: int, k: int, test=lambda s: True) -> int:
    return sum(1 for s in itertools.combinations(range(n), k) if test(s))


def _assignments(n: int, sizes: list[int], labeled: bool) -> int:
    g = len(sizes)
    fits = [t for t in itertools.product(range(g), repeat=n) if all(t.count(j) == sizes[j] for j in range(g))]
    if labeled:
        return len(fits)
    return len({frozenset(frozenset(i for i in range(n) if t[i] == j) for j in range(g)) for t in fits})


_X = sp.Symbol("x")


def _latex_to_sympy(tex: str):
    s = tex.replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\sqrt\{(\d+)\}", r"sqrt(\1)", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", s)
    while "\\frac" in s:
        s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
    s = re.sub(r"(\d)([a-z(])", r"\1*\2", s)
    s = re.sub(r"\)([a-z(\d])", r")*\1", s)
    return sp.sympify(s)


def _bags(line: str) -> list[int]:
    if m := re.search(r"每袋裝 \$(\d+)\$", line):
        return [int(m.group(1))] * ZH[re.search(r"裝入(.)個相同的袋子", line).group(1)]
    out = []
    for count, size in re.findall(r"(?:其中|另)(.)袋各?裝 \$(\d+)\$", line):
        out += [int(size)] * ZH[count]
    return out


def _groups(line: str, n: int) -> list[int]:
    if m := re.search(r"平分成(.)組", line):
        g = ZH[m.group(1)]
        return [n // g] * g
    out = []
    for count, size in re.findall(r"(?:其中|另)(.)組各?有 \$(\d+)\$", line):
        out += [int(size)] * ZH[count]
    return out


def _claim_value(tex: str) -> int:
    if m := re.fullmatch(r"C_\{(\d+)\}\^\{(\d+)\}", tex):
        return _comb_count(int(m.group(2)), int(m.group(1)))
    m = re.fullmatch(r"P_\{(\d+)\}\^\{(\d+)\}", tex)
    return sum(1 for _ in itertools.permutations(range(int(m.group(2))), int(m.group(1))))


def resolve(cid: int, text: str):
    """The correct answer, recomputed from the printed stem alone."""
    nums = _nums(text)
    if cid in (12812, 12817):
        out = []
        for item in re.findall(r"\(\d\)\$(.+?)\$。", text):
            if m := re.fullmatch(r"\\frac\{P_\{(\d+)\}\^\{(\d+)\}\}\{C_\{(\d+)\}\^\{(\d+)\}\}", item):
                k, n = int(m.group(1)), int(m.group(2))
                out.append(str(math.prod(range(n - k + 1, n + 1)) // _comb_count(n, k)))
            else:
                k, n = (int(v) for v in re.fullmatch(r"C_\{(\d+)\}\^\{(\d+)\}", item).groups())
                out.append(str(_comb_count(n, k)))
        return out
    if cid in (12813, 12818):
        n, k = nums[0], nums[1]
        out = []
        for line in text.split("\n")[1:]:
            if "共有多少種選法？" == line[3:]:
                test = lambda c: True  # noqa: E731
            elif "恰" in line:
                test = lambda c: c == 1  # noqa: E731
            elif "至少" in line:
                test = lambda c: c >= 1  # noqa: E731
            elif "都不能" in line:
                test = lambda c: c == 0  # noqa: E731
            else:
                assert "一定都要" in line, line
                test = lambda c: c == 2  # noqa: E731
            out.append(str(_comb_count(n, k, lambda s, t=test: t(sum(1 for v in s if v < 2)))))
        return out
    if cid == 12814:
        b, g = nums[0], nums[1]
        return str(sum(1 for t in itertools.permutations(range(b + g), 3) if any(v < b for v in t) and any(v >= b for v in t)))
    if cid == 12819:
        a, b, c = nums[:3]
        return str(sum(1 for t in itertools.permutations(range(a + b + c), 3) if any(v < a for v in t) and any(a <= v < a + b for v in t)))
    if cid == 12815:
        sizes = [int(v) for v in re.findall(r"[ABC]房住 \$(\d+)\$ 人", text)]
        return str(_assignments(nums[0], sizes, True))
    if cid == 12820:
        n = nums[0]
        if m := re.search(r"每班各 \$(\d+)\$ 人", text):
            sizes = [int(m.group(1))] * ZH[re.search(r"([兩三四])班", text).group(1)]
        else:
            sizes = [int(v) for v in re.findall(r"[甲乙丙丁]班 \$(\d+)\$ 人", text)]
        return str(_assignments(n, sizes, True))
    if cid == 12816:
        n, out = nums[0], []
        for line in text.split("\n")[1:]:
            if "分給" in line:
                people = ZH[re.search(r"([兩三四])人", line).group(1)]
                m = re.search(r"每人各得 \$(\d+)\$ 本", line)
                sizes = [int(m.group(1))] * people if m else [int(v) for v in re.findall(r"得 \$(\d+)\$ 本", line)]
                out.append(str(_assignments(n, sizes, True)))
            else:
                out.append(str(_assignments(n, _bags(line), False)))
        return out
    if cid == 12821:
        n = nums[0]
        return [str(_assignments(n, _groups(line, n), False)) for line in text.split("\n")[1:]]
    if cid == 12822:
        selected = []
        for i, item in enumerate(re.findall(r"^\(\d\)\$(.+)\$$", text, flags=re.M), 1):
            lhs, rhs = item.split("=")
            value = sum((-1 if sign == "-" else 1) * math.comb(int(n), int(k)) for sign, k, n in re.findall(r"([+-]?)C_\{(\d+)\}\^\{(\d+)\}", lhs))
            rk, rn = (int(v) for v in re.fullmatch(r"C_\{(\d+)\}\^\{(\d+)\}", rhs).groups())
            if value == math.comb(rn, rk):
                selected.append(str(i))
        return selected
    if cid == 12823:
        n, k = nums[0], nums[1]
        claim = re.search(r"組合數為 \$(.+?)\$", text).group(1)
        return "A" if _comb_count(n, k) == _claim_value(claim) else "B"
    if cid == 12824:
        k, n, m, pk, pn = (int(v) for v in re.search(r"C_\{(\d+)\}\^\{(\d+)\}\\times (\d+)!=P_\{(\d+)\}\^\{(\d+)\}", text).groups())
        return "A" if _comb_count(n, k) * math.factorial(m) == _claim_value(f"P_{{{pk}}}^{{{pn}}}") else "B"
    if cid == 12825:
        a, n, b, n2 = (int(v) for v in re.search(r"C_\{(\d+)\}\^\{(\d+)\}=C_\{(\d+)\}\^\{(\d+)\}", text).groups())
        return "A" if math.comb(n, a) == math.comb(n2, b) else "B"
    if cid == 12840:
        n = int(re.search(r"\\right\)\^\{(\d+)\}", text).group(1))
        x, y = sp.symbols("x y")
        poly = sp.Poly(sp.expand((x + y) ** n), x, y)
        monos = re.findall(r"\$(x(?:\^\{\d+\})?y(?:\^\{\d+\})?)\$ 項", text)
        coeffs = []
        for mono in monos:
            ex = re.fullmatch(r"x(?:\^\{(\d+)\})?y(?:\^\{(\d+)\})?", mono).groups()
            coeffs.append(poly.coeff_monomial(x ** int(ex[0] or 1) * y ** int(ex[1] or 1)))
        return "A" if coeffs[0] == coeffs[1] else "B"
    if cid == 12826:
        return str(_comb_count(nums[0], 2))
    if cid == 12831:
        return str(next(n for n in range(2, 300) if _comb_count(n, 2) == nums[0]))
    if cid == 12827:
        n, ks = nums[0], nums[1:]
        return str(sum(1 for t in itertools.product(range(len(ks) + 1), repeat=n) if all(t.count(j + 1) == ks[j] for j in range(len(ks)))))
    if cid == 12828:
        b, g, p, i = nums[:4]
        boys = lambda s: sum(1 for v in s if v < b)  # noqa: E731
        return [str(_comb_count(b + g, p, lambda s: boys(s) == i)), str(_comb_count(b + g, p, lambda s: boys(s) < p)),
                str(_comb_count(b + g, p, lambda s: 0 < boys(s) < p))]
    if cid == 12829:
        t, s, per = nums[0], nums[1], nums[4]
        students = sum(1 for a in itertools.product(range(t), repeat=s) if all(a.count(j) == per for j in range(t)))
        return str(students * math.factorial(t))
    if cid == 12830:
        n, m = nums[0], nums[1]
        return str(sum(1 for a in itertools.product(range(m), repeat=n) if len(set(a)) == m))
    if cid == 12832:
        top = max(int(v) for v in re.search(r"從([\d, ]+)這", text).group(1).split(","))
        want = 0 if "其和為偶數" in text else 1
        return str(sum(1 for c in itertools.combinations(range(1, top + 1), nums[0]) if sum(c) % 2 == want))
    if cid == 12833:
        word = re.search(r"「([a-z]+)」", text).group(1)
        return str(len(set(itertools.permutations(word, nums[1]))))
    if cid in (12835, 12836, 12842):
        base, n = re.search(r"\$\\left\((.+?)\\right\)\^\{(\d+)\}\$", text).groups()
        return sp.expand(_latex_to_sympy(base) ** int(n))
    if cid == 12843:
        base, n = re.search(r"\$\\left\((.+?)\\right\)\^\{(\d+)\}=", text).groups()
        p = int(re.search(r"sqrt\{(\d+)\}", base).group(1))
        value = sp.expand(_latex_to_sympy(base) ** int(n))
        b = value.coeff(sp.sqrt(p))
        return [str(sp.simplify(value - b * sp.sqrt(p))), str(b)]
    if cid in (12837, 12844, 12847):
        base, n = re.search(r"\$\\left\((.+?)\\right\)\^\{(\d+)\}\$", text).groups()
        terms = sp.expand(_latex_to_sympy(base) ** int(n)).as_coefficients_dict()
        if "常數項" in text:
            return str(terms.get(sp.Integer(1), 0))
        m = re.search(r"\$x(?:\^\{(\d+)\})?\$ 項的係數", text)
        return str(terms.get(_X ** int(m.group(1) or 1), 0))
    if cid in (12839, 12846):
        n, k = nums[0], nums[1]
        return str(sum(1 for mask in range(1 << n) if bin(mask).count("1") >= k))
    if cid == 12841:
        lo, start, hi = re.search(r"\$(\d+)<C_\{(\d)\}\^\{n\}.*<(\d+)\$", text).groups()
        found = [n for n in range(1, 40) if int(lo) < sum(math.comb(n, j) for j in range(int(start), n + 1)) < int(hi)]
        assert len(found) == 1
        return str(found[0])
    if cid == 12848:
        n = int(re.search(r"\\left\(1\+x\\right\)\^\{(\d+)\}", text).group(1))
        m = int(re.search(r"\$x\^\{(\d+)\}\$ 項的係數", text).group(1))
        a = sp.Symbol("a")
        coeff = sp.Poly(sp.expand((1 + a * _X) * (1 + _X) ** n), _X).coeff_monomial(_X ** m)
        (root,) = sp.solve(sp.Eq(coeff, nums[-1]), a)
        return str(Fraction(int(sp.numer(root)), int(sp.denom(root))))
    raise AssertionError(f"no re-solver for {cid}")


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_every_generated_stem_is_resolved_to_the_same_answer_from_its_text(cid):
    for seed in SEEDS:
        payload = _gen(cid, seed)
        expected = resolve(cid, payload["question_text"])
        if isinstance(expected, sp.Expr):  # an expansion: the canonical answer equals the expanded power and is itself expanded
            got = sp.sympify(re.sub(r"(\d)([a-z])", r"\1*\2", re.sub(r"([a-z])(?=[a-z])", r"\1*", _answers(payload))).replace("^", "**"))
            assert sp.expand(got - expected) == 0 and got == sp.expand(got), (cid, seed)
            continue
        assert _answers(payload) == expected, (cid, seed, payload["question_text"][:80])


# --- the shared validators reject tampered answers ------------------------------------------------------------------------------------------------

def _tamper(op: str, answer: dict) -> dict:
    bad = json.loads(json.dumps(answer))
    if op in ("combination_evaluate", "select_with_members", "group_partition", "gender_committee"):
        item = bad["items"][0]
        item["value" if "value" in item else "count"] += 1
    elif op == "combination_claim":
        bad["truth"] = not bad["truth"]
    elif op == "combination_identity_select":
        bad["selected"] = bad["selected"][:-1] if len(bad["selected"]) > 1 else bad["selected"] + [9]
    elif op == "binomial_expansion":
        bad["terms"][0][0] = str(Fraction(bad["terms"][0][0]) + 1)
    elif op == "radical_binomial_power":
        bad["a"] += 1
    elif op == "general_term_coefficient":
        bad["coefficient"] += 1
    elif op == "coefficient_solve_parameter":
        bad["a"] = str(Fraction(bad["a"]) + 1)
    elif op == "binomial_sum_bound" or (op == "pair_count" and bad["mode"] == "solve_n"):
        bad["n"] += 1
    else:
        bad["count"] += 1
    return bad


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_validators_reject_a_tampered_answer(cid, skill_id, operation):
    _s, op, source, _sampler = COMPONENTS[cid]
    matrix = D.build_combinations_matrix(domain_operation=op, constraints=dict(source))
    validate = getattr(D, f"validate_{op}_matrix")
    assert validate(matrix) is True
    assert validate({**matrix, "answer": _tamper(op, matrix["answer"])}) is False
    assert validate({**matrix, "domain_operation": "other"}) is False and validate("not a matrix") is False


def test_domain_refuses_degenerate_or_inconsistent_input():
    mk = lambda op, **g: D.build_combinations_matrix(domain_operation=op, constraints=g)  # noqa: E731
    for op, givens in [
        ("combination_evaluate", {"items": [{"kind": "comb", "n": 5, "k": 7}]}), ("combination_evaluate", {"items": [{"kind": "bogus", "n": 5, "k": 2}]}),
        ("combination_evaluate", {"items": []}), ("select_with_members", {"n": 6, "k": 6, "asks": ["total"]}),
        ("select_with_members", {"n": 6, "k": 2, "asks": ["both", "both"]}), ("select_with_members", {"n": 4, "k": 3, "asks": ["neither"]}),
        ("mixed_group_ordered", {"groups": [3, 2], "pick": 3, "require": [0, 0]}), ("mixed_group_ordered", {"groups": [3], "pick": 2, "require": [0]}),
        ("group_partition", {"n": 6, "asks": [{"sizes": [4, 1], "labeled": True}]}), ("group_partition", {"n": 6, "asks": [{"sizes": [3, 3], "labeled": "yes"}]}),
        ("combination_identity_select", {"statements": [{"form": "symmetry", "n": 10, "a": 3, "rhs": [10, 4]}] * 3}),
        ("combination_identity_select", {"statements": [{"form": "bogus", "n": 10, "a": 3, "rhs": [10, 4]}] * 3}),
        ("combination_claim", {"setting": {"kind": "comb_equal", "n": 10, "a": 3, "b": 3}}), ("combination_claim", {"setting": {"kind": "bogus"}}),
        ("pair_count", {"mode": "solve_n", "total": 50}), ("pair_count", {"mode": "bogus", "n": 5}),
        ("sequential_selection", {"n": 5, "ks": [3, 3]}), ("gender_committee", {"boys": 3, "girls": 2, "pick": 3, "asks": [{"kind": "exact", "boys": 0}]}),
        ("paired_group_assignment", {"teachers": 2, "students": 5}), ("surjective_distribution", {"people": 2, "places": 3}),
        ("parity_sum_selection", {"top": 9, "pick": 4, "parity": "prime"}), ("multiset_select_arrange", {"word": "abcde", "pick": 3}),
        ("binomial_expansion", {"a": 0, "b": 1, "n": 4, "vars": ["x", "y"]}), ("binomial_expansion", {"a": 1, "b": 1, "n": 4, "vars": ["y", "x"]}),
        ("radical_binomial_power", {"radicand": 4, "constant": 1, "n": 3}), ("radical_binomial_power", {"radicand": 2, "constant": 0, "n": 3}),
        ("general_term_coefficient", {"c1": 1, "p1": 2, "c2": 2, "p2": -1, "n": 6, "target": 4}),
        ("at_least_k_selection", {"n": 5, "k": 0}), ("binomial_sum_bound", {"low": 100, "high": 5000, "start": 1}),
        ("coefficient_solve_parameter", {"n": 5, "m": 2, "value": 10}),
    ]:
        with pytest.raises(ValueError):
            mk(op, **givens)
    with pytest.raises(ValueError):
        D.build_combinations_matrix(domain_operation="nonexistent", constraints={})
    with pytest.raises(ValueError):
        D.build_combinations_matrix(domain_operation="pair_count", constraints={"n": 5})


def test_claim_and_selection_operations_cover_both_outcomes():
    for cid in (12823, 12824, 12825, 12840):
        labels = {_gen(cid, s)["correct_answer"] for s in SEEDS}
        assert labels == {"A", "B"}, (cid, labels)  # both a correct and an incorrect statement appear among the variants
    selections = {tuple(_gen(12822, s)["correct_answer"]) for s in SEEDS}
    assert len(selections) >= 5 and any(len(s) < 5 for s in selections)


def test_expansion_answers_require_the_expanded_form_and_accept_reordered_terms():
    for cid in (12835, 12836, 12842):
        for seed in range(0, 20, 3):
            payload = _gen(cid, seed)
            base, n = re.search(r"\$\\left\((.+?)\\right\)\^\{(\d+)\}\$", payload["question_text"]).groups()
            unexpanded = f"({base})^{n}"
            assert grade(payload, payload["correct_answer"], _skill_of(cid))
            assert not grade(payload, unexpanded, _skill_of(cid)), unexpanded  # 展開式: the power itself is not an answer
            terms = re.findall(r"[+-]?[^+-]+", payload["correct_answer"])
            assert grade(payload, "".join(t if t[0] in "+-" else "+" + t for t in reversed(terms)).lstrip("+"), _skill_of(cid))
            assert not grade(payload, payload["correct_answer"] + "+1", _skill_of(cid))
