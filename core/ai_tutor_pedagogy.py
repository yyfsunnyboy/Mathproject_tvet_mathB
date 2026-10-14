"""Shared pedagogical contract for every AI Tutor surface (JH / GH / VH).

The rules here are curriculum-agnostic: they describe how to teach, never
which formula a particular skill uses.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

FULL_SOLUTION_MARKERS = (
    "直接告訴我答案", "告訴我答案", "給我答案", "答案是什麼", "看答案",
    "完整解答", "完整算一次", "完整解法", "完整過程", "完整步驟", "整題算給我", "詳解",
)

_INTENT_MARKERS = (
    ("full_solution", FULL_SOLUTION_MARKERS),
    ("where_wrong", ("哪裡錯", "錯在哪", "哪裡不對", "哪一步錯", "為什麼錯")),
    ("check_work", ("對嗎", "對不對", "有沒有錯", "檢查", "正確嗎", "可以嗎", "這樣寫")),
    ("why_step", ("為什麼", "為何", "怎麼來的", "怎麼得到")),
    ("next_step", ("下一步", "接下來", "然後呢")),
    ("formula_definition", ("公式", "定義", "是什麼", "什麼意思", "意思是", "代表什麼", "性質")),
    ("simpler", ("簡單一點", "聽不懂", "看不懂", "白話", "再說一次", "換個方式", "不太懂", "不懂")),
    ("next_step", ("不知道", "卡住", "怎麼做", "怎麼算", "從哪裡開始", "怎麼開始")),
)

INTENT_LABELS = {
    "full_solution": "要求完整解答",
    "where_wrong": "問哪裡錯",
    "check_work": "請你檢查手寫",
    "simpler": "要更簡單的解釋",
    "why_step": "問某一步為什麼",
    "formula_definition": "問公式／定義／概念",
    "next_step": "不知道下一步",
    "general": "一般提問",
}

_INTENT_INSTRUCTIONS = {
    "full_solution": "依步驟寫出完整解答，每一步都寫算式，最後寫答案。",
    "where_wrong": (
        "逐行驗算【學生目前已寫的內容】，只指出第一個你實際驗算出錯的行：引用該行、說錯在哪個數字或符號、寫出正確的那一行。"
        "若每一行驗算後都正確，要明確說「目前寫的步驟都正確」，再說還差哪一步，不可編造錯誤。"
    ),
    "check_work": (
        "逐行檢查【學生目前已寫的內容】：正確的行要引用並明確說正確；錯的行說錯在哪裡與正確寫法；"
        "若全部正確但還沒完成，說已經完成到哪裡（例如已求出的量），再給下一步的具體公式與代入式。"
    ),
    "simpler": "用更短、更白話的方式重講上一輪的重點，並配一個本題的具體算式或數字例子。",
    "why_step": "第一句直接說原因（引用本題的條件或數字），再說這個原因讓下一步要寫什麼算式。",
    "formula_definition": (
        "第一句直接寫出學生問的公式或定義（用 LaTeX），簡短說明每個符號的意思；"
        "接著連到本題：把題目條件或學生已算出的結果代入，寫出代入後的算式。"
    ),
    "next_step": (
        "先用一句話肯定學生已完成且正確的部分（若有），再給一個具體下一步：要用的公式或規則，以及代入本題數字後的算式。"
    ),
    "general": "先直接回答學生這一句，再給一個具體下一步算式。",
}

TUTOR_PEDAGOGICAL_CONTRACT = """【共用教學契約（所有課程共用；與上方較舊的風格規則衝突時，以本契約為準）】
1. 先確認：先自行逐行驗算【學生目前已寫的內容】。驗算正確的步驟要明確肯定並引用該行；沒有指出具體錯誤行與原因時，不可暗示學生錯了。
2. 系統提供的 [structured_analysis]、status、main_issue、error_mechanism 只比對最後一行，可能只是「還沒算完」；不可直接當作學生犯錯的證據。
3. 錯誤要具體：只有你實際驗算出錯的那一行才可說錯，並說明錯在哪個數字或符號、正確應寫成什麼。
4. 下一步要具體：給出要用的公式、規則或算式（含本題數字），讓學生能直接寫下一行。禁止只說「再想一想」「從第一步重新檢查」「哪裡不對呢」「試試看下一步」這類沒有數學內容的句子。
5. 直接回答：學生問公式、定義、概念或某一步為什麼時，第一句就直接回答，不可只用反問代替回答；之後再連結本題與學生先前的手寫。
6. 可檢查的數學：每次回覆至少包含一個具體公式、算式、推理步驟或本題的數字例子；數學式用 $...$ 包住的 LaTeX。
7. 辨識不確定：若某個符號看不清楚，直接說是哪一行的哪個符號看不清楚，請學生確認；不可假設學生寫錯。
8. 最後答案：依【本題教學輪次】決定。第 1、2 輪不可寫出本題完整最終答案（含移項、通分、約分後的任何等價寫法）；第 3 輪起只有學生明確要求時才寫。一般公式與部分代入的算式可以寫；學生自己已寫出的正確答案可以直接肯定。
9. 回覆 2 到 8 行，像老師對學生說話，不要提到系統、JSON 或欄位名稱。"""

SUGGESTED_QUESTION_RULES = """suggested_questions 規則（恰好 3 題）：
- 依「學生目前解題進度」與本次 reply 的下一步生成，像學生接著會問的話，每題以問號結尾、不超過 28 個中文字。
- 3 題各聚焦不同面向：①照 reply 的下一步去做時會卡住的具體操作（例如代入、計算哪一部分）；②reply 中用到的公式、定義或符號的意思；③如何檢查這一步或結果是否合理。
- 必須含本題的具體量或步驟名稱，不可是「為什麼要這樣做？」這類放到任何題目都成立的空泛問題。
- 不得重複學生剛問過的問題，不得使用「問題1／觀察／聯想／執行」等標籤，未要求完整解答時不得寫出最後答案。"""


def classify_tutor_intent(text: str) -> str:
    value = str(text or "")
    for intent, markers in _INTENT_MARKERS:
        if any(marker in value for marker in markers):
            return intent
    return "general"


FULL_SOLUTION_MIN_ROUND = 3

TEACHING_ROUND_RULES = {
    1: (
        "第 1 輪：診斷學生目前的作答。肯定並引用正確的步驟，具體指出錯在哪個數字或符號，"
        "提供需要的公式、定義或方向，再給一個學生可以立刻寫下的小步驟。"
        "學生問公式或定義時，直接寫出一般公式。不可寫出本題完整最終答案。"
    ),
    2: (
        "第 2 輪：承接第 1 輪的手寫與對話，先說學生這次改對了什麼、還差什麼，不要重複第 1 輪的說法。"
        "給更具體的示範：可以寫出部分代入與中間步驟，但至少保留一個關鍵步驟讓學生自己完成。"
        "不可寫出本題完整最終答案。"
    ),
    3: (
        "第 3 輪起：學生明確要求完整解答時，依步驟寫出完整推導與最終答案；"
        "學生只要求下一步或提示時，只給下一步，不主動公布最終答案。"
    ),
}


def full_solution_allowed(teaching_round: int, intent: str) -> bool:
    return int(teaching_round or 1) >= FULL_SOLUTION_MIN_ROUND and intent == "full_solution"


def teaching_round_block(teaching_round: int, intent: str) -> str:
    round_no = max(1, int(teaching_round or 1))
    rule = TEACHING_ROUND_RULES[min(round_no, FULL_SOLUTION_MIN_ROUND)]
    if full_solution_allowed(round_no, intent):
        disclosure = "允許：學生已明確要求完整解答，請寫出完整推導與最終答案。"
    elif intent == "full_solution":
        disclosure = (
            f"不允許：學生要求完整解答，但完整解答從第 {FULL_SOLUTION_MIN_ROUND} 輪起才提供。"
            "先用一句話說明，再給本輪允許的最具體提示；不可寫出本題完整最終答案或其等價寫法。"
        )
    else:
        disclosure = "不允許：不可寫出本題完整最終答案或其等價寫法（顯示前會再檢查）。"
    return (
        f"【本題教學輪次】第 {round_no} 輪（依同一題已完成的教學回覆計算，手寫檢查與文字追問共用；"
        "上方任何「寫出答案」的指示與本段衝突時，以本段為準）\n"
        f"{rule}\n【本輪答案揭露】{disclosure}"
    )


def tutor_intent_block(text: str, teaching_round: int | None = None) -> str:
    intent = classify_tutor_intent(text)
    instruction = _INTENT_INSTRUCTIONS[intent]
    if intent == "full_solution" and teaching_round is not None and not full_solution_allowed(teaching_round, intent):
        instruction = _INTENT_INSTRUCTIONS["next_step"]
    block = f"【本輪意圖】{INTENT_LABELS[intent]}\n【本輪回覆方式】{instruction}"
    if teaching_round is None:
        return block
    return f"{block}\n{teaching_round_block(teaching_round, intent)}"


def enforce_teaching_round_disclosure(reply: str, *, correct_answer: Any, teaching_round: int,
                                      intent: str, student_work: str = "",
                                      answer_items: Iterable[Any] | None = None) -> tuple[str, bool]:
    """Redact final-answer math that this round may not show; returns (reply, redacted)."""
    from core.ai_tutor_disclosure import find_answer_disclosure, redact_answer_disclosure

    if full_solution_allowed(teaching_round, intent):
        return reply, False
    finding = find_answer_disclosure(
        reply, correct_answer, student_work=student_work, answer_items=answer_items
    )
    if not finding.disclosed:
        return reply, False
    return redact_answer_disclosure(reply, finding), True


_LATEX_ESCAPE_DAMAGE = (
    ("\x0c", "\\f"),
    ("\x08", "\\b"),
)
_LATEX_AFTER_TAB = re.compile(r"\t(?=(?:imes|heta|au|ext|frac|an|riangle|o\b|op)\b)")
_LATEX_AFTER_CR = re.compile(r"\r(?=(?:ight|ho|angle|m)\b)")
_LATEX_AFTER_NL = re.compile(r"\n(?=(?:eq|abla|ot|e|ewline)(?![A-Za-z]))")


def repair_latex_escape_damage(text: str) -> str:
    """Undo JSON escapes that ate a LaTeX command (``\\frac`` parsed as form feed)."""
    if not isinstance(text, str):
        return text
    for damaged, latex in _LATEX_ESCAPE_DAMAGE:
        text = text.replace(damaged, latex)
    text = _LATEX_AFTER_TAB.sub(r"\\t", text)
    text = _LATEX_AFTER_CR.sub(r"\\r", text)
    return _LATEX_AFTER_NL.sub(r"\\n", text)


_LATEX_TO_PLAIN = (
    (r"\\left|\\right|\\displaystyle|\$", ""),
    (r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)"),
    (r"\\(?:times|cdot)|×|·", "*"),
    (r"÷", "/"),
    (r"\\(?:leq|le)\b", "≤"),
    (r"\\(?:geq|ge)\b", "≥"),
    (r"\\(?:neq|ne)\b", "≠"),
    (r"[{}\s]|\\[,;!]", ""),
    (r"[（]", "("),
    (r"[）]", ")"),
    (r"＝", "="),
)
_QUOTE_STOP = re.compile(r"[\u4e00-\u9fff，、；：。？！,;]")


def _plain_math(value: str) -> str:
    text = str(value or "")
    for pattern, repl in _LATEX_TO_PLAIN:
        text = re.sub(pattern, repl, text)
    return text.replace("(", "").replace(")", "")


def quoted_math_is_unseen(fragment: str, student_work: str) -> bool:
    """True when the math right after「你寫了…」never appears in the recognized work.

    LaTeX vs. plain notation and parentheses are ignored, so a faithful quote such
    as ``$\\frac{3+(-1)}{2}=1$`` of ``(3+(-1))/2 = 1`` is not treated as invented.
    """
    head = _QUOTE_STOP.split(str(fragment or "").strip(" ：:「」\"'"), 1)[0]
    quoted = _plain_math(head)
    if not re.search(r"[0-9A-Za-z]", quoted):
        return False
    return quoted not in _plain_math(student_work)


__all__ = [
    "FULL_SOLUTION_MARKERS",
    "FULL_SOLUTION_MIN_ROUND",
    "INTENT_LABELS",
    "SUGGESTED_QUESTION_RULES",
    "TEACHING_ROUND_RULES",
    "TUTOR_PEDAGOGICAL_CONTRACT",
    "classify_tutor_intent",
    "enforce_teaching_round_disclosure",
    "full_solution_allowed",
    "quoted_math_is_unseen",
    "repair_latex_escape_damage",
    "teaching_round_block",
    "tutor_intent_block",
]
