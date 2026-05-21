from core.textbook_processor import safe_load_gemini_json


def test_safe_load_gemini_json_repairs_latex_single_backslashes():
    raw = r'''
{
  "solution": "由公式可得 \(C_1^9 + C_3^9 + C_5^9 = 2^{9-1}\)。",
  "formula": "\binom{n}{r} = \frac{n!}{r!(n-r)!} \times 2"
}
'''

    data = safe_load_gemini_json(raw)

    assert data["solution"] == r"由公式可得 \(C_1^9 + C_3^9 + C_5^9 = 2^{9-1}\)。"
    assert data["formula"] == r"\binom{n}{r} = \frac{n!}{r!(n-r)!} \times 2"


def test_safe_load_gemini_json_preserves_valid_json_latex_escapes():
    raw = r'''
{
  "formula": "\\binom{n}{r} = \\frac{n!}{r!(n-r)!}",
  "solution": "\\((x+1)^5 = \\sum_{r=0}^{5} \\binom{5}{r}x^{5-r}\\)"
}
'''

    data = safe_load_gemini_json(raw)

    assert data["formula"] == r"\binom{n}{r} = \frac{n!}{r!(n-r)!}"
    assert data["solution"] == r"\((x+1)^5 = \sum_{r=0}^{5} \binom{5}{r}x^{5-r}\)"


def test_safe_load_gemini_json_handles_textbook_structure_case():
    raw = r'''
{
  "chapters": [
    {
      "chapter_title": "1 排列組合",
      "sections": [
        {
          "section_title": "1-5 二項式定理",
          "concepts": [
            {
              "concept_name": "二項式定理",
              "examples": [
                {
                  "problem": "展開 \((x+1)^5\)。",
                  "solution": "利用二項式定理：\((x+1)^5 = \sum_{r=0}^{5} \binom{5}{r}x^{5-r}\)。"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
'''

    data = safe_load_gemini_json(raw)
    solution = data["chapters"][0]["sections"][0]["concepts"][0]["examples"][0]["solution"]

    assert solution == r"利用二項式定理：\((x+1)^5 = \sum_{r=0}^{5} \binom{5}{r}x^{5-r}\)。"


def test_call_gemini_for_analysis_safety_cleaning(monkeypatch):
    import core.textbook_processor as processor
    from flask import Flask

    class DummyQueue:
        def __init__(self):
            self.messages = []
        def put(self, msg):
            self.messages.append(msg)

    captured_prompt = None

    def fake_get_model(name=None):
        return "fake_model"

    def fake_call_gemini_with_retry(model, prompt, queue, context_message="", parse_json=True):
        nonlocal captured_prompt
        captured_prompt = prompt
        return {"chapters": []}

    monkeypatch.setattr(processor, "get_model", fake_get_model)
    monkeypatch.setattr(processor, "_call_gemini_with_retry", fake_call_gemini_with_retry)

    # \u2160 is Ⅰ, \uff0d is － (full-width hyphen), \uff1d is ＝ (full-width equal), \u2460 is ①, \u201c and \u201d are “ and ”
    content_by_page = {
        "1": "例題\u2160：\u201c試求 2\uff0d1\uff1d1。\u201d\n\n\n\n\n\n\u2460 第一小題。\n\n\n\n\n\n||\n"
    }
    curriculum_info = {"curriculum": "vocational", "grade": 10, "volume": "數學B4"}

    app = Flask(__name__)
    with app.app_context():
        processor.call_gemini_for_analysis(content_by_page, curriculum_info, DummyQueue())

    assert captured_prompt is not None
    # Extract the full_content section from prompt
    content_part = captured_prompt.split("【以下是需要您切分、LaTeX化並結構化解析的課本標準文本內容】\n")[-1]
    # Check that full-width minus got replaced: '－' -> '-'
    assert '"試求 2-1＝1。"' in content_part
    assert "I" in content_part  # 'Ⅰ' becomes 'I'
    assert "(1)" in content_part  # '①' becomes '(1)'
    assert "\n\n\n" not in content_part  # Multiple newlines compressed inside full_content

