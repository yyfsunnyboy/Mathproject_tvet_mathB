"""Sandbox gate for 普高數學2 Unit 1 (數列與遞迴關係), skills gh_Sequence and gh_RecursiveRelation: per-component contract, oracle, grading.

Builds ``tmp/gh_math2_unit1_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived from the textbook stems (independent of the domain code); the textbook rows are read
from the formal database in read-only mode.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import sqlite3
from pathlib import Path

import pytest

from agent_domains_candidate.sequence_progression import build_sandbox as B
from agent_domains_candidate.sequence_progression import sequence_progression_domain as D
from agent_domains_candidate.sequence_progression.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.sequence_progression.sequence_progression_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.sequence_progression.verification import grade, verify_payload
from core.gencode.answer_format_hint import answer_format_example_for_contract
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
PKG = PROJECT_ROOT / "agent_domains_candidate" / "sequence_progression"
register_candidate_in_memory()
B.build_all()

FIGURE_COMPONENTS = {12668, 12673}  # 12668 draws its figure (coordinate_plane); 12673 reuses the reviewed textbook hand picture
CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u1_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)  # noqa


def _answer(cid: int):
    return _gen(cid)["correct_answer"]


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
        assert payload["fixed_domain_key"] == "sequence.progression"
        text = payload["question_text"]
        assert "$$" not in text and "承例題" not in text and "MATH_PARSE_FAILED" not in text
        if cid not in FIGURE_COMPONENTS:
            assert not payload.get("visual_spec") and not payload.get("image_assets")  # only the audited figure components carry a figure
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= SURFACE_FLOOR


def test_coverage_and_deferred_items_are_explicit():
    unit = set(range(12667, 12707)) - {12691}  # 12691 was the pseudo item removed in Stage 1: 39 formal rows
    assert set(COMPONENTS) | set(DEFERRED) == unit and len(unit) == 39
    assert not set(COMPONENTS) & set(DEFERRED)
    assert len(COMPONENTS) == 28 and len(DEFERRED) == 11
    assert {c for c in DEFERRED if c < 12686} == set() and FIGURE_COMPONENTS <= set(COMPONENTS)
    assert set(range(12700, 12707)) <= set(DEFERRED)  # gh_MathematicalInduction: proofs and figure patterns only
    assert all(len(reason) > 20 for reason in DEFERRED.values())


def test_solution_set_format_hints_do_not_expose_answers():
    for cid in (12671, 12676, 12683, 12684):
        for seed in SEEDS:
            payload = _gen(cid, seed)
            for part in payload["answer_contract"].get("parts") or [payload["answer_contract"]]:
                if part.get("checker_key") != "solution_set_checker":
                    continue
                hint = answer_format_example_for_contract(part)
                assert hint
                answer = part.get("expected_answer", payload["correct_answer"])
                shown = {D.num(value.strip()) for value in hint.split(",")}
                assert shown.isdisjoint({D.num(value) for value in answer}), (cid, seed, hint, answer)


def test_skill_bindings_and_stems_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: (r[1], r[2]) for r in con.execute("select id, skill_id, problem_text from textbook_examples where id between 12667 and 12706")}
        assert len(rows) == 39
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == {cid: rows[cid][0] for cid in COMPONENTS}
    figure_deferred = {12668, 12673, 12686, 12694, 12698, 12702, 12705}
    assert all(re.search("下圖|右圖|如圖", rows[cid][1]) for cid in figure_deferred)  # these deferred stems really depend on a figure
    assert all("數學歸納法" in rows[cid][1] for cid in {12696, 12700, 12701, 12703, 12704, 12706})  # these ask for an induction proof

    def numbers(s: str) -> set[str]:
        return set(re.findall(r"\d+", re.sub(r"\\left\\langle|\\right\\rangle|\\ldots", "", s)))

    for cid in [c for c in COMPONENTS if _skill_of(c) == "gh_Sequence" or c in (12689, 12693)]:  # variant 0 is the textbook stem: every number printed in the book stem is printed here too
        assert numbers(rows[cid][1]) <= numbers(_gen(cid)["question_text"]), cid


# --- source oracles: hand-derived answers ---------------------------------------------------------------------

def test_oracles_terms_and_geometric_readings():
    assert [_answer(12667)[f"part_{i}"] for i in range(1, 11)] == ["1", "3", "5", "7", "9", "1/4", "2/7", "3/10", "4/13", "5/16"]
    assert [_answer(12672)[f"part_{i}"] for i in range(1, 11)] == ["0", "-3", "-8", "-15", "-24", "-1/2", "1/4", "-1/6", "1/8", "-1/10"]
    assert _answer(12669) == {"part_1": "2", "part_2": "sqrt(2)", "part_3": "8*sqrt(2)", "part_4": "9"}  # 2(√2)^(n-1)=32 -> n=9
    assert _answer(12674) == {"part_1": "3", "part_2": "-2", "part_3": "48", "part_4": "8"}  # 3(-2)^(n-1)=-384 -> n=8


def test_oracles_geometric_relations():
    assert _answer(12670) == "1"  # r=-1/2, a1=16
    assert _answer(12675) == "1/2"  # a2=1, r=2
    assert _answer(12682) == {"part_1": "-1", "part_2": "-sqrt(3)"}  # r^3=-3sqrt3
    assert _answer(12683) == ["16", "27"]  # r=2 (a1=2) or r=3 (a1=1)


def test_oracles_three_numbers_arithmetic_and_statements():
    assert _answer(12671) == ["1", "4"] and _answer(12676) == ["1", "3"]
    assert _answer(12684) == ["1/2", "2"] and _answer(12685) == "3"  # 3, 10, 17
    assert _answer(12681) == {"part_1": "29", "part_2": "-1", "part_3": "31"}
    assert [_answer(c) for c in (12677, 12678, 12679, 12680)] == ["A", "A", "A", "A"]  # all four textbook statements are true


# --- grading behaviour ---------------------------------------------------------------------------------------

def test_radical_answers_accept_equivalent_forms_and_reject_neighbours():
    payload = _gen(12669)
    good = dict(payload["correct_answer"])
    for form in ("√2", "2^(1/2)", "sqrt(2)"):
        assert grade(payload, {**good, "part_2": form}, "gh_Sequence"), form
    assert grade(payload, {**good, "part_3": "8√2"}, "gh_Sequence")
    assert not grade(payload, {**good, "part_3": "8"}, "gh_Sequence")
    assert not grade(payload, {**good, "part_4": "8"}, "gh_Sequence")
    payload = _gen(12682)
    assert not grade(payload, {**payload["correct_answer"], "part_2": "sqrt(3)"}, "gh_Sequence")  # sign matters


def test_value_sets_are_order_free_but_complete():
    payload = _gen(12683)
    assert grade(payload, ["27", "16"], "gh_Sequence") and not grade(payload, ["16"], "gh_Sequence")
    assert not grade(payload, ["16", "27", "28"], "gh_Sequence")


def test_terms_are_graded_term_by_term_with_decimal_equivalents():
    payload = _gen(12667)
    good = dict(payload["correct_answer"])
    assert grade(payload, {**good, "part_6": "0.25"}, "gh_Sequence")
    assert not grade(payload, {**good, "part_6": "1/3"}, "gh_Sequence")


def test_domain_validators_reject_tampered_answers():
    for cid, (_s, op, source, _sampler) in COMPONENTS.items():
        matrix = D.build_sequence_progression_matrix(domain_operation=op, constraints=dict(source))
        validate = getattr(D, f"validate_{op}_matrix")
        assert validate(matrix), cid
        bad = json.loads(json.dumps(matrix))
        ans = bad["answer"]
        key = next(k for k in ("members", "terms", "first_terms", "shown_terms", "a_k", "a1", "smallest", "first_negative", "first_n", "n", "truth", "items", "ratio", "increment", "n_ups") if k in ans)
        value = ans[key]
        if key == "truth":
            ans[key] = not value
        elif key == "members":
            ans[key] = value + ["99"] if value else ["99"]
        elif key in ("first_negative", "first_n", "n"):
            ans[key] = value + 1
        elif key in ("first_terms", "shown_terms"):
            ans[key] = ["123"] + value[1:]
        elif key == "items":
            ans[key][0]["terms"][0] = "123"
        elif key == "terms":
            ans[key] = value[:-1] + ["999"]
        else:
            ans[key] = "12345"
        assert not validate(bad), (cid, key)


def test_degenerate_inputs_are_refused_by_the_domain():
    with pytest.raises(ValueError):
        D.geometric_from_terms(["1", "2", "5"], 4, 8)  # not geometric
    with pytest.raises(ValueError):
        D.geometric_from_relations("two_terms", m=1, A=1, n=3, B=4)  # even gap: r is ambiguous
    with pytest.raises(ValueError):
        D.progression_three_numbers("arith_positions", A=1, i=3, j=5)  # both solutions coincide
    with pytest.raises(ValueError):
        D.arithmetic_from_terms(1, 1, 3, 5)  # increasing: never negative


def test_no_backslash_in_fstring_expressions_for_python_311():
    for path in PKG.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FormattedValue):
                for inner in ast.walk(node.value):
                    assert not (isinstance(inner, ast.Constant) and isinstance(inner.value, str) and "\\" in inner.value), (path.name, node.lineno)


# --- ○× statements: both truth values, no fixed answer ----------------------------------------------------------------

@pytest.mark.parametrize("cid", [12677, 12678, 12679, 12680])
def test_true_false_statements_are_balanced_and_not_a_fixed_answer(cid):
    payloads = [_gen(cid, seed) for seed in SEEDS]
    answers = [p["correct_answer"] for p in payloads]
    assert 6 <= answers.count("A") <= 14  # ○ and × both occur often over the 20 served seeds
    assert len({p["question_text"] for p in payloads}) >= SURFACE_FLOOR
    assert len(set(answers[:8])) == 2  # not a long run of the same verdict at the start either
    for p in payloads:  # the stored verdict agrees with an independent re-derivation of the statement
        st = p["math_core"]["givens"]["statement"]
        assert p["math_core"]["target"]["truth"] == (p["correct_answer"] == "A")
        assert D.validate_sequence_statements_matrix({"domain": "sequence.progression", "domain_operation": "sequence_statements", "givens": {"statement": st},
                                                      "answer": p["math_core"]["target"], "validation_facts": {"domain_operation": "sequence_statements"}})


# --- student-facing text hygiene --------------------------------------------------------------------------------------

@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_student_text_is_displayable(cid, skill_id, operation):
    for seed in SEEDS:
        p = _gen(cid, seed)
        text = p["question_text"]
        assert text.count("$") % 2 == 0, (seed, text)
        assert "sqrt(" not in text and "None" not in text and "**" not in text and "\\\\\\\\" not in text
        assert p["display_answer"] and "sqrt(" not in p["display_answer"] and "None" not in p["display_answer"]
        assert p["explanation_steps"] and all(isinstance(s, str) and s.strip() and "None" not in s and s.count("$") % 2 == 0 for s in p["explanation_steps"])
        contract = p["answer_contract"]
        if contract["answer_type"] == "multi_part":  # every input box has its own prompt and a unique key
            keys = [part["key"] for part in contract["parts"]]
            assert len(keys) == len(set(keys)) and all(part.get("prompt") or part.get("label") for part in contract["parts"])
            assert set(p["correct_answer"]) == set(keys)


# --- gh_RecursiveRelation: hand-derived source oracles --------------------------------------------------------------------

def test_oracles_recurrence_processes():
    assert _answer(12687) == {"part_1": "1", "part_2": "3", "part_3": "243"}  # white triangles x3 each step: a6 = 3^5
    assert _answer(12690) == {"part_1": "1", "part_2": "2", "part_3": "256"}  # segments x2: a9 = 2^8
    assert _answer(12695) == {"part_1": "1", "part_2": "8", "part_3": "5"}  # 8^3 = 512 < 1000 < 8^4
    assert _answer(12689) == {"part_1": "8", "part_2": "3", "part_3": "33"}  # 2 + 3n = 101
    assert _answer(12688) == {"part_1": "1", "part_2": "4", "part_3": "9", "part_4": "16", "part_5": "2*n-1", "part_6": "36"}
    assert _answer(12692) == {"part_1": "n", "part_2": "21"}  # triangular numbers
    assert _answer(12699) == {"part_1": "sqrt(2)/2", "part_2": "sqrt(2)/2"}  # 16 (sqrt2/2)^9


def test_oracles_recurrence_statement_and_golden_ratio():
    assert _answer(12693) == "B"  # a1=2, a_n=2a_{n-1}: a4 = 16, not 8
    import sympy as sp

    assert sp.simplify(sp.sympify(_answer(12697)) - (1 + sp.sqrt(5)) / 2) == 0


def test_recurrence_blanks_are_graded_soundly():
    payload = _gen(12688)
    good = dict(payload["correct_answer"])
    assert grade(payload, {**good, "part_5": "-1+2n"}, "gh_RecursiveRelation") and grade(payload, {**good, "part_5": "2n-1"}, "gh_RecursiveRelation")
    assert not grade(payload, {**good, "part_5": "n"}, "gh_RecursiveRelation") and not grade(payload, {**good, "part_5": "2n+1"}, "gh_RecursiveRelation")
    payload = _gen(12699)
    good = dict(payload["correct_answer"])
    for form in ("√2/2", "1/√2", "sqrt(2)/2"):
        assert grade(payload, {**good, "part_1": form}, "gh_RecursiveRelation"), form
    assert not grade(payload, {**good, "part_1": "1/2"}, "gh_RecursiveRelation")


def test_value_set_format_hints_never_show_the_answer():
    for cid, (_s, _op, _src, _sampler) in COMPONENTS.items():
        for seed in SEEDS:
            contract = _gen(cid, seed)["answer_contract"]
            for part in contract.get("parts") or [contract]:
                example = str(part.get("answer_format_example") or "")
                expected = part.get("expected_answer", _gen(cid, seed)["correct_answer"])
                shown = ", ".join(map(str, expected)) if isinstance(expected, list) else str(expected)
                assert not example or example.replace(" ", "") != shown.replace(" ", ""), (cid, seed, example)


def test_every_variant_of_the_process_families_is_self_consistent():
    for cid in (12687, 12688, 12689, 12690, 12692, 12695, 12699):
        _s, op, source, sampler = COMPONENTS[cid]
        for variant in B.collect_variants(cid, op, source, sampler):
            matrix = D.build_sequence_progression_matrix(domain_operation=op, constraints=dict(variant))
            assert getattr(D, f"validate_{op}_matrix")(matrix), (cid, variant)


# --- figure / pattern components 12668 and 12673 (patch round after the Unit 1 publish) ----------------------------------------------

_DIR = {(0, 1): "U", (1, 0): "R", (0, -1): "D", (-1, 0): "L"}


def _ref_dir(n: int) -> str:
    """Textbook rule written out by hand: step 1->2 up, 2->3 right, 3->4 down, 4->5 right, 5->6 up, ..."""
    return "URDR"[(n - 1) % 4]


def _node(spec: dict, xy: list) -> dict:
    """The numbered point an arrow end belongs to (arrows stop short of the numbers)."""
    point = min(spec["points"], key=lambda p: (p["x"] - xy[0]) ** 2 + (p["y"] - xy[1]) ** 2)
    assert (point["x"] - xy[0]) ** 2 + (point["y"] - xy[1]) ** 2 < 0.5 ** 2
    return point


def _moves_of(arrow: dict) -> str:
    dx, dy = arrow["to"][0] - arrow["from"][0], arrow["to"][1] - arrow["from"][1]
    return _DIR[((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))]


def _stem_numbers(payload: dict) -> list[int]:
    return [int(x) for x in re.findall(r"\$(\d+)\$", payload["question_text"])]


def test_12668_answers_follow_the_rule_and_the_figure_matches_them():
    labels_seen, ups_seen = set(), set()
    for seed in SEEDS:
        payload = _gen(12668, seed)
        start, t, _t1, _t2, _start2, T = _stem_numbers(payload)
        assert start == 1
        want_ups = sum(1 for i in range(1, T) if _ref_dir(i) == "U")  # hand count of the up steps between 1 and T
        assert payload["correct_answer"]["part_2"] == str(want_ups)
        spec = payload["visual_spec"]
        assert spec["render_required"] and spec.get("show_grid") is False and spec["x_range"][0] > 0 and spec["y_range"][0] > 0  # no axes cross the picture
        want_pair = _ref_dir(t) + _ref_dir(t + 1)
        found = []
        for k, label in enumerate("ABCD"):  # read option k back out of the shipped figure
            lo = 20 + 3.9 * k
            first = [p for p in spec["points"] if p["label"] == str(t) and lo < p["x"] < lo + 3.6 and p["y"] < 23]
            assert len(first) == 1, (seed, k)
            x, y, moves = first[0]["x"], first[0]["y"], ""
            for number in (t, t + 1):
                arrow = next(a for a in spec["arrows"] if _node(spec, a["from"]) == {"x": x, "y": y, "label": str(number)})
                moves += _moves_of(arrow)
                end = _node(spec, arrow["to"])
                x, y = end["x"], end["y"]
                assert end["label"] == str(number + 1)
            if moves == want_pair:
                found.append(label)
        assert found == [payload["correct_answer"]["part_1"]], (seed, found)
        labels_seen.add(found[0])
        ups_seen.add(want_ups)
    assert labels_seen == set("ABCD") and len(ups_seen) >= 10


def test_12668_main_picture_is_the_textbook_spiral_and_options_are_distinct():
    payload = _gen(12668, 0)
    spec = payload["visual_spec"]
    main = [a for a in spec["arrows"] if a["from"][1] >= 24]
    assert [_moves_of(a) for a in main[:11]] == list("URDRURDRURD")  # 1 -> 12 as drawn in the textbook
    assert [_node(spec, a["from"])["label"] for a in main[:4]] == ["1", "2", "3", "4"]
    assert [a["color"] for a in main[:4]] == ["#c62828", "#111827", "#2e7d32", "#111827"]  # up red, down green, right black
    pairs = [tuple(o["pair"]) for o in payload["answer_contract"]["semantic_answer"]["options"]]
    assert len(set(pairs)) == 4


def test_12668_grading_contract():
    skill = _skill_of(12668)
    for seed in range(5):
        payload = _gen(12668, seed)
        parts = payload["answer_contract"]["parts"]
        assert [p["checker_key"] for p in parts] == ["choice_label_checker", "rational_checker"]
        good = payload["correct_answer"]
        assert grade(payload, good, skill)
        shown = next(c["value"] for c in parts[0]["choices"] if c["label"] == good["part_1"])  # the dropdown submits the option text
        assert grade(payload, {**good, "part_1": shown}, skill)
        wrong_choice = next(c["label"] for c in parts[0]["choices"] if c["label"] != good["part_1"])
        assert not grade(payload, {**good, "part_1": wrong_choice}, skill)
        assert not grade(payload, {**good, "part_2": str(int(good["part_2"]) + 1)}, skill)
        assert grade(payload, {**good, "part_2": f"{int(good['part_2'])}.0"}, skill)  # equivalent decimal


def test_12673_counts_follow_the_hand_and_the_reviewed_image_is_reused():
    ladder = ["大拇指", "食指", "中指", "無名指", "小指", "無名指", "中指", "食指"]
    skill = _skill_of(12673)
    fingers_seen, ks_seen = set(), set()
    for seed in SEEDS:
        payload = _gen(12673, seed)
        text = payload["question_text"]
        ks = [int(x) for x in re.findall(r"\$a_\{(\d+)\}\$", text)]
        N = int(re.findall(r"數到 \$(\d+)\$", text)[0])
        thumb = [n for n in range(1, 8 * max(ks) + 2) if ladder[(n - 1) % 8] == "大拇指"]  # hand count: thumb ... pinky ... back to thumb
        answer = payload["correct_answer"]
        assert [answer[f"part_{i + 1}"] for i in range(len(ks))] == [str(thumb[k - 1]) for k in ks]
        finger = ladder[(N - 1) % 8]
        last = f"part_{len(ks) + 1}"
        choices = payload["answer_contract"]["parts"][-1]["choices"]
        assert next(c["value"] for c in choices if c["label"] == answer[last]).endswith(finger)
        fingers_seen.add(finger)
        ks_seen.add(tuple(ks))
        assert payload["reuse_textbook_image"] is True and payload["textbook_example_id"] == 12673
        assert not payload.get("visual_spec")  # the hand figure is the reviewed crop, never redrawn
        assert grade(payload, answer, skill)
        shown = next(c["value"] for c in choices if c["label"] == answer[last])
        assert grade(payload, {**answer, last: shown}, skill)
        assert not grade(payload, {**answer, "part_1": str(int(answer["part_1"]) + 1)}, skill)
        assert not grade(payload, {**answer, last: next(c["label"] for c in choices if c["label"] != answer[last])}, skill)
    assert fingers_seen == {"大拇指", "食指", "中指", "無名指", "小指"} and len(ks_seen) >= 3


def test_pattern_validators_reject_tampered_answers():
    cases = (("figure_path_pattern", {"start": 1, "t": 106, "T": 107, "order": [2, 3, 0, 1]}, (("n_ups", 26), ("correct_option", "A"))),
             ("finger_counting_cycle", {"ks": [1, 2, 3, 4], "N": 999}, (("finger", "食指"), ("terms", ["1", "9", "17", "26"]))))
    for op, givens, tamper in cases:
        matrix = D.build_sequence_progression_matrix(domain_operation=op, constraints=dict(givens))
        validate = getattr(D, f"validate_{op}_matrix")
        assert validate(matrix)
        for key, bad in tamper:
            assert not validate({**matrix, "answer": {**matrix["answer"], key: bad}}), (op, key)
    with pytest.raises(ValueError):
        D.build_sequence_progression_matrix(domain_operation="figure_path_pattern", constraints={"start": 1, "t": 5, "T": 9, "order": [0, 0, 1, 2]})
    with pytest.raises(ValueError):
        D.build_sequence_progression_matrix(domain_operation="figure_path_pattern", constraints={"start": 1, "t": 5, "T": 9, "order": [0, 1, 2, 3], "cycle": ["U", "R", "U", "R"]})
