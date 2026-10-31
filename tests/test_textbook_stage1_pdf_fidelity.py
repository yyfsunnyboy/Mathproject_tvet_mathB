import json
from types import SimpleNamespace

from core.textbook_stage1_auto_review import _chinese, _pdf_fidelity


def _row(stem, page, order):
    notes = {"pdf_visual_enrichment": {"page": page},
             "question_anchor": {"source_order": order}}
    return SimpleNamespace(problem_text=stem, notes=json.dumps(notes))


def _check(row, rows, texts, blocks):
    return _pdf_fidelity(row, json.loads(row.notes), [_chinese(t) for t in texts], texts, blocks, rows)


def test_short_math_stem_requires_the_correct_local_formula():
    row = _row("求下列各數：\\(C_{2}^{10}\\)。", 1, 1)
    text = "求下列各數：\nC2\n10\n求下列各數：\nC4\n10"
    blocks = [[(0, 10, 10, 20, "求下列各數："), (0, 18, 10, 25, "C2\n10"),
               (0, 100, 10, 110, "求下列各數："), (0, 108, 10, 115, "C4\n10")]]
    assert _check(row, [row], [text], blocks) == (1, "localized_chinese_and_math_tokens")
    wrong = _row("求下列各數：\\(C_{8}^{100}\\)。", 1, 1)
    assert _check(wrong, [wrong], [text], blocks) is None


def test_missing_page_uses_neighbor_bounds_and_disambiguates_formula():
    before = _row("前一題內容完整。", 1, 1)
    target = _row("寫出\\((2x-y)^4\\)的展開式。", None, 2)
    after = _row("後一題內容完整。", 2, 3)
    texts = ["寫出x\ny\n5\n+\n的展開式。",
             "寫出\nx\ny\n2\n4\n-\n的展開式。",
             "寫出\nx\ny\n2\n4\n-\n的展開式。"]
    blocks = [[(0, 10, 10, 20, texts[0])], [(0, 10, 10, 20, texts[1])],
              [(0, 10, 10, 20, texts[2])]]
    # Two nearby pages contain the same stem and formula: ambiguity must still block.
    assert _check(target, [before, target, after], texts, blocks) is None
    texts[2] = "無關頁面"
    blocks[2] = [(0, 10, 10, 20, texts[2])]
    assert _check(target, [before, target, after], texts, blocks) == (2, "localized_chinese_and_math_tokens")


def test_far_wrong_page_recovers_only_from_one_unique_stem():
    stem = "袋中有5顆大小相同的球取一球後不放回再取一球兩球是1紅球1白球。\\(\\frac{1}{3}\\)。"
    wrong = "設每球被取出的機會均等求下列各事件的機率"
    true = "袋中有5顆大小相同的球取一球後不放回再取一球兩球是1紅球1白球 1 3"
    row = _row(stem, 9, 2)
    previous = _row("前一題已在別頁。", 8, 1)
    texts = ["無關", true, "無關", wrong]
    blocks = [[(0, 10, 10, 20, text)] for text in texts]
    assert _check(row, [previous, row], texts, blocks) == (2, "unique_stem_across_pdf")
    texts[1] = true
    texts.append(true)
    blocks.append([(0, 10, 10, 20, true)])
    assert _check(row, [previous, row], texts, blocks) is None


def test_shared_phrase_alone_does_not_verify_the_stem():
    stem = "同時擲三粒公正骰子觀察所出現的點數求三粒點數均不相同。\\(\\frac{2}{9}\\)。"
    row = _row(stem, 8, 1)
    texts = ["觀察所出現的點數", "觀察所出現的點數"]
    blocks = [[(0, 10, 10, 20, text)] for text in texts]
    assert _check(row, [row], texts, blocks) is None


def test_wrong_page_recovers_only_with_chinese_and_math_evidence():
    row = _row("設n為正整數，證明：\\(C_0^n-C_1^n=0\\)。", 3, 1)
    texts = ["設n為正整數，證明：C\n0\nn\n-\nC\n1\nn\n=\n0",
             "無關頁面", "其他題目"]
    blocks = [[(0, 10, 10, 20, texts[0])], [(0, 10, 10, 20, texts[1])],
              [(0, 10, 10, 20, texts[2])]]
    assert _check(row, [row], texts, blocks) == (1, "localized_chinese_and_math_tokens")
    texts[0] = "設n為正整數，證明：C\n0\nn\n+\nC\n1\nn\n=\n0"
    blocks[0] = [(0, 10, 10, 20, texts[0])]
    assert _check(row, [row], texts, blocks) is None
