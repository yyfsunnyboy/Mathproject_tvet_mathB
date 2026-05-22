# -*- coding: utf-8 -*-
"""Phase4 綜合練習／多維度座標防線與 Phase2 自我評量題塊（純函式，無 DB）。"""

import re

from core.textbook_processor import extract_section_code_from_title
from core.textbook_processor_v2 import (
    _STRONG_SOL_START_RE,
    MATHB1_CHAPTER1_CANONICAL_TITLE,
    _QUESTION_BOUNDARY_RE,
    _QUESTION_TRIGGER_PREFIX,
    _db_titles_from_curriculum_row,
    _force_mathb1_chapter_title,
    _import_scope_coords,
    _is_chapter_self_assessment_import,
    _is_vocational_math_b1,
    _lookup_question_block,
    _normalize_docx_line_text,
    _parse_boundary_question_number,
    _sanitize_db_latex_delimiters,
    _self_assessment_admin_label,
    normalize_chapter_title_for_db,
    phase2_deterministic_block_slice,
)


class _FakeCurriculum:
    def __init__(self, skill_id: str, chapter: str, section: str):
        self.skill_id = skill_id
        self.chapter = chapter
        self.section = section


def test_db_titles_from_curriculum_row_uses_db_strings_only():
    row = _FakeCurriculum("vh_數學B1_Foo", "1 坐標系與函數圖形", "1-2 平面坐標系與線型函數")
    info = {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}
    sid, ch, sec = _db_titles_from_curriculum_row(row, info)  # type: ignore[arg-type]
    assert sid == "vh_數學B1_Foo"
    assert ch == "1 坐標系與函數圖形"
    assert sec == "1-2 平面坐標系與線型函數"


def test_db_titles_keeps_wrong_db_chapter_for_section_code_21():
    """第 2 章小節即使 chapter 欄位錯躺第 1 章，入庫仍跟 DB 對齊避免盾誤殺。"""
    from core.textbook_processor_v2 import _reverse_align_textbook_source_from_curriculum

    row = _FakeCurriculum("outline_x", "1 坐標系與函數圖形", "2-1 斜率")
    row.curriculum = "vocational"
    row.volume = "數學B1"
    aligned = _reverse_align_textbook_source_from_curriculum(row)  # type: ignore[arg-type]
    assert aligned["source_curriculum"] == "vocational"
    assert aligned["source_volume"] == "數學B1"
    assert aligned["source_chapter"] == "1 坐標系與函數圖形"
    assert aligned["source_section"] == "2-1 斜率"
    _, ch, sec = _db_titles_from_curriculum_row(row, None)  # type: ignore[arg-type]
    assert ch == aligned["source_chapter"]
    assert sec == aligned["source_section"]


def test_section_code_boundary_matches():
    from core.textbook_processor_v2 import _section_code_boundary_matches

    assert _section_code_boundary_matches("2-1", "2-1 斜率")
    assert _section_code_boundary_matches("1-1", "1-1 數線與絕對值")
    assert not _section_code_boundary_matches("2-1", "2-10 其他")


def test_extract_section_code_from_section_title():
    assert extract_section_code_from_title("1-2 平面坐標系與線型函數") == "1-2"
    assert extract_section_code_from_title("自我評量") == ""


def test_mathb1_chapter_title_force():
    forced = _force_mathb1_chapter_title("第一章 自我評量", enabled=True)
    assert forced == MATHB1_CHAPTER1_CANONICAL_TITLE
    assert _force_mathb1_chapter_title("自我評量", enabled=False) == "自我評量"


def test_vocational_math_b1_scope_detection():
    info = {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}
    assert _is_vocational_math_b1(info) is True
    assert _is_vocational_math_b1({**info, "volume": "數學B2"}) is False


def test_self_assessment_import_detection():
    blocks = {"CH1自我評量 題1": "題幹"}
    assert _is_chapter_self_assessment_import("任意章", blocks) is True
    assert _is_chapter_self_assessment_import("第1章 自我評量", {}) is True


def test_normalize_chapter_title_for_db():
    assert normalize_chapter_title_for_db("第1章 坐標系與函數圖形") == "1 坐標系與函數圖形"


def test_import_scope_coords():
    coords = _import_scope_coords({"curriculum": "vocational", "grade": 10, "volume": "數學B1"})
    assert coords == {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}


def test_question_boundary_re_matches_self_assessment_stems():
    for line in ("1.\t若 $|x|=3$", "2. 設 $f(x)=2x+1$", "10. ", "12、解不等式", "1\t試求"):
        assert _QUESTION_BOUNDARY_RE.match(line), line
    assert _parse_boundary_question_number("1.\t若 $|x|=3$") == 1
    assert _parse_boundary_question_number("15.\t已知路邊") == 15


def test_phase2_chapter_self_assessment_canonical_keys():
    text = (
        "CH1自我評量\n"
        "自我評量\n"
        "1-1 數線與絕對值\n"
        "1.\t若 $|x|=3$，則 $x$ 為何？\n"
        "(A) 3\n"
        "1-2 函數\n"
        "2.\t設 $f(x)=2x+1$，求 $f(0)$。\n"
        "1-3 二次函數\n"
        "11.\t解 $x^2-1>0$。\n"
        "1-4 一元二次不等式\n"
        "15.\t已知路邊行動咖啡車製作n杯咖啡的成本為n + 50元。\n"
        "20.\t最後一題。\n"
    )
    blocks = phase2_deterministic_block_slice(
        text.splitlines(), source_scope="chapter_self_assessment"
    )
    assert "CH1自我評量 題1" in blocks
    assert "CH1自我評量 題2" in blocks
    assert "CH1自我評量 題11" in blocks
    assert "CH1自我評量 題15" in blocks
    assert "CH1自我評量 題20" in blocks
    assert len(blocks) == 5
    assert re.search(r"\$|x\|=3", blocks["CH1自我評量 題1"])


def test_normalize_docx_line_text_strips_nbsp():
    assert _normalize_docx_line_text("1.\xa0試求") == "1. 試求"


def test_phase2_question_trigger_nbsp_self_assessment():
    text = (
        "CH1自我評量\n"
        "自我評量\n"
        "1-1 數線\n"
        f"{_QUESTION_TRIGGER_PREFIX} 1.\xa0試求 $|x|=1$。\n"
        f"{_QUESTION_TRIGGER_PREFIX} 2.\t設 $f(x)=x$。\n"
    )
    blocks = phase2_deterministic_block_slice(
        text.splitlines(), source_scope="chapter_self_assessment"
    )
    assert "CH1自我評量 題1" in blocks
    assert "CH1自我評量 題2" in blocks
    assert "|x|=1" in blocks["CH1自我評量 題1"]


def test_strong_sol_start_matches_standalone_jie_line():
    for line in ("解", "解：", "[解]", "(解)", "解 由題意可知"):
        assert _STRONG_SOL_START_RE.match(line), line


def test_exam_end_re_matches_bracket_markers():
    from core.textbook_processor_v2 import (
        _EXAM_END_RE,
        _normalize_exam_category,
        _parse_exam_end_marker,
        _strip_exam_end_marker_from_line,
    )

    assert _EXAM_END_RE.search("〔105統測A〕")
    assert _EXAM_END_RE.search("答案見 [106統測B]")
    assert _EXAM_END_RE.search("【112統測C】")
    assert _EXAM_END_RE.search("（109\u3000統測\u3000Ｂ）")
    parsed = _parse_exam_end_marker("〔105統測A〕")
    assert parsed == ("105", "A")
    assert _parse_exam_end_marker("（109統測Ｂ）") == ("109", "B")
    assert _parse_exam_end_marker("【112統測c】") == ("112", "C")
    assert _normalize_exam_category("Ｃ") == "C"
    assert _strip_exam_end_marker_from_line("(A) 正確 〔109統測B〕") == "(A) 正確"


def test_phase2_exam_block_timu_start_and_marker_end():
    lines = [
        "統測歷屆試題",
        "題目",
        "下列何者正確？",
        "(A) 1",
        "〔105統測A〕",
        "題目",
        "第二題求 $x$。",
        "[106統測B]",
    ]
    blocks = phase2_deterministic_block_slice(lines, source_scope="section_textbook")
    assert "105統測A" in blocks
    assert "106統測B" in blocks
    assert "下列" in blocks["105統測A"]
    assert "$x$" in blocks["106統測B"]
    assert "〔105統測A〕" not in blocks["105統測A"]


def test_phase2_exam_block_fullwidth_marker_and_inline_tail():
    lines = [
        "統測歷屆試題",
        "題目",
        "求極值。",
        "(A) 選項一 (B) 選項二 （109\u3000統測\u3000Ｂ）",
        "題目",
        "第三題。",
        "【112統測C】",
    ]
    blocks = phase2_deterministic_block_slice(lines, source_scope="section_textbook")
    assert "109統測B" in blocks
    assert "112統測C" in blocks
    assert "選項二" in blocks["109統測B"]
    assert "統測" not in blocks["109統測B"]
    assert "第三題" in blocks["112統測C"]


def test_phase2_double_blank_line_fuses_practice_stem():
    lines = [
        "隨堂練習1",
        "求 $x$ 使得 $x>0$。",
        "",
        "",
        "另外觀察二次函數圖形可知結論不同。",
    ]
    blocks = phase2_deterministic_block_slice(lines, source_scope="section_textbook")
    assert "隨堂練習1" in blocks
    body = blocks["隨堂練習1"]
    assert "$x>0$" in body
    assert "另外觀察" not in body


def test_phase2_example_stops_before_solution_block():
    lines = [
        "例題7",
        "求 $f(x)$ 之最大值。",
        "解",
        "由配方法可知最大値為 3。",
        "例題8",
        "下一題題幹。",
    ]
    blocks = phase2_deterministic_block_slice(lines, source_scope="section_textbook")
    assert "例題7" in blocks
    body = blocks["例題7"]
    assert "最大值" in body
    assert "配方法" not in body
    assert "解" not in body or body.strip().endswith("。")


def test_sanitize_db_latex_delimiters():
    raw = r"(A)\[\left( -3,-3 \right)\]"
    assert _sanitize_db_latex_delimiters(raw) == r"(A)$\left( -3,-3 \right)$"


def test_self_assessment_admin_label_b1():
    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    assert _self_assessment_admin_label(info, "1 坐標系與函數圖形") == "第一章 自我評量"


def test_resolve_outline_grade_from_volume():
    from core.textbook_processor_v2 import _resolve_outline_grade

    assert _resolve_outline_grade({"volume": "數學B1", "grade": 10}) == 10
    assert _resolve_outline_grade({"volume": "數學B2"}) == 11
    assert _resolve_outline_grade({"volume": "數學B4"}) == 13


def test_canonical_outline_section_title():
    from core.textbook_processor_v2 import _canonical_outline_section_title

    code, title = _canonical_outline_section_title("1-4", "一元二次不等式")
    assert code == "1-4"
    assert title == "1-4 一元二次不等式"
    code2, title2 = _canonical_outline_section_title("", "1-2 平面坐標系與線型函數")
    assert code2 == "1-2"
    assert title2 == "1-2 平面坐標系與線型函數"


def test_normalize_outline_chapter_title_strict():
    from core.textbook_processor_v2 import (
        _canonical_outline_chapter_title,
        _normalize_outline_chapter_title_strict,
        MATHB1_CHAPTER1_CANONICAL_TITLE,
    )

    info = {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}
    assert _normalize_outline_chapter_title_strict("第1章 坐標系與函數圖形") == "1 坐標系與函數圖形"
    assert _normalize_outline_chapter_title_strict("第一章 坐標系與函數圖形") == "1 坐標系與函數圖形"
    assert _normalize_outline_chapter_title_strict("第 2 章 直線方程式") == "2 直線方程式"
    assert _normalize_outline_chapter_title_strict("第2章 直線方程式") == "2 直線方程式"
    assert _canonical_outline_chapter_title("第1章 坐標系與函數圖形", info) == MATHB1_CHAPTER1_CANONICAL_TITLE
    assert _canonical_outline_chapter_title("第2章 直線方程式", info) == "2 直線方程式"


def test_volume_labels_match_loose_b1():
    from core.textbook_processor_v2 import _volume_labels_match

    assert _volume_labels_match("數學B1", "數學B1") is True
    assert _volume_labels_match("數學B1", "B1") is True
    assert _volume_labels_match("數學 B1", "B1") is True
    assert _volume_labels_match("數學B1", "數學B2") is False


def test_normalize_parsed_pdf_outline_payload_strips_chapter_prefix():
    from core.textbook_processor_v2 import _normalize_parsed_pdf_outline_payload

    raw = {
        "chapters": [
            {
                "chapter_title": "第2章 直線方程式",
                "sections": [
                    {"section_code": "2-1", "section_title": "斜率"},
                ],
            }
        ]
    }
    info = {"curriculum": "vocational", "grade": 10, "volume": "數學B1"}
    out = _normalize_parsed_pdf_outline_payload(raw, info)
    assert out["chapters"][0]["chapter_title"] == "2 直線方程式"
    assert out["chapters"][0]["sections"][0]["section_title"] == "2-1 斜率"


def test_phase3_chunk_blocks_keys():
    from core.textbook_processor_v2 import _chunk_blocks_keys_for_phase3

    keys = [f"題{i}" for i in range(1, 28)]
    chunks = _chunk_blocks_keys_for_phase3(keys, 10)
    assert len(chunks) == 3
    assert len(chunks[0]) == 10
    assert len(chunks[1]) == 10
    assert len(chunks[2]) == 7


def test_phase3_merge_metadata_trees():
    from core.textbook_processor_v2 import _merge_phase3_metadata_trees

    merged: dict = {"chapters": []}
    part_a = {
        "chapters": [
            {
                "chapter_title": "第1章 坐標系與函數圖形",
                "sections": [
                    {
                        "section_title": "1-4 一元二次不等式",
                        "concepts": [
                            {
                                "concept_name": "概念A",
                                "examples": [{"title": "例題1", "source_description": "例題1"}],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    part_b = {
        "chapters": [
            {
                "chapter_title": "1 坐標系與函數圖形",
                "sections": [
                    {
                        "section_title": "1-4",
                        "concepts": [
                            {
                                "concept_name": "概念A",
                                "examples": [],
                                "practice_questions": [
                                    {"title": "隨堂練習11", "source_description": "隨堂練習11"}
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    _merge_phase3_metadata_trees(merged, part_a)
    _merge_phase3_metadata_trees(merged, part_b)
    assert len(merged["chapters"]) == 1
    secs = merged["chapters"][0]["sections"]
    assert len(secs) == 1
    concepts = secs[0]["concepts"]
    assert len(concepts) == 1
    titles = [x["title"] for x in concepts[0]["examples"] + concepts[0]["practice_questions"]]
    assert "例題1" in titles
    assert "隨堂練習11" in titles


def test_resolve_authoritative_section_code_prefers_filename():
    from core.textbook_processor_v2 import _resolve_authoritative_section_code

    info = {"section_code": "1-1", "volume": "數學B1"}
    assert (
        _resolve_authoritative_section_code(
            info,
            matched_key="隨堂練習5",
            gemini_section_code="1-3",
            title="5 解不等式",
        )
        == "1-1"
    )


def test_phase4_clean_source_description_labels():
    from core.textbook_processor_v2 import (
        _curriculum_authority_coords,
        _phase4_clean_source_description,
        _strip_source_description_pollution,
        _textbook_geometry_from_curriculum_row,
    )

    row = _FakeCurriculum("outline_vocational_數學B1_11", "1 坐標系與函數圖形", "1-1 數線與絕對值")
    row.curriculum = "vocational"
    row.volume = "數學B1"
    dirty = "隨堂練習5 [source_type=textbook_example | section=1-1 | dedupe=abc123]"
    assert _strip_source_description_pollution(dirty) == "隨堂練習5"
    assert (
        _phase4_clean_source_description(
            raw_description=dirty,
            authority_row=row,  # type: ignore[arg-type]
        )
        == "隨堂練習5"
    )
    assert (
        _phase4_clean_source_description(
            title="例題1",
            source_type="textbook_example",
            authority_row=row,  # type: ignore[arg-type]
        )
        == "例題1"
    )
    assert (
        _phase4_clean_source_description(
            is_self_assessment=True,
            authority_row=row,  # type: ignore[arg-type]
        )
        == "1 坐標系與函數圖形 1-1 數線與絕對值"
    )
    auth = _curriculum_authority_coords(row)  # type: ignore[arg-type]
    assert auth["section_title"] == "1-1 數線與絕對值"
    geo = _textbook_geometry_from_curriculum_row(row)  # type: ignore[arg-type]
    assert geo["source_curriculum"] == "vocational"
    assert geo["source_volume"] == "數學B1"
    assert geo["source_chapter"] == "1 坐標系與函數圖形"
    assert geo["source_section"] == "1-1 數線與絕對值"
    assert geo["source_volume"] != "vocational"


def test_lookup_question_block_exam_loose_title():
    from core.textbook_processor_v2 import _lookup_question_block

    blocks = {
        "105統測A": "統測題幹A",
        "111統測B": r"設 $f(x)=\[x^2+1\]$",
    }
    body, key = _lookup_question_block("111統測B_\n附註", blocks)
    assert key == "111統測B"
    assert "$" in body
    assert r"\[" not in body


def test_lookup_question_block_suitang_multiline_title():
    from core.textbook_processor_v2 import _lookup_question_block

    blocks = {
        "隨堂練習4": "第四題",
        "隨堂練習5": r"5. 解下列 \[x>0\]",
        "隨堂練習6": r"6. 另一題 \[a+b\]",
    }
    body5, key5 = _lookup_question_block("5 解下列不等式\n(A) 1", blocks)
    assert key5 == "隨堂練習5"
    assert "$" in body5
    body6, key6 = _lookup_question_block("隨堂練習6\n第二行", blocks)
    assert key6 == "隨堂練習6"


def test_is_short_section_code_only():
    from core.textbook_processor_v2 import _is_short_section_code_only

    assert _is_short_section_code_only("1-1")
    assert _is_short_section_code_only("2-10")
    assert not _is_short_section_code_only("1-1 數線與絕對值")
    assert not _is_short_section_code_only("")


def _fake_skill_curriculum_query_stub(monkeypatch, *, first_return, all_return):
    from unittest.mock import MagicMock

    class _Col:
        def __init__(self, name: str):
            self.name = name

        def __eq__(self, other):
            return (self.name, "eq", other)

        def startswith(self, other):
            return (self.name, "startswith", other)

        def asc(self):
            return self

    class _Row:
        def __init__(self, section: str, volume: str = "數學B1", skill_id: str = "vh_test"):
            self.section = section
            self.volume = volume
            self.skill_id = skill_id
            self.display_order = 1
            self.id = 1

    chain = MagicMock()
    chain.filter.return_value = chain
    chain.order_by.return_value = chain
    chain.first.return_value = first_return
    chain.all.return_value = all_return

    class _FakeSkillCurriculum:
        curriculum = _Col("curriculum")
        volume = _Col("volume")
        section = _Col("section")
        display_order = _Col("display_order")
        id = _Col("id")
        query = chain

    monkeypatch.setattr(
        "core.textbook_processor_v2.SkillCurriculum",
        _FakeSkillCurriculum,
    )
    return chain, _Row, _FakeSkillCurriculum


def test_lookup_exact_three_dimensions_uses_equality_not_like(monkeypatch):
    """Phase4 大綱查詢：先三維 ==，短代碼才 prefix；不得使用 section LIKE %。"""
    from core.textbook_processor_v2 import _lookup_curriculum_exact_three_dimensions

    class _Row:
        def __init__(self, section: str):
            self.section = section
            self.volume = "數學B1"
            self.skill_id = "vh_test"
            self.display_order = 1
            self.id = 1

    chain, _, _ = _fake_skill_curriculum_query_stub(
        monkeypatch,
        first_return=_Row("1-1 數線與絕對值"),
        all_return=[],
    )

    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    hit = _lookup_curriculum_exact_three_dimensions(
        info,
        section_label="1-1 數線與絕對值",
        section_code="1-1",
    )
    assert hit is not None
    assert hit.section == "1-1 數線與絕對值"
    chain.first.assert_called()
    chain.all.assert_not_called()


def test_curriculum_authority_coords_from_row():
    from core.textbook_processor_v2 import _curriculum_authority_coords

    row = _FakeCurriculum("vh_x", "2 直線方程式", "2-1 斜率")
    row.curriculum = "vocational"
    row.volume = "數學B2"
    auth = _curriculum_authority_coords(row)  # type: ignore[arg-type]
    assert auth["skill_id"] == "vh_x"
    assert auth["curriculum"] == "vocational"
    assert auth["volume"] == "數學B2"
    assert auth["chapter_title"] == "2 直線方程式"
    assert auth["section_title"] == "2-1 斜率"


def test_lookup_exact_prefix_fallback_for_short_code(monkeypatch):
    from core.textbook_processor_v2 import _lookup_curriculum_exact_three_dimensions

    class _Row:
        def __init__(self, section: str):
            self.section = section
            self.volume = "數學B1"
            self.skill_id = "vh_1"
            self.display_order = 1
            self.id = 2

    chain, _, _ = _fake_skill_curriculum_query_stub(
        monkeypatch,
        first_return=None,
        all_return=[_Row("1-1 數線與絕對值")],
    )

    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    hit = _lookup_curriculum_exact_three_dimensions(
        info,
        section_label="",
        section_code="1-1",
        gemini_section_title="1-1",
    )
    assert hit is not None
    assert hit.section == "1-1 數線與絕對值"
    chain.first.assert_not_called()
    chain.all.assert_called()


def test_lookup_readonly_ignores_gemini_section_title(monkeypatch):
    """Gemini 誤標 1-3 不得參與大綱撞擊；僅權威小節碼 1-1。"""
    from core.textbook_processor_v2 import _lookup_readonly_curriculum_row

    calls: list[dict] = []

    def _spy(info, code, **kwargs):
        calls.append({"code": code, "kwargs": kwargs})
        return None

    monkeypatch.setattr(
        "core.textbook_processor_v2._dynamic_curriculum_lookup_by_section_code",
        _spy,
    )
    info = {"curriculum": "vocational", "volume": "數學B1", "section_code": "1-1"}
    _lookup_readonly_curriculum_row(
        info,
        "1-1",
        gemini_section_title="1-3 二次函數",
        section_title="1-3 二次函數",
    )
    assert calls[0]["code"] == "1-1"
    assert calls[0]["kwargs"].get("gemini_section_title", "UNUSED") == "UNUSED"


def test_phase4_sync_skill_info_category_overwrites_ai_pollution(monkeypatch):
    from core.textbook_processor_v2 import _phase4_sync_skill_info_category

    class _Row:
        skill_id = "vh_test"
        section = "1-1 數線與絕對值"

    class _Skill:
        def __init__(self):
            self.category = "1-3 二次函數"

    skill = _Skill()

    class _Query:
        @staticmethod
        def get(sid):
            return skill if sid == "vh_test" else None

    class _FakeSkillInfo:
        query = _Query

    monkeypatch.setattr("core.textbook_processor_v2.SkillInfo", _FakeSkillInfo)
    assert _phase4_sync_skill_info_category(_Row(), "vh_test") is True
    assert skill.category == "1-1 數線與絕對值"


def test_textbook_processor_v2_has_no_section_like_queries():
    import pathlib

    src = pathlib.Path("core/textbook_processor_v2.py").read_text(encoding="utf-8")
    assert ".like(" not in src
    assert "section.like" not in src


def test_lookup_question_block_loose_match_question_9():
    blocks = {
        "CH1自我評量 題9": "9. 利用截距定義求函數圖形之方程式。",
        "CH1自我評量 題10": "10. 另一題。",
    }
    text, key = _lookup_question_block(
        "9. 利用截距定義求函數圖形之方程式",
        blocks,
        is_self_assessment=True,
    )
    assert key == "CH1自我評量 題9"
    assert "截距" in text
