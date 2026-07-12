# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/demo.py
功能說明 (Description): 公開唯讀 Demo 模式。提供未登入使用者可瀏覽的展示頁面
    （/demo, /demo/practice, /demo/teacher-overview）。所有內容皆為固定假資料，
    不讀取任何真實資料庫紀錄，也不提供任何新增/修改/刪除/發布/匯入等寫入操作。
執行語法 (Usage): 由 app.py 於 create_app() 中註冊 demo_bp
版本資訊 (Version): V1.0
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
from flask import Blueprint, render_template, jsonify, request

# 獨立的 Blueprint，刻意不重用 core_bp / practice_bp，避免與既有登入保護邏輯耦合。
demo_bp = Blueprint('demo', __name__, url_prefix='/demo', template_folder='../../templates')

DEMO_BANNER = "公開展示模式，資料修改功能已停用"

# 固定假資料：示範題目（僅供展示，非真實題庫資料）
DEMO_QUESTION = {
    'skill_ch_name': '一元一次方程式（示範題目）',
    'question_text': '解方程式：2x + 3 = 11，求 x 的值。',
    'correct_answer': '4',
    'explanation': '兩邊同減 3 得 2x = 8，再同除以 2，得 x = 4。',
}

DEMO_HINT_TEXT = (
    "示範 AI 助教：先把常數項移到等號右側，再將 x 的係數除到另一邊，就能求出 x。"
    "（此為固定展示文字，非即時 AI 回覆）"
)

# 固定假資料：教師總覽儀表板（皆為虛構姓名與數字，非真實學生資料）
DEMO_STUDENTS = [
    {'display_name': '示範學生 A', 'mastery': 82, 'completed': 24},
    {'display_name': '示範學生 B', 'mastery': 65, 'completed': 18},
    {'display_name': '示範學生 C', 'mastery': 91, 'completed': 30},
]

DEMO_MISTAKES = [
    {'question': '示範錯題：一元一次方程式應用題', 'count': 12},
    {'question': '示範錯題：分數運算化簡', 'count': 9},
    {'question': '示範錯題：絕對值不等式', 'count': 7},
]


@demo_bp.route('')
def index():
    """Demo 模式入口頁。"""
    return render_template('demo_index.html', banner=DEMO_BANNER)


@demo_bp.route('/practice', methods=['GET'])
def practice():
    """展示固定數學題目與作答流程（唯讀，僅 GET）。"""
    return render_template('demo_practice.html', banner=DEMO_BANNER, question=DEMO_QUESTION)


@demo_bp.route('/practice/check', methods=['POST'])
def practice_check():
    """展示批改流程：僅與寫死的示範題目比對，不寫入任何資料庫。"""
    payload = request.get_json(silent=True) or {}
    submitted = str(payload.get('answer', '')).strip()
    is_correct = submitted == DEMO_QUESTION['correct_answer']
    return jsonify({
        'demo_mode': True,
        'correct': is_correct,
        'correct_answer': DEMO_QUESTION['correct_answer'],
        'explanation': DEMO_QUESTION['explanation'],
        'message': DEMO_BANNER,
    })


@demo_bp.route('/practice/hint', methods=['POST'])
def practice_hint():
    """展示 AI 助教流程：回傳固定提示文字，不呼叫真實 AI 服務或資料庫。"""
    return jsonify({
        'demo_mode': True,
        'hint': DEMO_HINT_TEXT,
        'message': DEMO_BANNER,
    })


@demo_bp.route('/teacher-overview')
def teacher_overview():
    """教師總覽唯讀假資料儀表板。"""
    return render_template(
        'demo_teacher_overview.html',
        banner=DEMO_BANNER,
        students=DEMO_STUDENTS,
        mistakes=DEMO_MISTAKES,
    )
