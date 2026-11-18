"""Cross-question source dependency ("承例題N"): resolver, GenCode V3 phase 1 / prompt / gate, correlation math.

Real-data cases open the formal DB read-only; everything else is synthetic.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from core.textbook_source_dependency import (
    NEED_FIGURE,
    NEED_TABLE,
    STATUS_BLOCKED,
    STATUS_NONE,
    STATUS_RELATED,
    STATUS_RESOLVED,
    compose_practice_stem,
    generated_payload_dependency_issues,
    generation_contract,
    merge_image_assets,
    resolve_from_conn,
    resolve_source_dependency,
)

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "instance" / "kumon_math.db"
needs_prod = pytest.mark.skipif(not PROD.exists(), reason="formal database not present")

EX6_POINTS = [(24.5, 160), (25, 158), (25, 163), (25.5, 163), (26, 161), (26, 163), (26.5, 168), (27, 170), (27.5, 168), (28, 173)]
TABLE = "\\(\\begin{array}{|c|c|c|}\\hline x & 1 & 2 \\\\ \\hline y & 3 & 5 \\\\ \\hline \\end{array}\\)"


def _row(rid, title, text, notes=None, desc_extra=""):
    return {"id": rid, "source_description": f"{title} [source_type=x{desc_extra}]", "problem_text": text,
            "notes": json.dumps(notes or {}, ensure_ascii=False)}


def _no_assets(_notes):
    return []


def _one_asset(_notes):
    return [{"path": "uploads/fig.png", "url": "/static/fig.png", "display_path": "uploads/fig.png"}]


EXAMPLE_TABLE = _row(1, "例題6", f"某人測量資料如下表。\n{TABLE}\n(1)\t選出散布圖。\n(2)\t估計其身高。")
PRACTICE = _row(2, "隨堂練習7", "承例題6，若今新增一筆資料 \\((26,174)\\)，相關係數會變大還是變小？",
                desc_extra=" | linked_example=例題6")


def test_explicit_continuation_resolves_only_the_example_setup_without_its_sub_questions():
    res = resolve_source_dependency(PRACTICE, [EXAMPLE_TABLE, PRACTICE], image_assets_for=_one_asset)
    assert res["status"] == STATUS_RESOLVED and res["example_title"] == "例題6" and res["example_id"] == 1
    assert res["needs"] == ["example_text", NEED_TABLE]
    assert TABLE in res["context_text"] and "(1)" not in res["context_text"] and "身高" not in res["context_text"]
    assert res["image_assets"] == []  # the example's option pictures belong to its (1), not to the shared data
    assert res["provenance"]["dependent_row_id"] == 2 and len(res["provenance"]["example_problem_text_sha256"]) == 64


def test_served_stem_carries_the_data_and_keeps_the_original_stem_verbatim():
    res = resolve_source_dependency(PRACTICE, [EXAMPLE_TABLE, PRACTICE], image_assets_for=_one_asset)
    served = compose_practice_stem(res, PRACTICE["problem_text"])
    assert served.endswith(PRACTICE["problem_text"]) and TABLE in served and served.startswith("【例題6的資料】")


def test_figure_setup_needs_an_accepted_example_figure():
    example = _row(1, "例題9", "以下為兩科級分的人數百分比分布圖。\n(1)\t下列敘述何者正確？\n(2)\t頂標何者較高？")
    practice = _row(2, "隨堂練習10", "承例題9，前標何者較高？")
    blocked = resolve_source_dependency(practice, [example, practice], image_assets_for=_no_assets)
    assert blocked["status"] == STATUS_BLOCKED and blocked["reason"] == "example_figure_missing"
    ok = resolve_source_dependency(practice, [example, practice], image_assets_for=_one_asset)
    assert ok["status"] == STATUS_RESOLVED and NEED_FIGURE in ok["needs"] and len(ok["image_assets"]) == 1
    own = [{"path": "uploads/fig.png"}]
    assert merge_image_assets(own, ok) == own  # the same crop already bound to the row is not shown twice


@pytest.mark.parametrize(
    "rows, reason",
    [
        ([PRACTICE], "example_not_found"),
        ([PRACTICE, EXAMPLE_TABLE, dict(EXAMPLE_TABLE, id=3)], "example_ambiguous"),
        ([PRACTICE, _row(1, "例題6", "已知 \\(E=300d^{-2}\\)，檯燈高 0.4 公尺，求照度。")], "example_boundary_uncertain"),
        ([PRACTICE, _row(1, "例題6", "說明如下。\n(1)\t求值。")], "example_setup_has_no_data"),
    ],
)
def test_unresolvable_dependency_is_blocked_not_guessed(rows, reason):
    res = resolve_source_dependency(PRACTICE, rows, image_assets_for=_one_asset)
    assert res["status"] == STATUS_BLOCKED and res["reason"] == reason
    assert compose_practice_stem(res, "x") == "x" and generation_contract(res) is None


def test_recorded_dependency_conflicting_with_the_stem_is_blocked():
    notes = {"source_dependency": {"kind": "continues_example", "example_title": "例題5"}}
    practice = _row(2, "隨堂練習7", PRACTICE["problem_text"], notes)
    res = resolve_source_dependency(practice, [EXAMPLE_TABLE, practice])
    assert res["status"] == STATUS_BLOCKED and res["reason"] == "example_reference_conflict"


def test_linked_example_alone_is_only_related_and_plain_rows_are_untouched():
    related = _row(2, "隨堂練習2", "求相關係數。", desc_extra=" | linked_example=例題2")
    assert resolve_source_dependency(related, [EXAMPLE_TABLE])["status"] == STATUS_RELATED
    plain = _row(5, "例題2", "求 \\(f(2)\\)。")
    res = resolve_source_dependency(plain, [EXAMPLE_TABLE])
    assert res == {"status": STATUS_NONE}
    assert compose_practice_stem(res, plain["problem_text"]) == plain["problem_text"]


def _formal_conn():
    return sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)


def _formal_id(conn, volume, chapter, title):
    for rid, desc in conn.execute(
            "select id, source_description from textbook_examples where source_curriculum='general' and source_volume=? "
            "and source_chapter=?", (volume, chapter)):
        if desc.split(" [")[0] == title:
            return rid
    pytest.skip(f"{volume} {chapter} {title} not imported")


@needs_prod
def test_unit9_practice7_gets_the_ten_example6_data_points():
    conn = _formal_conn()
    try:
        rid = _formal_id(conn, "數學2", "單元9 二維數據分析", "隨堂練習7")
        res = resolve_from_conn(conn, rid)
    finally:
        conn.close()
    assert res["status"] == STATUS_RESOLVED and res["example_title"] == "例題6" and res["evidence"] == "notes.source_dependency"
    assert res["needs"] == ["example_text", NEED_TABLE] and res["image_assets"] == []
    for value in ("24.5", "27.5", "160", "173"):
        assert value in res["context_text"]
    assert "迴歸" not in res["context_text"] and "①" not in res["context_text"]


@needs_prod
def test_unit8_practice10_gets_the_example9_bar_chart():
    conn = _formal_conn()
    try:
        rid = _formal_id(conn, "數學2", "單元8 一維數據分析", "隨堂練習10")
        res = resolve_from_conn(conn, rid)
    finally:
        conn.close()
    assert res["status"] == STATUS_RESOLVED and res["example_title"] == "例題9" and res["evidence"] == "stem_continuation_cue"
    assert NEED_FIGURE in res["needs"] and len(res["image_assets"]) == 1 and "分布圖" in res["context_text"]


@needs_prod
def test_single_part_examples_elsewhere_are_blocked_until_a_boundary_is_confirmed():
    conn = _formal_conn()
    try:
        rid = _formal_id(conn, "數學1", "單元3 指數", "隨堂練習6")
        assert resolve_from_conn(conn, rid)["reason"] == "example_boundary_uncertain"
        plain = _formal_id(conn, "數學2", "單元9 二維數據分析", "例題2")
        assert resolve_from_conn(conn, plain)["status"] == STATUS_NONE
    finally:
        conn.close()


# --- GenCode V3 -------------------------------------------------------------------------------------------------------

_SCHEMA = ("create table textbook_examples (id integer primary key, skill_id text, source_description text, "
           "source_section text, source_paragraph text, problem_type text, problem_text text, correct_answer text, "
           "detailed_solution text, notes text, source_curriculum text, source_volume text, source_chapter text)")


def _v3_conn(with_example=True):
    conn = sqlite3.connect(":memory:")
    conn.execute(_SCHEMA)
    rows = [PRACTICE] + ([EXAMPLE_TABLE] if with_example else []) + [_row(9, "例題2", "求 \\(1+1\\)。")]
    for r in rows:
        conn.execute("insert into textbook_examples (id, skill_id, source_description, problem_text, correct_answer, "
                     "detailed_solution, notes, source_curriculum, source_volume, source_chapter) values (?,?,?,?,?,?,?,?,?,?)",
                     (r["id"], "gh_X", r["source_description"], r["problem_text"], "", "", r["notes"], "general", "數學2", "單元9"))
    conn.execute("create table gencode_component_tracker (textbook_example_id integer, induced_spec_payload text)")
    return conn


@pytest.fixture
def stub_core(monkeypatch):
    import core.gencode.pipeline_orchestrator as po

    calls = []

    def core(skill_id, row, *, conn=None, skill_examples=None):
        calls.append(row["id"])
        return {"classification_status": "resolved", "problem_type_id": "pt", "classification_source": "stub",
                "required_capabilities": ["pt"], "source_hash": po._compute_v3_example_source_hash(row)}

    monkeypatch.setattr(po, "_run_v3_no_llm_phase1_core", core)
    return po, calls


def _fetch(po, conn, rid):
    return po._load_textbook_example_row_from_conn(conn, rid)


def test_v3_phase1_attaches_the_generation_contract_for_a_resolved_dependency(stub_core):
    po, calls = stub_core
    conn = _v3_conn()
    out = po.run_v3_no_llm_phase1_for_example("gh_X", _fetch(po, conn, 2), conn=conn)
    sd = out["source_dependency"]
    assert out["classification_status"] == "resolved" and calls == [2]
    assert sd["self_contained_required"] is True and sd["example_title"] == "例題6" and TABLE in sd["source_setup_text"]
    plain = po.run_v3_no_llm_phase1_for_example("gh_X", _fetch(po, conn, 9), conn=conn)
    assert "source_dependency" not in plain


def test_v3_phase1_blocks_a_dependency_without_its_example(stub_core):
    po, calls = stub_core
    conn = _v3_conn(with_example=False)
    out = po.run_v3_no_llm_phase1_for_example("gh_X", _fetch(po, conn, 2), conn=conn)
    assert out["classification_status"] == "unresolved" and calls == []
    assert out["reason"] == "SOURCE_DEPENDENCY_UNRESOLVED:example_not_found"
    no_conn = po.run_v3_no_llm_phase1_for_example("gh_X", {"id": 2, "problem_text": PRACTICE["problem_text"]})
    assert no_conn["reason"] == "SOURCE_DEPENDENCY_UNRESOLVED:dependency_lookup_unavailable"


def test_v3_cached_spec_without_the_dependency_is_not_reused(stub_core):
    po, calls = stub_core
    conn = _v3_conn()
    for rid in (2, 9):
        row = _fetch(po, conn, rid)
        cached = {"classification_status": "resolved", "problem_type_id": "pt", "classification_source": "old",
                  "required_capabilities": ["pt"], "source_hash": po._compute_v3_example_source_hash(row)}
        conn.execute("insert into gencode_component_tracker values (?, ?)", (rid, json.dumps(cached)))
    assert po.resolve_v3_admin_induced_spec(conn, "gh_X", 9)["reused"] is True
    fresh = po.resolve_v3_admin_induced_spec(conn, "gh_X", 2)
    assert fresh["reused"] is False and fresh["induced_spec"]["source_dependency"]["example_title"] == "例題6"
    conn.execute("update gencode_component_tracker set induced_spec_payload=? where textbook_example_id=2",
                 (json.dumps(fresh["induced_spec"]),))
    assert po.resolve_v3_admin_induced_spec(conn, "gh_X", 2)["reused"] is True


def test_generator_prompt_demands_self_contained_items_only_for_dependent_sources(stub_core):
    from core.gencode.problem_type_spec import build_generator_code_prompt, build_generator_plan_prompt

    po, _ = stub_core
    conn = _v3_conn()
    spec = po.run_v3_no_llm_phase1_for_example("gh_X", _fetch(po, conn, 2), conn=conn)
    for prompt in (build_generator_code_prompt(spec), build_generator_plan_prompt(spec)):
        assert "SOURCE DEPENDENCY" in prompt and TABLE in prompt and "self-contained" in prompt
    assert "SOURCE DEPENDENCY" not in build_generator_code_prompt({"problem_type_id": "pt"})


def _dep_spec(needs=("example_text", NEED_TABLE)):
    return {"problem_type_id": "pt", "source_dependency": {"self_contained_required": True, "needs": list(needs)}}


def test_generated_item_still_pointing_at_the_example_fails_the_gate():
    from core.gencode.validators import validate_generator_payload

    stale = {"question_text": "承例題6，若今新增一筆資料 \\((26,174)\\)，相關係數會變大還是變小？", "answer": "變小"}
    issues = generated_payload_dependency_issues(stale, _dep_spec()["source_dependency"])
    assert issues == ["generated_stem_references_external_example", "generated_stem_missing_data_table"]
    errors = validate_generator_payload(stale, problem_type_spec=_dep_spec())
    assert "SOURCE_DEPENDENCY_SELF_CONTAINED: generated_stem_references_external_example" in errors
    unrelated = [e for e in validate_generator_payload(stale, problem_type_spec={"problem_type_id": "pt"})
                 if e.startswith("SOURCE_DEPENDENCY")]
    assert unrelated == []  # specs without a source dependency (e.g. published units) are not affected
    figure = generated_payload_dependency_issues({"question_text": "如下圖。"}, {"needs": ["example_text", NEED_FIGURE]})
    assert figure == ["generated_item_missing_figure"]


# --- correlation math ---------------------------------------------------------------------------------------------------

def test_example6_correlation_and_practice7_direction():
    from core.domain.statistics.bivariate_statistics import correlation_change_after_adding_point, pearson_r

    assert pearson_r(EX6_POINTS) == pytest.approx(0.90026, abs=5e-6)
    change = correlation_change_after_adding_point(EX6_POINTS, (26, 174))
    assert change["r_after"] == pytest.approx(0.75219, abs=5e-6) and change["direction"] == "變小"
    on_line = [(1, 2), (2, 4), (3, 6)]
    assert correlation_change_after_adding_point(on_line, (4, 8))["direction"] == "不變"
    with pytest.raises(ValueError):
        pearson_r([(1, 5), (2, 5), (3, 5)])


def test_generated_variants_are_self_contained_varied_and_consistent():
    from core.domain.statistics.bivariate_statistics import build_correlation_change_item, correlation_change_after_adding_point

    spec = _dep_spec()
    seen_answers, seen_tables = set(), set()
    for seed in range(200):
        item = build_correlation_change_item(seed)
        assert generated_payload_dependency_issues(item, spec["source_dependency"]) == []
        givens = item["metadata"]["givens"]
        points = [tuple(p) for p in givens["points"]]
        recomputed = correlation_change_after_adding_point(points, tuple(givens["new_point"]))
        assert item["answer"] == recomputed["direction"] and item["answer"] in item["choices"]
        assert all(p[0] in item["question_text"] and p[1] in item["question_text"] for p in givens["points"])
        assert "相關係數" in item["question_text"] and item["question_text"].count("\\(") == item["question_text"].count("\\)")
        seen_answers.add(item["answer"])
        seen_tables.add(item["question_text"])
    assert seen_answers == {"變大", "變小"} and len(seen_tables) == 200
