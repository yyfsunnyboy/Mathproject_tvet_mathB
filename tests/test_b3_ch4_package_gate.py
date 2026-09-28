# -*- coding: utf-8 -*-
"""B3 Chapter 4 (exponents and logarithms) package gate.

Coverage, generator samples, independent math verification, presentation
gates, checker contracts, visuals, runtime, publication, and mock exam scope.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _b3_ch4_tex import log_arguments_positive, math_segments, numeric, tex_to_sympy  # noqa: E402
from core.domain.exponential_logarithmic_domain import (  # noqa: E402
    OPS,
    SOURCE_SPECS,
    ZERO_SOURCE_SKILLS,
    build_exponential_logarithmic_matrix,
    validate_exponential_logarithmic_matrix,
)
from core.gencode.choice_contract_validator import validate_vocational_multiple_choice  # noqa: E402
from core.gencode.exponential_logarithmic_capability_adapter import (  # noqa: E402
    adapt_exponential_logarithmic_matrix,
)
from core.gencode.runtime_skill_wrapper import check_answer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_IDS = list(range(12127, 12273))
SKILLS = [
    "vh_數學B3_SubSection_4_1_1",
    "vh_數學B3_SubSection_4_1_2",
    "vh_數學B3_SubSection_4_1_3",
    "vh_數學B3_SubSection_4_2_1",
    "vh_數學B3_SubSection_4_2_2",
    "vh_數學B3_SubSection_4_3_1",
    "vh_數學B3_SubSection_4_3_2",
    "vh_數學B3_SubSection_4_4_1",
    "vh_數學B3_SubSection_4_4_2",
    "vh_數學B3_SubSection_4_5_1",
    "vh_數學B3_SubSection_4_5_3",
]
ZERO_SOURCE_SKILL = "vh_數學B3_SubSection_4_5_2"
SAMPLES_PER_FAMILY = 100

SOURCE_LABEL_RE = re.compile(r"例\s*\d|隨堂|習題|基礎題|進階題|自我評量|統測|〔|〕|CH4")
SOLUTION_MARKER_RE = re.compile(r"(?:^|[\n。．；])\s*(?:解|答|詳解)\s*[：:]|【解】|〈解〉|\[解\]")
EQ_RESIDUE_RE = re.compile(r"\bEQ\b|\\eq\b|\\rm\b|MERGEFORMAT|\{\s*\}")
HTML_TAG_RE = re.compile(r"<[A-Za-z/!]")
_MATH_SPAN_RE = re.compile(r"\\\(.+?\\\)", re.S)

EVAL_OPS = {
    "exp_integer_power_eval", "exp_zero_negative_eval", "exp_rational_power_eval", "exp_rational_power_combo",
    "exp_integer_exponent_simplify", "exp_rational_exponent_simplify",
    "log_definition_eval", "log_basic_property_eval", "log_rational_value_eval", "log_product_quotient_eval",
    "log_linear_combination_eval", "log_change_base_chain_eval", "log_change_base_product_eval",
}
EQUATION_OPS = {
    "exp_equation_same_base", "exp_equation_convert_base", "exp_equation_quadratic_sub",
    "exp_equation_factor_common", "log_equation_linear_arg", "log_equation_product_quadratic",
    "log_equation_quadratic_arg", "log_equation_solve_base",
}
SYMBOL_VALUES = {sp.Symbol("a"): sp.Rational(17, 10), sp.Symbol("b"): sp.Rational(23, 10), sp.Symbol("c"): sp.Rational(13, 10)}


# ---------------------------------------------------------------- helpers

def _matrix(example_id: int, seed: int) -> dict:
    return build_exponential_logarithmic_matrix(seed, {"textbook_example_id": example_id})


def _payload(example_id: int, matrix: dict) -> dict:
    spec = SOURCE_SPECS[example_id]
    payload = adapt_exponential_logarithmic_matrix(
        matrix,
        domain_operation=spec["op"],
        presentation_mode=spec["presentation"],
        answer_type=matrix["answer_type"],
        component_id=f"src_{example_id}",
        textbook_example_id=example_id,
    )
    payload["skill_id"] = spec["skill_id"]
    payload["curriculum_profile"] = "vocational_high_b"
    return payload


def _student_answer(payload: dict):
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    if len(parts) >= 2:
        return {str(part.get("key")): part.get("expected_answer") for part in parts}
    if payload.get("answer_type") == "single_choice" or payload.get("presentation_mode") == "single_choice":
        return payload.get("correct_answer")
    return payload.get("semantic_answer")


def _ids_by_op() -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        grouped[spec["op"]].append(example_id)
    return grouped


def _stem_violations(text: str) -> list[str]:
    errors = []
    if SOURCE_LABEL_RE.search(text):
        errors.append("source_label")
    if SOLUTION_MARKER_RE.search(text):
        errors.append("solution_marker")
    if EQ_RESIDUE_RE.search(text):
        errors.append("eq_residue")
    if HTML_TAG_RE.search(text):
        errors.append("html_markup")
    outside = _MATH_SPAN_RE.sub("", text)
    if "\\" in outside or "^" in outside or "_{" in outside:
        errors.append("raw_tex_outside_math")
    if re.search(r"(?<![A-Za-z\\])log", outside):
        errors.append("bare_log_outside_math")
    if text.count(r"\(") != text.count(r"\)"):
        errors.append("unbalanced_math")
    return errors


def _delimiters_wellformed(text: str) -> bool:
    if any(r"\(" in seg or r"\)" in seg for seg in re.findall(r"\$(.*?)\$", text, flags=re.S)):
        return False
    rest = re.sub(r"\$.*?\$", "", text, flags=re.S)
    depth = 0
    for token in re.findall(r"\\\(|\\\)", rest):
        depth += 1 if token == r"\(" else -1
        if depth not in (0, 1):
            return False
    return depth == 0 and "$" not in rest


def _payload_display_texts(payload: dict) -> list[str]:
    texts = [str(payload.get("question_text") or "")]
    for row in [*(payload.get("choices") or []), *(payload.get("choices_display") or [])]:
        if isinstance(row, dict):
            texts += [str(row.get("text") or ""), str(row.get("display") or "")]
        else:
            texts.append(str(row))
    texts += [str(opt) for opt in payload.get("options") or []]
    return texts


def _all_student_text(matrix: dict) -> list[str]:
    texts = [matrix["question_text"]]
    for item in (matrix.get("stem_structure") or {}).get("items") or []:
        texts.append(str(item.get("text") or ""))
    for choice in matrix.get("choices") or []:
        texts.append(str(choice.get("text") or ""))
    return texts


def _givens(matrix: dict) -> dict[str, Decimal]:
    raw = matrix["validation_facts"].get("given_approximations") or {}
    return {str(k): Decimal(str(v)) for k, v in raw.items() if str(k).startswith("log ")}


def _num(value) -> float:
    return float(sp.N(sp.sympify(str(value).replace("^", "**"))))


def _close(u: complex, v: complex) -> bool:
    return abs(u - v) < 1e-9 * max(1.0, abs(v))


def _answer_expr(text: str) -> sp.Expr:
    return sp.sympify(str(text).replace("^", "**"), locals={name: sp.Symbol(name) for name in "abc"})


# ---------------------------------------------------------------- coverage

def test_source_coverage_is_complete_and_matches_formal_skills():
    assert set(SOURCE_SPECS) == set(CHAPTER_IDS)
    assert len(SOURCE_SPECS) == 146
    assert {spec["skill_id"] for spec in SOURCE_SPECS.values()} == set(SKILLS)
    assert ZERO_SOURCE_SKILLS == frozenset({ZERO_SOURCE_SKILL})
    assert all("SubSection" in skill for skill in SKILLS)
    for skill in ("vh_數學B3_SubSection_4_3_1", "vh_數學B3_SubSection_4_3_2"):
        assert any(spec["skill_id"] == skill for spec in SOURCE_SPECS.values())


def test_zero_source_skill_is_not_fabricated():
    assert not (ROOT / "skills" / f"{ZERO_SOURCE_SKILL}.py").exists()
    assert not (ROOT / "agent_skills_v3" / ZERO_SOURCE_SKILL).exists()
    assert all(spec["skill_id"] != ZERO_SOURCE_SKILL for spec in SOURCE_SPECS.values())


def test_every_family_is_bound_and_every_op_is_registered():
    from core.registry.domain_operation_registry import get_domain_spec

    assert set(_ids_by_op()) == set(OPS)
    domain = get_domain_spec("exponential.logarithmic")
    assert domain is not None
    assert set(domain.operations) == set(OPS)


def test_packages_match_source_specs():
    for skill in SKILLS:
        manifest = json.loads((ROOT / "agent_skills_v3" / skill / "component_manifest.json").read_text(encoding="utf-8"))
        expected = sorted(eid for eid, spec in SOURCE_SPECS.items() if spec["skill_id"] == skill)
        rows = manifest["components"]
        assert manifest["skill_id"] == skill
        assert manifest["publish_status"] == "package_ready"
        assert manifest["component_count"] == len(rows) == len(expected)
        assert [row["textbook_example_id"] for row in rows] == expected
        for row in rows:
            spec = SOURCE_SPECS[row["textbook_example_id"]]
            assert row["status"] == "verified"
            assert row["problem_type_id"] == spec["op"]
            assert row["presentation_mode"] == spec["presentation"]
            assert (ROOT / "agent_skills_v3" / skill / row["generate_py"]).is_file()


def test_runtime_files_have_no_scratch_or_absolute_paths():
    files = [
        *sorted((ROOT / "core" / "domain").glob("exponential_logarithmic_*.py")),
        ROOT / "core" / "gencode" / "exponential_logarithmic_capability_adapter.py",
        *[ROOT / "skills" / f"{skill}.py" for skill in SKILLS],
        *sorted(p for skill in SKILLS for p in (ROOT / "agent_skills_v3" / skill).rglob("*.py")),
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"[A-Za-z]:\\\\|scratch/|reports/|cache/", text), path


# ---------------------------------------------------------------- generator samples

def test_family_sample_gate():
    """Generator sample gate plus stem, MCQ identity, arity, and self-check gates."""
    grouped = _ids_by_op()
    failures: list[tuple] = []
    total = 0
    for op, example_ids in sorted(grouped.items()):
        for offset in range(SAMPLES_PER_FAMILY):
            example_id = example_ids[offset % len(example_ids)]
            seed = 7919 * offset + example_id
            try:
                matrix = _matrix(example_id, seed)
            except Exception as exc:  # noqa: BLE001
                failures.append((op, example_id, seed, f"build:{exc}"))
                continue
            total += 1
            if not validate_exponential_logarithmic_matrix(matrix):
                failures.append((op, example_id, seed, "invalid_matrix"))
                continue
            for text in _all_student_text(matrix):
                for err in _stem_violations(text):
                    failures.append((op, example_id, seed, err, text[:80]))
            payload = _payload(example_id, matrix)
            for text in _payload_display_texts(payload):
                if not _delimiters_wellformed(text):
                    failures.append((op, example_id, seed, "malformed_math_delimiters", text[:80]))
            if matrix["presentation_mode"] == "single_choice":
                choices = payload["choices"]
                values = [row["value"] for row in choices]
                if len(values) != 4 or len(set(values)) != 4:
                    failures.append((op, example_id, seed, "mcq_shape"))
                if any("<" in str(row.get("text") or "") for row in matrix["choices"]):
                    failures.append((op, example_id, seed, "raw_lt_in_choice_html"))
                errors = validate_vocational_multiple_choice(payload, payload["skill_id"])
                if errors:
                    failures.append((op, example_id, seed, "mcq_contract", errors))
                label = matrix["correct_label"]
                for row in choices:
                    accepted = check_answer(row["label"], payload.get("correct_answer"), payload=payload)
                    if accepted != (row["label"] == label):
                        failures.append((op, example_id, seed, "mcq_grading", row["label"]))
            else:
                if matrix["answer_type"] == "multi_part":
                    parts = payload["answer_contract"]["parts"]
                    if len(parts) != matrix["validation_facts"]["multipart_count"] or len(parts) < 2:
                        failures.append((op, example_id, seed, "multipart_arity"))
                if not check_answer(_student_answer(payload), payload.get("correct_answer"), payload=payload):
                    failures.append((op, example_id, seed, "self_check"))
    assert total >= max(1500, len(OPS) * 60)
    summary = Counter((row[0], row[3]) for row in failures)
    assert not failures, (summary, failures[:5])


def test_generated_questions_differ_from_source_stems_across_seeds():
    for op, example_ids in _ids_by_op().items():
        example_id = example_ids[0]
        stems = set()
        for seed in range(12):
            matrix = _matrix(example_id, seed)
            stems.add((matrix["question_text"], tuple(c["text"] for c in matrix.get("choices") or [])))
        assert len(stems) >= 3, op


# ---------------------------------------------------------------- independent math

def _target_expression(matrix: dict) -> str:
    seg = max(math_segments(matrix["question_text"]), key=len)
    if seg.endswith("="):
        return seg[:-1]
    if "=" in seg:
        return seg.split("=", 1)[1]
    return seg


def _item_texts(matrix: dict) -> list[str]:
    return [str(row["text"]) for row in (matrix.get("stem_structure") or {}).get("items") or []]


@pytest.mark.parametrize("op", sorted(EVAL_OPS))
def test_evaluation_answers_rederived_from_student_tex(op):
    for example_id in _ids_by_op()[op]:
        for seed in range(12):
            matrix = _matrix(example_id, seed)
            value = matrix["answer"]["value"]
            if isinstance(value, dict):
                pairs = [(math_segments(item)[0], ans) for item, ans in zip(_item_texts(matrix), value.values())]
            else:
                pairs = [(_target_expression(matrix), value)]
            for tex, answer in pairs:
                got = numeric(tex_to_sympy(tex), SYMBOL_VALUES)
                want = numeric(_answer_expr(answer), SYMBOL_VALUES)
                assert _close(got, want), (example_id, seed, tex, answer)


@pytest.mark.parametrize("op", sorted(EQUATION_OPS))
def test_equation_roots_satisfy_student_equation_and_log_domain(op):
    for example_id in _ids_by_op()[op]:
        for seed in range(12):
            matrix = _matrix(example_id, seed)
            value = matrix["answer"]["value"]
            if isinstance(value, dict) and op != "log_equation_quadratic_arg":
                pairs = [(math_segments(item), ans) for item, ans in zip(_item_texts(matrix), value.values())]
            else:
                answers = list(value.values()) if isinstance(value, dict) else [value]
                pairs = [(math_segments(matrix["question_text"]), ans) for ans in answers]
            for segments, answer in pairs:
                equation = max((s for s in segments if "=" in s and not s.endswith("=")), key=len)
                left, right = equation.split("=", 1)
                symbols: dict = {}
                lhs, rhs = tex_to_sympy(left, symbols), tex_to_sympy(right, symbols)
                var = symbols.get("x") or symbols.get("a")
                sub = {var: _answer_expr(answer)}
                assert _close(numeric(lhs, sub), numeric(rhs, sub)), (example_id, seed, equation, answer)
                assert log_arguments_positive(lhs, sub) and log_arguments_positive(rhs, sub)
                if op == "log_equation_product_quadratic":
                    rejected = {var: sp.Integer(matrix["params"]["rejected"])}
                    assert not (log_arguments_positive(lhs, rejected) and log_arguments_positive(rhs, rejected))
            if op == "log_equation_quadratic_arg":
                roots = [Fraction(v) for v in value.values()]
                assert roots == sorted(roots)


def test_log_express_in_ab_matches_definitions():
    for example_id in _ids_by_op()["log_express_in_ab"]:
        for seed in range(12):
            matrix = _matrix(example_id, seed)
            defs = {}
            for seg in math_segments(matrix["question_text"]):
                m = re.fullmatch(r"(.+)=([ab])", seg)
                if m and r"\log" in m.group(1):
                    defs[sp.Symbol(m.group(2))] = sp.N(tex_to_sympy(m.group(1)), 40)
            assert set(defs) == {sp.Symbol("a"), sp.Symbol("b")}
            value = matrix["answer"]["value"]
            if isinstance(value, dict):
                pairs = [(math_segments(item)[0], ans) for item, ans in zip(_item_texts(matrix), value.values())]
            else:
                target = max((s for s in math_segments(matrix["question_text"]) if not re.fullmatch(r".+=[ab]", s)), key=len)
                pairs = [(target, value)]
            for tex, answer in pairs:
                got = numeric(tex_to_sympy(tex))
                want = numeric(_answer_expr(answer), defs)
                assert _close(got, want), (example_id, seed, tex, answer)


# ---------------------------------------------------------------- approximation families

def _log_from_givens(n: Fraction, givens: dict[str, Decimal]) -> Decimal:
    total = Decimal(0)
    for prime, exp in sp.factorint(n.numerator).items():
        total += exp * _given_prime(int(prime), givens)
    for prime, exp in sp.factorint(n.denominator).items():
        total -= exp * _given_prime(int(prime), givens)
    return total


def _given_prime(prime: int, givens: dict[str, Decimal]) -> Decimal:
    key = f"log {prime}"
    if key in givens:
        return givens[key]
    if prime == 5 and "log 2" in givens:
        return 1 - givens["log 2"]
    raise AssertionError(f"missing_given:{prime}:{sorted(givens)}")


def test_digit_count_is_exact_and_consistent_with_givens():
    for example_id in _ids_by_op()["log_power_digit_count"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            base, n = int(matrix["params"]["base"]), int(matrix["params"]["n"])
            exact = len(str(base**n))
            approx = math.floor(n * _log_from_givens(Fraction(base), _givens(matrix))) + 1
            assert int(matrix["answer"]["value"]) == exact == approx


def test_first_nonzero_position_is_exact_and_consistent_with_givens():
    for example_id in _ids_by_op()["log_power_first_nonzero"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            p, q, n = (int(matrix["params"][key]) for key in ("p", "q", "n"))
            k = 1
            while 10**k * p**n < q**n:
                k += 1
            log_value = n * _log_from_givens(Fraction(p, q), _givens(matrix))
            assert int(matrix["answer"]["value"]) == k == -math.floor(log_value)


def test_growth_years_are_exact():
    for example_id in _ids_by_op()["log_growth_years"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            params = matrix["params"]
            rate, start, target = int(params["rate"]), Fraction(params["start"]), Fraction(params["target"])
            stem = matrix["question_text"]
            answer = int(matrix["answer"]["value"])
            if "折舊" in stem:
                factor = Fraction(100 - rate, 100)
                assert start * factor**answer < target <= start * factor ** (answer - 1)
            elif "最接近" in stem:
                factor = Fraction(100 + rate, 100)
                options = [int(c["value"]) for c in matrix.get("choices") or []] or list(range(1, 200))
                best = min(options, key=lambda n: abs(start * factor**n - target))
                assert answer == best
            else:
                factor = Fraction(100 + rate, 100)
                assert start * factor**answer > target >= start * factor ** (answer - 1)


def test_characteristic_and_mantissa_follow_shown_log():
    for example_id in _ids_by_op()["log_characteristic_mantissa"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            shown = Decimal(str(matrix["params"]["shown"]))
            char = math.floor(shown)
            value = matrix["answer"]["value"]
            rows = value.items() if isinstance(value, dict) else [("首數", value)]
            for key, answer in rows:
                if "首數" in key:
                    assert int(answer) == char
                elif "尾數" in key:
                    assert Decimal(answer) == shown - char
                elif "位數" in key:
                    assert char >= 0 and int(answer) == char + 1
                elif "第幾位" in key:
                    assert char < 0 and int(answer) == -char
                else:
                    raise AssertionError(key)


def test_given_approximation_eval_uses_givens():
    for example_id in _ids_by_op()["common_log_given_approx_eval"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            n = Fraction(str(matrix["params"]["n"]))
            answer = Decimal(str(matrix["answer"]["value"]))
            assert answer == _log_from_givens(n, _givens(matrix))
            assert abs(float(answer) - math.log10(n)) < 0.002


def test_decibel_answers_follow_formula():
    for example_id in _ids_by_op()["log_decibel_application"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            k1 = matrix["params"].get("k1")
            k2 = matrix["params"].get("k2")
            value = matrix["answer"]["value"]
            answers = list(value.values()) if isinstance(value, dict) else [value]
            if k1 is not None:
                assert str(10 * (12 - int(k1))) in answers
                assert m_contains(matrix["question_text"], f"10^{{-{int(k1)}}}")
            if k2 is not None:
                assert f"10^(-{int(k2)})" in answers
                assert f"{10 * (12 - int(k2))} 分貝" in matrix["question_text"]


def m_contains(text: str, fragment: str) -> bool:
    return any(fragment in seg for seg in math_segments(text))


def test_threshold_choice_is_smallest_crossing():
    for example_id in _ids_by_op()["log_threshold_application_choice"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            p = matrix["params"]
            crossing = [x for x in p["choices"] if p["c"] * math.log10(x) + p["d"] >= p["threshold"]]
            assert int(matrix["answer"]["value"]) == min(crossing)
            for x in p["choices"]:
                approx = p["c"] * float(_log_from_givens(Fraction(x), _givens(matrix))) + p["d"]
                assert (approx >= p["threshold"]) == (x in crossing)


def test_table_lookup_answers_come_from_the_printed_table():
    for example_id in _ids_by_op()["common_log_table_lookup"]:
        for seed in range(30):
            matrix = _matrix(example_id, seed)
            table = " ".join(math_segments(matrix["question_text"]))
            main_table = table.split(r"\end{array} \end{array}")[0]
            cells = re.findall(r"&\s*(\d+)", main_table)
            header_free = [cell for cell in cells if len(cell) > 1]
            assert header_free and all(len(cell) == 4 for cell in header_free), main_table[:200]
            entries = {int(d) for d in header_free}
            value = matrix["answer"]["value"]
            for item, answer in zip(_item_texts(matrix), value.values()):
                assert re.fullmatch(r"\d\.\d{4}", answer), answer
                true_log = float(sp.N(tex_to_sympy(math_segments(item)[0]), 30))
                assert abs(float(answer) - true_log) <= 0.00015, (item, answer, true_log)
                mantissa = int(round((Decimal(answer) - math.floor(Decimal(answer))) * 10000))
                assert any(0 <= mantissa - entry <= 45 for entry in entries), (item, answer)


def test_every_given_approximation_is_printed_in_the_stem():
    for example_id, spec in SOURCE_SPECS.items():
        matrix = _matrix(example_id, 3)
        for key, value in _givens(matrix).items():
            if key.startswith("log "):
                assert format(value, "f") in matrix["question_text"], (example_id, key)


# ---------------------------------------------------------------- checker contracts

def test_checker_accepts_equivalent_fraction_and_rejects_wrong():
    for seed in range(40):
        matrix = _matrix(12144, seed)
        answer = str(matrix["answer"]["value"])
        if "/" in answer:
            break
    payload = _payload(12144, matrix)
    num, den = answer.split("/")
    assert check_answer(f"{int(num) * 3}/{int(den) * 3}", payload.get("correct_answer"), payload=payload)
    assert not check_answer(f"{int(num) + 1}/{den}", payload.get("correct_answer"), payload=payload)


@pytest.mark.parametrize("example_id", [12135, 12162, 12269])
def test_mixed_text_choices_keep_separate_math_spans(example_id):
    for seed in range(12):
        payload = _payload(example_id, _matrix(example_id, seed))
        for row in payload["choices"]:
            for text in (row["text"], row["display"]):
                assert _delimiters_wellformed(text), text
                assert not (text.startswith("$") and r"\)" in text), text


def test_ordered_comparison_parts_reject_permutations():
    matrix = _matrix(12150, 5)
    payload = _payload(12150, matrix)
    answer = _student_answer(payload)
    assert check_answer(answer, payload.get("correct_answer"), payload=payload)
    key = next(iter(answer))
    names = answer[key].split("<")
    wrong = dict(answer)
    wrong[key] = "<".join(reversed(names))
    assert not check_answer(wrong, payload.get("correct_answer"), payload=payload)


def test_domain_validity_text_parts_are_exact():
    matrix = _matrix(12188, 5)
    payload = _payload(12188, matrix)
    answer = _student_answer(payload)
    assert check_answer(answer, payload.get("correct_answer"), payload=payload)
    key = next(iter(answer))
    wrong = dict(answer)
    wrong[key] = "有意義" if answer[key] == "無意義" else "無意義"
    assert not check_answer(wrong, payload.get("correct_answer"), payload=payload)


def test_table_answer_accepts_trailing_zero_variants():
    for seed in range(60):
        matrix = _matrix(12221, seed)
        answers = matrix["answer"]["value"]
        if any(a.endswith("0") for a in answers.values()):
            break
    payload = _payload(12221, matrix)
    trimmed = {k: (v.rstrip("0").rstrip(".") or "0") for k, v in answers.items()}
    assert check_answer(trimmed, payload.get("correct_answer"), payload=payload)


def test_multipart_characteristic_keys_are_labelled():
    matrix = _matrix(12225, 5)
    payload = _payload(12225, matrix)
    keys = [row["key"] for row in payload["answer_contract"]["parts"]]
    assert keys == list(matrix["answer"]["value"])
    assert any("首數" in key for key in keys) and any("尾數" in key for key in keys)


# ---------------------------------------------------------------- visuals

def _visual_samples():
    for op, example_ids in _ids_by_op().items():
        for example_id in example_ids:
            for seed in range(8):
                matrix = _matrix(example_id, seed)
                visual = matrix.get("visual_spec") or {}
                if visual and visual.get("kind") not in {"none", "no_visual"}:
                    yield op, example_id, seed, matrix


def test_visual_specs_match_function_semantics():
    seen_ops = set()
    for op, example_id, seed, matrix in _visual_samples():
        seen_ops.add(op)
        visual = matrix["visual_spec"]
        assert visual["kind"] == "coordinate_plane_spec"
        x0, x1 = visual["x_range"]
        y0, y1 = visual["y_range"]
        for point in visual.get("points") or []:
            assert x0 <= point["x"] <= x1 and y0 <= point["y"] <= y1
        for curve in visual.get("curves") or []:
            pts = curve["points"]
            assert len(pts) >= 10
            assert all(x0 - 1e-6 <= x <= x1 + 1e-6 and y0 - 0.1 <= y <= y1 + 0.1 for x, y in pts)
            fn = curve.get("function") or visual.get("function")
            if fn and fn.get("type") == "exp":
                base = float(fn.get("base_value") or _num(fn.get("base")))
                coef = _num(fn.get("coef", 1)) * float(fn.get("sign", 1))
                for x, y in pts:
                    assert abs(coef * base**x - y) < 1e-3, (op, example_id, x, y)
                ys = [y for _, y in pts]
                increasing = (base > 1) == (coef > 0)
                assert all((b > a) == increasing for a, b in zip(ys, ys[1:]))
        if op == "exp_model_from_graph":
            fn = visual["function"]
            coef, base = Fraction(fn["coef"]), Fraction(fn["base"])
            for point in visual["points"]:
                assert abs(float(coef) * float(base) ** point["x"] - point["y"]) < 1e-9
            assert matrix["answer"]["value"]["(1)"].replace(" ", "") in {
                f"{fn['base']}^x" if coef == 1 else f"{fn['coef']}*{fn['base']}^x",
                f"{fn['coef']}*({fn['base']})^x", f"({fn['base']})^x",
            }
        if op == "exp_graph_identify_choice":
            target = matrix["answer"]["value"]
            curve = next(c for c in visual["curves"] if c["label"] == target)
            assert curve["function"]["sign"] == 1
            assert abs(curve["function"]["base_value"] - _num(matrix["params"]["base"])) < 1e-6
    assert {"exp_model_from_graph", "exp_graph_identify_choice", "graph_property_choice"} <= seen_ops


def _node() -> str:
    node = shutil.which("node")
    if not node:
        candidates = sorted((Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe"))
        node = str(candidates[0]) if candidates else None
    assert node, "Node.js runtime is required for frontend visual-spec tests"
    return node


def test_curve_visual_renders_polylines_and_labels():
    matrix = _matrix(12160, 3)
    script = (
        "const runtime=require(process.argv[1]);"
        "const spec=JSON.parse(process.argv[2]);"
        "let lines=0,moves=0;const texts=[];"
        "const ctx={fillRect(){},clearRect(){},setTransform(){},beginPath(){},"
        "moveTo(){moves++},lineTo(){lines++},stroke(){},arc(){},fill(){},save(){},restore(){},rect(){},clip(){},"
        "setLineDash(){},measureText(t){return {width:String(t).length*7}},fillText(t){texts.push(String(t))},"
        "canvas:{width:390,height:300}};"
        "const ok=runtime.renderToContext(ctx,spec,390,300,{padding:16,visualOpacity:1,backgroundFill:'#ffffff'});"
        "process.stdout.write(JSON.stringify({ok,lines,moves,texts}));"
    )
    completed = subprocess.run(
        [_node(), "-e", script, str(ROOT / "static" / "js" / "visual_spec.js"), json.dumps(matrix["visual_spec"])],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["lines"] >= 4 * 40
    for mark in ("①", "②", "③", "④"):
        assert mark in result["texts"]


def test_template_loads_curve_capable_visual_runtime():
    text = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "visual_spec.js') }}?v=exp-log-curves-1" in text
    js = (ROOT / "static" / "js" / "visual_spec.js").read_text(encoding="utf-8")
    assert "visualSpec.curves" in js and "label_at" in js


# ------------------------------- CH4_MULTIPART_PRESENTATION_NO_DUPLICATE_STEM

# The checker takes only the right-hand side, so "(1) f(x)=" is an input cue.
SEMANTIC_PREFIX_OPS = {"exp_model_from_graph"}
MULTIPART_DOM_CASES = {
    "exp_integer_power_eval": ("vh_數學B3_SubSection_4_1_1", 3),
    "exp_fill_integer_exponent": ("vh_數學B3_SubSection_4_1_2", 4),
    "exp_rational_power_eval": ("vh_數學B3_SubSection_4_1_3", 3),
    "graph_sketch_table": ("vh_數學B3_SubSection_4_2_1", 4),
    "log_basic_property_eval": (None, 4),
    "common_log_table_lookup": (None, 2),
    "log_characteristic_mantissa": (None, None),
}


def _visible_label(part: dict) -> str:
    return str(part.get("display_label") or part.get("label") or part.get("prompt") or part.get("key") or "")


def _multipart_label_violations(payload: dict) -> list[str]:
    items = [str(i.get("text") or "").strip() for i in (payload.get("stem_structure") or {}).get("items") or []]
    errors = []
    for part in (payload.get("answer_contract") or {}).get("parts") or []:
        label = _visible_label(part).strip()
        if "□" in label or r"\square" in label:
            errors.append(f"box_in_label:{label}")
        if r"\(" in label or "$" in label:
            errors.append(f"math_in_label:{label}")
        if len(label) > 10:
            errors.append(f"long_label:{label}")
        if any(label == item or (len(label) > 4 and label in item) for item in items):
            errors.append(f"stem_repeated:{label}")
    return errors


def test_multipart_labels_do_not_repeat_stem():
    """CH4_MULTIPART_PRESENTATION_NO_DUPLICATE_STEM over every multipart source."""
    failures = []
    multipart_ops = set()
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        for seed in range(6):
            matrix = _matrix(example_id, seed)
            if matrix["answer_type"] != "multi_part":
                continue
            multipart_ops.add(spec["op"])
            payload = _payload(example_id, matrix)
            parts = payload["answer_contract"]["parts"]
            for err in _multipart_label_violations(payload):
                failures.append((example_id, seed, err))
            keys = [str(part["key"]) for part in parts]
            if keys != list(matrix["answer"]["value"]) or keys != list(payload["correct_answer"]):
                failures.append((example_id, seed, "answer_order_changed", keys))
            if len(parts) != matrix["validation_facts"]["multipart_count"]:
                failures.append((example_id, seed, "arity"))
            if spec["op"] in SEMANTIC_PREFIX_OPS:
                continue
            by_group: dict[str, set[int]] = defaultdict(set)
            for part in parts:
                by_group[str(part.get("group_label") or "")].add(len(_visible_label(part)))
            if any(len(lengths) > 1 for lengths in by_group.values()):
                failures.append((example_id, seed, "uneven_label_width", [_visible_label(p) for p in parts]))
    assert len(multipart_ops) == 26
    assert failures == [], failures[:10]


_DOM_SHIM = r"""
function El(tag){this.tagName=tag.toUpperCase();this.children=[];this.dataset={};this.attrs={};
  this.textContent='';const self=this;this.classList={add(c){self.className=((self.className||'')+' '+c).trim();},
  remove(c){self.className=(self.className||'').split(' ').filter(x=>x!==c).join(' ');}};}
El.prototype.appendChild=function(c){this.children.push(c);return c;};
El.prototype.setAttribute=function(k,v){this.attrs[k]=String(v);};
El.prototype.getAttribute=function(k){return k==='type'?(this.type||null):(this.attrs[k]??null);};
Object.defineProperty(El.prototype,'innerHTML',{set(){this.children=[];},get(){return '';}});
global.document={createElement:(t)=>new El(t)};
const R=require(process.argv[1]);
const out=[];
for(const payload of JSON.parse(process.argv[2])){
  const root=new El('div');R.render(root,payload);
  const rows=[];const walk=(n,group)=>{for(const c of n.children){
    if(c.className==='multi-part-group-label'){group=c.textContent;}
    if(c.className==='multi-part-row'){const label=c.children.find(x=>x.tagName==='LABEL');
      const ctl=c.children.find(x=>x.tagName==='INPUT'||x.tagName==='SELECT');
      rows.push({group,label:label?label.textContent:'',tag:ctl?ctl.tagName:'',key:ctl?ctl.dataset.fieldKey:''});}
    walk(c,group);}};
  walk(root,'');out.push(rows);}
process.stdout.write(JSON.stringify(out));
"""


def test_multipart_dom_controls_match_arity_and_labels():
    grouped = _ids_by_op()
    payloads, expectations = [], []
    for op, (skill, arity) in MULTIPART_DOM_CASES.items():
        for example_id in grouped[op][:2]:
            if skill:
                assert SOURCE_SPECS[example_id]["skill_id"] == skill
            payload = _payload(example_id, _matrix(example_id, 17))
            keys = list(payload["correct_answer"])
            if arity:
                assert len(keys) == arity, (example_id, keys)
            payloads.append({k: payload[k] for k in ("answer_contract", "stem_structure", "ui_contract") if k in payload})
            expectations.append((example_id, payload, keys))
    completed = subprocess.run(
        [_node(), "-e", _DOM_SHIM, str(ROOT / "static" / "js" / "multipart_field_renderer.js"), json.dumps(payloads)],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    rendered = json.loads(completed.stdout)
    for (example_id, payload, keys), rows in zip(expectations, rendered):
        items = [str(i["text"]) for i in payload["stem_structure"]["items"]]
        assert [row["key"] for row in rows] == keys, example_id
        assert all(row["tag"] == "INPUT" for row in rows), example_id
        for row in rows:
            assert "□" not in row["label"] and r"\square" not in row["label"], (example_id, row)
            assert r"\(" not in row["label"], (example_id, row)
            assert not any(row["label"] and row["label"] in item and len(row["label"]) > 4 for item in items), (example_id, row)
        assert len({len(row["label"]) for row in rows if not row["group"]}) <= 1, (example_id, rows)
        answer = {row["key"]: part["expected_answer"] for row, part in zip(rows, payload["answer_contract"]["parts"])}
        assert check_answer(answer, payload["correct_answer"], payload=payload), example_id


# ---------------------------------------------------------------- production corpus (read-only)

def _prod_conn():
    db_path = ROOT / "instance" / "kumon_math.db"
    if not db_path.exists():
        pytest.skip("production db absent")
    uri = "file:" + str(db_path.resolve()).replace("\\", "/") + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def test_production_corpus_matches_source_specs_readonly():
    conn = _prod_conn()
    try:
        rows = conn.execute(
            "SELECT id, skill_id FROM textbook_examples WHERE id BETWEEN 12127 AND 12272"
        ).fetchall()
        active = dict(conn.execute(
            "SELECT skill_id, is_active FROM skills_info WHERE skill_id LIKE 'vh_數學B3_SubSection_4_%'"
        ).fetchall())
    except sqlite3.OperationalError:
        pytest.skip("textbook tables unavailable")
    finally:
        conn.close()
    assert len(rows) == 146
    assert {eid: skill for eid, skill in rows} == {eid: spec["skill_id"] for eid, spec in SOURCE_SPECS.items()}
    assert all(active.get(skill) for skill in SKILLS)
    assert not active.get(ZERO_SOURCE_SKILL)


def test_12231_source_is_clean_readonly():
    conn = _prod_conn()
    try:
        row = conn.execute("SELECT skill_id, problem_text FROM textbook_examples WHERE id = 12231").fetchone()
    except sqlite3.OperationalError:
        pytest.skip("textbook tables unavailable")
    finally:
        conn.close()
    assert row is not None
    skill_id, stem = row
    assert skill_id == SOURCE_SPECS[12231]["skill_id"]
    assert not SOURCE_LABEL_RE.search(stem)
    assert not SOLUTION_MARKER_RE.search(stem)
    assert "位數" in stem


# ---------------------------------------------------------------- publication

def test_runtime_publication_selects_every_source():
    from core.gencode.services.gencode_status_query_service import inspect_skill_runtime_publication

    for skill in SKILLS:
        publication = inspect_skill_runtime_publication(skill_id=skill, project_root=ROOT)
        expected = {eid for eid, spec in SOURCE_SPECS.items() if spec["skill_id"] == skill}
        assert publication["runtime_ready"] is True, skill
        assert set(publication["selectable_components"]) == expected


def test_teacher_status_is_published_from_production_evidence_readonly():
    from core.gencode.services.gencode_status_query_service import build_admin_skills_gencode_status_map

    conn = _prod_conn()
    conn.row_factory = sqlite3.Row
    try:
        status = build_admin_skills_gencode_status_map(conn, SKILLS, project_root=ROOT)
    except sqlite3.OperationalError:
        pytest.skip("status tables unavailable")
    finally:
        conn.close()
    for skill in SKILLS:
        teacher = status[skill]["teacher_status"]
        assert teacher["status_key"] == "published", (skill, teacher)
        assert teacher["label"] == "已上線"


# ---------------------------------------------------------------- mock exam

def test_mock_exam_unit_ten_scope():
    from core.vocational_mock_exam_scope import MOCK_EXAM_SCOPE, official_unit_for_chapter

    assert official_unit_for_chapter("第4章 指數與對數") == 10
    assert 10 in MOCK_EXAM_SCOPE["exam_5"]["units"]
    assert 10 not in MOCK_EXAM_SCOPE["exam_1"]["units"]
    assert 10 not in MOCK_EXAM_SCOPE["exam_2"]["units"]


def test_production_curriculum_chapter_maps_to_unit_ten_readonly():
    from core.vocational_mock_exam_scope import official_unit_for_chapter

    conn = _prod_conn()
    try:
        rows = conn.execute(
            "SELECT skill_id, chapter FROM skill_curriculum WHERE curriculum = 'vocational' "
            "AND volume = '數學B3' AND skill_id LIKE 'vh_數學B3_SubSection_4_%'"
        ).fetchall()
    except sqlite3.OperationalError:
        pytest.skip("curriculum table unavailable")
    finally:
        conn.close()
    assert {skill for skill, _ in rows} >= set(SKILLS)
    assert all(official_unit_for_chapter(chapter) == 10 for _, chapter in rows)


# ---------------------------------------------------------------- practice page contracts

def test_deeplink_is_consumed_once_in_template():
    """PRACTICE_TEXTBOOK_EXAMPLE_DEEPLINK_GATE"""
    text = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert "__textbookExampleIdConsumed" in text
    assert "/get_next_question" in text


# ---------------------------------------------------------------- real runtime

@pytest.fixture(scope="module")
def auth_client(tmp_path_factory):
    import config
    from werkzeug.security import generate_password_hash

    db_path = tmp_path_factory.mktemp("b3ch4") / "gate.db"
    db_uri = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    patch = pytest.MonkeyPatch()
    patch.setattr(config.Config, "SQLALCHEMY_DATABASE_URI", db_uri)
    from app import create_app
    from models import SkillCurriculum, SkillInfo, TextbookExample, User, db

    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.session.add(User(username="b3_ch4_gate", password_hash=generate_password_hash("pass1234"), role="student"))
        for order, skill in enumerate(SKILLS, start=1):
            db.session.add(SkillInfo(
                skill_id=skill, skill_en_name=skill, skill_ch_name=skill, description="ch4",
                gemini_prompt="", is_active=True,
            ))
            db.session.add(SkillCurriculum(
                skill_id=skill, curriculum="vocational", grade=11, volume="數學B3",
                chapter="第4章 指數與對數", section=f"4-{skill[-3]}", display_order=order,
            ))
        db.session.add(TextbookExample(
            id=12231, skill_id=SOURCE_SPECS[12231]["skill_id"], source_curriculum="vocational",
            source_volume="數學B3", source_chapter="第4章 指數與對數", source_section="4-5",
            source_description="deeplink", problem_text="已知 \\(\\log 2\\approx 0.3010\\)，則 \\(2^{100}\\) 為幾位數？",
            correct_answer="31",
        ))
        db.session.commit()
    client = app.test_client()
    login = client.post("/login", data={"username": "b3_ch4_gate", "password": "pass1234"})
    assert login.status_code in {302, 303}
    try:
        yield client, app
    finally:
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        patch.undo()


def _runtime_cases():
    picked = {}
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        picked.setdefault(spec["skill_id"], example_id)
    for example_id in (12135, 12160, 12162, 12188, 12219, 12225, 12231, 12241, 12249, 12261, 12266, 12269, 12272):
        picked[f"extra_{example_id}"] = example_id
    return sorted(set(picked.values()))


def _post_answer(client, question, answer):
    body = {
        "skill_id": question.get("skill_id"),
        "question_uid": question.get("question_uid"),
        "problem_type_id": question.get("problem_type_id") or "",
        "answer": answer,
    }
    if isinstance(answer, dict):
        body["answers"] = answer
        body["user_answer"] = answer
    response = client.post("/check_answer", data=json.dumps(body), content_type="application/json")
    assert response.status_code == 200, response.get_data(as_text=True)[:300]
    return response.get_json(silent=True) or {}


def _get_question(client, example_id, seed):
    spec = SOURCE_SPECS[example_id]
    response = client.get(
        "/get_next_question",
        query_string={"skill": spec["skill_id"], "level": 1, "component_id": f"src_{example_id}", "gen_seed": seed},
    )
    assert response.status_code == 200, response.get_data(as_text=True)[:500]
    return response.get_json()


@pytest.mark.parametrize("example_id", _runtime_cases())
def test_runtime_get_next_and_check(auth_client, example_id):
    client, _app = auth_client
    question = _get_question(client, example_id, 4)
    assert question.get("component_id") == f"src_{example_id}"
    assert question.get("problem_type_id") == SOURCE_SPECS[example_id]["op"]
    stem = question.get("question_text") or ""
    assert _stem_violations(stem) == []
    for text in _payload_display_texts(question):
        assert _delimiters_wellformed(text), text
    assert _multipart_label_violations(question) == []
    assert not question.get("reuse_textbook_image")
    assert not question.get("image_assets")
    answer = _student_answer(question)
    assert _post_answer(client, question, answer).get("correct") is True
    question = _get_question(client, example_id, 5)
    answer = _student_answer(question)
    if isinstance(answer, dict):
        wrong = dict(answer)
        wrong[next(iter(wrong))] = "12345"
    elif question.get("presentation_mode") == "single_choice":
        wrong = next(c["label"] for c in question["choices"] if c["label"] != answer)
    else:
        wrong = "12345"
    assert _post_answer(client, question, wrong).get("correct") is not True


def test_runtime_deeplink_only_affects_first_request(auth_client):
    client, _app = auth_client
    skill = SOURCE_SPECS[12231]["skill_id"]
    first = client.get("/get_next_question", query_string={"skill": skill, "level": 1, "textbook_example_id": 12231})
    assert first.status_code == 200
    assert int(first.get_json().get("textbook_example_id")) == 12231
    second = client.get("/get_next_question", query_string={"skill": skill, "level": 1})
    assert second.status_code == 200
    body = second.get_json()
    assert str(body.get("component_id") or "").startswith("src_")
    assert body.get("problem_type_id") in OPS


def test_runtime_hint_comes_from_domain(auth_client):
    client, _app = auth_client
    from core.domain.exponential_logarithmic_domain import hint_steps

    for example_id in (12127, 12206, 12231):
        module_path = ROOT / "agent_skills_v3" / SOURCE_SPECS[example_id]["skill_id"] / "components" / f"src_{example_id}" / "get_hint.py"
        spec = importlib.util.spec_from_file_location(f"b3ch4_hint_{example_id}", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        assert module.get_hint(1) == hint_steps(SOURCE_SPECS[example_id]["op"])[0]


def test_mock_exam_scope_includes_chapter_four_only_in_exam_five(auth_client):
    _client, app = auth_client
    from core.vocational_mock_exam_scope import build_mock_exam_scope

    def skills_in(exam_id):
        with app.app_context():
            scope = build_mock_exam_scope(exam_id)
        return {
            row["skill_id"]
            for volume in scope["volumes"]
            for unit in volume["units"]
            for row in unit["skills"]
        }

    assert set(SKILLS) <= skills_in("exam_5")
    assert not (set(SKILLS) & skills_in("exam_1"))
    assert not (set(SKILLS) & skills_in("exam_2"))
