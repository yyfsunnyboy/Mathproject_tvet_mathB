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
