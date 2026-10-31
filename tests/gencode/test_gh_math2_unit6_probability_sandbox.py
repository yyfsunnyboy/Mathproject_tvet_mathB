"""Sandbox gate for 普高數學2 Unit 6 (古典機率).

The candidate domain is registered in memory only. Textbook rows are read from a private snapshot
and compared with the formal database in read-only mode. Seed 0 of every component is checked
against an independent count written in this file.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.classical_probability import build_sandbox as B
from agent_domains_candidate.classical_probability.classical_probability_domain import DOMAIN_KEY
from agent_domains_candidate.classical_probability.classical_probability_specs import (
    COMPONENTS,
    FAMILY,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
)
from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.classical_probability.verification import verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
FORMAL_DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(50)
UNIT_IDS = set(range(12849, 12891))
PROB_OPS = {
    "uniform_draw_probability",
    "coin_count_probability",
    "dice_count_probability",
    "urn_draw_probability",
    "replacement_count_probability",
    "probability_algebra",
    "password_guess",
}
FIGURE_CUES = ("如圖", "右圖", "下圖", "在圖", "左圖", "上圖")

register_candidate_in_memory()
B.build_all()


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _load(cid: int, filename: str):
    path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"m2u6_{cid}_{path.stem}", path)
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


def _die_codes(predicate) -> list[int]:
    return sorted(10 * a + b for a in range(1, 7) for b in range(1, 7) if predicate(a, b))


def _draw_expected(labels: list[int], asks: list[tuple[str, int]]) -> list:
    out = []
    for mode, k in asks:
        if mode == "ordered_no_replace":
            seqs = itertools.permutations(labels, k)
        elif mode == "ordered_replace":
            seqs = itertools.product(labels, repeat=k)
        else:
            seqs = itertools.combinations(labels, k)
        codes = sorted(int("".join(str(digit) for digit in seq)) for seq in seqs)
        out.extend([codes, str(len(codes))])
    return out


EXPECTED = {
    12849: [list(range(4)), "4", [0, 1, 2], "3"],
    12851: [list(range(8)), "8", list(range(4)), "4"],
    12850: _draw_expected([1, 2, 3, 4], [("ordered_no_replace", 2), ("unordered", 2)]),
    12852: _draw_expected([1, 2, 3], [("ordered_no_replace", 3), ("ordered_replace", 2), ("unordered", 2)]),
    12853: [list(range(4)), [0, 1, 2], [1, 2]],
    12854: [[1, 4, 5], [0], [2, 3, 6, 7]],
    12855: [
        _die_codes(lambda a, b: a + b > 9),
        _die_codes(lambda a, b: a == b),
        _die_codes(lambda a, b: a + b > 9 and a == b),
        _die_codes(lambda a, b: a + b > 9 or a == b),
    ],
    12856: [[0, 3], "A", "A"],
    12857: [
        _die_codes(lambda a, b: a + b == 7),
        _die_codes(lambda a, b: a * b == 12),
        _die_codes(lambda a, b: a + b == 7 and a * b == 12),
        _die_codes(lambda a, b: a + b == 7 or a * b == 12),
    ],
    12858: [[0], "B", "A"],
    12859: ["B"],
    12860: ["1/6", "1/2"],
    12861: ["1/2", "3/8"],
    12862: ["1/2"],
    12863: ["1/9", "1/6"],
    12864: ["3/10", "3/10"],
    12865: ["5/9", "5/12"],
    12866: ["1/13", "1/4"],
    12867: ["5/9", "2/9"],
    12868: ["1/8", "3/8"],
    12869: ["5/18", "5/18"],
    12870: ["3/5", "3/5"],
    12871: ["25/72"],
    12872: ["B"],
    12873: ["B"],
    12874: ["A"],
    12875: ["1/6", "5/12"],
    12876: ["1/4", "1/6"],
    12877: ["9/20", "9/10"],
    12878: ["3/5", "4/5"],
    12879: ["2/3"],
    12880: ["119/190"],
    12881: ["91/216", "25/216"],
    12882: ["3/7"],
    12883: ["1/24", "7/8"],
    12884: ["10"],
    12885: ["2/3", "2/3", "0"],
    12886: ["2/3"],
    12887: ["4/9"],
    12888: ["4/5", "5/6"],
    12889: ["4/5"],
    12890: ["13/18"],
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
        for value in _values(payload):
            if operation in PROB_OPS and isinstance(value, str):
                number = Fraction(value)
                assert 0 <= number <= 1
            if isinstance(value, list):
                assert value and len(value) == len(set(value)) <= 36
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= 20


def test_seed_zero_matches_independent_oracle():
    assert set(EXPECTED) == UNIT_IDS
    for cid, expected in EXPECTED.items():
        assert _values(_gen(cid, 0)) == expected, cid


def test_ordered_and_unordered_color_draws_agree():
    assert _values(_gen(12864, 0))[0] == _values(_gen(12864, 0))[1]
    assert _values(_gen(12870, 0))[0] == _values(_gen(12870, 0))[1]


def test_complement_matches_direct_count():
    different = Fraction(math.perm(6, 3), 6**3)
    assert _values(_gen(12887, 0)) == [str(1 - different)]
    assert _values(_gen(12865, 0))[0] == str(different)


def test_coverage_binds_the_formal_skills():
    assert set(COMPONENTS) == UNIT_IDS and not FIXED_ROWS
    assert set(FAMILY) == UNIT_IDS
    con = sqlite3.connect(f"file:{FORMAL_DB.as_posix()}?mode=ro", uri=True)
    snap = sqlite3.connect(f"file:{B.isolated_db().as_posix()}?mode=ro", uri=True)
    try:
        query = (
            "select id, skill_id, ifnull(correct_answer, ''), problem_text, source_chapter "
            "from textbook_examples where id between 12849 and 12890"
        )
        formal = {row[0]: row[1:] for row in con.execute(query)}
        frozen = {row[0]: row[1:] for row in snap.execute(query)}
    finally:
        con.close()
        snap.close()
    assert formal == frozen
    assert len(formal) == 42
    assert {row[3] for row in formal.values()} == {"單元6 古典機率"}
    assert all(row[1] == "" for row in formal.values())
    counts: dict[str, int] = {}
    for cid, (skill_id, _answer, _text, _chapter) in formal.items():
        counts[skill_id] = counts.get(skill_id, 0) + 1
        assert skill_id == _skill_of(cid)
    assert counts == {
        "gh_SampleSpace": 6,
        "gh_Event": 5,
        "gh_DefinitionOfClassicalProbability": 25,
        "gh_PropertiesOfProbability": 6,
    }
    for key, ops in SKILL_OPERATIONS.items():
        used = {spec[1] for spec in COMPONENTS.values() if spec[0] == key}
        assert used <= set(ops)
