# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "core" / "routes" / "analysis.py"
text = path.read_text(encoding="utf-8")
marker = "ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}"
idx = text.find(marker)
if idx == -1:
    raise SystemExit("marker missing")

header = '''# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/analysis.py

說明 (Description):
  練習與測驗相關之 AI 分析路由：手寫辨識／批改、Chat AI 對話、考卷影像分析等。

用法 (Usage):
  由 Flask 應用程式註冊 blueprint 後載入。

版本 (Version): V2.0
日期 (Date): 2026-01-13
維護者 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, render_template, current_app, url_for, session
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

import os
import base64
import re
import tempfile
import uuid
import traceback

from . import core_bp, practice_bp
from core.session import get_current
from config import Config
from core.ai_analyzer import (
    build_chat_prompt,
    get_chat_response,
    analyze,
    diagnose_error,
    diversify_follow_up_prompts,
    build_dynamic_follow_up_prompts_variant,
    clean_and_parse_json,
    enforce_strict_mode,
)
from core.ai_client import call_ai, call_google_model
from core.adaptive.judge import (
    judge_answer_with_feedback,
    _as_symbolic_tolerant,
    _normalize_math_text,
    _parse_quotient_remainder,
    _symbolic_equal,
    _extract_divisor_from_question,
)
from core.exam_analyzer import analyze_exam_image, save_analysis_result
from core.diagnosis_analyzer import perform_weakness_analysis
from core.rag_engine import rag_search, rag_chat
from models import db, MistakeNotebookEntry, ExamAnalysis, SkillInfo


'''

new_text = header + text[idx:]
path.write_text(new_text, encoding="utf-8")
print("header ok", len(new_text))
