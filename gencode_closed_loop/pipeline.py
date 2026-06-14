# -*- coding: utf-8 -*-
import json
import logging
import traceback
from pathlib import Path
from typing import Any, Dict
from core.gencode.pipeline_orchestrator import run_gencode_phase3_package_raw, PROJECT_ROOT, _resolve_gencode_ai_client, call_ai_with_retry
from core.gencode.pipeline_state import phase_summary_path

logger = logging.getLogger(__name__)

def execute_phase_3(skill_id: str, accepted_generator_keys: list | None = None, dry_run: bool = True) -> Dict[str, Any]:
    """
    Global Scheduler for Phase 3 packaging.
    Implements try-catch error capturing and self-healing for environment crashes.
    """
    draft_spec_path = phase_summary_path(skill_id, "generator_draft_spec")
    backup_spec_path = draft_spec_path.with_name(f"{draft_spec_path.stem}_backup.json")
    
    if draft_spec_path.exists():
        try:
            backup_spec_path.write_text(draft_spec_path.read_text(encoding="utf-8"), encoding="utf-8")
            logger.info(f"[PIPELINE SCHEDULER] Backup of draft_spec created at {backup_spec_path}")
        except Exception as backup_err:
            logger.warning(f"[PIPELINE SCHEDULER] Failed to create draft_spec backup: {backup_err}")

    try:
        logger.info(f"[PIPELINE SCHEDULER] Executing Phase 3 Packaging for skill {skill_id}...")
        result = run_gencode_phase3_package_raw(
            skill_id=skill_id,
            accepted_generator_keys=accepted_generator_keys,
            dry_run=dry_run
        )
        return result
        
    except Exception as e:
        crash_log = traceback.format_exc()
        logger.error(f"💥 [PIPELINE SCHEDULER] System crash detected during execute_phase_3:\n{crash_log}")
        
        logger.info("[PIPELINE SCHEDULER] Starting AI self-healing and draft restoration...")
        
        self_healing_prompt = f"""
你現在是系統層自我修復 Agent。自動化管線在執行 Phase 3 封裝打包時發生系統級崩潰（例如：未定義變數、代碼編譯或環境毀損）。
請注意：這是【系統/程式碼代碼環境結構損壞】，而非單一題目內容出錯。

【系統崩潰堆疊日誌（Crash Log）】:
{crash_log}

請指引系統自癒：
1. 分析此崩潰的根本原因是否與 `generator_draft_spec.json` 的參數配置或 generated candidate 代碼結構衝突有關。
2. 我們將嘗試自動恢復上一版穩定的 draft_spec 結構。請提供修復的參數配置或建議的自癒修改方案。
請僅回傳 JSON 格式的自癒建議報告，包含 "reason" 和 "action"。
""".strip()

        client, _ = _resolve_gencode_ai_client(["architect", "default"])
        if client:
            try:
                resp = call_ai_with_retry(client, self_healing_prompt, max_retries=2, retry_delay=2, timeout=90)
                logger.info(f"[PIPELINE SCHEDULER] AI self-healing report: {getattr(resp, 'text', '')}")
            except Exception as ai_err:
                logger.error(f"[PIPELINE SCHEDULER] Failed to get self-healing suggestion from AI: {ai_err}")

        if backup_spec_path.exists():
            try:
                logger.info(f"[PIPELINE SCHEDULER] Restoring last stable draft_spec from backup: {backup_spec_path} -> {draft_spec_path}")
                draft_spec_path.write_text(backup_spec_path.read_text(encoding="utf-8"), encoding="utf-8")
                
                logger.info("[PIPELINE SCHEDULER] Retrying execute_phase_3 after restoration...")
                result = run_gencode_phase3_package_raw(
                    skill_id=skill_id,
                    accepted_generator_keys=accepted_generator_keys,
                    dry_run=dry_run
                )
                return result
            except Exception as retry_err:
                logger.error(f"[PIPELINE SCHEDULER] Retry after draft restoration failed: {retry_err}")
                
        return {
            "ok": False,
            "phase": "phase3",
            "skill_id": skill_id,
            "error": f"System crash in Phase 3 packaging. Crashed with: {str(e)}",
            "phase_status": "phase3_packaged_draft_smoke_failed",
            "can_continue": False
        }
