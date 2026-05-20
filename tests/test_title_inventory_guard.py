"""Phase B: Title inventory scanner vs returned title canonicalization."""

from core import textbook_processor as processor


def _sample_chapter_doc():
    """Section code 3-2 來自原文，不依題號推斷 zone。"""
    lines = [f"例{i}" for i in range(1, 9)]
    lines += [f"隨堂練習 {i}" for i in range(1, 9)]
    lines += [
        "3-2習題",
        "基礎題",
        "1 利用十字交乘法因式分解下列各式：",
        "2 解下列不等式：",
        "3 x",
        "4 x",
        "5 x",
        "6 x",
        "7 x",
        "8 最後一題基礎",
        "進階題",
        "9 已知…",
        "10 設…",
        "〔109統測B〕",
    ]
    return "\n".join(lines)


def test_scanner_zones_from_text_not_number_heuristic():
    doc = _sample_chapter_doc()
    items = processor.scan_docx_title_inventory(doc)
    ex_nums = {(it["number"], it["zone"], it["canonical_title"]) for it in items if it.get("kind") == "chapter_exercise"}
    assert ("1", "基礎題", "3-2習題 基礎題1") in ex_nums
    assert ("8", "基礎題", "3-2習題 基礎題8") in ex_nums
    assert ("9", "進階題", "3-2習題 進階題9") in ex_nums
    assert ("10", "進階題", "3-2習題 進階題10") in ex_nums


def test_map_xiti_1_and_9_via_inventory():
    doc = _sample_chapter_doc()
    items = processor.scan_docx_title_inventory(doc)
    m1 = processor.map_returned_import_title("習題 1", section_code="3-2", inventory_items=items)
    assert m1["returned_canonical"] == "3-2習題 基礎題1"
    assert m1["mapping_method"] == "exercise_context_map"
    assert m1["needs_review"] is False
    m9 = processor.map_returned_import_title("習題 9", section_code="3-2", inventory_items=items)
    assert m9["returned_canonical"] == "3-2習題 進階題9"
    assert m9["needs_review"] is False


def test_full_alignment_returned_vs_scanner_missing_zero():
    doc = _sample_chapter_doc()
    items = processor.scan_docx_title_inventory(doc)
    expected = sorted({it["canonical_title"] for it in items if it.get("canonical_title")})
    returned = (
        [f"例題 {i}" for i in range(1, 9)]
        + [f"隨堂練習 {i}" for i in range(1, 9)]
        + [f"習題 {i}" for i in range(1, 11)]
        + ["109統測B"]
    )
    inv = processor.build_title_inventory(
        expected,
        returned,
        section_code="3-2",
        inventory_items=items,
    )
    assert inv["missing_titles_count"] == 0
    assert inv["extra_titles_count"] == 0


def test_inventory_guard_remains_report_only():
    inv = processor.build_title_inventory(["例題1", "例題2"], ["例題1"], inventory_items=[])
    assert inv["missing_titles_count"] > 0
