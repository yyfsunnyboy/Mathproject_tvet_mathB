# -*- coding: utf-8 -*-







"""







=============================================================================







璅∠??迂 (Module Name): core/routes/analysis.py







?隤芣? (Description): AI ???那?瑟芋蝯?? AI ?予?拇? (Chat AI)??撖怨儘霅??銝?那??(Exam Analysis)?憿?摹暺????賬?







?瑁?隤? (Usage): ?梁頂蝯梯矽??







?鞈? (Version): V2.0







?湔?交? (Date): 2026-01-13







蝬剛風?? (Maintainer): Math AI Project Team







=============================================================================







"""















from flask import request, jsonify, render_template, current_app, url_for, session







from flask_login import current_user, login_required







from werkzeug.utils import secure_filename







import os







import uuid







import traceback















from . import core_bp, practice_bp







from core.session import get_current







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
from core.ai_wrapper import get_ai_client, call_ai_with_retry

from core.exam_analyzer import analyze_exam_image, save_analysis_result







from core.diagnosis_analyzer import perform_weakness_analysis







from core.rag_engine import rag_search, rag_chat







from models import db, MistakeNotebookEntry, ExamAnalysis, SkillInfo















ALLOWED_EXAM_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}







def allowed_exam_file(filename):







    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXAM_EXTENSIONS















# ==========================================







# AI Chat & Handwriting (AI 鈭?)







# ==========================================















@practice_bp.route('/chat_ai', methods=['POST'])







def chat_ai():







    """AI chat API."""







    data = request.get_json()







    user_question = data.get('question', '').strip()







    context = data.get('context', '')







    question_text = data.get('question_text', '')







    family_id = (data.get('family_id') or '').strip()







    question_context = (data.get('question_context') or context or '').strip()







    subskill_nodes = data.get('subskill_nodes') or []















    if not user_question:







        return jsonify({"reply": "隢撓?亙?憿?"}), 400















    current = get_current()







    skill_id = current.get("skill")







    prereq_skills = current.get('prereq_skills', [])







    if not family_id:







        family_id = (current.get('family_id') or current.get('skill') or skill_id or '').strip()







    







    full_question_context = question_text if question_text else (current.get("question") or question_context)







    







    if not skill_id and context:







        # 蝪∪?冽葫 skill_id (Fallback)







        if '擗?' in context: skill_id = 'remainder'







        elif '??' in context: skill_id = 'factor_theorem'















    full_prompt = build_chat_prompt(







        skill_id=skill_id,







        user_question=user_question,







        full_question_context=full_question_context,







        context=context,







        prereq_skills=prereq_skills







    )















    current_app.logger.info(







        "[chat_ai] received question='%s' context_head='%s'",







        user_question[:120],







        (full_question_context or '')[:120]







    )







    







    result = get_chat_response(







        full_prompt,







        user_question=user_question,







        question_context=full_question_context







    )















    # 瘥憚?寞?摮貊??嗅????蝝餈賢???嚗?摰芋?輸?銴??







    chat_state = session.get('chat_followup_state', {}) if isinstance(session.get('chat_followup_state', {}), dict) else {}







    last_prompts = chat_state.get('last_prompts', [])







    turn_index = int(chat_state.get('turn_index', 0))







    last_context = chat_state.get('last_context', '')















    if last_context != full_question_context:







        last_prompts = []







        turn_index = 0















    # 隞交頛芸飛????詨??Ｙ?蝝?內閰???頝刻憚?駁?嚗Ⅱ靽?頛芷????霈???







    per_turn_prompts = build_dynamic_follow_up_prompts_variant(







        user_question=user_question,







        question_context=full_question_context,







        ai_reply=result.get('reply', ''),







        variant=turn_index







    )







    result['follow_up_prompts'] = diversify_follow_up_prompts(







        per_turn_prompts,







        last_prompts,







        user_question=user_question,







        question_context=full_question_context,







        ai_reply=result.get('reply', ''),







        turn_index=turn_index







    )















    current_app.logger.info(







        "[chat_ai] generated follow_up_prompts=%s",







        result.get('follow_up_prompts', [])







    )















    session['chat_followup_state'] = {







        'last_prompts': result.get('follow_up_prompts', [])[:3],







        'turn_index': turn_index + 1,







        'last_question': user_question[:120],







        'last_context': full_question_context







    }















    subskill_map = {







        'sign_handling': '正負號判讀',







        'add_sub': '整數加減',







        'mul_div': '整數乘除',







        'mixed_ops': '四則混合運算',







        'absolute_value': '絕對值',







        'parentheses': '括號運算',







        'divide_terms': '分項整理',







        'conjugate_rationalize': '分母有理化',







    }







    focus_points = []







    for item in subskill_nodes:







        label = subskill_map.get(str(item), str(item).replace('_', ' '))







        if label and label not in focus_points:







            focus_points.append(label)







    if not focus_points:







        focus_points.append('先抓這一題的核心觀念')







    result['subskill_labels'] = focus_points















    result['question_text'] = question_text







    result['family_id'] = family_id







    result['question_context'] = question_context or question_text















    return jsonify(result)















@practice_bp.route('/analyze_handwriting', methods=['POST'])







@login_required







def analyze_handwriting():







    """Student diagnosis page."""







    data = request.get_json()







    img = data.get('image_data_url')







    if not img: return jsonify({"reply": "蝻箏???"}), 400







    







    state = get_current()







    prereq_skills = state.get('prereq_skills', [])
    question_text = (data.get('question_text') or state.get('question_text') or state.get('question') or "").strip()
    question_context = (data.get('question_context') or state.get('question') or "").strip()
    family_id = (data.get('family_id') or state.get('family_id') or state.get('skill') or "").strip()
    skill_labels = {
        'sign_handling': '?????',
        'add_sub': '????',
        'mul_div': '????',
        'mixed_ops': '??????',
        'absolute_value': '???',
        'parentheses': '????',
        'divide_terms': '????',
        'conjugate_rationalize': '?????',
    }
    prereq_text = ", ".join(
        f"{skill_labels.get(item.get('id'), item.get('name', item.get('id', '')))}"
        for item in prereq_skills
        if isinstance(item, dict)
    )
    prompt = (
        "You are a handwriting math assistant for Taiwanese middle school students. "
        "Analyze the whiteboard image together with the problem context. "
        "Return ONLY valid JSON, no markdown, no extra explanation. "
        "The JSON must contain keys: reply, is_process_correct, correct, next_question, follow_up_prompts, error_type. "
        "Reply in Traditional Chinese. Keep it short and helpful. "
        "Do not reveal the final answer directly. "
        "First check numbers, symbols, and operation order.\n"
        f"Problem context: {question_context or question_text}\n"
        f"Current family_id: {family_id or 'unknown'}\n"
        f"Prerequisite concepts: {prereq_text or 'none'}\n"
        "Rules:\n"
        "1. Traditional Chinese only.\n"
        "2. Short and clear for middle school students.\n"
        "3. Hint only, do not give the final answer.\n"
        "4. Focus on digits, signs, and operation order.\n"
    )
    _, b64 = img.split(',', 1)
    img_data = base64.b64decode(b64)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name
        client = get_ai_client(role='vision_analyzer')
        response = call_ai_with_retry(
            client,
            prompt,
            image_path=temp_path,
            max_retries=2,
            retry_delay=1,
            verbose=False,
        )
        raw_text = (getattr(response, 'text', '') or '').strip()
        cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
        result = clean_and_parse_json(cleaned)
        if 'reply' in result:
            result['reply'] = enforce_strict_mode(result['reply'])
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)















    # [Start of modification] Diagnosis for handwriting







    if result.get('correct') is False:







        try:







            current_app.logger.info(f"[Handwriting Check] Incorrect answer detected, diagnosing...")







            question_text = state.get('question_text', '')







            correct_answer = state.get('correct_answer', '')







            student_answer = f"?神蝑???: {result.get('reply', '')}"







            







            # [Phase 6] Diagnosis







            diagnosis = diagnose_error(







                question_text=question_text,







                correct_answer=correct_answer,







                student_answer=student_answer,







                prerequisite_units=prereq_skills







            )







            







            if diagnosis.get('related_prerequisite_id'):







                prereq_id = diagnosis['related_prerequisite_id']







                # Find name







                prereq_name = "?箇??桀?"







                if prereq_skills:







                    for p in prereq_skills:







                        # prereq_skills structure: [{'id':..., 'name':...}]







                        if str(p.get('id')) == str(prereq_id) or str(p.get('skill_id')) == str(prereq_id):







                            prereq_name = p.get('name') or p.get('skill_ch_name')







                            break







                







                result['suggested_prerequisite'] = {







                    'id': prereq_id,







                    'name': prereq_name,







                    'reason': diagnosis.get('prerequisite_explanation', '撱箄降銴?')







                }







        except Exception as e:







            current_app.logger.error(f"Handwriting diagnosis failed: {e}")







    # [End of modification]







    







    # ?ㄐ??update_progress ?摩?交??閬?冽迨???helper







    







    return jsonify(result)































# ==========================================







# Mistake Notebook & Diagnosis (?舫??祈?閮箸)







# ==========================================















@core_bp.route('/mistake-notebook')







@login_required







def mistake_notebook():







    return render_template('mistake_notebook.html', username=current_user.username)















@core_bp.route('/api/mistake-notebook', methods=['GET'])







@login_required







def api_mistake_notebook():







    entries = db.session.query(MistakeNotebookEntry).filter_by(student_id=current_user.id).order_by(MistakeNotebookEntry.created_at.desc()).all()







    return jsonify([entry.to_dict() for entry in entries])















@core_bp.route('/mistake-notebook/add', methods=['POST'])







@login_required







def add_mistake_entry():







    try:







        data = request.get_json()







        db.session.add(MistakeNotebookEntry(







            student_id=current_user.id,







            exam_image_path=data.get('exam_image_path'),







            question_data=data.get('question_data'),







            notes=data.get('notes'),







            skill_id=data.get('skill_id')







        ))







        db.session.commit()







        return jsonify({'success': True, 'message': '成功'})







    except Exception as e:







        db.session.rollback()







        return jsonify({'success': False, 'message': str(e)}), 500















@core_bp.route('/student/analyze_weakness', methods=['POST'])







@login_required







def analyze_weakness():







    """Analyze student weakness data for radar chart."""







    try:







        force_refresh = request.json.get('force_refresh', False) if request.json else False







        result = perform_weakness_analysis(current_user.id, force_refresh)







        return jsonify(result)







    except Exception as e:







        current_app.logger.error(f"撘梢????航炊: {e}")







        return jsonify({'success': False, 'error': str(e)}), 500















# ==========================================







# [?箸?鋆?] Mistake Notebook Helpers







# ==========================================















@core_bp.route('/add_mistake_page')







@login_required







def add_mistake_page():







    """Render the mistake notebook page."""







    skills = db.session.query(SkillInfo).filter_by(is_active=True).order_by(SkillInfo.skill_ch_name).all()







    return render_template('add_mistake.html', skills=skills, username=current_user.username)















@core_bp.route('/mistake-notebook/upload-image', methods=['POST'])







@login_required







def upload_mistake_image():







    """Upload a mistake notebook image."""







    if 'file' not in request.files: return jsonify({'success': False, 'message': '瘝?瑼?'}), 400







    file = request.files['file']







    if file.filename == '' or not allowed_exam_file(file.filename):







        return jsonify({'success': False, 'message': '瑼??⊥?'}), 400















    try:







        upload_dir = os.path.join(current_app.static_folder, 'mistake_uploads', str(current_user.id))







        os.makedirs(upload_dir, exist_ok=True)







        







        filename = secure_filename(file.filename)







        unique_filename = f"{uuid.uuid4().hex}_{filename}"







        path = os.path.join(upload_dir, unique_filename)







        file.save(path)







        







        rel_path = os.path.join('mistake_uploads', str(current_user.id), unique_filename).replace('\\', '/')







        return jsonify({'success': True, 'path': rel_path})







    except Exception as e:







        return jsonify({'success': False, 'message': str(e)}), 500















# ==========================================







# Student Diagnosis (摮貊?摮貊?閮箸?)







# ==========================================















@core_bp.route('/student/diagnosis')







@login_required







def student_diagnosis():







    """







    憿舐內摮貊?摮貊?閮箸?







    """







    return render_template('student_diagnosis.html', username=current_user.username)















# ==========================================







# Naive RAG (RAG 瑼Ｙ揣 + LLM ??)







# ==========================================







# RAG??? + ???







# ==========================================















@practice_bp.route('/api/rag_search', methods=['POST'])







def api_rag_search():







    """RAG search API."""







    data = request.get_json(silent=True) or {}







    query = (data.get('query') or '').strip()















    if not query:







        return jsonify({"results": [], "error": "???????"}), 400















    results = rag_search(query, top_k=5)







    return jsonify({"results": results})























@practice_bp.route('/api/rag_chat', methods=['POST'])







def api_rag_chat():







    """RAG + LLM chat API."""







    data = request.get_json(silent=True) or {}







    query = (data.get('query') or '').strip()







    top_skill_id = (data.get('top_skill_id') or '').strip()















    if not query or not top_skill_id:







        return jsonify({"reply": "??????????"}), 400















    result = rag_chat(query, top_skill_id)







    return jsonify(result)







