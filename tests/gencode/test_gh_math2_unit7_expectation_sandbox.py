"""Sandbox gate for 普高數學2 Unit 7 (數學期望值).

The candidate domain is registered in memory only. Textbook rows are read from a private snapshot
and compared with the formal database in read-only mode. Seed 0 of every component is checked against
the textbook values written in this file, and every seed is checked against a brute-force oracle written here.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import re
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.mathematical_expectation import build_sandbox as B
from agent_domains_candidate.mathematical_expectation.mathematical_expectation_domain import DOMAIN_KEY, WIN_SETS
from agent_domains_candidate.mathematical_expectation.mathematical_expectation_specs import (
    COMPONENTS,
    FAMILY,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
)
from agent_domains_candidate.mathematical_expectation.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.mathematical_expectation.verification import grade, verify_payload
from core.gencode.multipart_answer_arity import (
    checker_answer_count,
    expected_answer_field_count,
    rendered_answer_field_count,
)
from core.gencode.multipart_stem_contract import extract_stem_structure, stem_structure_to_question_text
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
FORMAL_DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(50)
UNIT_IDS = set(range(12891, 12912))
FIGURE_CUES = ("如圖", "右圖", "下圖", "在圖", "左圖", "上圖", "下表", "如表", "附表")
BARE_MARKER = re.compile(r"[\(（]\s*\d{1,2}\s*[\)）]")

register_candidate_in_memory()
B.build_all()


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u7_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


def _values(payload: dict) -> list:
    answer = payload["correct_answer"]
    if isinstance(answer, dict):
        return [answer[key] for key in sorted(answer, key=lambda item: int(item.split("_")[1]))]
    return [answer]


def _math_ok(text: str) -> None:
    assert "$$" not in text and text.count("$") % 2 == 0
    for index, segment in enumerate(text.split("$")):
        if index % 2 == 1:
            assert segment.count("{") == segment.count("}")
            assert "@" not in segment


def _outside_math(text: str) -> str:
    return "".join(segment for index, segment in enumerate(text.split("$")) if index % 2 == 0)


def _mean(values) -> Fraction:
    values = [Fraction(v) for v in values]
    return sum(values, Fraction(0)) / len(values)


def _label(choices: list[dict], value: str) -> str:
    return next(c["label"] for c in choices if c["value"] == value)


# --- brute-force oracle written independently of the domain ----------------------------------------------------------------------


def _oracle(op: str, g: dict, payload: dict) -> list:
    if op == "die_payout_expectation":
        return [str(_mean(g["payouts"]))]
    if op == "coin_payout_expectation":
        return [str(_mean(row[sum(t)] for t in itertools.product((0, 1), repeat=g["n"]))) for row in g["scenarios"]]
    if op == "urn_draw_expectation":
        bag = [(i, grp.get("value")) for i, grp in enumerate(g["groups"]) for _ in range(grp["count"])]
        var = g["variable"]
        outcomes = []
        for hand in itertools.combinations(bag, g["draw"]):
            if var["kind"] == "sum_of_values":
                outcomes.append(sum(v for _i, v in hand))
            else:
                hits = sum(1 for i, _v in hand if i == var["index"])
                if var["kind"] == "count":
                    outcomes.append(hits)
                else:
                    outcomes.append(dict(map(tuple, var["payouts"])).get(hits, var["default"]))
        return [str(_mean(outcomes))]
    if op == "two_dice_match_game":
        m, a = g["multiplier"], g["amount"]
        gains = [m * x if x == y else -a for x in range(1, 7) for y in range(1, 7)]
        e = _mean(gains)
        who = "乙" if e > 0 else ("甲" if e < 0 else "雙方公平")
        fair = Fraction(sum(m * x for x in range(1, 7)), 30)
        assert _mean([m * x if x == y else -fair for x in range(1, 7) for y in range(1, 7)]) == 0
        return [str(e), _label(payload["answer_contract"]["parts"][1]["choices"], who), str(fair)]
    if op == "single_die_game":
        wins = WIN_SETS[g["win_set"]]
        e = _mean(g["multiplier"] * x if x in wins else -x for x in range(1, 7))
        verdict = "公平" if e - g["fee"] == 0 else "不公平"
        return [str(e), _label(payload["answer_contract"]["parts"][1]["choices"], verdict)]
    if op == "insurance_expectation":
        stated = Fraction(g["stated_prob"])
        p = stated if g["prob_kind"] == "event" else 1 - stated
        if g["ask"] == "profit":
            return [str(g["premium"] * (1 - p) + (g["premium"] - g["payout"]) * p)]
        return [str(g["profit"] + g["payout"] * p)]
    if op == "decision_by_expectation":
        means = [sum(Fraction(p) * v for p, v in zip(g["probs"], row)) for row in g["profits"]]
        assert means[0] != means[1]
        return [_label(payload["choices"], "甲地" if means[0] > means[1] else "乙地")]
    if op == "expectation_claim":
        faces = (0, 1) if g["model"] == "coin" else range(1, 7)
        true = _mean(sum(t) for t in itertools.product(faces, repeat=g["n"]))
        return [_label(payload["choices"], "○" if Fraction(g["stated"]) == true else "×")]
    if op == "multiple_choice_guess_expectation":
        r = g["options"] - g["known"]
        table = list(g["scores"]) + [0] * 10
        return [str(_mean(table[sum(1 for ok in t if not ok)] for t in itertools.product((True, False), repeat=r)))]
    if op == "lottery_expectation":
        return [str(Fraction(sum(a * c for a, c in g["prizes"]), g["total"]))]
    if op == "prize_ball_expectation":
        single = _mean(g["values"])
        balls = [v for v in g["values"] for _ in range(2)]
        double = _mean(max(x, y) for x, y in itertools.combinations(balls, 2))
        first = payload["answer_contract"]["parts"][0]["choices"]
        yes_no = payload["answer_contract"]["parts"][1]["choices"]
        return [_label(first, f"{single}元"), _label(yes_no, "是" if double > single else "否"), str(double - single)]
    raise AssertionError(op)


EXPECTED = {
    12891: ["20"],
    12892: ["320"],
    12893: ["3/5"],
    12894: ["-5", "0"],
    12895: ["2000"],
    12896: ["15"],
    12897: ["160"],
    12898: ["9/7"],
    12899: ["-115/6", "A", "7"],
    12900: ["B"],
    12901: ["A"],
    12902: ["B"],
    12903: ["35"],
    12904: ["60"],
    12905: ["22800"],
    12906: ["12/5"],
    12907: ["19/6", "B"],
    12908: ["2000"],
    12909: ["17/8"],
    12910: ["29"],
    12911: ["C", "A", "1400"],
}


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_component_samples_grade_and_vary(cid):
    skill_id = _skill_of(cid)
    operation = OP[COMPONENTS[cid][1]]
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {path.name for path in directory.iterdir() if path.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator, metadata = _load(cid, "generate.py"), _load(cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation
    surfaces = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)
        assert payload["domain_operation"] == operation and payload["fixed_domain_key"] == DOMAIN_KEY
        text = payload["question_text"]
        _math_ok(text)
        assert "承例題" not in text and "MATH_PARSE_FAILED" not in text
        assert not any(cue in text for cue in FIGURE_CUES)
        assert not payload.get("visual_spec") and not payload.get("reuse_textbook_image")
        assert not payload["answer_contract"].get("answer_format_example")
        problems = verify_payload(payload, skill_id, f"src_{cid}")
        assert problems == [], (seed, problems)
        assert _values(payload) == _oracle(operation, payload["math_core"]["givens"], payload), (seed, payload["math_core"]["givens"])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= 20


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_answer_fields_match_stem_items(cid):
    skill = _skill_of(cid)
    for seed in range(10):
        payload = _gen(cid, seed)
        contract = payload["answer_contract"]
        n = expected_answer_field_count(payload)
        assert n == rendered_answer_field_count(payload) == checker_answer_count(payload), (cid, seed)
        if contract["answer_type"] != "multi_part":
            assert n == 1 and "stem_structure" not in payload, (cid, seed)
            assert not BARE_MARKER.search(_outside_math(payload["question_text"])), (cid, seed)
            continue
        stem = extract_stem_structure(payload)
        labels = [f"({i})" for i in range(1, n + 1)]
        assert stem is not None and [item["group_label"] for item in stem["items"]] == labels, (cid, seed)
        assert [p["group_label"] for p in contract["parts"]] == labels, (cid, seed)
        assert payload["question_text"] == stem_structure_to_question_text(stem), (cid, seed)
        assert not BARE_MARKER.search(_outside_math(stem["prompt"])), (cid, seed)
        for item in stem["items"]:
            assert not BARE_MARKER.search(_outside_math(item["text"])), (cid, seed)
        for index, part in enumerate(contract["parts"]):
            if part["answer_type"] == "single_choice":
                assert [c["label"] for c in part["choices"]] == sorted(c["label"] for c in part["choices"]), (cid, seed)
            only_this_wrong = dict(payload["correct_answer"])
            only_this_wrong[part["key"]] = "999999" if part["checker"] == "rational_checker" else next(
                c["label"] for c in part["choices"] if c["label"] != part["expected_answer"])
            assert not grade(payload, only_this_wrong, skill), (cid, seed, index)


def test_seed_zero_matches_textbook_values():
    assert set(EXPECTED) == UNIT_IDS
    for cid, expected in EXPECTED.items():
        assert _values(_gen(cid, 0)) == expected, cid


def test_guess_stem_keeps_textbook_wording():
    text = _gen(12909, 0)["question_text"]
    flat = re.sub(r"\s+", "", text.replace("$", "").replace("\\left(", "(").replace("\\right)", ")"))
    textbook = (
        "學科能力測驗中，多重選擇題每題有5個選項，其中至少有一個選項是正確的。其計分方式為：「所有選項均答對者，得5分；"
        "答錯1個選項者，得3分；答錯2個選項者，得1分；答錯多於2個選項或所有選項均未做答者，該題以零分計算。」"
        "今有一題某考生已經確定選項(1)與(2)是正確的，其餘3個選項則隨意猜測，求此考生在該題得分的期望值。"
    )
    assert flat == textbook
    for added in ("機會均等", "猜對與猜錯", "機率"):
        assert added not in text
    assert not BARE_MARKER.search(_outside_math(text))
    for seed in SEEDS:
        assert "機會均等" not in _gen(12909, seed)["question_text"]


def test_guess_answer_is_the_same_for_every_hidden_answer_key():
    """Uniform marking of the guessed options (the modelling reading of 隨意猜測) gives one value whatever the key is."""
    scores = {0: 5, 1: 3, 2: 1}
    for key in itertools.product((True, False), repeat=3):
        marks = list(itertools.product((True, False), repeat=3))
        total = sum(scores.get(sum(1 for k, m in zip(key, mark) if k != m), 0) for mark in marks)
        assert Fraction(total, len(marks)) == Fraction(17, 8), key
    assert _values(_gen(12909, 0)) == ["17/8"]


def test_decision_table_is_a_renderable_array():
    text = _gen(12900, 0)["question_text"]
    assert "\\begin{array}{|c|c|c|c|}" in text and "\\end{array}" in text
    for word in ("經濟狀況", "機率", "甲地利潤", "乙地利潤"):
        assert f"\\text{{{word}}}" in text
    assert "|" not in _outside_math(text)


def test_coverage_binds_the_formal_skill():
    assert set(COMPONENTS) == UNIT_IDS and not FIXED_ROWS
    assert set(FAMILY) == UNIT_IDS
    con = sqlite3.connect(f"file:{FORMAL_DB.as_posix()}?mode=ro", uri=True)
    snap = sqlite3.connect(f"file:{B.isolated_db().as_posix()}?mode=ro", uri=True)
    try:
        query = (
            "select id, skill_id, ifnull(correct_answer, ''), problem_text, source_chapter "
            "from textbook_examples where id between 12891 and 12911"
        )
        formal = {row[0]: row[1:] for row in con.execute(query)}
        frozen = {row[0]: row[1:] for row in snap.execute(query)}
    finally:
        con.close()
        snap.close()
    assert formal == frozen
    assert len(formal) == 21
    assert {row[3] for row in formal.values()} == {"單元7 數學期望值"}
    assert all(row[0] == "gh_MathematicalExpectation" for row in formal.values())
    assert all(row[1] == "" for row in formal.values())
    assert "\\begin{array}" in formal[12900][2]
    assert "隨意猜測" in formal[12909][2]
    for key, ops in SKILL_OPERATIONS.items():
        used = {spec[1] for spec in COMPONENTS.values() if spec[0] == key}
        assert used == set(ops)
