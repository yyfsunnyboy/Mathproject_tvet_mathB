"""Teacher analysis "最近練習紀錄": display-only math copies (all curricula, never written back)."""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from core.attempt_math_display import answer_display, question_summary, repair_display_text

ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = ROOT / "static" / "js" / "math_display_normalizer.js"


# --- historical control-character damage (display copy only) ---------------

@pytest.mark.parametrize("raw,shown", [
    ("x \\ge 2 \text{ or } x \\le -6", "x \\ge 2 \\text{ or } x \\le -6"),
    ("\frac{1}{2}", "\\frac{1}{2}"),
    ("\\left|x\right|", "\\left|x\\right|"),
    ("a \neq b", "a \\neq b"),
    ("3 \times 4", "3 \\times 4"),
])
def test_recognisable_latex_damage_is_restored_for_display(raw, shown):
    assert repair_display_text(raw) == (shown, "repaired")


def test_unrecognisable_control_characters_are_marked_not_guessed():
    shown, status = repair_display_text("x\tq 3")
    assert status == "uncertain"
    assert shown == "x\ufffdq 3"


def test_clean_and_multiline_text_is_unchanged():
    assert repair_display_text("第一行\n第二行 \\frac{1}{2}") == ("第一行\n第二行 \\frac{1}{2}", "clean")
    assert repair_display_text("a\r\nb") == ("a\nb", "clean")


# --- answer cells -----------------------------------------------------------

def _texts(raw):
    return [(part["label"], part["text"]) for part in answer_display(raw)["parts"]]


def test_multi_part_answers_are_split_in_part_order():
    raw = json.dumps({"part_2": "3/4", "part_1": "-5/4", "part_3": "", "part_4": "不存在"}, ensure_ascii=False)
    assert _texts(raw) == [("(1)", "-5/4"), ("(2)", "3/4"), ("(3)", "未作答"), ("(4)", "不存在")]
    assert _texts('{"part_1": "63"}') == [("", "63")]
    assert _texts('["A", "C"]') == [("(1)", "A"), ("(2)", "C")]


@pytest.mark.parametrize("raw", [
    "[1, 2]", "[-29/2,7/2]", "{x | x > 3}", "{1, 2, 3}", "(-\\infty,-4]\\cup[4,\\infty)",
    "\\frac{a}{b}", "\\sqrt{x^2+y^2}", "\\left|x\\right|", "x\\geq3", "A", "B", "C", "D",
])
def test_math_and_choice_answers_are_one_unchanged_part(raw):
    assert _texts(raw) == [("", raw)]


def test_blank_answer_has_no_parts():
    assert answer_display(None)["parts"] == [] and answer_display("  ")["parts"] == []


# --- question summary -------------------------------------------------------

def test_long_question_is_not_cut_inside_a_math_span():
    text = "已知" + "甲" * 100 + " $\\left| 3x - a \\right| < 12$ 之解為 $b < x < 2$，求點所在象限。"
    shown = question_summary(text)["text"]
    assert shown.endswith("…")
    assert shown.count("$") % 2 == 0
    assert "\\left|" not in shown or "\\right|" in shown


def test_long_bare_latex_is_not_cut_inside_braces():
    shown = question_summary("說明" * 58 + "求 \\frac{12345}{67890} 的值")["text"]
    assert shown.count("{") == shown.count("}")


# --- route: all curricula, three fields, XSS, DB untouched ------------------

UNITS = {
    "junior_high": ("數學1上", "第1章 整數", "jh_test_math_display"),
    "general_high": ("數學1", "第1章 數與式", "gh_test_math_display"),
    "vocational": ("數學B1", "2 直線方程式", "vh_test_math_display"),
}
ROWS = [
    ("若不等式 $\\left| 3x - a \\right| < 12$ 之解為 $b < x < 2$", "x \\ge 2 \text{ or } x \\le -6", "(-\\infty,-4]\\cup[4,\\infty)"),
    ("求 \\frac{2}{3} 與 \\sqrt{x^2+y^2}", '{"part_1": "-5/4", "part_2": "x\\\\geq3"}', '{"part_1": "-1", "part_2": "x\\\\geq3"}'),
    ("選出正確選項", "<img src=x onerror=alert(1)>", "D"),
    ("求區間", "[-29/2,7/2]", "{x | x > 3}"),
]


@pytest.fixture()
def teacher_app(tmp_path):
    import config as config_module
    from app import create_app
    from models import Class, ClassStudent, PracticeAttempt, SkillCurriculum, SkillInfo, User, db

    previous = config_module.Config.SQLALCHEMY_DATABASE_URI
    db_path = tmp_path / f"teacher_math_{uuid.uuid4().hex[:8]}.db"
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.session.add_all([
                User(id=501, username="math_teacher", password_hash="x", role="teacher"),
                User(id=601, username="math_student", password_hash="x", role="student"),
                Class(id=51, name="數學班", teacher_id=501, class_code="MATH5151"),
            ])
            db.session.flush()
            db.session.add(ClassStudent(class_id=51, student_id=601))
            now = datetime.utcnow()
            for curriculum, (volume, chapter, skill_id) in UNITS.items():
                db.session.add(SkillInfo(skill_id=skill_id, skill_en_name=skill_id, skill_ch_name=f"技能 {curriculum}",
                                         description="d", gemini_prompt="p"))
                db.session.add(SkillCurriculum(skill_id=skill_id, curriculum=curriculum, grade=1, volume=volume,
                                               chapter=chapter, section="1-1", display_order=1))
                for index, (question, answer, expected) in enumerate(ROWS):
                    db.session.add(PracticeAttempt(
                        student_id=601, skill_id=skill_id, question_text=question, user_answer=answer,
                        expected_answer=expected, is_correct=False, source="general_practice",
                        problem_type_id="type-a", created_at=now - timedelta(minutes=index),
                    ))
            db.session.commit()
        yield app
    finally:
        config_module.Config.SQLALCHEMY_DATABASE_URI = previous


@pytest.mark.parametrize("curriculum", sorted(UNITS))
def test_recent_attempts_render_display_copies_for_every_curriculum(teacher_app, curriculum):
    from models import PracticeAttempt

    volume, chapter, skill_id = UNITS[curriculum]
    client = teacher_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "501"
        sess["_fresh"] = True
    response = client.get("/teacher/analysis", query_string={
        "class_id": 51, "student_id": 601, "volume": volume, "chapter": chapter})
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    table = page[page.index('id="recent-attempts"'):page.index("</table>", page.index('id="recent-attempts"'))]

    assert "startup: { typeset: false }" in page
    assert "math_display_normalizer.js" in page
    assert page.index('id="recent-attempts"') < page.index("typesetMathDisplay(document.getElementById('recent-attempts'))")
    assert table.count('data-math-display="text"') == len(ROWS)
    cells = [html.unescape(m) for m in re.findall(r'data-math-display="answer">([^<]*)<', table)]
    assert "x \\ge 2 \\text{ or } x \\le -6" in cells
    assert "(-\\infty,-4]\\cup[4,\\infty)" in cells
    assert "-5/4" in cells and "x\\geq3" in cells and "D" in cells
    assert "[-29/2,7/2]" in cells and "{x | x > 3}" in cells
    assert '<span class="part-label">(2)</span>' in table
    assert "<img" not in table and "&lt;img src=x onerror=alert(1)&gt;" in table
    assert "\t" not in table
    assert "$\\left| 3x - a \\right| &lt; 12$" in table

    with teacher_app.app_context():
        stored = {row.user_answer for row in PracticeAttempt.query.filter_by(skill_id=skill_id)}
    assert "x \\ge 2 \text{ or } x \\le -6" in stored


def test_other_teacher_views_do_not_load_mathjax(teacher_app):
    client = teacher_app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = "501"
        sess["_fresh"] = True
    page = client.get("/teacher/analysis", query_string={"class_id": 51}).get_data(as_text=True)
    assert "tex-svg.js" not in page


# --- shared normalizer (Node) -------------------------------------------------

def _node() -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    return node


def _run(function: str, values: list[str]) -> list[str]:
    script = (
        "const n=require(process.argv[1]);"
        f"process.stdout.write(JSON.stringify(JSON.parse(process.argv[2]).map(v=>n.{function}(v))));"
    )
    completed = subprocess.run(
        [_node(), "-e", script, str(NORMALIZER), json.dumps(values, ensure_ascii=False)],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(completed.stdout)


def test_answer_math_gets_one_span_and_choices_stay_text():
    assert _run("normalizeAnswerText", [
        "\\frac{a}{b}", "\\sqrt{x^2+y^2}", "\\left|x\\right|", "x \\leq 3", "x\\geq3", "\\infty",
        "(-\\infty,-4]\\cup[4,\\infty)", "[-29/2,7/2]", "-7/2<X<13/2", "{x | x > 3}", "$\\frac{1}{2}$",
    ]) == [
        "\\(\\frac{a}{b}\\)", "\\(\\sqrt{x^2+y^2}\\)", "\\(\\left|x\\right|\\)", "\\(x \\leq 3\\)", "\\(x\\geq3\\)",
        "\\(\\infty\\)", "\\((-\\infty,-4]\\cup[4,\\infty)\\)", "\\([-\\frac{29}{2},\\frac{7}{2}]\\)",
        "\\(-\\frac{7}{2}<X<\\frac{13}{2}\\)", "\\(\\{x | x > 3\\}\\)", "$\\frac{1}{2}$",
    ]
    plain = ["A", "B", "C", "D", "(B)", "37", "不存在", "m不存在", "none", "<img src=x onerror=alert(1)>"]
    assert _run("normalizeAnswerText", plain) == plain


def test_question_text_wraps_only_math_never_chinese():
    assert _run("normalizeQuestionText", [
        "若不等式 $\\left| 3x - a \\right| < 12$ 之解為 $b < x < 2$",
        "求 \\frac{2}{3} 與 \\sqrt{x^2+y^2}。",
        "（答案範例：任意實數/無解/ -1<x<3）",
    ]) == [
        "若不等式 $\\left| 3x - a \\right| < 12$ 之解為 $b < x < 2$",
        "求 \\(\\frac{2}{3}\\) 與 \\(\\sqrt{x^2+y^2}\\)。",
        "（答案範例：任意實數/無解/ -1<x<3）",
    ]


def test_display_typeset_is_normalized_once_and_serialized():
    source = NORMALIZER.read_text(encoding="utf-8")
    start = source.index("function typesetMathDisplay(root)")
    body = source[start:source.index("\n  }\n", start)]
    assert 'element.dataset.mathNormalized === "1"' in body
    assert "element.textContent = normalized" in body and "innerHTML" not in body
    assert "typesetSerialized(root, true)" in body
