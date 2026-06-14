from __future__ import annotations

from typing import Any

PHASE1_ENFORCEMENT_ASSERTION_ZH = (
    "【強制合約｜最高優先級】\n"
    "目前的 skill_id 與傳入的來源例題 100% 正確對齊，已由教師與課本 skill_id 欄位確認。\n"
    "你被禁止評估這些例題是否屬於其他家族（例如 absolute_value_inequality_family）。\n"
    "你的唯一任務，是 100% 相信這些題目就是該技能的標準核心，"
    "並直接在此 anchor 範圍內切分子技能（subskills）。\n"
    "禁止輸出 needs_review 或 contextual_application 作為跨家族質疑的結果；"
    "若規則分類已在 anchor 子技能清單內，必須接受。\n"
)


def phase1_enforcement_assertion_block(
    main_skill_anchor: dict[str, Any] | None,
    *,
    include_anchor_fields: bool = True,
) -> str:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    lines = [PHASE1_ENFORCEMENT_ASSERTION_ZH]
    mandate = str(anchor.get("classification_mandate", "")).strip()
    if mandate and mandate != PHASE1_ENFORCEMENT_ASSERTION_ZH.strip():
        lines.append(mandate)
    if include_anchor_fields and anchor:
        lines.extend(
            [
                "Trusted skill anchor (do not override):",
                f"- skill_id: {anchor.get('skill_id', '')}",
                f"- skill_ch_name: {anchor.get('skill_ch_name', '')}",
                f"- skill_en_name: {anchor.get('skill_en_name', '')}",
                f"- expected_task_families: {anchor.get('expected_task_families', [])}",
                f"- expected_subskill_candidates: {anchor.get('expected_subskill_candidates', [])}",
                f"- skill_anchor_scope: {anchor.get('skill_anchor_scope', '')}",
                f"- source_skill_scope_locked: {anchor.get('source_skill_scope_locked', True)}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
