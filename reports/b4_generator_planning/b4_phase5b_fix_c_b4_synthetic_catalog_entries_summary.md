# Phase 5B-Fix-C: B4 Synthetic Catalog Entries Summary

## Root Cause
- 前端 payload bridge 已修正，但 backend 回傳：
  - `error: "No catalog entries available for the requested adaptive scope"`
  - `target_skill_ids_count: 5`
  - `unit_skill_ids_count: 13`
- 代表 `session_engine` 在 `_select_entries(payload)` + B4 allowlist filter 後，仍得到空 `entries`，接著在 `submit_and_get_next` 直接 `raise ValueError(...)`，導致 API 400。

## Before Error JSON (manual browser smoke)
```json
{
  "entry_mode": "chapter",
  "error": "No catalog entries available for the requested adaptive scope",
  "missing_fields": [],
  "mode": "teaching",
  "received_keys": [
    "chapter_id",
    "curriculum",
    "entry_mode",
    "learning_mode",
    "mode",
    "routing_state",
    "skill_id",
    "skill_ids",
    "starter_skill_id",
    "step_number",
    "student_id",
    "target_skill_ids",
    "unit_skill_ids",
    "volume"
  ],
  "skill_id": "vh_數學B4_AdditionPrinciple",
  "step_number": 0,
  "target_skill_ids_count": 5,
  "unit_skill_ids_count": 13
}
```

## Files Inspected
- `core/routes/adaptive_api.py`
- `core/adaptive/session_engine.py`
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`

## Files Changed
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- `reports/b4_generator_planning/b4_phase5b_fix_c_b4_synthetic_catalog_entries_summary.md`

## Synthetic Catalog Design
當符合以下條件時才啟用（B4 專用）：
- `entry_mode=chapter`（或 chapter 語意）
- `curriculum=vocational`
- `volume=數學B4`
- `chapter_id=1`
- 正常 catalog lookup/filter 後 `entries` 為空
- 請求中的 `target_skill_ids / unit_skill_ids / skill_ids / starter/skill_id` 至少有 allowlisted B4 skill

建立 synthetic entries（最小可用欄位）：
- `skill_id`: allowlisted B4 skill
- `skill_name`: `skill_id`
- `family_id`: `B4C1_SYN_XX`（穩定 placeholder）
- `family_name`: `B4 Chapter1 Synthetic Family XX`
- `theme`: `b4_generator_synthetic_catalog`
- `subskill_nodes`: `["b4_chapter1_synthetic_bootstrap"]`
- `notes`: `source_type=b4_generator_synthetic_catalog`

保護機制：
- synthetic entries 會再次通過
  - `filter_catalog_entries_for_b4_chapter1_deterministic_adaptive`
- 因此不會納入 manual_review / future_ai_judged skill，也不會擴張 allowlist。
- 題型排除仍由既有 payload validator 生效（`binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation` 仍阻擋）。

## Added Audit / Log
- 新增：
  - `[Phase5B-FixC][b4_synthetic_catalog] requested_skill_ids_count=... synthetic_entries_count=... source_type=b4_generator_synthetic_catalog`

## QA Commands / Result
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- 結果：
  - `9 passed, 12 warnings`

## Test Coverage Added/Updated
1. Browser 等價 B4 chapter bootstrap payload + empty catalog 時，API 回 200（非 400）。
2. Synthetic catalog 僅使用 allowlisted B4 skill（混入非 allowlist skill 仍不會被採用）。
3. Excluded problem types 仍被阻擋（既有測試持續通過）。
4. Non-B4 空 catalog 維持既有錯誤行為（仍回 400）。
5. 回傳題目仍為 generator-backed deterministic（非 `catalog_fallback`）。

## Manual Browser Smoke Result
- 本回合未直接操作瀏覽器；以你提供的真實 400 JSON 作為修正依據，並以更新後測試覆蓋驗證。
