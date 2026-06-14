# -*- coding: utf-8 -*-
import json
import logging
import traceback
from pathlib import Path
from typing import Any, List, Dict
from core.gencode.pipeline_orchestrator import run_gencode_phase2_raw, PROJECT_ROOT, _resolve_gencode_ai_client, call_ai_with_retry
from core.gencode.repair_catalog import GENERATOR_REPAIR_CATALOG

logger = logging.getLogger(__name__)

def execute_phase_2(
    skill_id: str,
    accepted_problem_types: List[str] | None = None,
    excluded_example_ids: List[int] | None = None,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Central Decision Controller for Phase 2.
    Implements the Rollback & Retry state machine with Negative Feedback loops.
    """
    MAX_RETRY = 3
    current_attempt = 1
    last_error_log = ""
    
    while current_attempt <= MAX_RETRY:
        logger.info(f"[CLOSED-LOOP CONTROLLER] Executing Phase 2 (Attempt {current_attempt}/{MAX_RETRY})...")
        
        try:
            # We run run_gencode_phase2
            phase2_response = run_gencode_phase2_raw(
                skill_id=skill_id,
                accepted_problem_types=accepted_problem_types,
                excluded_example_ids=excluded_example_ids,
                dry_run=dry_run
            )
            
            can_continue = phase2_response.get("can_continue", False)
            generator_results = phase2_response.get("generator_results", [])
            
            # Find if there are semantic errors/blockers
            semantic_unsafe = False
            error_details = []
            
            for r in generator_results:
                blockers = r.get("blockers", []) or []
                div_report = r.get("diversity_sampling", {}) or {}
                gen_errors = div_report.get("generation_errors", []) or []
                
                for err in gen_errors:
                    if "generator_semantically_unsafe" in err:
                        semantic_unsafe = True
                        error_details.append(err)
                
                if r.get("usable_for_phase3") is False or not can_continue:
                    for b in blockers:
                        error_details.append(f"Blocker: {b} on problem type {r.get('problem_type_id')}")

            if not can_continue or semantic_unsafe:
                logger.warning(f"[CLOSED-LOOP CONTROLLER] Phase 2 failed validation. can_continue: {can_continue}, semantic_unsafe: {semantic_unsafe}")
                
                # Compile error log for AI feedback loop
                error_log = "\n".join(error_details) if error_details else "Phase 2 validation failed due to diversity blockers or missing templates."
                logger.info(f"[CLOSED-LOOP CONTROLLER] Error details compiled:\n{error_log}")
                
                negative_feedback = f"Error details from validation:\n{error_log}"
                
                # Iterate and repair each failed generator candidate code
                for r in generator_results:
                    pt_id = r.get("problem_type_id")
                    if r.get("usable_for_phase3") is False or pt_id in [err.split(" ")[-1] for err in error_details if "problem type" in err]:
                        rep_info = GENERATOR_REPAIR_CATALOG.get(pt_id)
                        if rep_info:
                            code_path = PROJECT_ROOT / rep_info.get("module_path")
                            if code_path.exists():
                                current_code = code_path.read_text(encoding="utf-8")
                                
                                logger.info(f"[CLOSED-LOOP CONTROLLER] Sending negative feedback to Gemini to repair: {code_path}")
                                
                                repair_prompt = f"""
你先前設計的題型生成器代碼在 Phase 2 驗證中失敗。
【錯誤日誌（Negative Feedback Context）】:
{negative_feedback}

【目前程式碼】:
```python
{current_code}
```

請扮演修復 Agent，修正此 Python 代碼中的語意/合約錯誤（例如：選項內容與正確答案不一致、選項數量不正確、或者數學公式表示有 Sympy 無法解析的語法）。
請確保 generate() 函數產生的題型與選項完全正確、可被 Sympy 解析且符合 answer_contract。
請僅回傳修正後的完整 Python 程式碼，不要有 Markdown 格式或額外說明。
""".strip()
                                
                                client, _ = _resolve_gencode_ai_client(["architect", "tutor", "default"])
                                if client:
                                    try:
                                        resp = call_ai_with_retry(client, repair_prompt, max_retries=2, retry_delay=2, timeout=90)
                                        resp_text = str(getattr(resp, "text", "") or "").strip()
                                        if resp_text.startswith("```python"):
                                            resp_text = resp_text.split("```python", 1)[-1].split("```", 1)[0].strip()
                                        elif resp_text.startswith("```"):
                                            resp_text = resp_text.split("```", 1)[-1].split("```", 1)[0].strip()
                                        
                                        if resp_text:
                                            logger.info(f"[CLOSED-LOOP CONTROLLER] Overwriting {code_path} with repaired generator code...")
                                            code_path.write_text(resp_text, encoding="utf-8")
                                    except Exception as ex:
                                        logger.error(f"[CLOSED-LOOP CONTROLLER] Failed to call Gemini for repair: {ex}")
                
                current_attempt += 1
                last_error_log = error_log
                continue
            
            logger.info("✅ [CLOSED-LOOP CONTROLLER] Phase 2 execute_phase_2 successfully completed.")
            return phase2_response

        except Exception as e:
            logger.error(f"[CLOSED-LOOP CONTROLLER] Exception during execute_phase_2 attempt {current_attempt}: {e}")
            current_attempt += 1
            last_error_log = str(e)
            
    raise RuntimeError(f"SYSTEM_INTERRUPT: Phase 2 closed-loop retry exceeded limit. Human intervention required. Last error: {last_error_log}")
