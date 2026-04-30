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


def _run_docx_asset_save(monkeypatch, app_root, q_assets, convert_ok=True, parsed_override=None, formula_blocks=None):
    app = Flask(__name__)
    app.root_path = app_root
    os.makedirs(os.path.join(app_root, "uploads", "media", "media"), exist_ok=True)
    for p in ("image_png.png", "image_jpg.jpg", "image_wmf.wmf", "image_emf.emf", "orphan.png"):
        with open(os.path.join(app_root, "uploads", "media", "media", p), "wb") as f:
            f.write(b"x")
    ex_rows = _prepare_fake_env(monkeypatch, app_root)

    def _fake_convert(inp, out):
        if convert_ok:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as f:
                f.write(b"png")
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
        app.config["ENABLE_DOCX_FORMULA_OCR_FALLBACK"] = False
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
    assert result["examples_imported"] == 1
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
