import re
import codecs

with codecs.open('core/routes/analysis.py', 'r', 'utf-8') as f:
    content = f.read()

target = r"""        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name
        print("calling handwriting analyzer (recognition then analysis)")
        print("question_text:", question_text)"""

replacement = r"""        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            f.write(img_data)
            temp_path = f.name

        problem_type = (data.get('problem_type') or state.get('problem_type') or "").strip()
        if problem_type == "tree_diagram_listing":
            expected_paths = data.get('expected_paths') or state.get('expected_paths') or []
            expected_count = data.get('expected_count') or state.get('expected_count') or len(expected_paths)
            variant = data.get('variant') or state.get('variant') or ""
            
            prompt = (
                "You are an AI teacher grading a student's tree diagram or listing answer. "
                "The student has drawn or written their answer on the provided whiteboard image.\n"
                f"Question: {question_text}\n"
                f"The correct expected paths are: {expected_paths}\n"
                f"Total expected paths count: {expected_count}\n\n"
                "Rubric:\n"
                "- If the student has drawn a tree diagram or listed paths that completely match all expected paths, return status 'correct'.\n"
                "- If the student wrote the final count (e.g. '6種') but didn't draw the tree or list the paths, return status 'partial'.\n"
                "- If the student missed some paths (e.g. missing '甲乙乙'), return status 'partial'.\n"
                "- If the variant is 'early_stopping_game' and the student lists fixed 3-round paths (e.g. '甲甲甲', '乙乙乙'), return status 'incorrect' or 'partial' because they didn't stop early.\n"
                "- If the image is illegible or has no paths, return status 'needs_review'.\n\n"
                "Respond in valid JSON with these keys:\n"
                "  \"status\": \"correct\" | \"partial\" | \"incorrect\" | \"needs_review\",\n"
                "  \"feedback\": \"Your short explanation to the student\"\n"
            )
            
            if ai_provider == 'google':
                vision_cfg = dict(Config.LEGACY_MODEL_ROLES.get('vision_analyzer') or {})
                tree_response = call_google_model(
                    vision_cfg,
                    prompt,
                    image_path=temp_path,
                    max_retries=2,
                    retry_delay=1,
                    verbose=False,
                )
            else:
                tree_response = call_ai(
                    role="vision_analyzer",
                    prompt=prompt,
                    image_path=temp_path,
                    max_retries=2,
                    retry_delay=1,
                    verbose=False,
                )
            raw_text = (getattr(tree_response, 'text', '') or '').strip()
            cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE)
            parsed = clean_and_parse_json(cleaned)
            
            st = parsed.get("status", "needs_review") if isinstance(parsed, dict) else "needs_review"
            feedback = parsed.get("feedback", "無法判讀答案。") if isinstance(parsed, dict) else "無法判讀答案。"
            
            _hw_err = {
                "correct": "handwriting_ok",
                "partial": "handwriting_partial",
                "incorrect": "handwriting_wrong",
                "needs_review": "handwriting_unknown",
            }
            
            result = {
                "reply": enforce_strict_mode(feedback),
                "is_process_correct": st in ("correct", "partial"),
                "correct": st == "correct",
                "next_question": st == "correct",
                "follow_up_prompts": [],
                "error_type": _hw_err.get(st, "handwriting_unknown"),
                "success": True,
                "auto_next": st == "correct",
                "handwriting_analysis": {"status": st, "feedback": feedback},
                "handwriting_status": st,
            }
            
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            return jsonify(result)

        print("calling handwriting analyzer (recognition then analysis)")
        print("question_text:", question_text)"""

content = content.replace(target, replacement)

with codecs.open('core/routes/analysis.py', 'w', 'utf-8') as f:
    f.write(content)
