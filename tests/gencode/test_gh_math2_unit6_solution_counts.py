"""Solution text must state unreduced favorable counts.

Loads the existing staging generators. Does not rebuild them and does not write the formal database.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import re
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.classical_probability.classical_probability_specs import COMPONENTS, FAMILY, OP, SKILLS
from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.classical_probability.verification import grade, verify_payload, wrong_value, parts_of

ROOT = Path(__file__).resolve().parents[2]
DRYRUN = ROOT / "tmp" / "gh_math2_unit6_sandbox_dryrun"
FORMAL = ROOT / "instance" / "kumon_math.db"
SNAPSHOT = ROOT / "tmp" / "gh_math2_unit6_isolated" / "unit6_snapshot.db"
BUNDLE = ROOT / "reports/domain_operation_workspaces/capability_discrete_classical_probability_f8c6199f/revision_0001"
SEEDS = range(20)
BAD_FAVORABLE = re.compile(r"有利 \d+/\d+")
COUNT_LINE = re.compile(r"(\d+) 個，有利 (\d+) 個，機率 (?:(\d+)/(\d+) = )?([0-9]+(?:/[0-9]+)?)")
ENGLISH_MODES = ("ordered_no_replace", "ordered_replace", "unordered")

register_candidate_in_memory()
_MODULES: dict[int, object] = {}


def _skill(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _module(cid: int):
    if cid not in _MODULES:
        path = DRYRUN / _skill(cid) / "components" / f"src_{cid}" / "generate.py"
        spec = importlib.util.spec_from_file_location(f"u6sol_{cid}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[cid] = module
    return _MODULES[cid]


def _payload(cid: int, seed: int) -> dict:
    return _module(cid).generate(seed=seed)


def _item_lines(payload: dict) -> list[str]:
    stem = payload.get("stem_structure")
    if stem:
        return [item["text"] for item in stem["items"]]
    return payload["question_text"].splitlines()[-1:]


def _answers(payload: dict) -> list:
    answer = payload["correct_answer"]
    if isinstance(answer, dict):
        return [answer[key] for key in sorted(answer, key=lambda item: int(item.split("_")[1]))]
    return [answer]


def _show(value) -> str:
    if isinstance(value, dict):
        return "；".join(f"{key}={_show(value[key])}" for key in sorted(value, key=lambda item: int(item.split("_")[1])))
    if isinstance(value, list):
        return "{" + ", ".join(str(item) for item in value) + "}"
    return str(value)


def _dice_hit(outcome: tuple[int, ...], line: str) -> bool:
    if "恰有兩粒點數相同" in line:
        return len(outcome) == 3 and len(set(outcome)) == 2
    if "至少有兩粒點數相同" in line:
        return len(set(outcome)) < len(outcome)
    if "每粒點數都不同" in line:
        return len(set(outcome)) == len(outcome)
    if "每粒點數都相同" in line:
        return len(set(outcome)) == 1
    if "兩粒點數相同" in line:
        return len(outcome) == 2 and outcome[0] == outcome[1]
    if "第一粒點數大於第二粒" in line:
        return outcome[0] > outcome[1]
    matched = re.search(r"點數和等於 \$(\d+)\$", line)
    if matched:
        return sum(outcome) == int(matched.group(1))
    matched = re.search(r"兩粒點數差的絕對值等於 \$(\d+)\$", line)
    if matched:
        return abs(outcome[0] - outcome[1]) == int(matched.group(1))
    matched = re.search(r"兩粒點數都大於 \$(\d+)\$", line)
    if matched:
        return outcome[0] > int(matched.group(1)) and outcome[1] > int(matched.group(1))
    matched = re.search(r"恰有 (\d+) 粒出現 \$(\d+)\$ 點", line)
    if matched:
        return outcome.count(int(matched.group(2))) == int(matched.group(1))
    matched = re.search(r"至少有 (\d+) 粒出現 \$(\d+)\$ 點", line)
    if matched:
        return outcome.count(int(matched.group(2))) >= int(matched.group(1))
    raise AssertionError(f"unparsed dice line: {line}")


def _assert_count_line(step: str, answer: str) -> None:
    assert BAD_FAVORABLE.search(step) is None, step
    matched = COUNT_LINE.search(step)
    if matched is None:
        return
    total, favorable = int(matched.group(1)), int(matched.group(2))
    value = Fraction(favorable, total)
    assert value == Fraction(str(answer)), (step, answer)
    assert matched.group(5) == str(value)
    if matched.group(3) is not None:
        assert int(matched.group(3)) == favorable and int(matched.group(4)) == total
        assert value.denominator != total


def _grade_seed(cid: int, payload: dict) -> None:
    skill = _skill(cid)
    assert verify_payload(payload, skill, f"src_{cid}") == []
    assert grade(payload, payload["correct_answer"], skill)
    contract = payload["answer_contract"]
    parts = parts_of(payload)
    if contract["answer_type"] in {"multi_part", "table_fill"}:
        bad = dict(payload["correct_answer"])
        bad[parts[0]["key"]] = wrong_value(parts[0])
        assert not grade(payload, bad, skill)
    else:
        assert not grade(payload, wrong_value(parts[0]), skill)


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_solution_counts_match_answers_across_seeds(cid: int):
    operation = COMPONENTS[cid][1]
    stems = set()
    for seed in SEEDS:
        payload = _payload(cid, seed)
        stems.add(payload["question_text"])
        answers = _answers(payload)
        steps = payload["explanation_steps"]
        assert len(steps) == len(answers)
        text = "\n".join(steps)
        assert BAD_FAVORABLE.search(text) is None
        assert not any(mode in text for mode in ENGLISH_MODES)
        for step, answer in zip(steps, answers):
            if not isinstance(answer, list):
                _assert_count_line(step, str(answer))
                coin = re.search(
                    r"C\(\d+,\d+\) = (\d+) 種，全部 (\d+) 種，機率 (?:(\d+)/(\d+) = )?([0-9]+(?:/[0-9]+)?)",
                    step,
                )
                if coin:
                    favorable, total = int(coin.group(1)), int(coin.group(2))
                    value = Fraction(favorable, total)
                    assert value == Fraction(str(answer))
                    assert coin.group(5) == str(value)
            listed = re.search(r"共 (\d+) 個", step)
            if listed and isinstance(answer, list):
                assert int(listed.group(1)) == len(answer)
            counted = re.search(r"個數為 (\d+)，", step)
            if counted:
                assert str(answer) == counted.group(1)
            power = re.search(r"樣本點個數為 2\^(\d+) = (\d+)", step)
            if power:
                assert 2 ** int(power.group(1)) == int(power.group(2)) == int(answer)
        if operation == "dice_count_probability":
            assert "將骰子編號區別" in payload["question_text"]
            size = re.search(r"擲 (\d+) 粒各有 (\d+) 面", payload["question_text"])
            dice, faces = int(size.group(1)), int(size.group(2))
            lines = _item_lines(payload)
            assert len(lines) == len(steps)
            for line, step, answer in zip(lines, steps, answers):
                favorable = sum(
                    1 for outcome in itertools.product(range(1, faces + 1), repeat=dice) if _dice_hit(outcome, line)
                )
                total = faces**dice
                assert f"有利 {favorable} 個" in step
                assert f"{total} 個" in step
                assert Fraction(favorable, total) == Fraction(str(answer))
        if operation == "urn_draw_probability":
            lines = _item_lines(payload)
            for line, step in zip(lines, steps):
                if "依序取出、不放回" in line:
                    assert "依序取出、不放回" in step
                if "同時取出" in line:
                    assert "同時取出、不計順序" in step
        if operation == "replacement_count_probability":
            assert "放回" in text
        if operation == "draw_outcome_space":
            assert "不放回" in payload["question_text"] or "放回" in payload["question_text"] or "不計順序" in payload["question_text"]
    assert len(stems) >= 2


def test_12871_seed_zero_and_other_seeds_keep_75_over_216():
    textbook = _payload(12871, 0)
    step = textbook["explanation_steps"][0]
    assert textbook["correct_answer"] == "25/72"
    assert "已編號、等可能的樣本點 216 個，有利 75 個，機率 75/216 = 25/72。" in step
    assert "有利 25/72" not in step
    _grade_seed(12871, textbook)
    seen = {textbook["question_text"]}
    for seed in range(1, 20):
        payload = _payload(12871, seed)
        seen.add(payload["question_text"])
        line = _item_lines(payload)[0]
        size = re.search(r"各有 (\d+) 面", payload["question_text"])
        event = re.search(r"恰有 (\d+) 粒出現 \$(\d+)\$ 點", line)
        faces = int(size.group(1))
        count, face = int(event.group(1)), int(event.group(2))
        assert 1 <= face <= faces
        favorable = math.comb(3, count) * (faces - 1) ** (3 - count)
        total = faces**3
        assert f"有利 {favorable} 個" in payload["explanation_steps"][0]
        assert payload["correct_answer"] == str(Fraction(favorable, total))
        _grade_seed(12871, payload)
    assert len(seen) >= 2


def test_named_sources_keep_counts_and_answers():
    ordered = _payload(12864, 0)
    assert ordered["correct_answer"] == {"part_1": "3/10", "part_2": "3/10"}
    assert "依序取出、不放回的等可能取法 20 個，有利 6 個，機率 6/20 = 3/10。" in ordered["explanation_steps"][0]
    assert "同時取出、不計順序的等可能取法 10 個，有利 3 個，機率 3/10。" in ordered["explanation_steps"][1]
    complement = _payload(12887, 0)
    assert complement["correct_answer"] == "4/9"
    assert "216 個，有利 96 個，機率 96/216 = 4/9。" in complement["explanation_steps"][0]
    clubs = _payload(12890, 0)
    assert clubs["correct_answer"] == "13/18"
    assert "放回（或各自選擇）的樣本點有 1296 個，有利 936 個，機率 936/1296 = 13/18。" in clubs["explanation_steps"][0]
    password = _payload(12883, 0)
    assert password["correct_answer"] == {"part_1": "1/24", "part_2": "7/8"}
    assert "排列有 24 個，有利 1 個，機率 1/24。" in password["explanation_steps"][0]
    assert "等可能排列 24 個，有利 21 個，機率 21/24 = 7/8。" in password["explanation_steps"][1]


def test_seed_zero_answers_and_checker_do_not_regress():
    frozen_path = ROOT / "reports" / "gh_math2_unit6_bundle" / "acceptance_audit.json"
    frozen = {
        item["textbook_example_id"]: item["seed0_answer"]
        for item in json.loads(frozen_path.read_text(encoding="utf-8"))["checklist"]
    }
    assert set(frozen) == set(range(12849, 12891))
    for cid, expected in frozen.items():
        payload = _payload(cid, 0)
        assert _show(payload["correct_answer"]) == expected
        _grade_seed(cid, payload)


def test_package_shape_and_formal_rows_stay_put():
    assert len(COMPONENTS) == 42
    assert set(COMPONENTS) == set(range(12849, 12891))
    assert len(set(FAMILY.values())) == 14
    assert len(OP) == 14
    bundle = json.loads((BUNDLE / "promotion_bundle.json").read_text(encoding="utf-8"))
    assert bundle["review"]["status"] == "ready_for_human_review"
    assert bundle["review"]["approved_by"] == ""
    assert bundle["coverage_rows"] == 42
    source = ROOT / "agent_domains_candidate" / "classical_probability" / "classical_probability_domain.py"
    packaged = BUNDLE / "production_package" / "classical_probability_domain.py"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert hashlib.sha256(packaged.read_bytes()).hexdigest() == digest
    assert bundle["files"]["classical_probability_domain.py"] == digest
    query = (
        "select id, skill_id, ifnull(correct_answer, ''), problem_text, source_chapter "
        "from textbook_examples where id between 12849 and 12890 order by id"
    )
    formal = sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True)
    snap = sqlite3.connect(f"file:{SNAPSHOT.as_posix()}?mode=ro", uri=True)
    try:
        assert list(formal.execute(query)) == list(snap.execute(query))
    finally:
        formal.close()
        snap.close()
