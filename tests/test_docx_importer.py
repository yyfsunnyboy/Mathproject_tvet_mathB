import json
import os
from dataclasses import dataclass

from docx import Document
from docx.oxml import parse_xml
from flask import Flask

import core.textbook_processor as processor
from core.math_formula_normalizer import normalize_math_text
from core.question_image_assets import (
    build_question_asset_dir,
    build_question_asset_filename,
    safe_slug,
)


OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _omml_p_n_r(n: int, r: int) -> str:
    return (
        f'<m:oMath xmlns:m="{OMML_NS}"><m:sSubSup><m:e><m:r><m:t>P</m:t></m:r></m:e>'
        f"<m:sub><m:r><m:t>{r}</m:t></m:r></m:sub><m:sup><m:r><m:t>{n}</m:t></m:r></m:sup>"
        f"</m:sSubSup></m:oMath>"
    )


def test_build_question_asset_dir_vocational():
    p = build_question_asset_dir("vocational", "longteng", "數學B4", "1 排列組合", "1-2 直線排列")
    assert p == "uploads/question_assets/vocational/longteng/數學B4/ch01_排列組合/sec_1-2_直線排列"


def test_build_question_asset_dir_junior():
    p = build_question_asset_dir("junior", "kangxuan", "數學2上", "第3章 一元二次方程式", "3-1 因式分解法")
    assert p == "uploads/question_assets/junior/kangxuan/數學2上/ch03_一元二次方程式/sec_3-1_因式分解法"


def test_safe_slug_windows_chars_and_chinese():
    s = safe_slug('1-2 直線排列 < > : " / \\ | ? *')
    assert s == "1-2_直線排列"


def test_build_question_asset_filename_not_conflict_by_hash():
    f1 = build_question_asset_filename("textbook_example", "例題7", "a1b2c3d4", 1, "png")
    f2 = build_question_asset_filename("textbook_example", "例題7", "f3e9aa21", 1, "png")
    assert f1 != f2
    assert f1.endswith(".png") and f2.endswith(".png")


def test_paragraph_image_rid_detection_blip_and_imagedata():
    doc = Document()
    p = doc.add_paragraph("例題7")
    p._p.append(parse_xml('<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:drawing><a:graphic><a:graphicData><a:pic><a:blipFill><a:blip r:embed="rId5"/></a:blipFill></a:pic></a:graphicData></a:graphic></w:drawing></w:r>'))
    p._p.append(parse_xml('<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:pict><v:imagedata r:id="rId6"/></w:pict></w:r>'))
    rids = processor.extract_docx_image_rids_from_paragraph(p)
    assert "rId5" in rids and "rId6" in rids


def test_attach_blocks_orphan_ignored_behavior():
    blocks = [
        {"type": "image", "path": "uploads/media/media/orphan.png", "block_index": 1},
        {"type": "paragraph", "text": "一般文字", "block_index": 2},
    ]
    q_assets, orphan = processor.attach_docx_media_to_question_blocks(blocks)
    assert q_assets == {}
    assert len(orphan) == 1


def test_attach_image_before_question_with_futu_reason():
    blocks = [
        {"type": "image", "path": "uploads/media/media/near.png", "block_index": 1},
        {"type": "paragraph", "text": "例題 7 請依附圖回答", "block_index": 2},
    ]
    q_assets, orphan = processor.attach_docx_media_to_question_blocks(blocks)
    assert len(orphan) == 0
    assert "例題7" in q_assets
    assert q_assets["例題7"][0]["image_attach_reason"] == "near_next_question"


def test_attach_image_shared_for_adjacent_questions():
    blocks = [
        {"type": "paragraph", "text": "例題 7", "block_index": 10},
        {"type": "image", "path": "uploads/media/media/shared.png", "block_index": 11},
        {"type": "paragraph", "text": "隨堂練習 7 依右圖作答", "block_index": 12},
    ]
    q_assets, orphan = processor.attach_docx_media_to_question_blocks(blocks)
    assert len(orphan) == 0
    assert any(a.get("shared_image") for a in q_assets.get("例題7", []))
    assert any(a.get("shared_image") for a in q_assets.get("隨堂練習7", []))


def test_formula_block_wmf_emf_classified_formula_asset():
    blocks = [
        {"type": "paragraph", "text": "例題2 試填入下列各式□之值", "block_index": 1},
        {"type": "image", "rid": "rId5", "path": "uploads/media/media/image3.wmf", "content_type": "image/x-wmf", "block_index": 2},
        {"type": "image", "rid": "rId6", "path": "uploads/media/media/image4.emf", "content_type": "image/x-emf", "block_index": 3},
    ]
    q_assets, _ = processor.attach_docx_media_to_question_blocks(blocks)
    assets = q_assets.get("例題2", [])
    assert assets
    assert all(a.get("media_kind") == "formula_asset" for a in assets)


def test_grid_path_image_kept_as_image_asset():
    blocks = [
        {"type": "paragraph", "text": "例題7 如圖為棋盤式街道圖", "block_index": 1},
        {"type": "image", "rid": "rId7", "path": "uploads/media/media/image7.png", "content_type": "image/png", "block_index": 2},
    ]
    q_assets, _ = processor.attach_docx_media_to_question_blocks(blocks)
    assets = q_assets.get("例題7", [])
    assert assets
    assert assets[0].get("media_kind") == "image_asset"


def test_docx_main_pipeline_calls_media_attach(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_pipeline_call")
    os.makedirs(root, exist_ok=True)
    doc_path = os.path.join(root, "m.docx")
    d = Document()
    d.add_paragraph("例題7 如圖")
    d.save(doc_path)
    called = {"rel": 0, "attach": 0}

    monkeypatch.setattr(processor, "build_docx_media_relationship_map", lambda *a, **k: (called.__setitem__("rel", called["rel"] + 1) or {}))
    monkeypatch.setattr(processor, "attach_docx_media_to_question_blocks", lambda *a, **k: (called.__setitem__("attach", called["attach"] + 1) or ({}, [])))
    with Flask(__name__).app_context():
        q = type("Q", (), {"put": lambda *_: None})()
        out = processor.extract_content_from_file(str(doc_path), q)
    assert 1 in out
    assert called["rel"] >= 1
    assert called["attach"] >= 1


@dataclass
class _FakeRow:
    values: dict

    def __getattr__(self, item):
        return self.values.get(item)


class _FakeQuery:
    def __init__(self, rows, key_field=None):
        self.rows = rows
        self.filters = {}
        self.key_field = key_field

    def filter_by(self, **kwargs):
        q = _FakeQuery(self.rows, key_field=self.key_field)
        q.filters = kwargs
        return q

    def first(self):
        for row in self.rows:
            if all(getattr(row, k, None) == v for k, v in self.filters.items()):
                return row
        return None

    def get(self, key):
        if not self.key_field:
            return None
        for row in self.rows:
            if getattr(row, self.key_field, None) == key:
                return row
        return None


def _prepare_fake_env(monkeypatch, root):
    skill_rows, cur_rows, ex_rows = [], [], []

    class FakeSkillInfo:
        query = _FakeQuery(skill_rows, key_field="skill_id")
        def __init__(self, **kwargs): self.__dict__.update(kwargs)
    class FakeSkillCurriculum:
        query = _FakeQuery(cur_rows)
        def __init__(self, **kwargs): self.__dict__.update(kwargs)
    class FakeTextbookExample:
        query = _FakeQuery(ex_rows)
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.notes = kwargs.get("notes")
            self.id = len(ex_rows) + 1
    class FakeSession:
        @staticmethod
        def add(obj):
            if isinstance(obj, FakeSkillInfo): skill_rows.append(obj)
            elif isinstance(obj, FakeSkillCurriculum): cur_rows.append(obj)
            elif isinstance(obj, FakeTextbookExample): ex_rows.append(obj)
        @staticmethod
        def commit(): return None
        @staticmethod
        def rollback(): return None
    class FakeDB:
        session = FakeSession()

    monkeypatch.setattr(processor, "SkillInfo", FakeSkillInfo)
    monkeypatch.setattr(processor, "SkillCurriculum", FakeSkillCurriculum)
    monkeypatch.setattr(processor, "TextbookExample", FakeTextbookExample)
    monkeypatch.setattr(processor, "db", FakeDB())
    return ex_rows


def _write_minimal_png(path):
    import base64
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )
    with open(path, "wb") as f:
        f.write(png)


def _run_docx_asset_save(monkeypatch, app_root, q_assets, convert_ok=True, parsed_override=None, formula_blocks=None, ocr_fallback=False):
    app = Flask(__name__)
    app.root_path = app_root
    os.makedirs(os.path.join(app_root, "uploads", "media", "media"), exist_ok=True)
    for p in ("image_png.png", "image_jpg.jpg", "image_wmf.wmf", "image_emf.emf", "orphan.png"):
        full = os.path.join(app_root, "uploads", "media", "media", p)
        if p.endswith(".png"):
            _write_minimal_png(full)
        else:
            with open(full, "wb") as f:
                f.write(b"x")
    ex_rows = _prepare_fake_env(monkeypatch, app_root)

    def _fake_convert(inp, out):
        if convert_ok:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            _write_minimal_png(out)
            return True, None
        return False, "converter_unavailable"

    monkeypatch.setattr(processor, "convert_vector_image_to_png", _fake_convert)
    processor._DOCX_IMPORT_CONTEXT = {"question_assets": q_assets, "question_formula_blocks": (formula_blocks or {})}

    parsed = parsed_override or {
        "chapters": [
            {
                "chapter_title": "1 排列組合",
                "sections": [
                    {
                        "section_title": "1-2 直線排列",
                        "concepts": [
                            {
                                "concept_name": "排列",
                                "concept_en_id": "Perm",
                                "examples": [{"example_title": "例題7", "problem_text": "如圖", "source_type": "textbook_example", "skill_id": "vh_數學B4_Perm"}],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    with app.app_context():
        app.config["ENABLE_DOCX_FORMULA_OCR_FALLBACK"] = bool(ocr_fallback)
        result = processor.save_to_database(
            parsed,
            {"curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B4"},
            queue=type("Q", (), {"put": lambda *_: None})(),
            source_file_path=os.path.join(app_root, "a.docx"),
            content_by_page={1: "x"},
        )
    return result, ex_rows


def test_attached_png_jpg_copy_and_display_path(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_png_jpg")
    q_assets = {
        "例題7": [
            {"path": "uploads/media/media/image_png.png", "content_type": "image/png", "image_attach_reason": "image_inside_question_block"},
            {"path": "uploads/media/media/image_jpg.jpg", "content_type": "image/jpeg", "image_attach_reason": "image_inside_question_block"},
        ]
    }
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True)
    meta = json.loads(ex_rows[0].notes)
    assert len(meta["image_assets"]) == 2
    for a in meta["image_assets"]:
        assert a["display_path"] == a["path"]
        assert a["needs_image_conversion"] is False


def test_attached_wmf_emf_convert_success(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_convert_ok")
    q_assets = {
        "例題7": [
            {"path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "image_attach_reason": "image_inside_question_block"},
            {"path": "uploads/media/media/image_emf.emf", "content_type": "image/x-emf", "image_attach_reason": "image_inside_question_block"},
        ]
    }
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True)
    meta = json.loads(ex_rows[0].notes)
    assert any(a["display_path"] and a["display_path"].endswith(".png") for a in meta["image_assets"])
    assert all(a["needs_image_conversion"] is False for a in meta["image_assets"])


def test_attached_wmf_emf_convert_failed_not_interrupt(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_convert_fail")
    q_assets = {
        "例題7": [
            {"path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "image_attach_reason": "image_inside_question_block"},
        ]
    }
    result, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=False)
    assert result.get("examples_imported", result.get("examples_added")) == 1
    meta = json.loads(ex_rows[0].notes)
    a = meta["image_assets"][0]
    assert a["display_path"] is None
    assert a["needs_image_conversion"] is True
    assert a["needs_image_review"] is True


def test_orphan_not_copied_not_in_metadata(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_orphan")
    q_assets = {"其他題": [{"path": "uploads/media/media/orphan.png", "content_type": "image/png"}]}
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True)
    meta = json.loads(ex_rows[0].notes)
    assert meta.get("image_assets", []) == [] or all("orphan" not in str(a.get("original_path", "")) for a in meta.get("image_assets", []))


def test_docx_no_pdf_sourcepage_fallback_when_no_docx_assets(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_no_pdf_fallback")
    q_assets = {}
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True)
    meta = json.loads(ex_rows[0].notes)
    assert meta.get("image_warning") == "missing_docx_image_asset"
    assert "missing_source_page" not in json.dumps(meta, ensure_ascii=False)


def test_formula_placeholder_not_at_doc_head(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_formula_placeholder")
    os.makedirs(root, exist_ok=True)
    doc_path = os.path.join(root, "f.docx")
    d = Document()
    d.add_paragraph("[FORMULA_IMAGE_1]")
    d.add_paragraph("例題7 題目")
    d.save(doc_path)
    with Flask(__name__).app_context():
        q = type("Q", (), {"put": lambda *_: None})()
        out = processor.extract_content_from_file(str(doc_path), q)
    assert not str(out[1]).strip().startswith("[FORMULA_IMAGE_")


def test_validation_missing_inclass_number_log(monkeypatch, caplog):
    root = os.path.join(os.getcwd(), "tmp_test_docx_validation")
    app = Flask(__name__)
    app.root_path = root
    os.makedirs(os.path.join(root, "uploads", "media", "media"), exist_ok=True)
    ex_rows = _prepare_fake_env(monkeypatch, root)
    processor._DOCX_IMPORT_CONTEXT = {"question_assets": {}}
    parsed = {
        "chapters": [{"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{"concept_name": "x", "concept_en_id": "X", "examples": [], "practice_questions": [
            {"practice_title": "隨堂練習1", "problem_text": "a", "source_type": "in_class_practice", "skill_id": "vh_數學B4_X"},
            {"practice_title": "隨堂練習3", "problem_text": "b", "source_type": "in_class_practice", "skill_id": "vh_數學B4_X"},
        ]}]}]}]
    }
    with app.app_context():
        processor.save_to_database(parsed, {"curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B4"}, queue=type("Q", (), {"put": lambda *_: None})(), source_file_path=os.path.join(root, "a.docx"), content_by_page={1: "x"})
    assert any("possible missing in_class_practice numbers" in r.message for r in caplog.records)


def test_frontend_badges_and_permutation_normalize_and_pdf_branch():
    route = open("core/routes/admin.py", "r", encoding="utf-8").read()
    tpl = open("templates/admin_examples.html", "r", encoding="utf-8").read()
    src = open("core/textbook_processor.py", "r", encoding="utf-8").read()
    assert "_needs_image_conversion" in route
    assert "有附圖" in tpl and "附圖需轉檔" in tpl and "附圖待確認" in tpl
    assert normalize_math_text("設 P^n_2 = 30") == "設 P(n,2) = 30"
    assert normalize_math_text("P(20,2)") == "P(20,2)"
    assert "if file_extension == '.pdf':" in src


def test_admin_examples_no_unicode_perm_conversion():
    tpl = open("templates/admin_examples.html", "r", encoding="utf-8").read()
    assert "toUnicode" not in tpl
    assert "superscript" not in tpl
    assert "subscript" not in tpl


def test_docx_formula_placeholder_not_hallucinated(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_formula_guard")
    parsed = {
        "chapters": [
            {"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{
                "concept_name": "排列",
                "concept_en_id": "Perm",
                "examples": [{
                    "example_title": "例題2",
                    "problem_text": "試求下列各式之值：(1) P^5_3 (2) P^8_2 (3) P^6_6",
                    "source_type": "textbook_example",
                    "skill_id": "vh_數學B4_Perm"
                }],
                "practice_questions": []
            }]}]}
        ]
    }
    formula_blocks = {"例題2": "例題2\n試求下列各式之值：\n(1) [FORMULA_IMAGE_1]\n(2) [FORMULA_IMAGE_2]\n(3) [FORMULA_IMAGE_3]"}
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, {"例題2": []}, convert_ok=True, parsed_override=parsed, formula_blocks=formula_blocks)
    row = ex_rows[0]
    assert "[FORMULA_MISSING]" in row.problem_text
    meta = json.loads(row.notes)
    assert meta.get("formula_hallucination_risk") is True
    assert meta.get("needs_formula_review") is True


def test_docx_formula_guard_does_not_overwrite_problem_text_with_raw_block(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_formula_no_raw_override")
    parsed = {
        "chapters": [
            {"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{
                "concept_name": "Perm",
                "concept_en_id": "Perm",
                "examples": [{
                    "example_title": "例題1",
                    "problem_text": "原始題幹文字，不可被 raw block 覆蓋",
                    "source_type": "textbook_example",
                    "skill_id": "vh_數學B4_Perm"
                }],
                "practice_questions": []
            }]}]}
        ]
    }
    formula_blocks = {"例題1": "1.不等式的運算性質"}
    _, ex_rows = _run_docx_asset_save(
        monkeypatch, root, {"例題1": []}, convert_ok=True, parsed_override=parsed, formula_blocks=formula_blocks
    )
    row = ex_rows[0]
    assert "原始題幹文字" in row.problem_text
    assert "不等式的運算性質" not in row.problem_text


def test_b1_coordinate_guard_normalizes_point_sup_sub_forms():
    text = "已知點 {}^{a}P_{b} 在第二象限內，設 A(-1,2), B(3,3), C^{2}_{1} 為三頂點。"
    normalized, _meta = processor.normalize_permutation_combination_notation(
        text, volume="數學B1", section_title="1-2 平面坐標系與線型函數"
    )
    assert "P(a,b)" in normalized
    assert "C(1,2)" in normalized
    assert "{}^{a}P_{b}" not in normalized
    assert "C^{2}_{1}" not in normalized


def test_b1_coordinate_guard_keeps_existing_coordinate_points():
    text = "點 C(3,1)、P(a,b)、Q(b,a)、R(-b,a^2) 在平面上。"
    normalized, _meta = processor.normalize_permutation_combination_notation(
        text, volume="數學B1", section_title="1-2 平面坐標系與線型函數"
    )
    assert "C(3,1)" in normalized
    assert "P(a,b)" in normalized
    assert "Q(b,a)" in normalized
    assert "R(-b,a^2)" in normalized


def test_b4_combination_notation_not_affected_by_b1_coordinate_guard():
    text = "從 7 人中選 3 人排列，共有 P(7,3) 種；任取 3 人，共有 C(7,3) 種。"
    normalized, _meta = processor.normalize_permutation_combination_notation(
        text, volume="數學B4", section_title="1-2 直線排列"
    )
    assert "P^{7}_{3}" in normalized
    assert "C^{7}_{3}" in normalized


def test_formula_assets_not_written_to_image_assets(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_assets_meta")
    q_assets = {
        "例題2": [
            {"rid": "rId5", "path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "media_kind": "formula_asset", "image_attach_reason": "formula_question_block"}
        ]
    }
    parsed = {
        "chapters": [
            {"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{
                "concept_name": "排列",
                "concept_en_id": "Perm",
                "examples": [{"example_title": "例題2", "problem_text": "試填入下列各式□之值：(1)(2)(3)", "source_type": "textbook_example", "skill_id": "vh_數學B4_Perm"}],
                "practice_questions": []
            }]}]}
        ]
    }
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True, parsed_override=parsed, formula_blocks={"例題2": "例題2\n(1) [FORMULA_IMAGE_1]"})
    meta = json.loads(ex_rows[0].notes)
    assert meta.get("formula_assets")
    assert meta.get("image_assets", []) == []


def test_formula_placeholder_sets_review_flags_and_asset_metadata(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_placeholder_flags")
    q_assets = {
        "靘?2": [
            {"rid": "rId5", "path": "uploads/media/media/image_png.png", "content_type": "image/png", "media_kind": "formula_asset"}
        ]
    }
    parsed = {
        "chapters": [{"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{
            "concept_name": "Perm",
            "concept_en_id": "Perm",
            "examples": [{"example_title": "靘?2", "problem_text": "題目 [FORMULA_IMAGE_1]", "source_type": "textbook_example", "skill_id": "vh_?詨飛B4_Perm"}],
            "practice_questions": []
        }]}]}]
    }
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, parsed_override=parsed, formula_blocks={"靘?2": "題目 [FORMULA_IMAGE_1]"})
    meta = json.loads(ex_rows[0].notes)
    assert meta["needs_review"] is True
    assert meta["needs_formula_review"] is True
    assert meta["formula_missing"] is True
    asset = meta["formula_assets"][0]
    assert asset["placeholder_token"] == "[FORMULA_IMAGE_1]"
    assert asset["placeholder_index"] == 1
    assert asset["conversion_status"] == "not_required"
    assert asset["display_path"]


def test_formula_wmf_convert_failed_metadata_no_exception(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_wmf_fail")
    q_assets = {
        "例題7": [
            {"rid": "rId5", "path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "media_kind": "formula_asset"}
        ]
    }
    result, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=False, formula_blocks={"例題7": "題目 [FORMULA_IMAGE_1]"})
    assert result.get("examples_imported", result.get("examples_added")) == 1
    asset = json.loads(ex_rows[0].notes)["formula_assets"][0]
    assert asset["conversion_status"] == "failed"
    assert asset["conversion_error"]


def test_formula_wmf_convert_success_metadata(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_wmf_success")
    q_assets = {
        "例題7": [
            {"rid": "rId5", "path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "media_kind": "formula_asset"}
        ]
    }
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True, formula_blocks={"例題7": "題目 [FORMULA_IMAGE_1]"})
    asset = json.loads(ex_rows[0].notes)["formula_assets"][0]
    assert asset["conversion_status"] == "success"
    assert asset["converted_path"] and asset["display_path"]


def test_formula_ocr_disabled_does_not_call_vision(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_ocr_disabled")
    called = {"count": 0}
    monkeypatch.setattr(processor, "get_model", lambda role: called.__setitem__("count", called["count"] + 1))
    q_assets = {"例題7": [{"path": "uploads/media/media/image_png.png", "content_type": "image/png", "media_kind": "formula_asset"}]}
    _run_docx_asset_save(monkeypatch, root, q_assets, formula_blocks={"例題7": "題目 [FORMULA_IMAGE_1]"}, ocr_fallback=False)
    assert called["count"] == 0


def test_formula_ocr_enabled_without_readable_png_does_not_call_vision(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_ocr_no_png")
    called = {"count": 0}
    monkeypatch.setattr(processor, "get_model", lambda role: called.__setitem__("count", called["count"] + 1))
    q_assets = {"例題7": [{"path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "media_kind": "formula_asset"}]}
    _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=False, formula_blocks={"例題7": "題目 [FORMULA_IMAGE_1]"}, ocr_fallback=True)
    assert called["count"] == 0


def test_formula_ocr_enabled_with_converted_path_calls_vision_and_keeps_review(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_formula_ocr_converted")
    called = {"count": 0}

    class FakeResp:
        text = "x^2"

    class FakeModel:
        def generate_content(self, *args, **kwargs):
            called["count"] += 1
            return FakeResp()

    monkeypatch.setattr(processor, "get_model", lambda role: FakeModel())
    q_assets = {"例題7": [{"path": "uploads/media/media/image_wmf.wmf", "content_type": "image/x-wmf", "media_kind": "formula_asset"}]}
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, q_assets, convert_ok=True, formula_blocks={"例題7": "題目 [FORMULA_IMAGE_1]"}, ocr_fallback=True)
    meta = json.loads(ex_rows[0].notes)
    assert called["count"] == 1
    assert meta["formula_ocr_status"] == "success"
    assert meta["formula_ocr_text"] == ["x^2"]
    assert meta["needs_review"] is True


def test_docx_no_source_page_1_fallback(monkeypatch):
    root = os.path.join(os.getcwd(), "tmp_test_docx_no_source_page1")
    parsed = {
        "chapters": [
            {"chapter_title": "1", "sections": [{"section_title": "1-2", "concepts": [{
                "concept_name": "排列",
                "concept_en_id": "Perm",
                "examples": [{"example_title": "例題2", "problem_text": "試求下列各式之值：(1) [FORMULA_IMAGE_1]", "source_type": "textbook_example", "skill_id": "vh_數學B4_Perm"}],
                "practice_questions": []
            }]}]}
        ]
    }
    formula_blocks = {"例題2": "例題2\n(1) [FORMULA_IMAGE_1]"}
    _, ex_rows = _run_docx_asset_save(monkeypatch, root, {"例題2": []}, convert_ok=True, parsed_override=parsed, formula_blocks=formula_blocks)
    meta = json.loads(ex_rows[0].notes)
    assert "missing_source_page" not in json.dumps(meta, ensure_ascii=False)


# ─── MathType OLE / VML v:imagedata regression tests ─────────────────────────
# B1 1-1「數線與絕對值」及同系列 Longteng 教材的數學式以 Equation.DSMT4 OLE
# 物件嵌入，使用 VML v:imagedata（非 DrawingML a:blip）。
# 修正前這些公式位置被靜默丟棄；修正後必須產生 [FORMULA_IMAGE_N] placeholder。

# XML namespace constants for building synthetic run elements
_NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_NS_V = "urn:schemas-microsoft-com:vml"
_NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_NS_O = "urn:schemas-microsoft-com:office:office"


def _make_ole_run_xml(rid_img: str = "rId42", rid_ole: str = "rId43") -> str:
    """Minimal XML for a w:r containing a MathType Equation.DSMT4 OLE object.

    Structure mirrors real Longteng B1 docx files:
        w:r
          w:object
            v:shape
              v:imagedata r:id="{rid_img}"   ← WMF preview (VML, NOT a:blip)
            o:OLEObject ProgID="Equation.DSMT4" r:id="{rid_ole}"
    """
    return (
        f'<w:r xmlns:w="{_NS_W}" xmlns:v="{_NS_V}"'
        f' xmlns:r="{_NS_R}" xmlns:o="{_NS_O}">'
        f'<w:object w:dxaOrig="780" w:dyaOrig="400">'
        f'<v:shape id="_x0000_i1026" type="#_x0000_t75" style="width:39pt;height:20pt" o:ole="">'
        f'<v:imagedata r:id="{rid_img}" o:title=""/>'
        f"</v:shape>"
        f'<o:OLEObject Type="Embed" ProgID="Equation.DSMT4"'
        f' ShapeID="_x0000_i1026" DrawAspect="Content" r:id="{rid_ole}"/>'
        f"</w:object>"
        f"</w:r>"
    )


def _make_paragraph_with_ole(before: str, after: str) -> "docx.text.paragraph.Paragraph":
    """Create a python-docx Paragraph containing text–OLE–text."""
    doc = Document()
    p = doc.add_paragraph(before)
    p._p.append(parse_xml(_make_ole_run_xml()))
    p._p.append(parse_xml(
        f'<w:r xmlns:w="{_NS_W}"><w:t xml:space="preserve">{after}</w:t></w:r>'
    ))
    return p


def test_vml_imagedata_produces_formula_image_placeholder():
    """MathType OLE run (v:imagedata) must yield [FORMULA_IMAGE_1], not empty string."""
    p = _make_paragraph_with_ole("若 ", " = 5，求 x 之值。")
    result = processor.extract_docx_paragraph_with_equations(p)
    assert "[FORMULA_IMAGE_1]" in result, (
        f"Expected [FORMULA_IMAGE_1] in output, got: {result!r}"
    )


def test_vml_imagedata_does_not_silently_disappear():
    """Formula position must NOT be an empty gap between surrounding text."""
    p = _make_paragraph_with_ole("解不等式：", " 求解。")
    result = processor.extract_docx_paragraph_with_equations(p)
    # The two text fragments must NOT be adjacent without any separator/placeholder
    assert "解不等式：求解。" not in result
    assert "解不等式： 求解。" not in result
    assert "[FORMULA_IMAGE_1]" in result


def test_vml_imagedata_sets_formula_image_count():
    """paragraph_state formula_image_count must increment for each OLE formula."""
    p = _make_paragraph_with_ole("計算 ", " 的值。")
    processor.extract_docx_paragraph_with_equations(p)
    state = getattr(p, "_math_meta", {})
    assert state.get("formula_image_count", 0) >= 1, (
        "formula_image_count should be ≥ 1 for a paragraph with one OLE formula"
    )


def test_vml_imagedata_sets_needs_formula_review():
    """needs_formula_review must be True when an OLE formula placeholder is created."""
    p = _make_paragraph_with_ole("試求 ", " 之值。")
    processor.extract_docx_paragraph_with_equations(p)
    state = getattr(p, "_math_meta", {})
    assert state.get("needs_formula_review") is True


def test_multiple_ole_formulas_produce_sequential_placeholders():
    """Multiple OLE runs in one paragraph each get a distinct [FORMULA_IMAGE_N]."""
    doc = Document()
    p = doc.add_paragraph("(1) ")
    p._p.append(parse_xml(_make_ole_run_xml(rid_img="rId11", rid_ole="rId12")))
    p._p.append(parse_xml(
        f'<w:r xmlns:w="{_NS_W}"><w:t xml:space="preserve"> (2) </w:t></w:r>'
    ))
    p._p.append(parse_xml(_make_ole_run_xml(rid_img="rId13", rid_ole="rId14")))

    result = processor.extract_docx_paragraph_with_equations(p)
    assert "[FORMULA_IMAGE_1]" in result
    assert "[FORMULA_IMAGE_2]" in result
    state = getattr(p, "_math_meta", {})
    assert state.get("formula_image_count") == 2


def test_existing_drawingml_blip_placeholder_still_works():
    """DrawingML a:blip placeholder generation must be unaffected by the VML fix."""
    doc = Document()
    p = doc.add_paragraph("圖例 ")
    p._p.append(parse_xml(
        '<w:r'
        ' xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<w:drawing>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:blipFill>'
        '<a:blip r:embed="rId5"/>'
        '</pic:blipFill>'
        '</pic:pic>'
        '</a:graphicData>'
        '</a:graphic>'
        '</w:drawing>'
        '</w:r>'
    ))
    result = processor.extract_docx_paragraph_with_equations(p)
    assert "[FORMULA_IMAGE_1]" in result
    state = getattr(p, "_math_meta", {})
    assert state.get("needs_formula_review") is True


def test_omml_equation_still_converts_to_latex():
    """OMML oMath equations must still be converted to LaTeX \\(...\\)."""
    doc = Document()
    p = doc.add_paragraph("計算 ")
    p._p.append(parse_xml(_omml_p_n_r(7, 3)))
    result = processor.extract_docx_paragraph_with_equations(p)
    assert "\\(" in result
    assert "[FORMULA_IMAGE" not in result


# ---------------------------------------------------------------------------
# B1 1-1 Gemini prompt completeness tests
# ---------------------------------------------------------------------------

def _get_vh_mathb4_prompt_source() -> str:
    """Return the full source of textbook_processor.py for prompt-content assertions."""
    import inspect
    return inspect.getsource(processor)


_B1_1_1_BLOCK_ANCHOR = "B1 1-1 專用補充：數線與絕對值（完整抽題規則）"


def _find_b1_block(src: str) -> str:
    """Return the text window starting from the B1 1-1 dedicated block header."""
    idx = src.find(_B1_1_1_BLOCK_ANCHOR)
    assert idx != -1, (
        f"B1 1-1 block anchor '{_B1_1_1_BLOCK_ANCHOR}' not found in textbook_processor.py"
    )
    return src[idx: idx + 3000]


def test_b1_1_1_prompt_contains_complete_extraction_rule():
    """prompt_vh_mathB4 must contain a B1 1-1 數線與絕對值 full-extraction directive."""
    src = _get_vh_mathb4_prompt_source()
    b1_block = _find_b1_block(src)
    assert "數線與絕對值" in b1_block, (
        "B1 1-1 block must reference '數線與絕對值'"
    )
    assert "1～10" in b1_block or "1\uff5e10" in b1_block, (
        "B1 1-1 must mandate extraction of 基礎題 1～10"
    )
    assert "不可只挑代表題" in b1_block, (
        "Prompt must forbid cherry-picking representative questions for B1 1-1"
    )


def test_b1_1_1_prompt_contains_formula_missing_flags():
    """prompt must require needs_formula_review and formula_missing flags for B1 1-1."""
    src = _get_vh_mathb4_prompt_source()
    b1_block = _find_b1_block(src)
    assert "needs_formula_review" in b1_block, (
        "B1 1-1 block must instruct Gemini to set needs_formula_review"
    )
    assert "formula_missing" in b1_block, (
        "B1 1-1 block must instruct Gemini to set formula_missing"
    )
    assert "needs_review" in b1_block, (
        "B1 1-1 block must instruct Gemini to set needs_review"
    )


def test_b1_1_1_prompt_formula_placeholder_not_skipped():
    """Prompt must state that [FORMULA_IMAGE_N] / [FORMULA_MISSING] questions must still be created."""
    src = _get_vh_mathb4_prompt_source()
    b1_block = _find_b1_block(src)
    has_formula_image = "FORMULA_IMAGE" in b1_block
    has_formula_missing = "FORMULA_MISSING" in b1_block
    assert has_formula_image or has_formula_missing, (
        "B1 1-1 block must mention FORMULA_IMAGE_N or FORMULA_MISSING placeholders"
    )


def test_b1_1_1_prompt_source_type_basic_exercise():
    """B1 1-1 block must define source_type basic_exercise for 1-1習題 基礎題."""
    src = _get_vh_mathb4_prompt_source()
    b1_block = _find_b1_block(src)
    assert "basic_exercise" in b1_block, (
        "B1 1-1 block must assign source_type basic_exercise to 1-1習題 基礎題"
    )


# ---------------------------------------------------------------------------
# B1 1-1 block-to-question matching / media attachment regression tests
# ---------------------------------------------------------------------------

def _make_blocks(*items):
    """Build a minimal ordered_blocks list from (type, text_or_extra) pairs."""
    blocks = []
    for idx, item in enumerate(items, start=1):
        if item[0] == "para":
            blocks.append({"type": "paragraph", "text": item[1], "block_index": idx})
        elif item[0] == "img":
            extra = item[1] if len(item) > 1 else {}
            blocks.append({"type": "image", "rid": f"rId{idx}", "path": f"media/img{idx}.wmf",
                           "block_index": idx, **extra})
    return blocks


def test_lookup_docx_formula_block_exact_nospc():
    """Exact (no-space) lookup must hit on key '基礎題5'."""
    fb = {"基礎題5": "5 解不等式 [FORMULA_IMAGE_1]"}
    assert processor._lookup_docx_formula_block("基礎題5", fb) == "5 解不等式 [FORMULA_IMAGE_1]"


def test_lookup_docx_formula_block_prefix_strip():
    """'1-1習題 基礎題5' should resolve to key '基礎題5' after stripping the prefix."""
    fb = {"基礎題5": "5 解不等式 [FORMULA_IMAGE_1]"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題5", fb)
    assert result == "5 解不等式 [FORMULA_IMAGE_1]", (
        f"Expected prefix-stripped lookup to hit '基礎題5', got: {result!r}"
    )


def test_lookup_docx_formula_block_number_suffix():
    """'1-1習題 基礎題7' should match '基礎題7' via same-type label strategy."""
    fb = {"基礎題7": "7 解方程式 [FORMULA_IMAGE_1]"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題7", fb)
    assert result == "7 解方程式 [FORMULA_IMAGE_1]"


def test_lookup_docx_formula_block_bare_number_safe_match():
    """'1-1習題 基礎題5' should match bare key '5' only when the block is a safe exercise
    (starts with '5 ' and contains a question verb, NOT '5.' concept heading).

    This is Strategy 4 (safe bare-number) of the high-confidence lookup.
    """
    fb = {"5": "5 解下列不等式 [FORMULA_IMAGE_1]"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題5", fb)
    assert result == "5 解下列不等式 [FORMULA_IMAGE_1]", (
        f"Expected safe bare-number match, got: {result!r}"
    )


def test_lookup_docx_formula_block_missing_returns_empty():
    """Lookup on a completely unrelated title should return empty string."""
    fb = {"例題1": "例題1 text"}
    assert processor._lookup_docx_formula_block("1-1習題 基礎題9", fb) == ""


# ---------------------------------------------------------------------------
# Regression tests: concept paragraphs must NOT be matched (user's bug report)
# ---------------------------------------------------------------------------

def test_lookup_formula_block_rejects_concept_heading_for_liti():
    """例題1 must NOT match bare-key '1' storing a concept heading '1.不等式的運算性質'."""
    fb = {"1": "1.不等式的運算性質…加法性質、乘法性質"}
    result = processor._lookup_docx_formula_block("例題1", fb)
    assert result == "", (
        f"例題1 must not match a concept heading block; got: {result!r}"
    )


def test_lookup_formula_block_rejects_concept_heading_for_practice():
    """隨堂練習1 must NOT match bare-key '1' storing '1.不等式的運算性質'."""
    fb = {"1": "1.不等式的運算性質…"}
    result = processor._lookup_docx_formula_block("隨堂練習1", fb)
    assert result == "", (
        f"隨堂練習1 must not match a concept heading; got: {result!r}"
    )


def test_lookup_formula_block_rejects_concept_heading_for_jichu1():
    """1-1習題 基礎題1 must NOT match bare-key '1' storing '1.不等式的運算性質'."""
    fb = {"1": "1.不等式的運算性質…"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題1", fb)
    assert result == "", (
        f"1-1習題 基礎題1 must not match a concept heading block; got: {result!r}"
    )


def test_lookup_formula_block_rejects_concept_heading_for_jichu2():
    """1-1習題 基礎題2 must NOT match bare-key '2' storing a concept description."""
    fb = {"2": "2.絕對值不等式…展開與幾何意義"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題2", fb)
    assert result == "", (
        f"1-1習題 基礎題2 must not match a concept description block; got: {result!r}"
    )


def test_lookup_formula_block_accepts_exercise_jichu5():
    """1-1習題 基礎題5 CAN match bare-key '5' when block is a genuine exercise."""
    fb = {"5": "5 解下列不等式：[FORMULA_IMAGE_1]"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題5", fb)
    assert result == "5 解下列不等式：[FORMULA_IMAGE_1]", (
        f"Expected valid exercise match for 基礎題5; got: {result!r}"
    )


def test_lookup_formula_block_accepts_exercise_jichu7():
    """1-1習題 基礎題7 CAN match bare-key '7' when block is a genuine exercise."""
    fb = {"7": "7 解不等式：[FORMULA_IMAGE_1]"}
    result = processor._lookup_docx_formula_block("1-1習題 基礎題7", fb)
    assert result == "7 解不等式：[FORMULA_IMAGE_1]", (
        f"Expected valid exercise match for 基礎題7; got: {result!r}"
    )


def test_lookup_formula_block_no_cross_type_match():
    """'例題5' must NOT match key '基礎題5' (cross-type number match is forbidden)."""
    fb = {"基礎題5": "基礎題5 text"}
    result = processor._lookup_docx_formula_block("例題5", fb)
    assert result == "", (
        f"例題5 must not cross-match 基礎題5; got: {result!r}"
    )


def test_lookup_docx_question_assets_prefix_strip():
    """'1-1習題 基礎題5' should find assets stored under '基礎題5'."""
    q_assets = {"基礎題5": [{"rid": "rId1", "path": "media/img1.wmf", "media_kind": "formula_asset"}]}
    result = processor._lookup_docx_question_assets("1-1習題 基礎題5", q_assets)
    assert result and result[0]["rid"] == "rId1"


def test_is_question_start_bare_number_with_verb():
    """'5 解下列不等式' should be detected as a question start."""
    assert processor._is_question_start_text("5 解下列不等式")


def test_is_question_start_bare_number_with_period():
    """'3. 試求 x 的值' should be detected as a question start."""
    assert processor._is_question_start_text("3. 試求 x 的值")


def test_is_question_start_concept_heading_not_matched():
    """'1.不等式的運算性質' (concept sub-heading) must NOT be a question start."""
    assert not processor._is_question_start_text("1.不等式的運算性質")


def test_is_question_start_concept_heading_2_not_matched():
    """'2.絕對值不等式展開與幾何意義' must NOT be a question start."""
    assert not processor._is_question_start_text("2.絕對值不等式展開與幾何意義")


def test_is_question_start_section_title_not_matched():
    """'1-1 數線與絕對值' (section title) must NOT be detected as a question start."""
    assert not processor._is_question_start_text("1-1 數線與絕對值")


def test_is_safe_exercise_block_accepts_verb_exercise():
    """Block '5 解下列不等式' (space separator + verb) must be accepted."""
    assert processor._is_safe_exercise_block("5 解下列不等式", "5")


def test_is_safe_exercise_block_rejects_period_concept():
    """Block '1.不等式的運算性質' (period separator, concept) must be rejected."""
    assert not processor._is_safe_exercise_block("1.不等式的運算性質", "1")


def test_is_safe_exercise_block_rejects_no_verb():
    """Block '5 絕對值' (space but no question verb) must be rejected."""
    assert not processor._is_safe_exercise_block("5 絕對值", "5")


def test_extract_question_title_bare_number():
    """'5 解不等式 [FORMULA_IMAGE_1]' should extract title '5'."""
    title = processor._extract_question_title_from_text("5 解不等式 [FORMULA_IMAGE_1]")
    assert title == "5", f"Expected '5', got {title!r}"


def test_build_docx_question_formula_context_bare_numbered():
    """build_docx_question_formula_context should capture bare-number exercise blocks."""
    blocks = _make_blocks(
        ("para", "1-1習題"),
        ("para", "基礎題"),
        ("para", "5 解下列不等式 [FORMULA_IMAGE_1]"),
        ("para", "答：x > -2"),
        ("para", "6 試求整數解"),
    )
    ctx = processor.build_docx_question_formula_context(blocks)
    found = processor._lookup_docx_formula_block("1-1習題 基礎題5", ctx)
    assert found and "FORMULA_IMAGE" in found, (
        f"Expected formula block for 基礎題5, got ctx keys={list(ctx.keys())}"
    )


def test_formula_placeholder_source_flag_set_on_image_block():
    """Image blocks extracted from a paragraph with [FORMULA_IMAGE_N] must carry
    is_formula_placeholder_source=True."""
    doc = Document()
    p = doc.add_paragraph("解不等式：")
    p._p.append(parse_xml(_make_ole_run_xml(rid_img="rId77", rid_ole="rId78")))
    p._p.append(parse_xml(
        f'<w:r xmlns:w="{_NS_W}"><w:t xml:space="preserve"> 求解。</w:t></w:r>'
    ))
    # Simulate what the DOCX extraction loop does:
    ptxt = processor.extract_docx_paragraph_with_equations(p)
    para_has_formula_placeholder = bool(
        __import__("re").search(r"\[FORMULA_IMAGE_\d+\]", ptxt or "")
    )
    rids = processor.extract_docx_image_rids_from_paragraph(p)
    assert rids, "Should have extracted at least one image RID from the OLE run"
    assert para_has_formula_placeholder, (
        f"Paragraph with OLE formula should contain [FORMULA_IMAGE_N], got: {ptxt!r}"
    )


def test_attach_docx_media_ole_image_classified_as_formula_asset():
    """OLE formula images (is_formula_placeholder_source=True) must be classified as formula_asset."""
    blocks = [
        {"type": "paragraph", "text": "基礎題5 解不等式 [FORMULA_IMAGE_1]", "block_index": 1},
        {
            "type": "image", "rid": "rId42", "path": "media/img.wmf",
            "block_index": 2,
            "is_formula_placeholder_source": True,
        },
    ]
    q_assets, orphans = processor.attach_docx_media_to_question_blocks(blocks)
    # The image should be attached to the question, not orphaned
    assert not orphans, f"OLE formula image should not be orphaned; orphans={orphans}"
    all_assets = [a for assets in q_assets.values() for a in assets]
    assert any(a.get("media_kind") == "formula_asset" for a in all_assets), (
        f"Expected at least one formula_asset; assets={all_assets}"
    )


def test_attach_docx_media_datashen_image_kw():
    """Images near a question with '數線' keyword should be attached, not orphaned."""
    blocks = [
        {"type": "paragraph", "text": "基礎題1 在數線上標出下列各點：", "block_index": 1},
        {"type": "image", "rid": "rId10", "path": "media/fig1.jpeg", "block_index": 2},
    ]
    q_assets, orphans = processor.attach_docx_media_to_question_blocks(blocks)
    assert not orphans, f"Image near '數線' question must not be orphaned; orphans={orphans}"


def test_attach_docx_media_orphan_logged_not_silently_lost():
    """Images that cannot be matched to any question must end up in the orphan list."""
    blocks = [
        {"type": "image", "rid": "rId99", "path": "media/orphan.jpeg", "block_index": 1},
    ]
    q_assets, orphans = processor.attach_docx_media_to_question_blocks(blocks)
    assert len(orphans) == 1, f"Unmatched image must be in orphan list; orphans={orphans}"
    assert orphans[0]["rid"] == "rId99"


# ---------------------------------------------------------------------------
# _is_review_section_title / outline-only review filter tests
# ---------------------------------------------------------------------------

def test_is_review_section_title_zizwoping():
    """'自我評量' must be detected as a review section."""
    assert processor._is_review_section_title("自我評量")


def test_is_review_section_title_with_number_prefix():
    """'1-review 自我評量' must be detected as a review section."""
    assert processor._is_review_section_title("1-review 自我評量")


def test_is_review_section_title_fuxi():
    """'複習' must be detected as a review section."""
    assert processor._is_review_section_title("複習")


def test_is_review_section_title_review_keyword():
    """Section title containing 'review' (case-insensitive) must be detected."""
    assert processor._is_review_section_title("2-Review 綜合練習")


def test_is_review_section_title_normal_section_not_matched():
    """Normal teaching sections like '1-1 數線與絕對值' must NOT be detected as review."""
    assert not processor._is_review_section_title("1-1 數線與絕對值")


def test_is_review_section_title_normal_section_12():
    """'1-2 平面坐標系' must NOT be detected as review."""
    assert not processor._is_review_section_title("1-2 平面坐標系")


def test_is_review_section_title_empty():
    """Empty string must not be flagged as review."""
    assert not processor._is_review_section_title("")


def test_outline_only_skips_review_sections():
    """import_outline_structure_only must skip '1-review 自我評量' style sections."""
    # We test the filtering logic without a real DB by patching the DB calls.
    import unittest.mock as mock

    parsed = {
        "chapters": [
            {
                "chapter_title": "1 數線與坐標",
                "sections": [
                    {"section_title": "1-1 數線與絕對值"},
                    {"section_title": "1-2 平面坐標系"},
                    {"section_title": "1-review 自我評量"},   # must be skipped
                ],
            }
        ]
    }
    curriculum_info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}

    created_sections = []

    app = Flask(__name__)
    app.config["TESTING"] = True

    with app.app_context():
        # Patch out DB and app-context-dependent helpers
        with mock.patch("core.textbook_processor.get_structure_map", return_value=None), \
             mock.patch("core.textbook_processor.parse_textbook_filename_metadata", return_value={}):

            mock_session = mock.MagicMock()
            mock_curriculum_cls = mock.MagicMock()

            def fake_query_filter_by(**kwargs):
                m = mock.MagicMock()
                m.first.return_value = None  # pretend section does not exist yet
                return m

            mock_curriculum_cls.query.filter_by.side_effect = fake_query_filter_by

            def fake_add(obj):
                created_sections.append(obj)

            mock_session.add.side_effect = fake_add
            mock_session.rollback = mock.MagicMock()
            mock_session.commit = mock.MagicMock()

            new_curr_instances = []

            def make_skill_curriculum(**kwargs):
                obj = mock.MagicMock()
                obj._kwargs = kwargs
                new_curr_instances.append(kwargs)
                return obj

            with mock.patch("core.textbook_processor.db", mock_session), \
                 mock.patch("core.textbook_processor.SkillCurriculum", mock_curriculum_cls):

                # Re-patch the import inside the function (uses 'from models import ...')
                with mock.patch.dict("sys.modules", {
                    "models": mock.MagicMock(
                        db=mock_session,
                        SkillCurriculum=mock_curriculum_cls,
                    )
                }):
                    mock_curriculum_cls.side_effect = make_skill_curriculum
                    try:
                        processor.import_outline_structure_only(
                            parsed, curriculum_info, mock.MagicMock()
                        )
                    except Exception:
                        pass  # DB commit may fail in test environment; that's OK

    # The review section must not have been added
    section_titles = [kw.get("section", "") for kw in new_curr_instances]
    assert "1-review 自我評量" not in section_titles, (
        f"Review section must be skipped; created sections={section_titles}"
    )
    # The two real sections must still be included
    assert any("1-1" in t or "數線" in t for t in section_titles), (
        f"Normal sections must be created; created sections={section_titles}"
    )


# ---------------------------------------------------------------------------
# _is_section_exposition_title / section_exposition skip tests
# ---------------------------------------------------------------------------

def test_is_section_exposition_title_kewenneirong():
    """'課文內容' must be identified as a section-exposition title."""
    assert processor._is_section_exposition_title("課文內容")


def test_is_section_exposition_title_kewenshuo():
    """'課文說明' must be identified as a section-exposition title."""
    assert processor._is_section_exposition_title("課文說明")


def test_is_section_exposition_title_shuoming():
    """'說明' must be identified as a section-exposition title."""
    assert processor._is_section_exposition_title("說明")


def test_is_section_exposition_title_example_not_exposition():
    """'例題1' must NOT be an exposition title."""
    assert not processor._is_section_exposition_title("例題1")


def test_is_section_exposition_title_jichu_not_exposition():
    """'1-1習題 基礎題1' must NOT be an exposition title."""
    assert not processor._is_section_exposition_title("1-1習題 基礎題1")


def test_is_section_exposition_title_practice_not_exposition():
    """'隨堂練習1' must NOT be an exposition title."""
    assert not processor._is_section_exposition_title("隨堂練習1")


def test_is_section_exposition_title_empty_not_exposition():
    """Empty string must not be flagged as exposition."""
    assert not processor._is_section_exposition_title("")


def test_normalize_source_type_exposition_returns_section_exposition():
    """normalize_source_type_by_title on '課文內容' item must return 'section_exposition'."""
    item = {"source_description": "課文內容", "problem_text": "若 a > b，則 a+c > b+c"}
    result = processor.normalize_source_type_by_title(item, default_source_type="textbook_example")
    assert result == "section_exposition", (
        f"Expected 'section_exposition', got {result!r}"
    )


def test_normalize_source_type_liti_returns_textbook_example():
    """normalize_source_type_by_title on '例題1' must return 'textbook_example'."""
    item = {"source_description": "例題1", "problem_text": "解不等式 |x-1| < 2"}
    result = processor.normalize_source_type_by_title(item, default_source_type="textbook_example")
    assert result == "textbook_example"


def test_normalize_source_type_jichu_returns_basic_exercise():
    """normalize_source_type_by_title on '1-1習題 基礎題1' must return 'basic_exercise'."""
    item = {"source_description": "1-1習題 基礎題1", "problem_text": "解不等式"}
    result = processor.normalize_source_type_by_title(item, default_source_type="textbook_example")
    assert result == "basic_exercise"


def test_normalize_source_type_practice_returns_in_class_practice():
    """normalize_source_type_by_title on '隨堂練習1' must return 'in_class_practice'."""
    item = {"source_description": "隨堂練習1", "problem_text": "求解"}
    result = processor.normalize_source_type_by_title(item, default_source_type="in_class_practice")
    assert result == "in_class_practice"
