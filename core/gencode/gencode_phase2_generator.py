# -*- coding: utf-8 -*-
"""Phase 2 Ab4 Matrix Generator Engine.
承接 Phase 1 定錨的雙通道合約，將課本例題與隨堂練習的解題脈絡，演化為結構完整的 2D 題目變化矩陣。
"""

from __future__ import annotations

import logging
from typing import Any
from core.prompts.prompt_builder import PromptBuilder
from core.ai_wrapper import call_ai_with_retry, get_ai_client

logger = logging.getLogger(__name__)

def build_ab4_prompt(
    master_spec: str,
    textbook_example: str = "",
    topic: str = "",
    skill_id: str = ""
) -> str:
    """承接 Phase 1 定錨雙通道合約，調用 PromptBuilder ablation_id=4 構建 2D 矩陣出題 Prompt"""
    return PromptBuilder.build(
        master_spec=master_spec,
        ablation_id=4,
        textbook_example=textbook_example,
        topic=topic,
        skill_id=skill_id
    )

def generate_ab4_candidate_code(
    master_spec: str,
    textbook_example: str = "",
    topic: str = "",
    skill_id: str = "",
    ai_client: Any = None
) -> str:
    """呼叫 LLM 以 Ab4 雙通道與防禦退化 Prompt 產出 2D 矩陣題型生成器"""
    prompt = build_ab4_prompt(
        master_spec=master_spec,
        textbook_example=textbook_example,
        topic=topic,
        skill_id=skill_id
    )
    
    client = ai_client or get_ai_client("architect")
    if not client:
        raise RuntimeError("AI client is unavailable for Ab4 code generation.")
        
    logger.info(f"Generating Ab4 candidate code for skill {skill_id}...")
    resp = call_ai_with_retry(client, prompt, max_retries=2, retry_delay=2, timeout=120)
    raw_code = str(getattr(resp, "text", "") or "").strip()
    
    # Clean up code blocks if present
    if raw_code.startswith("```python"):
        raw_code = raw_code.split("```python", 1)[-1].split("```", 1)[0].strip()
    elif raw_code.startswith("```"):
        raw_code = raw_code.split("```", 1)[-1].split("```", 1)[0].strip()
        
    return raw_code
