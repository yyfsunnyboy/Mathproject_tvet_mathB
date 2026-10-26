"""Sandbox gate for 普高數學2 Unit 2 (級數), skills gh_Series and gh_CommonSeriesSummationFormulas: per-component contract, oracle, grading.

Builds ``tmp/gh_math2_unit2_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory only.
Source oracles are hand-derived from the textbook stems (independent of the domain code); the textbook rows are read from the
formal database in read-only mode.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import sqlite3
from pathlib import Path

import pytest
import sympy as sp

from agent_domains_candidate.series_summation import build_sandbox as B
from agent_domains_candidate.series_summation import series_summation_domain as D
from agent_domains_candidate.series_summation.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.series_summation.series_summation_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.series_summation.verification import equivalent_value, grade, parts_of, verify_payload, wrong_value
from core.gencode.answer_format_hint import answer_format_example_for_contract
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
PKG = PROJECT_ROOT / "agent_domains_candidate" / "series_summation"
FIGURE_COMPONENTS = {12709, 12712, 12743, 12734}  # the reviewed textbook picture is reused; nothing is drawn
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
FLOOR = {12740: 4}  # four distinct statements exist; every other component must show many different questions


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u2_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


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
        assert payload["fixed_domain_key"] == "sequence.series_sums"
        text = payload["question_text"]
        assert "$$" not in text and "承例題" not in text and "MATH_PARSE_FAILED" not in text
        if cid in FIGURE_COMPONENTS:
            assert payload["reuse_textbook_image"] is True and not payload.get("visual_spec")  # reviewed crop reused, never redrawn
        else:
            assert not payload.get("reuse_textbook_image") and not payload.get("visual_spec") and not payload.get("image_assets")
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= FLOOR.get(cid, 10), len(surfaces)


def test_coverage_and_deferred_items_are_explicit():
    unit = set(range(12707, 12744))
    assert set(COMPONENTS) | set(DEFERRED) == unit and len(unit) == 37
    assert not set(COMPONENTS) & set(DEFERRED)
    assert len(COMPONENTS) == 33 and set(DEFERRED) == {12719, 12727, 12731, 12735}
    assert all(len(reason) > 20 for reason in DEFERRED.values())
    per_skill = {skill: sum(1 for s in COMPONENTS.values() if SKILLS[s[0]] == skill) for skill in SKILLS.values()}
    assert per_skill == {"gh_Series": 24, "gh_CommonSeriesSummationFormulas": 9}


def test_skill_bindings_and_stems_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = {r[0]: (r[1], r[2]) for r in con.execute("select id, skill_id, source_description from textbook_examples where id between 12707 and 12743")}
        assert len(rows) == 37
        for cid in COMPONENTS:
            assert rows[cid][0] == _skill_of(cid), cid
    finally:
        con.close()
    for cid in COMPONENTS:  # variant 0 is the textbook question: every number the textbook stem prints appears in the generated stem
        con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
        try:
            source = con.execute("select problem_text from textbook_examples where id=?", (cid,)).fetchone()[0]
        finally:
            con.close()
        stem = _gen(cid, 0)["question_text"]
        digits = lambda t: re.findall(r"\d+", re.sub(r"\s", "", t))  # noqa: E731
        assert sorted(set(digits(source))) == sorted(set(digits(stem))) or set(digits(source)) <= set(digits(stem)) | {"1", "2", "3", "4", "5"}, (cid, digits(source), digits(stem))


# --- hand-derived source oracles (the textbook answers, computed by hand; not through the domain) -------------------------------------

def _eq(a, b):
    return sp.simplify(sp.sympify(str(a), rational=True) - sp.sympify(str(b), rational=True)) == 0


def test_oracles_arithmetic_series():
    assert _answers(12707) == ["-3", "300"]    # 24+6d... S7=7*24+21d=105 -> d=-3 ; 3+7+...+47 = 12*(3+47)/2
    assert _answers(12714) == ["3", "-21"]     # 8*6+28d=132 -> d=3 ; 9+5+1+...+(-15): 7 terms, 7*(9-15)/2
    assert _answers(12722) == ["-5", "140"]    # 9*36+36d=144 -> d=-5 ; (-3)+...+23: 14 terms, 14*20/2
    assert _answers(12708) == ["22", "275"]    # a1+a25 = 2*a13 ; S25 = 25*11
    assert _answers(12715) == ["1", "1"]       # S20=10 -> every symmetric pair sums to 10*2/20
    assert _answers(12723) == ["456"]          # 19 rows * middle row 24
    assert _answers(12729) == ["270"]          # 12*(15+75)/4
    assert _answers(12716) == ["13"]           # 40n > 500 -> n >= 13
    assert _answers(12724) == ["6"]            # 1.5*n(n+1) >= 63 -> n = 6
    p = _gen(12709)["correct_answer"]
    assert p["part_1"] == "100" and _eq(sp.sympify(p["part_2"], locals={"n": sp.Symbol("n")}).subs("n", 7), 49)  # first 10 rows 10^2 ; n^2


def test_oracles_geometric_series():
    p = _gen(12710)["correct_answer"]
    assert _eq(p["part_1"], 21 + 21 * sp.sqrt(2)) and p["part_2"] == "765"  # 3(1-8)/(1-sqrt2) ; 3*(2^8-1)
    assert _answers(12717) == ["33", "1089"]   # 3(1+32)/3 ; 729(1-(1/3)^5)/(2/3)
    assert _answers(12725) == ["189", "29524"]  # 96*(1-1/64)*2 ; -2*(1-3^10)/4
    assert sorted(_gen(12711)["correct_answer"], key=int) == ["-122", "242"]  # r = +-3
    assert _answers(12718) == ["-85"]          # r=-2, a1=1 -> (1-256)/3
    assert _answers(12726) == ["4", "5"]       # 2(1-4^5)/(1-4) = 682
    assert _answers(12730) == ["1023/8"]       # 96*(1-4^-5)/(1-1/4)
    assert _answers(12712) == ["1365"]         # 1+4+...+4^5
    assert _answers(12743) == ["1022", "1022"]  # 2^10-2 squares ; 1024*(1-2^-9)


def test_oracles_partial_sums_and_statements():
    n = sp.Symbol("n")
    p = _gen(12713)["correct_answer"]
    assert (p["part_1"], p["part_2"]) == ("2", "18") and _eq(sp.sympify(p["part_3"], locals={"n": n}).subs(n, 4), 54)  # S_n=3^n-1 -> 2*3^(n-1)
    p = _gen(12720)["correct_answer"]
    assert (p["part_1"], p["part_2"]) == ("5", "-1") and all(_eq(sp.sympify(p["part_3"], locals={"n": n}).subs(n, k), 7 - 2 * k) for k in range(1, 6))
    p = _gen(12728)["correct_answer"]
    assert p["part_1"] == "-1" and all(_eq(sp.sympify(p["part_2"], locals={"n": n}).subs(n, k), 3 - 4 * k) for k in range(1, 6))
    assert [_gen(c)["correct_answer"] for c in (12721, 12739, 12740)] == ["A", "B", "A"]  # true, false (exponent 11), true


def test_oracles_power_sums():
    assert _answers(12732) == ["2870", "2485"]
    assert _answers(12736) == ["44100", "41075"]
    assert _answers(12733) == ["1540", "1330"]
    assert _answers(12737) == ["21168"]
    assert _answers(12741) == ["1185", "24200"]
    assert _answers(12738) == ["470"]          # (11^2+...+15^2) - (1^2+...+10^2) = 855 - 385
    assert _answers(12742) == ["14"]           # (n(n+1)/2)^2 = 11025 -> n = 14
    p = _gen(12734)["correct_answer"]
    assert p["part_1"] == "B" and p["part_2"] == "650"  # option (2) 12^2 ; 12*13*25/6


def _answers(cid: int) -> list[str]:
    ans = _gen(cid)["correct_answer"]
    if isinstance(ans, dict):
        return [ans[k] if isinstance(ans[k], str) else ans[k] for k in sorted(ans, key=lambda k: int(k.split("_")[1]))]
    return [ans]


# --- grading: equivalent forms accepted, neighbours rejected -------------------------------------------------------------------------

def test_radical_and_expression_answers_accept_equivalent_forms_and_reject_neighbours():
    skill = _skill_of(12710)
    p = _gen(12710)
    assert grade(p, {"part_1": "21*sqrt(2)+21", "part_2": "765"}, skill) and grade(p, {"part_1": "21(1+sqrt(2))", "part_2": "765.0"}, skill)
    assert not grade(p, {"part_1": "21*sqrt(2)", "part_2": "765"}, skill) and not grade(p, {"part_1": "21+21*sqrt(2)", "part_2": "764"}, skill)
    skill = _skill_of(12713)
    p = _gen(12713)
    assert grade(p, {"part_1": "2", "part_2": "18", "part_3": "2*3^(n-1)"}, skill) and grade(p, {"part_1": "2", "part_2": "18", "part_3": "(2/3)*3^n"}, skill)
    assert not grade(p, {"part_1": "2", "part_2": "18", "part_3": "3^n-1"}, skill)
    p = _gen(12720)
    assert grade(p, {"part_1": "5", "part_2": "-1", "part_3": "-2n+7"}, _skill_of(12720)) and not grade(p, {"part_1": "5", "part_2": "-1", "part_3": "-2n+6"}, _skill_of(12720))


def test_value_sets_are_order_free_but_complete():
    skill, p = _skill_of(12711), _gen(12711)
    assert grade(p, "-122, 242", skill) and grade(p, "242,-122", skill)
    assert not grade(p, "242", skill) and not grade(p, "242, -122, 5", skill) and not grade(p, "242, 122", skill)


def test_set_format_hints_never_show_the_answer():
    for cid in (12711,):
        for seed in SEEDS:
            payload = _gen(cid, seed)
            for part in payload["answer_contract"].get("parts") or [payload["answer_contract"]]:
                if part.get("checker_key") != "solution_set_checker":
                    continue
                hint = answer_format_example_for_contract(part)
                assert hint
                answer = part.get("expected_answer", payload["correct_answer"])
                shown = {D.num(v.strip()) for v in hint.split(",")}
                assert not (shown & {D.num(m) for m in answer}), (seed, hint, answer)


def test_two_choice_statements_are_balanced_and_not_a_fixed_answer():
    for cid in (12721, 12739, 12740):
        answers = [_gen(cid, s)["correct_answer"] for s in SEEDS]
        assert {"A", "B"} == set(answers) and 4 <= answers.count("A") <= 16, (cid, answers)


def test_tower_choices_follow_the_shuffled_order():
    seen = set()
    for seed in SEEDS:
        p = _gen(12734, seed)
        contract = p["answer_contract"]
        layers = int(re.findall(r"堆成 \$(\d+)\$ 層高", p["question_text"])[0])
        choices = {c["label"]: c["value"] for c in contract["parts"][0]["choices"]}
        right = choices[p["correct_answer"]["part_1"]]
        assert right.endswith(f"{layers}²") and "+" not in right  # the correct one is always the plain "L squared"
        seen.add(p["correct_answer"]["part_1"])
    assert seen == set("ABCD")


# --- validators ---------------------------------------------------------------------------------------------------------------------

def test_domain_validators_reject_tampered_answers():
    tamper = {"arithmetic_series_items": lambda a: a["items"][0].update(value="999"),
              "arithmetic_series_relation": lambda a: a.update({k: "12345" for k in ("total", "pair_sum", "count", "days", "values") if k in a and k != "values"}) or (a.update(values=["99"] * len(a["values"])) if "values" in a else None),
              "geometric_series_items": lambda a: a["items"][0].update(value="999"),
              "geometric_series_relation": lambda a: a.update({k: ("12345" if isinstance(a[k], str) else 12345) for k in ("sum", "total", "ratio", "count", "n") if k in a}) or (a.update(sums=["1", "2"]) if "sums" in a else None),
              "partial_sum_terms": lambda a: a["values"][0].update(value="12345"),
              "power_sums": lambda a: a.update({k: ("12345" if isinstance(a[k], str) else 12345) for k in ("difference", "total", "n", "bottom") if k in a}) or (a.update(values=["1"] * len(a["values"])) if "values" in a else None),
              "series_statements": lambda a: a.update(truth=not a["truth"]),
              "fish_rows": lambda a: a.update(first_k="12345")}
    done = set()
    for cid, (_s, op, source, _sampler) in COMPONENTS.items():
        matrix = D.build_series_summation_matrix(domain_operation=op, constraints=dict(source))
        validate = getattr(D, f"validate_{op}_matrix")
        assert validate(matrix), cid
        bad = json.loads(json.dumps(matrix))
        tamper[op](bad["answer"])
        assert not validate(bad), (cid, op)
        done.add(op)
    assert done == set(OP)


def test_degenerate_inputs_are_refused_by_the_domain():
    build = D.build_series_summation_matrix
    for op, givens in (("geometric_series_items", {"items": [{"kind": "ratio_sum", "a1": 3, "r": 1, "n": 5}]}),
                       ("arithmetic_series_items", {"items": [{"kind": "sum_terms", "first": 3, "d": 4, "last": 46}]}),
                       ("arithmetic_series_relation", {"kind": "mid_total", "n": 20, "mid": 5}),
                       ("geometric_series_relation", {"kind": "two_terms", "p": 2, "q": 4, "A": 6, "B": 50, "n": 5}),
                       ("partial_sum_terms", {"form": {"kind": "exp", "c": 1, "base": 3}, "asks": [["median"]]}),
                       ("power_sums", {"kind": "layer_split", "layers": 10, "top": 12}),
                       ("power_sums", {"kind": "tower", "layers": 12, "order": [0, 0, 1, 2]}),
                       ("series_statements", {"statement": {"kind": "cube_sum", "claim": "nonsense"}})):
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
        assert p["display_answer"] and "sqrt(" not in p["display_answer"] and "None" not in p["display_answer"] and "**" not in p["display_answer"]
        assert p["explanation_steps"] and all(isinstance(s, str) and s.strip() and "None" not in s and "@" not in s and s.count("$") % 2 == 0 for s in p["explanation_steps"])
        contract = p["answer_contract"]
        if contract["answer_type"] == "multi_part":
            keys = [part["key"] for part in contract["parts"]]
            assert len(keys) == len(set(keys)) and all(part.get("prompt") or part.get("label") for part in contract["parts"])
            assert set(p["correct_answer"]) == set(keys)
