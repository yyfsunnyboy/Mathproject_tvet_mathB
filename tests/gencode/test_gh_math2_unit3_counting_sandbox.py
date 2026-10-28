"""Sandbox gate for 普高數學2 Unit 3 (計數原理), skills gh_LogicAndSets and gh_CountingPrinciples: per-component contract, oracle, grading.

Builds ``tmp/gh_math2_unit3_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived from the textbook stems (independent of the domain code); the textbook rows are read from a private snapshot
of the Stage 1 database.  Every dynamic stem is also re-solved here from the numbers it prints, by brute force, so a varied question is
proved to keep its mathematical meaning.
"""

from __future__ import annotations

import ast
import importlib.util
import itertools
import json
import math
import re
import sqlite3
from pathlib import Path

import pytest

from agent_domains_candidate.counting_sets import build_sandbox as B
from agent_domains_candidate.counting_sets import counting_sets_adapter as AD
from agent_domains_candidate.counting_sets import counting_sets_domain as D
from agent_domains_candidate.counting_sets.counting_sets_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.counting_sets.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.counting_sets.verification import grade, verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = B.isolated_db()
SEEDS = range(20)
PKG = PROJECT_ROOT / "agent_domains_candidate" / "counting_sets"
FIGURE_COMPONENTS = {12756, 12773}  # the reviewed textbook picture is reused; the stated data is the figure's structure
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
FLOOR = {12773: 6, 12757: 9, 12768: 9, 12749: 12, 12756: 12, 12764: 14}  # small families of genuinely different questions; the rest show many
UNIT_IDS = set(range(12744, 12774))


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u3_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


def _nums(text: str) -> list[int]:
    return [int(v) for v in re.findall(r"\$(-?\d+)\$", text)]


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
        if cid in FIGURE_COMPONENTS:
            assert payload["reuse_textbook_image"] is True and not payload.get("visual_spec")  # reviewed crop reused, never redrawn
        else:
            assert not payload.get("reuse_textbook_image") and not payload.get("visual_spec") and not payload.get("image_assets")
            assert not any(cue in text for cue in ("如圖", "右圖", "下圖"))
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= FLOOR.get(cid, 10), len(surfaces)


def test_coverage_and_deferred_items_are_explicit():
    assert set(COMPONENTS) | set(DEFERRED) == UNIT_IDS and len(UNIT_IDS) == 30
    assert not set(COMPONENTS) & set(DEFERRED)
    assert len(COMPONENTS) == 29 and set(DEFERRED) == {12746}
    assert all(len(reason) > 20 for reason in DEFERRED.values())
    per_skill = {skill: sum(1 for s in COMPONENTS.values() if SKILLS[s[0]] == skill) for skill in SKILLS.values()}
    assert per_skill == {"gh_LogicAndSets": 8, "gh_CountingPrinciples": 21}


def test_skill_bindings_and_stems_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: (r[1], r[2]) for r in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12744 and 12773")}
    finally:
        con.close()
    assert len(rows) == 30
    assert sum(1 for s, _t in rows.values() if s == "gh_LogicAndSets") == 9 and sum(1 for s, _t in rows.values() if s == "gh_CountingPrinciples") == 21
    for cid in COMPONENTS:
        assert rows[cid][0] == _skill_of(cid), cid
    assert rows[12746][0] == "gh_LogicAndSets"
    digits = lambda t: set(re.findall(r"\d+", re.sub(r"\s", "", re.sub(r"\\\w+", "", t))))  # noqa: E731
    for cid in COMPONENTS:  # variant 0 is the textbook question: every number the textbook stem prints appears in the generated stem
        source, stem = rows[cid][1], _gen(cid, 0)["question_text"]
        assert digits(source) <= digits(stem) | {"1", "2", "3", "4", "5"}, (cid, digits(source), digits(stem))


# --- hand-derived source oracles (the textbook answers, computed by hand; not through the domain) -------------------------------------

def _answers(cid: int, seed: int = 0):
    ans = _gen(cid, seed)["correct_answer"]
    if isinstance(ans, dict):
        return [ans[k] for k in sorted(ans, key=lambda k: int(k.split("_")[1]))]
    return ans


def test_oracles_sets_and_logic():
    assert _answers(12744) == ["2<=x<=3", "1<=x<=4", "1<=x<2", "x<1 or x>3"]
    assert _answers(12748) == [["2", "3"], ["1", "2", "3", "4"], ["1"], ["4", "5"]]
    assert _answers(12766) == [["1"], ["1", "2", "3", "4", "5", "6"], ["2", "4", "5"], ["3", "6"]]
    assert _answers(12767) == [["-1"], ["-1", "1", "3"]]  # A={-1,1}, B={-1,3}
    assert _answers(12745) == ["2", "4"]  # P false, Q true, R false: Q, Q or R
    assert _answers(12747) == "B"  # x=3 implies |x|=3 (necessary), |x|=3 does not give x=3
    assert _answers(12763) == "A" and _answers(12764) == "B"  # 5<7 is true, so the "or" holds; ab=0 only needs one factor 0


def test_oracles_counting():
    assert _answers(12749) == ["6", "3"]
    assert _answers(12750) == "24" and _answers(12758) == "48"
    assert _answers(12751) == ["24", "6"] and _answers(12759) == ["20", "6"]  # 360=2^3 3^2 5, 240=2^4 3 5
    assert _answers(12752) == "22" and _answers(12760) == "52"  # 4+6+12 ; 9*8-5*4
    assert _answers(12753) == ["38", "2"] and _answers(12754) == ["27", "13"] and _answers(12771) == "24"
    assert _answers(12755) == "4"  # 10a+50b=160: b=0..3
    assert _answers(12756) == "4"  # ABC, ABDC, ADBC, ADC
    assert _answers(12757) == "7"  # sums 5 (4 ways) and 10 (3 ways)
    assert _answers(12761) == "13" and _answers(12770) == "35" and _answers(12772) == ["25", "15"]
    assert _answers(12762) == ["220", "80"]  # 150+100+60-50-30-20+10
    assert _answers(12765) == "A"  # 1 + 3 = 4
    assert _answers(12768) == "8"  # HH TT HTT THH HTHH THTT HTHT THTH
    assert _answers(12769) == ["72", "54"]
    assert _answers(12773) == "13"  # matchings of the path T-1-2-3-4-5 (Fibonacci)


def test_tiling_distribution_by_hand():
    cells = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1)}
    # the region is the path T-1-2-3-4-5; k disjoint dominoes = k-matchings of a 6-vertex path = C(6-k, k)
    assert {str(k): math.comb(6 - k, k) for k in range(4)} == D.tiling_count(cells=[list(c) for c in cells], ask={"kind": "total"})["distribution"]
    assert sorted(AD.FIGURE_REGION_CELLS) == sorted(cells)
    assert _answers(12773) == "13"
    wants = {("exactly", 1): 5, ("exactly", 2): 6, ("exactly", 3): 1, ("at_least", 1): 12, ("at_least", 2): 7}
    seen = {}
    for seed in SEEDS:
        ask = _gen(12773, seed)
        sem = ask["semantic_answer"]
        seen[json.dumps(ask["math_core"]["givens"]["ask"], sort_keys=True)] = sem["value"]
    for (kind, k), value in wants.items():
        assert seen.get(json.dumps({"k": k, "kind": kind}, sort_keys=True)) == value


def test_path_graph_by_hand():
    edges = {frozenset(e) for e in ("AB", "AD", "BC", "CD", "BD")}  # read from the textbook figure: A-B, A-D, B-C, C-D, and the vertical B-D
    assert edges == AD.FIGURE_GRAPH_EDGES
    simple = {"AC": 4, "CA": 4, "BD": 3, "DB": 3, "AB": 3, "BA": 3, "AD": 3, "DA": 3, "BC": 3, "CB": 3, "CD": 3, "DC": 3}
    for seed in SEEDS:
        p = _gen(12756, seed)
        g = p["math_core"]["givens"]
        assert p["correct_answer"] == str(simple[g["start"] + g["end"]]), g


# --- grading: equivalent forms accepted, neighbours rejected -------------------------------------------------------------------------

def test_interval_answers_accept_equivalent_forms_and_reject_neighbours():
    skill, p = _skill_of(12744), _gen(12744)
    right = {"part_1": "2<=x<=3", "part_2": "1<=x<=4", "part_3": "1<=x<2", "part_4": "x<1 or x>3"}
    assert grade(p, right, skill)
    assert grade(p, {**right, "part_1": "3>=x>=2", "part_4": "x>3 or x<1"}, skill)
    for part, wrong in (("part_1", "2<x<=3"), ("part_2", "1<=x<=5"), ("part_3", "1<=x<=2"), ("part_4", "x<=1 or x>3"), ("part_4", "x<1")):
        assert not grade(p, {**right, part: wrong}, skill), (part, wrong)


def test_value_sets_are_order_free_but_complete():
    skill, p = _skill_of(12766), _gen(12766)
    right = {"part_1": "1", "part_2": "1,2,3,4,5,6", "part_3": "2,4,5", "part_4": "3,6"}
    assert grade(p, right, skill) and grade(p, {**right, "part_2": "6, 5, 4, 3, 2, 1", "part_3": "{5, 2, 4}"}, skill)
    for part, wrong in (("part_1", "1,2"), ("part_2", "1,2,3,4,5"), ("part_3", "2,4"), ("part_3", "2,4,5,6"), ("part_4", "3,5")):
        assert not grade(p, {**right, part: wrong}, skill), (part, wrong)


def test_selection_answer_is_an_exact_option_set():
    skill, p = _skill_of(12745), _gen(12745)
    assert grade(p, "2,4", skill) and grade(p, "4, 2", skill)
    for wrong in ("2", "4", "2,4,5", "1,3", "2,3,4"):
        assert not grade(p, wrong, skill), wrong


def test_counts_accept_equivalent_numbers_and_reject_neighbours():
    skill, p = _skill_of(12753), _gen(12753)
    assert grade(p, {"part_1": "38", "part_2": "2"}, skill) and grade(p, {"part_1": "38.0", "part_2": "2"}, skill)
    assert not grade(p, {"part_1": "37", "part_2": "2"}, skill) and not grade(p, {"part_1": "38", "part_2": "3"}, skill)
    assert not grade(p, {"part_1": "35", "part_2": "5"}, skill)  # the typical slip: forgetting to subtract the overlap
    skill, p = _skill_of(12755), _gen(12755)
    assert grade(p, "4", skill) and not grade(p, "5", skill) and not grade(p, "3", skill) and not grade(p, "1", skill)


def test_typical_wrong_counts_are_rejected():
    typical = {12750: "9", 12758: "14", 12752: "24", 12760: "72", 12757: "10", 12768: "16", 12773: "12", 12756: "5", 12765: "B"}
    for cid, wrong in typical.items():
        assert not grade(_gen(cid), wrong, _skill_of(cid)), cid
    assert not grade(_gen(12754), {"part_1": "27", "part_2": "14"}, _skill_of(12754))
    assert not grade(_gen(12772), {"part_1": "25", "part_2": "0"}, _skill_of(12772))  # the min must account for the 40 students
    assert not grade(_gen(12762), {"part_1": "220", "part_2": "100"}, _skill_of(12762))


def test_set_and_interval_format_hints_never_show_the_answer():
    for cid in (12744, 12745, 12748, 12766, 12767):
        for seed in SEEDS:
            payload = _gen(cid, seed)
            contract = payload["answer_contract"]
            parts = contract.get("parts") or [{**contract, "expected_answer": payload["correct_answer"]}]
            canonicals = [p["expected_answer"] for p in parts if p["checker"] == "inequality_solution_checker"]
            for part in parts:
                hint = part.get("answer_format_example") or contract.get("answer_format_example")
                assert hint, (cid, seed)
                if part["checker"] == "solution_set_checker":
                    shown = {int(v) for v in hint.split(",")}
                    assert not (shown & {int(m) for m in part["expected_answer"]}), (cid, seed, hint, part["expected_answer"])
                else:
                    assert hint not in canonicals, (cid, seed, hint)


def test_two_choice_statements_are_balanced_and_not_a_fixed_answer():
    for cid in (12763, 12764, 12765):
        answers = [_gen(cid, s)["correct_answer"] for s in SEEDS]
        assert {"A", "B"} == set(answers) and 4 <= answers.count("A") <= 16, (cid, answers)
    labels = {_gen(12747, s)["correct_answer"] for s in SEEDS}
    assert len(labels) >= 2
    sizes = {len(_gen(12745, s)["correct_answer"]) for s in SEEDS}
    assert len(sizes) >= 2


def test_condition_choices_and_statement_selection_vary_sensibly():
    p = _gen(12747)
    assert [c["value"] for c in p["answer_contract"]["choices"]] == ["充分", "必要", "充要"]
    for seed in SEEDS:
        q = _gen(12747, seed)
        label = {c["label"]: c["value"] for c in q["answer_contract"]["choices"]}[q["correct_answer"]]
        assert label == q["semantic_answer"]["label"]
        assert "「" in q["question_text"] and "條件" in q["question_text"]


# --- the stems are re-solved from the numbers they print (brute force, independent of the domain) --------------------------------------------

def _stem_numbers(cid: int, seed: int):
    p = _gen(cid, seed)
    return p, _nums(p["question_text"])


def test_varied_menu_and_staff_stems_keep_their_meaning():
    for seed in SEEDS:
        p, n = _stem_numbers(12750, seed)
        assert p["correct_answer"] == str(math.prod(n)) and len(n) == 3
        p, n = _stem_numbers(12758, seed)
        assert p["correct_answer"] == str(math.prod(n)) and len(n) == 2


def test_varied_divisor_stems_keep_their_meaning():
    for seed in SEEDS:
        for cid in (12751, 12759):
            p, n = _stem_numbers(cid, seed)
            number, m = n[0], n[1]
            divisors = [d for d in range(1, number + 1) if number % d == 0]
            if cid == 12751:
                want = [len(divisors), sum(1 for d in divisors if d % m == 0)]
            else:
                want = [len(divisors), sum(1 for d in divisors if d % m == 0 and d % n[2] != 0)]
            assert [int(v) for v in p["correct_answer"].values()] == want, (cid, seed, n)


def test_varied_pairing_and_ranking_stems_keep_their_meaning():
    for seed in SEEDS:
        p, n = _stem_numbers(12752, seed)
        t1, v1, new1, t2, v2, new2 = n
        assert t1 == v1 + new1 and t2 == v2 + new2
        pairs = [(i, j) for i in range(t1) for j in range(t2) if i < v1 or j < v2]
        assert p["correct_answer"] == str(len(pairs))
        p, n = _stem_numbers(12760, seed)
        k = 3 if "前三名" in p["question_text"] else 2
        people = ["m"] * n[0] + ["w"] * n[1]
        labelled = [f"{c}{i}" for i, c in enumerate(people)]
        assert p["correct_answer"] == str(sum(1 for seq in itertools.permutations(labelled, k) if any(x[0] == "w" for x in seq))), (seed, n)


def test_varied_two_set_stems_keep_their_meaning():
    for seed in SEEDS:
        p, nums = _stem_numbers(12753, seed)
        total, a, b, ab = nums[:4]
        assert nums[4] == total
        union = len(set(range(a)) | set(range(a - ab, a - ab + b)))
        assert p["correct_answer"] == {"part_1": str(union), "part_2": str(total - union)}
        p, (total, a, b, ab) = _stem_numbers(12770, seed)
        assert p["correct_answer"] == str(len(set(range(a)) | set(range(a - ab, a - ab + b))))
        p, (union, a, ab) = _stem_numbers(12761, seed)
        b = next(x for x in range(1, 200) if len(set(range(a)) | set(range(a - ab, a - ab + x))) == union)
        assert p["correct_answer"] == str(b)
        p, (total, a, b) = _stem_numbers(12772, seed)
        overlaps = [k for k in range(min(a, b) + 1) if a + b - k <= total]
        assert p["correct_answer"] == {"part_1": str(max(overlaps)), "part_2": str(min(overlaps))}


def test_varied_three_set_stems_keep_their_meaning():
    for seed in SEEDS:
        p, n = _stem_numbers(12754, seed)
        total, a, b, c, ab, bc, ca, abc = n
        regions = [a - (ab - abc) - (ca - abc) - abc, b - (ab - abc) - (bc - abc) - abc, c - (bc - abc) - (ca - abc) - abc, ab - abc, bc - abc, ca - abc, abc]
        assert min(regions) >= 0 and p["correct_answer"] == {"part_1": str(sum(regions)), "part_2": str(total - sum(regions))}
        p, n = _stem_numbers(12771, seed)
        a, b, c, ab, bc, ca, abc = n
        regions = [a - (ab - abc) - (ca - abc) - abc, b - (ab - abc) - (bc - abc) - abc, c - (bc - abc) - (ca - abc) - abc, ab - abc, bc - abc, ca - abc, abc]
        assert min(regions) >= 0 and p["correct_answer"] == str(sum(regions))


def test_varied_enumeration_stems_keep_their_meaning():
    for seed in SEEDS:
        p = _gen(12755, seed)
        c1, c2, total = _nums(p["question_text"])
        assert p["correct_answer"] == str(sum(1 for a in range(total // c1 + 1) for b in range(total // c2 + 1) if a * c1 + b * c2 == total))
        p = _gen(12757, seed)
        (k,) = _nums(p["question_text"])
        assert p["correct_answer"] == str(sum(1 for x in range(1, 7) for y in range(1, 7) if (x + y) % k == 0))
        p = _gen(12762, seed)
        limit = _nums(p["question_text"])[1]
        either = re.search(r"\(1\)有多少個是 (.+?) 的倍數", p["question_text"]).group(1)
        divisors = [int(v) for v in re.findall(r"\d+", either)]
        hit = sum(1 for v in range(1, limit + 1) if any(v % d == 0 for d in divisors))
        assert p["correct_answer"] == {"part_1": str(hit), "part_2": str(limit - hit)}
        p = _gen(12769, seed)
        sizes = _nums(p["question_text"])
        students = [(g, i) for g, s in enumerate(sizes) for i in range(s)]
        assert p["correct_answer"] == {"part_1": str(math.prod(sizes)), "part_2": str(sum(1 for x, y in itertools.combinations(students, 2) if x[0] != y[0]))}


def test_varied_tree_stems_keep_their_meaning():
    for seed in SEEDS:
        p = _gen(12749, seed)
        n = {"二": 2, "三": 3}[re.search(r"先勝(.)局", p["question_text"]).group(1)]
        finished = []

        def play(seq: str) -> None:
            if seq.count("a") == n or seq.count("b") == n:
                finished.append(seq)
                return
            play(seq + "a")
            play(seq + "b")

        play("")
        assert p["correct_answer"] == {"part_1": str(len(finished)), "part_2": str(sum(1 for s in finished if s.count("a") == n))}
        p = _gen(12768, seed)
        k, r, r_again = _nums(p["question_text"])
        assert r == r_again
        done = []

        def toss(seq: str) -> None:
            if len(seq) == k or (len(seq) >= r and len(set(seq[-r:])) == 1):
                done.append(seq)
                return
            toss(seq + "H")
            toss(seq + "T")

        toss("")
        assert p["correct_answer"] == str(len(done))


def test_varied_proposition_and_set_stems_keep_their_meaning():
    for seed in SEEDS:
        p = _gen(12763, seed)
        g = p["math_core"]["givens"]
        values = []
        for atom in g["atoms"]:
            if atom["kind"] == "compare":
                values.append({">": atom["a"] > atom["b"], "<": atom["a"] < atom["b"]}[atom["op"]])
            else:
                n = atom["n"]
                values.append({"prime": all(n % d for d in range(2, n)) and n > 1, "even": n % 2 == 0, "odd": n % 2 == 1,
                               "multiple_of": n % atom.get("k", 1) == 0}[atom["prop"]])
        joined = all(values) if g["options"][0][0] == "and" else any(values)
        assert p["correct_answer"] == ("A" if joined else "B"), seed
        p = _gen(12767, seed)
        g = p["math_core"]["givens"]
        a_set = {x for x in range(-60, 61) if x * x == g["A"]["rhs"]}
        b_set = {x for x in range(-60, 61) if x * x + g["B"]["b"] * x + g["B"]["c"] == 0}
        assert [sorted(int(v) for v in part) for part in p["correct_answer"].values()] == [sorted(a_set & b_set), sorted(a_set | b_set)]


def test_varied_interval_stems_keep_their_meaning():
    from fractions import Fraction

    for seed in SEEDS:
        p = _gen(12744, seed)
        g = p["math_core"]["givens"]
        def mem(spec, x):
            return (spec["lo"] < x or (spec.get("lc", True) and x == spec["lo"])) and (x < spec["hi"] or (spec.get("hc", True) and x == spec["hi"]))
        rules = {"intersection": lambda a, b: a and b, "union": lambda a, b: a or b, "a_minus_b": lambda a, b: a and not b,
                 "b_minus_a": lambda a, b: b and not a, "a_complement": lambda a, b: not a, "b_complement": lambda a, b: not b}
        for item, part in zip(g["items"], p["correct_answer"].values()):
            predicate = D._predicate(part)
            for k in range(-100, 101):
                x = Fraction(k, 8)
                assert predicate(x) == rules[item](mem(g["A"], x), mem(g["B"], x)), (seed, item, part, x)


def test_figure_components_only_attach_the_figure_to_the_figure_structure():
    base = dict(vertices=list("ABCD"), edges=[list(e) for e in ("AB", "AD", "BC", "CD", "BD")], start="A", end="C")
    matrix = D.build_counting_sets_matrix(domain_operation="graph_paths", constraints=base)
    assert AD.adapt_counting_sets_matrix(matrix, domain_operation="graph_paths")["reuse_textbook_image"] is True
    other = dict(base, edges=[list(e) for e in ("AB", "BC", "CD")])
    with pytest.raises(ValueError, match="differs_from_the_textbook_figure"):
        AD.adapt_counting_sets_matrix(D.build_counting_sets_matrix(domain_operation="graph_paths", constraints=other), domain_operation="graph_paths")
    cells = [[x, 0] for x in range(5)] + [[0, 1]]
    ok = D.build_counting_sets_matrix(domain_operation="tiling_count", constraints={"cells": cells, "ask": {"kind": "total"}})
    assert AD.adapt_counting_sets_matrix(ok, domain_operation="tiling_count")["reuse_textbook_image"] is True
    bad = D.build_counting_sets_matrix(domain_operation="tiling_count", constraints={"cells": [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1]], "ask": {"kind": "total"}})
    with pytest.raises(ValueError, match="differs_from_the_textbook_figure"):
        AD.adapt_counting_sets_matrix(bad, domain_operation="tiling_count")
    for cid in COMPONENTS:  # no other component refers to a figure
        text = _gen(cid, 0)["question_text"]
        assert (("如圖" in text or "右圖" in text) == (cid in FIGURE_COMPONENTS)), cid


def test_figure_stems_keep_the_textbook_wording():
    source_6 = _gen(12756, 0)["question_text"]
    assert "$A$" in source_6 and "$C$" in source_6 and "如圖" in source_6
    assert "L 形" in _gen(12773, 0)["question_text"] and "如右圖所示" in _gen(12773, 0)["question_text"]


# --- validators ---------------------------------------------------------------------------------------------------------------------

def test_domain_validators_reject_tampered_answers():
    tamper = {"interval_set_operations": lambda a: a["items"][0].update(canonical="x>100"),
              "finite_set_operations": lambda a: a["items"][0]["members"].append(99),
              "equation_root_sets": lambda a: a.update(A=[-2, 2]),
              "proposition_truth": lambda a: a["truths"].__setitem__(0, not a["truths"][0]),
              "implication_truth": lambda a: a.update(truth=not a["truth"]),
              "condition_relation": lambda a: a.update(relation="sufficient", label="充分"),
              "choice_product": lambda a: a.update(total=a["total"] + 1),
              "grade_selection": lambda a: a.update(different_pairs=a["different_pairs"] + 1),
              "divisor_counting": lambda a: a.update(total=a["total"] + 1),
              "at_least_one_pairing": lambda a: a.update(count=a["count"] + 1),
              "ordered_at_least_one": lambda a: a.update(count=a["count"] + 1),
              "two_set_counting": lambda a: a.update({next(k for k in a if k != "kind"): 999}),
              "three_set_counting": lambda a: a.update(union=a["union"] + 1),
              "multiples_counting": lambda a: a.update({"any": a["any"] + 1}),
              "coin_payment": lambda a: a.update(ways=a["ways"] + 1),
              "dice_sum_multiples": lambda a: a.update(count=a["count"] + 1),
              "race_outcomes": lambda a: a.update(total=a["total"] + 2),
              "graph_paths": lambda a: a.update(count=a["count"] + 1),
              "coin_toss_sequences": lambda a: a.update(count=a["count"] + 1),
              "tiling_count": lambda a: a.update(value=a["value"] + 1),
              "region_pairs_claim": lambda a: a.update(truth=not a["truth"])}
    done = set()
    for cid, (_s, op, source, _sampler) in COMPONENTS.items():
        matrix = D.build_counting_sets_matrix(domain_operation=op, constraints=dict(source))
        validate = getattr(D, f"validate_{op}_matrix")
        assert validate(matrix), cid
        bad = json.loads(json.dumps(matrix))
        tamper[op](bad["answer"])
        assert not validate(bad), (cid, op)
        done.add(op)
    assert done == set(OP)


def test_degenerate_inputs_are_refused_by_the_domain():
    build = D.build_counting_sets_matrix
    L = [[x, 0] for x in range(5)] + [[0, 1]]
    path = dict(vertices=list("ABCD"), edges=[["A", "B"], ["B", "C"]], start="A", end="D")
    atoms = [{"kind": "compare", "a": 5, "op": ">", "b": 1}, {"kind": "compare", "a": 5, "op": ">", "b": 2}]
    for op, givens in (("interval_set_operations", {"A": {"lo": 3, "hi": 1}, "B": {"lo": 1, "hi": 2}, "items": ["union"]}),
                       ("interval_set_operations", {"A": {"lo": 1, "hi": 2}, "B": {"lo": 5, "hi": 6}, "items": ["intersection"]}),
                       ("finite_set_operations", {"A": [1, 2], "B": [3, 4], "items": ["intersection"]}),
                       ("finite_set_operations", {"A": [1, 2], "B": [2, 3], "items": ["a_complement"]}),
                       ("equation_root_sets", {"A": {"kind": "square", "rhs": 2}, "B": {"kind": "quad", "b": -2, "c": -3}, "items": ["union"]}),
                       ("equation_root_sets", {"A": {"kind": "square", "rhs": 4}, "B": {"kind": "quad", "b": -2, "c": -3}, "items": ["intersection"]}),
                       ("proposition_truth", {"atoms": atoms, "options": [["atom", 0], ["atom", 1], ["and", 0, 1], ["or", 0, 1], ["atom", 0]], "mode": "select_true"}),
                       ("proposition_truth", {"atoms": atoms, "options": [["atom", 9]], "mode": "truth"}),
                       ("implication_truth", {"claim": "nonsense"}),
                       ("condition_relation", {"cond": {"kind": "gt", "c": 3}, "target": {"kind": "lt", "c": 1}}),
                       ("choice_product", {"groups": [{"label": "x", "count": 3}]}),
                       ("grade_selection", {"grades": [3, 4]}),
                       ("divisor_counting", {"n": 360, "multiple_of": 7}),
                       ("at_least_one_pairing", {"head": {"total": 4, "vet": 4}, "tail": {"total": 3, "vet": 1}}),
                       ("ordered_at_least_one", {"others": 2, "special": 3, "picks": 3}),
                       ("two_set_counting", {"kind": "union", "U": 10, "A": 8, "B": 7, "AB": 9}),
                       ("two_set_counting", {"kind": "intersection_range", "U": 40, "A": 10, "B": 12}),
                       ("three_set_counting", {"kind": "union", "A": 5, "B": 5, "C": 5, "AB": 2, "BC": 2, "CA": 2, "ABC": 3}),
                       ("multiples_counting", {"limit": 100, "divisors": [1, 3]}),
                       ("coin_payment", {"coins": [10, 50], "total": 10}),
                       ("dice_sum_multiples", {"modulus": 2}),
                       ("race_outcomes", {"wins_needed": 2, "winner": "丙"}),
                       ("graph_paths", path),
                       ("graph_paths", {**path, "end": "A"}),
                       ("coin_toss_sequences", {"max_tosses": 2, "run": 3}),
                       ("tiling_count", {"cells": [[x, y] for x in range(5) for y in range(3)], "ask": {"kind": "total"}}),
                       ("tiling_count", {"cells": L, "ask": {"kind": "exactly", "k": 9}}),
                       ("region_pairs_claim", {"south": 2, "north": 3, "claimed": 4, "relation": "nonsense"})):
        with pytest.raises(ValueError):
            build(domain_operation=op, constraints=givens)


def test_no_backslash_in_fstring_expressions_for_python_311():
    for path in PKG.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FormattedValue):
                for inner in ast.walk(node.value):
                    assert not (isinstance(inner, ast.Constant) and isinstance(inner.value, str) and "\\" in inner.value), (path.name, node.lineno)


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_student_text_is_displayable(cid, skill_id, operation):
    for seed in SEEDS:
        p = _gen(cid, seed)
        text = p["question_text"]
        assert text.count("$") % 2 == 0, (seed, text)
        assert "sqrt(" not in text and "None" not in text and "**" not in text and "@" not in text and "\\\\" not in text
        assert p["display_answer"] and "None" not in p["display_answer"] and "**" not in p["display_answer"]
        assert p["explanation_steps"] and all(isinstance(s, str) and s.strip() and "None" not in s and "@" not in s and s.count("$") % 2 == 0 for s in p["explanation_steps"])
        contract = p["answer_contract"]
        if contract["answer_type"] == "multi_part":
            keys = [part["key"] for part in contract["parts"]]
            assert len(keys) == len(set(keys)) and all(part.get("prompt") or part.get("label") for part in contract["parts"])
            assert set(p["correct_answer"]) == set(keys)


def test_option_selection_hint_never_names_an_option():
    """12745: the format example may not eliminate (or hint at) any of the numbered options."""
    from agent_domains_candidate.counting_sets import build_sandbox as B
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    _skill, op, source, sampler = COMPONENTS[12745]
    seen = 0
    for variant in B.collect_variants(12745, op, source, sampler):
        payload = dispatch_registered_operation(B.DOMAIN_KEY, op, seed=0, constraints=dict(variant))[1]
        options = len(re.findall(r"\(\d\)", payload["question_text"].split("選出正確的命題。", 1)[1]))
        shown = {int(x) for x in payload["answer_contract"]["answer_format_example"].split(",")}
        assert options >= 4 and not (shown & set(range(1, options + 1))), (shown, options)
        seen += 1
    assert seen >= 8
