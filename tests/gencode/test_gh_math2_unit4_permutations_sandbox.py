"""Sandbox gate for 普高數學2 Unit 4 (排列), skills gh_LinearPermutation / gh_PermutationWithIdenticalItems / gh_RepeatedPermutation.

Builds ``tmp/gh_math2_unit4_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived (and, where the textbook prints a solution, checked against it); the textbook rows are read from a private
snapshot of the Stage 1 database.  Every generated stem is also RE-SOLVED here from the text it prints (numbers, names, letters), by brute
force, so a varied question is proved to keep its mathematical meaning independently of the givens that produced it.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

import pytest

from agent_domains_candidate.permutations import build_sandbox as B
from agent_domains_candidate.permutations import permutations_adapter as AD
from agent_domains_candidate.permutations import permutations_domain as D
from agent_domains_candidate.permutations.permutations_specs import COMPONENTS, FIXED_ROWS, OP, SKILLS
from agent_domains_candidate.permutations.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.permutations.verification import grade, verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = B.isolated_db()
SEEDS = range(20)
FIGURE_COMPONENTS = {12794: "example7", 12797: "practice7", 12803: "balloons"}  # the reviewed crop is reused only for the figure's own structure
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
FLOOR = {12774: 7, 12779: 7, 12777: 10, 12782: 10, 12789: 10, 12790: 10, 12791: 10, 12804: 10, 12806: 10, 12807: 10}  # small families of genuinely different questions
UNIT_IDS = set(range(12774, 12812))
ZH = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "十一": 11, "十二": 12}


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u4_{cid}_{path.stem}", path)
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
        assert "$$" not in text and "承例題" not in text and "MATH_PARSE_FAILED" not in text
        has_cue = any(cue in text for cue in ("如圖", "右圖", "下圖"))
        assert not payload.get("visual_spec") and not payload.get("image_assets")  # nothing is ever redrawn
        assert bool(payload.get("reuse_textbook_image")) == has_cue  # the crop is attached exactly when the stem points to it
        if cid not in FIGURE_COMPONENTS:
            assert not has_cue and not payload.get("reuse_textbook_image")
        assert not payload["answer_contract"].get("answer_format_example")  # nothing a student sees before submitting can name the answer
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= FLOOR.get(cid, 10), len(surfaces)


def test_coverage_and_fixed_items_are_explicit():
    assert set(COMPONENTS) | set(FIXED_ROWS) == UNIT_IDS and len(UNIT_IDS) == 38
    assert not set(COMPONENTS) & set(FIXED_ROWS)
    assert len(COMPONENTS) == 37 and set(FIXED_ROWS) == {12801}
    assert all(len(reason) > 20 for reason in FIXED_ROWS.values())
    per_skill = {skill: sum(1 for s in COMPONENTS.values() if SKILLS[s[0]] == skill) for skill in SKILLS.values()}
    assert per_skill == {"gh_LinearPermutation": 19, "gh_PermutationWithIdenticalItems": 10, "gh_RepeatedPermutation": 8}
    from agent_domains_candidate.permutations.permutations_specs import SKILL_OPERATIONS

    for key, ops in SKILL_OPERATIONS.items():  # every component's operation is allowed for its own skill
        assert {s[1] for s in COMPONENTS.values() if s[0] == key} <= set(ops)
    assert set(D.OPERATIONS) == set(OP) == {s[1] for s in COMPONENTS.values()}


def test_skill_bindings_and_stems_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: (r[1], r[2]) for r in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12774 and 12811")}
    finally:
        con.close()
    assert len(rows) == 38
    counts = Counter(s for s, _t in rows.values())
    assert counts == {"gh_LinearPermutation": 19, "gh_PermutationWithIdenticalItems": 11, "gh_RepeatedPermutation": 8}
    for cid in COMPONENTS:
        assert rows[cid][0] == _skill_of(cid), cid
    assert rows[12801][0] == "gh_PermutationWithIdenticalItems"
    digits = lambda t: set(re.findall(r"\d+", re.sub(r"\s", "", re.sub(r"\\\w+", "", t))))  # noqa: E731
    for cid in COMPONENTS:  # variant 0 is the textbook question: every number the textbook stem prints appears in the generated stem
        source, stem = rows[cid][1], _gen(cid, 0)["question_text"]
        assert digits(source) <= digits(stem) | {"1", "2", "3", "4", "5"}, (cid, digits(source), digits(stem))


# --- hand-derived source oracles ---------------------------------------------------------------------------------------------------------

SOURCE_ORACLES = {
    12774: "720", 12775: "840", 12776: "48", 12777: ["720", "1440"], 12778: "620", 12779: "120", 12780: "120", 12781: "300",
    12782: ["5760", "2880"], 12783: "78", 12784: "A", 12785: "A", 12786: "60", 12787: ["100", "64"], 12788: "78", 12789: "48", 12790: "24",
    12791: "42", 12792: "480", 12793: "35", 12794: ["120", "63", "87", "33"], 12795: "60", 12796: "35", 12797: ["210", "80", "122", "88"],
    12798: "80", 12799: "B", 12800: ["1728", "43200"], 12802: "6", 12803: "560", 12804: ["81", "36"], 12805: ["81", "65", "32"],
    12806: ["216", "120"], 12807: ["81", "240"], 12808: "B", 12809: "90", 12810: "240", 12811: "14",
}


def test_source_oracles_by_hand():
    assert set(SOURCE_ORACLES) == set(COMPONENTS)
    for cid, want in SOURCE_ORACLES.items():
        assert _answers(_gen(cid, 0)) == want, cid
    # a few of them by hand, written out (independent of every code path above)
    assert 6 * 5 * 4 * 3 * 2 == 720 and 7 * 6 * 5 * 4 == 840 and 4 * 4 * 3 == 48
    assert math.factorial(5) * math.factorial(3) == 720 and math.factorial(4) * 5 * 4 * 3 == 1440
    assert 840 - (120 + 120 - 20) == 620 and 360 - 60 == 300 and 120 - 2 * 24 + 6 == 78
    assert 2 * 24 * 120 == 5760 and 24 * 120 == 2880 and 5 * 5 * 4 == 100 and 100 - (5 * 4 + 4 * 4) == 64
    assert math.factorial(10) // (math.factorial(7) * math.factorial(3)) == 120 and 3 * 21 == 63
    assert 63 + (15 * 4) - (3 * 3 * 4) == 87 and 120 - 87 == 33
    assert math.comb(10, 4) == 210 and 4 * 20 == 80 and 80 + 15 * 6 - 4 * 2 * 6 == 122 and 210 - 122 == 88
    assert math.factorial(6) // 8 - math.factorial(5) // 4 == 60 and 3 ** 4 - 3 * 2 ** 4 + 3 == 36 and 3 ** 4 - 2 ** 4 == 65 and 4 * 2 ** 3 == 32
    assert 6 ** 3 == 216 and 6 * 5 * 4 == 120 and 3 ** 5 - 3 == 240 and 2 ** 4 - 2 == 14 and math.factorial(6) // 8 == 90
    assert math.factorial(8) // (2 * 6 * 6) == 560 and math.comb(6, 1) == 6 and math.factorial(7) // (6 * 6) - 60 == 80


def test_oracles_agree_with_the_solutions_printed_in_the_textbook():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        solutions = {r[0]: r[1] or "" for r in con.execute("select id, detailed_solution from textbook_examples where id between 12774 and 12811")}
    finally:
        con.close()
    printed = {12774: ["720"], 12775: ["840"], 12776: ["48"], 12777: ["720", "1440"], 12778: ["620"], 12795: ["60"], 12804: ["81", "36"],
               12805: ["81", "65", "32"], 12794: ["120", "63"]}
    for cid, numbers in printed.items():
        tokens = set(re.findall(r"\d+", solutions[cid]))
        assert set(numbers) <= tokens, (cid, numbers)


# --- every stem re-solved from its own text ---------------------------------------------------------------------------------------------------------

def _nums(text: str) -> list[int]:
    return [int(v) for v in re.findall(r"\$([+-]?\d+)\$", text)]


def _zh(s: str) -> int:
    return ZH[s]


def _count(items, test) -> int:
    return sum(1 for t in items if test(t))


def _eval_claim(text: str) -> int:
    tex = re.search(r"共有 \$(.+?)\$ 種", text) or re.search(r"共有(.+?)種", text)
    body = tex.group(1)
    if m := re.fullmatch(r"P_\{(\d+)\}\^\{(\d+)\}", body):
        return math.perm(int(m.group(2)), int(m.group(1)))
    if m := re.fullmatch(r"(\d+)\^\{(\d+)\}", body):
        return int(m.group(1)) ** int(m.group(2))
    if m := re.fullmatch(r"(\d+)!", body):
        return math.factorial(int(m.group(1)))
    if m := re.fullmatch(r"\\frac\{(\d+)!\}\{((?:\d+!)+)\}", body):
        out = math.factorial(int(m.group(1)))
        for c in re.findall(r"(\d+)!", m.group(2)):
            out //= math.factorial(int(c))
        return out
    return int(body)


def _patterns_count(counts, test) -> int:
    return sum(1 for w in set(itertools.permutations([i for i, c in enumerate(counts) for _ in range(c)])) if test(w))


def _distinct_perms(counts) -> int:
    return len(set(itertools.permutations([i for i, c in enumerate(counts) for _ in range(c)])))


def resolve(cid: int, text: str):
    """The correct answer, recomputed from the printed stem alone."""
    nums = _nums(text)
    if cid in (12774, 12779):
        return str(math.factorial(nums[0]))
    if cid in (12775, 12780, 12786):
        return str(_count(itertools.permutations(range(nums[0]), nums[1]), lambda p: True))
    if cid in (12776, 12787):
        digits = [int(d) for d in re.search(r"(?:從|用.個數字)([\d, ]+?)(?:等|組成)", text).group(1).split(",")]
        length = _zh(re.search(r"([一二三四五])位數", text).group(1))
        numbers = [p for p in itertools.permutations(digits, length) if p[0] != 0]
        out = [str(len(numbers))]
        if cid == 12787:
            out.append(str(_count(numbers, lambda p: p[-1] % 5 != 0)))
        return out if len(out) > 1 else out[0]
    if cid == 12777:
        m, w = nums[0], nums[1]
        together = apart = 0
        for seats in itertools.combinations(range(m + w), w):
            together += seats[-1] - seats[0] == w - 1
            apart += all(b - a >= 2 for a, b in zip(seats, seats[1:]))
        f = math.factorial(m) * math.factorial(w)
        return [str(together * f), str(apart * f)]
    if cid == 12778:
        n, k = nums[0], nums[1]
        unis = ["臺大", "臺師大", "清大", "陽明交大"]
        a, b = (unis.index(x) for x in re.search(r"甲同學不到(.+?)，乙同學不到(.+?)。", text).groups())
        return str(_count(itertools.permutations(range(n), k), lambda p: p[a] != 0 and p[b] != 1))
    if cid == 12781:
        n, k = nums[0], nums[1]
        who = "甲乙丙丁戊己庚辛".index(re.search(r"若(.)選手", text).group(1))
        return str(_count(itertools.permutations(range(n), k), lambda p: p[0] != who))
    if cid == 12783:
        n = nums[0]
        (r1, w1, r2, w2) = re.search(r"若(.+?)不排(首位|末位)，(.+?)不排(首位|末位)", text).groups()
        place = {"首位": 0, "末位": n - 1}
        return str(_count(itertools.permutations(range(n)), lambda p: p[place[w1]] != 0 and p[place[w2]] != 1))
    if cid == 12788:
        n, p1, p2 = nums[0], nums[2] - 1, nums[3] - 1
        return str(_count(itertools.permutations(range(n)), lambda p: p[p1] != 0 and p[p2] != 1))
    if cid == 12782:
        a, b = (nums[1], nums[2]) if len(nums) == 4 else (nums[0], nums[1])
        together = alternate = 0
        for seats in itertools.combinations(range(a + b), a):
            mark = [i in seats for i in range(a + b)]
            runs = 1 + sum(1 for x, y in zip(mark, mark[1:]) if x != y)
            together += runs == 2
            alternate += runs == a + b
        f = math.factorial(a) * math.factorial(b)
        return [str(together * f), str(alternate * f)]
    if cid in (12784, 12785, 12799, 12808):
        if cid == 12784:
            actual = math.factorial(len(re.findall(r"「.」", text.split("\n", 1)[1])))
        elif cid == 12785:
            actual = math.perm(nums[0], nums[1])
        elif cid == 12799:
            word = re.search(r"個字母([A-Z]+)任意", text).group(1)
            actual = math.factorial(len(word)) // math.prod(math.factorial(c) for c in Counter(word).values())
        else:
            actual = nums[1] ** nums[0]
        return "A" if _eval_claim(text) == actual else "B"
    if cid == 12789:
        total, special = nums[0], nums[2]
        return str(_count(itertools.permutations(range(total)), lambda p: p[0] < special and p[-1] < special))
    if cid == 12790:
        f, s, b = (2, 2, 2) if not nums else (nums[0], nums[1], nums[2])
        block = set(range(f + s, f + s + b))

        def ok(p):
            if not (p[0] < f and p[-1] < f):
                return False
            at = [i for i, v in enumerate(p) if v in block]
            return at[-1] - at[0] == b - 1

        return str(_count(itertools.permutations(range(f + s + b)), ok))
    if cid == 12791:
        old, new = nums[0], nums[1]
        return str(_count(itertools.permutations(range(old + new)), lambda p: [v for v in p if v < old] == list(range(old))))
    if cid == 12792:
        n = _zh(re.search(r"([四五六七八])個字母", text).group(1))
        letters = "ABCDEFGH"
        if "同一側" in text:
            a, b, c = (letters.index(x) for x in re.search(r"若(.), (.)都須在(.)的同一側", text).groups())
            return str(_count(itertools.permutations(range(n)), lambda p: (p.index(a) < p.index(c)) == (p.index(b) < p.index(c))))
        c, a, b = (letters.index(x) for x in re.search(r"若(.)必須排在(.), (.)之間", text).groups())
        return str(_count(itertools.permutations(range(n)), lambda p: min(p.index(a), p.index(b)) < p.index(c) < max(p.index(a), p.index(b))))
    if cid in (12793, 12796):
        return str(_distinct_perms([nums[1], nums[2]]))
    if cid in (12794, 12797):
        if not nums:
            return None  # the figure carries the data (checked against the figure structure below)
        w, h, cx, cy, dx, dy = nums[:6]
        paths: list = []

        def walk(x, y, trail):
            trail = trail + [(x, y)]
            if (x, y) == (w, h):
                paths.append(trail)
                return
            if x < w:
                walk(x + 1, y, trail)
            if y < h:
                walk(x, y + 1, trail)

        walk(0, 0, [])
        c, d = (cx, cy), (dx, dy)
        return [str(len(paths)), str(_count(paths, lambda p: c in p)), str(_count(paths, lambda p: c in p or d in p)),
                str(_count(paths, lambda p: c not in p and d not in p))]
    if cid in (12795, 12798):
        digits = [int(d) for d in re.search(r"個數字([\d, ]+?)排成", text).group(1).split(",")]
        numbers = {p for p in itertools.permutations(digits) if p[0] != 0}
        if "偶數" in text:
            return str(_count(numbers, lambda p: p[-1] % 2 == 0))
        if "奇數" in text:
            return str(_count(numbers, lambda p: p[-1] % 2 == 1))
        return str(len(numbers))
    if cid == 12800:
        zh = re.search(r"其中(.)隻(.)色、(.)隻(.)色及(.)隻(.)色", text).groups()
        counts = [_zh(zh[0]), _zh(zh[2]), _zh(zh[4])]
        scale = math.prod(math.factorial(c) for c in counts)
        together = _patterns_count(counts, lambda w: 1 + sum(1 for x, y in zip(w, w[1:]) if x != y) == 3)
        apart = _patterns_count(counts, lambda w: not any(x == y == 2 for x, y in zip(w, w[1:])))
        return [str(together * scale), str(apart * scale)]
    if cid == 12802:
        steps, target = nums[1], nums[2]
        return str(_count(itertools.product((-1, 1), repeat=steps), lambda j: sum(j) == target))
    if cid == 12803:
        counts = [int(c) for c in re.findall(r"\$?(\d+)\$? ?個[紅黃藍]氣球", text)]
        return str(_distinct_perms(counts))
    if cid == 12804:
        holes = _zh(re.search(r"挖了(.+?)個", text).group(1))
        nights = _zh(re.search(r"未來的(.+?)個晚上", text).group(1))
        every = list(itertools.product(range(holes), repeat=nights))
        return [str(len(every)), str(_count(every, lambda t: len(set(t)) == holes))]
    if cid == 12805:
        boxes = 4 if "甲、乙、丙、丁" in text else 3
        n, k = nums[0], nums[1]
        every = list(itertools.product(range(boxes), repeat=n))
        return [str(len(every)), str(_count(every, lambda t: t.count(0) >= k)), str(_count(every, lambda t: t.count(0) == k))]
    if cid == 12806:
        boxes, people = nums[0], _zh(re.search(r"，(.+?)個人運動完後", text).group(1))
        every = list(itertools.product(range(boxes), repeat=people))
        return [str(len(every)), str(_count(every, lambda t: len(set(t)) == len(t)))]
    if cid == 12807:
        boxes = len(re.search(r"有([A-D, ]+)", text).group(1).replace(" ", "").split(","))
        cap, n1, n2 = nums[0], nums[1], nums[2]
        return [str(_count(itertools.product(range(boxes), repeat=n), lambda t: max(Counter(t).values()) <= cap)) for n in (n1, n2)]
    if cid == 12809:
        counts = [_zh(re.search(r"每人參加(.)天", text).group(1))] * 3 if "每人參加" in text else nums[1:4]
        return str(_distinct_perms(counts))
    if cid == 12810:
        n, boxes, cap = nums[0], nums[1], nums[2]
        return str(_count(itertools.product(range(boxes), repeat=n), lambda t: max(Counter(t).values()) <= cap))
    if cid == 12811:
        digits = [int(d) for d in re.search(r"由數字([\d, ]+?)組成", text).group(1).split(",")]
        n = _zh(re.search(r"組成(.+?)位數", text).group(1))
        return str(_count(itertools.product(digits, repeat=n), lambda t: set(t) == set(digits)))
    raise AssertionError(f"no re-solver for {cid}")


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_every_generated_stem_is_resolved_to_the_same_answer_from_its_text(cid):
    for seed in SEEDS:
        payload = _gen(cid, seed)
        expected = resolve(cid, payload["question_text"])
        if expected is None:  # figure stem of the two grid rows: the data lives in the figure
            assert payload["reuse_textbook_image"] and _answers(payload) == SOURCE_ORACLES[cid]
            continue
        assert _answers(payload) == expected, (cid, seed, payload["question_text"][:80])


# --- the shared validators reject tampered answers ------------------------------------------------------------------------------------------------

def _tamper(answer: dict) -> dict:
    bad = json.loads(json.dumps(answer))
    if "items" in bad:
        bad["items"][0]["count"] += 1
    elif "truth" in bad:
        bad["truth"] = not bad["truth"]
    else:
        key = next(k for k in ("count", "adjacent", "contiguous") if k in bad)
        bad[key] += 1
    return bad


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_validators_reject_a_tampered_answer(cid, skill_id, operation):
    _s, op, source, _sampler = COMPONENTS[cid]
    matrix = D.build_permutations_matrix(domain_operation=op, constraints=dict(source))
    validate = getattr(D, f"validate_{op}_matrix")
    assert validate(matrix) is True
    assert validate({**matrix, "answer": _tamper(matrix["answer"])}) is False
    assert validate({**matrix, "domain_operation": "other"}) is False and validate("not a matrix") is False


def test_domain_refuses_degenerate_or_inconsistent_input():
    mk = lambda op, **g: D.build_permutations_matrix(domain_operation=op, constraints=g)  # noqa: E731
    for op, givens in [
        ("selected_arrangement", {"n": 3, "k": 5}), ("selected_arrangement", {"n": 1, "k": 1}),
        ("adjacent_separated", {"men": 2, "women": 4}), ("two_group_line", {"a": 3, "b": 6}),
        ("restricted_assignment", {"n": 5, "k": 5, "forbidden": [[0, 0], [0, 1]]}), ("restricted_assignment", {"n": 5, "k": 5, "forbidden": [[0, 0], [1, 0]]}),
        ("restricted_assignment", {"n": 5, "k": 5, "forbidden": []}), ("relative_order_three", {"n": 6, "pair": [0, 1], "ref": 1, "mode": "same_side"}),
        ("line_walk", {"steps": 6, "target": 3}), ("line_walk", {"steps": 6, "target": 6}), ("line_walk", {"steps": 6, "target": 0}),
        ("grid_paths", {"width": 5, "height": 3, "points": {"C": [0, 0], "D": [1, 1]}, "asks": ["any"]}),
        ("grid_paths", {"width": 5, "height": 3, "points": {"C": [1, 1], "D": [1, 1]}, "asks": ["any"]}),
        ("distribute_distinct", {"boxes": 3, "asks": [{"kind": "onto", "items": 2}]}), ("distribute_distinct", {"boxes": 3, "asks": [{"kind": "all_different", "items": 4}]}),
        ("distribute_distinct", {"boxes": 3, "asks": [{"kind": "bogus", "items": 4}]}), ("counting_claim", {"setting": {"kind": "bogus"}, "claim": {"form": "number", "value": 1}}),
        ("counting_claim", {"setting": {"kind": "arrangement", "n": 3}, "claim": {"form": "perm", "n": 3, "k": 5}}),
        ("multiset_digit_numbers", {"digits": [1, 1, 1, 1], "ask": "number"}), ("colored_distinct_items", {"counts": [2, 2, 6], "asks": ["last_color_apart"]}),
        ("column_shooting_order", {"counts": [3]}), ("identical_arrangement", {"counts": [5]}),
        ("distinct_digit_numbers", {"digits": [1, 2, 3], "length": 2, "asks": ["bogus"]}),
    ]:
        with pytest.raises(ValueError):
            mk(op, **givens)
    with pytest.raises(ValueError):
        D.build_permutations_matrix(domain_operation="nonexistent", constraints={})
    with pytest.raises(ValueError):
        D.build_permutations_matrix(domain_operation="selected_arrangement", constraints={"n": 5})


def test_figure_is_attached_only_when_the_stated_data_is_the_figure():
    for cid, name in (("12794", "example7"), ("12797", "practice7")):
        _s, op, source, _sampler = COMPONENTS[int(cid)]
        assert source["figure"] == name
        bad = {**source, "width": source["width"] + 1}
        with pytest.raises(ValueError, match="differs_from_the_textbook_figure"):
            AD.adapt_permutations_matrix(D.build_permutations_matrix(domain_operation=op, constraints=bad), domain_operation=op)
        other = {**source, "figure": "practice7" if name == "example7" else "example7"}
        with pytest.raises(ValueError, match="differs_from_the_textbook_figure"):
            AD.adapt_permutations_matrix(D.build_permutations_matrix(domain_operation=op, constraints=other), domain_operation=op)
        without = {k: v for k, v in source.items() if k != "figure"}  # the same data in words: no figure, no cue
        text = AD.adapt_permutations_matrix(D.build_permutations_matrix(domain_operation=op, constraints=without), domain_operation=op)
        assert not text.get("reuse_textbook_image") and "右圖" not in text["question_text"] and "個街區" in text["question_text"]
        assert _answers(text) == _answers(_gen(int(cid), 0))
    _s, op, source, _sampler = COMPONENTS[12803]
    with pytest.raises(ValueError, match="differ_from_the_textbook_figure"):
        AD.adapt_permutations_matrix(D.build_permutations_matrix(domain_operation=op, constraints={**source, "counts": [2, 3, 4]}), domain_operation=op)
    for cid in FIGURE_COMPONENTS:
        assert _gen(cid, 0)["reuse_textbook_image"] is True  # variant 0 (the textbook data) keeps the figure


def test_non_figure_stems_never_point_at_a_picture():
    for cid in COMPONENTS:
        if cid in FIGURE_COMPONENTS:
            continue
        for seed in range(0, 20, 4):
            assert not any(cue in _gen(cid, seed)["question_text"] for cue in ("如圖", "右圖", "下圖", "在圖"))


def test_claim_operation_covers_true_and_false_statements():
    for cid in (12784, 12785, 12799, 12808):
        labels = {_gen(cid, s)["correct_answer"] for s in SEEDS}
        assert labels == {"A", "B"}, (cid, labels)  # both a correct and an incorrect statement appear among the variants




