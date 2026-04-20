# -*- coding: utf-8 -*-
"""
Prompt Registry 反向同步腳本（DB -> YAML）

用途：
1. 讀取 prompt_templates（以 DB 現況為準）
2. 轉換為 loader 相容的 prompt_registry.yaml
3. 先備份原 YAML，再覆寫
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 確保可由 scripts 目錄直接執行
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from core.models.prompt_template import PromptTemplate


TARGET_KEYS = [
    "chat_guardrail_prompt",
    "chat_tutor_prompt",
    "rag_tutor_prompt",
    "tutor_hint_prompt",
    "concept_prompt",
    "mistake_prompt",
    "handwriting_feedback_prompt",
]


def _log(msg: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def _parse_required_variables(raw: Any, prompt_key: str) -> list[str]:
    if raw is None:
        return []

    text = str(raw).strip()
    if not text:
        return []

    # 首選：JSON（目前 loader 寫入格式）
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        if isinstance(parsed, str):
            if parsed.strip():
                return [parsed.strip()]
            return []
        _log(
            f"[WARN] required_variables JSON 型別非 list/string "
            f"prompt_key={prompt_key} type={type(parsed).__name__}"
        )
        return []
    except json.JSONDecodeError:
        # 相容舊格式：a,b,c
        if "," in text:
            parts = [p.strip() for p in text.split(",") if p.strip()]
            _log(
                f"[WARN] required_variables 非 JSON，改用逗號切分 "
                f"prompt_key={prompt_key} raw={text!r}"
            )
            return parts
        _log(
            f"[WARN] required_variables parse 失敗（非 JSON / 非逗號格式） "
            f"prompt_key={prompt_key} raw={text!r}"
        )
        return []


def _normalize_content(text: str) -> str:
    """盡量保留 DB 內容，但若是 '\\n' 轉義字串則還原成真正換行。"""
    normalized = text
    # 若 DB 內存的是 JSON 字串（含外層引號與跳脫），先反序列化
    if len(normalized) >= 2 and normalized[0] == '"' and normalized[-1] == '"':
        try:
            loaded = json.loads(normalized)
            if isinstance(loaded, str):
                normalized = loaded
        except Exception:
            pass
    normalized = normalized.replace("\\n", "\n")
    return normalized


def export_prompt_registry_from_db() -> int:
    project_root = Path(__file__).resolve().parents[1]
    yaml_path = project_root / "configs" / "prompts" / "prompt_registry.yaml"
    backup_path = yaml_path.with_suffix(yaml_path.suffix + ".bak")

    if not yaml_path.exists():
        raise FileNotFoundError(f"找不到目標 YAML：{yaml_path}")

    shutil.copy2(yaml_path, backup_path)
    _log(f"[Backup] created: {backup_path}")

    with app.app_context():
        rows = (
            PromptTemplate.query.filter_by(is_active=True)
            .order_by(PromptTemplate.prompt_key.asc())
            .all()
        )

    if not rows:
        _log("[WARN] prompt_templates 查無 active prompt，取消覆寫 YAML。")
        return 1

    by_key = {r.prompt_key: r for r in rows}
    missing_required = [k for k in TARGET_KEYS if k not in by_key]
    if missing_required:
        _log(f"[WARN] DB 缺少指定重點 prompt: {missing_required}")

    ordered_keys = []
    for k in TARGET_KEYS:
        if k in by_key:
            ordered_keys.append(k)
    for k in sorted(by_key.keys()):
        if k not in ordered_keys:
            ordered_keys.append(k)

    prompts_out: dict[str, dict[str, Any]] = {}
    skipped = []
    parse_warn_count = 0

    for key in ordered_keys:
        row = by_key[key]
        role = str(row.category or "").strip()
        content = _normalize_content(str(row.content or "").strip())
        required_variables = _parse_required_variables(row.required_variables, key)

        if not role:
            _log(f"[WARN] 缺 role/category，已跳過 prompt_key={key}")
            skipped.append(key)
            continue
        if not content:
            _log(f"[WARN] 缺 content，已跳過 prompt_key={key}")
            skipped.append(key)
            continue

        # 簡易 parse 警告計數（供匯出摘要）
        raw_rv = str(row.required_variables or "").strip()
        if raw_rv and not raw_rv.startswith("["):
            parse_warn_count += 1

        prompts_out[key] = {
            "role": role,
            "required_variables": required_variables,
            "content": content,
        }

    # 以手動方式寫出 YAML，確保 content 一律使用 block scalar '|'
    lines: list[str] = [
        "version: 1.0",
        'description: "AI Tutor Prompt Registry (source of truth)"',
        "",
        "prompts:",
    ]
    for key, data in prompts_out.items():
        lines.append(f"  {key}:")
        lines.append(f"    role: {data['role']}")
        req_vars = data.get("required_variables", [])
        if req_vars:
            lines.append("    required_variables:")
            for item in req_vars:
                lines.append(f"      - {item}")
        else:
            lines.append("    required_variables: []")
        lines.append("    content: |")
        content_lines = str(data.get("content", "")).splitlines()
        if content_lines:
            for ln in content_lines:
                lines.append(f"      {ln}")
        else:
            lines.append("      ")
        lines.append("")

    yaml_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")

    _log("[Prompt Export]")
    _log("- source: DB")
    _log(f"- exported: {len(prompts_out)}")
    _log(f"- skipped: {len(skipped)}")
    _log(f"- required_variables_parse_warn: {parse_warn_count}")
    _log(f"- target: {yaml_path}")
    _log(f"- backup: {backup_path}")
    if skipped:
        _log(f"- skipped_keys: {skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(export_prompt_registry_from_db())
