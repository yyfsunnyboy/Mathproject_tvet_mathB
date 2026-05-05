# B4 Phase 5B Fix-E：B4 Chapter 1 Remediation Mapping Bridge

## Root Cause
- B4 Chapter 1 synthetic catalog 可正常出題，但缺少可用的補救映射候選，導致：
  - `mapping_candidates=[]`
  - `suggested_prereq_skill=None`
  - `remediation_candidates=[]`
- 同時 `remediation_review_ready` 原本依賴 `textbook_cfg`，在 synthetic/無 textbook progression 情境下幾乎無法進入補救分流。

## Observed Logs
- `allowed_actions=['stay', 'remediate']`
- `ppo_action=stay`
- `why_remediate_masked=ppo_chose_stay`
- `remediation_review_ready=False`
- `suggested_prereq_skill=None`
- `suggested_prereq_subskill=None`
- `remediation_candidates empty`
- `mapping_candidates=[]`
- `fallback_reason=phase1_no_matching_family_mapping`
- `selected_subskill=b4_chapter1_synthetic_bootstrap`
- `selected_subskill_without_mapping_candidates`

## Mapping Design
- 新增 B4 Chapter 1 deterministic remediation bridge（小型表格）：
  - 以 `skill_id -> remediation target skill_id(s)` 方式定義。
  - 優先 B4-to-B4（例如：`CombinationProperties -> CombinationDefinition`，`BinomialTheorem -> BinomialCoefficientIdentities/CombinationDefinition`）。
  - 僅使用 allowlist deterministic 技能，不含 manual_review / future_ai_judged。
- Synthetic family 改為帶入 per-skill subskill key：
  - `b4_skill::<skill_id>`
  - 使 phase1 filter 能對映到實際 B4 synthetic entry，而非全部共用 `b4_chapter1_synthetic_bootstrap`。
- B4 Chapter 1 teaching 專屬 safety override：
  - 若 repeated wrong + 高挫折且 PPO 仍選 `stay`，僅此路徑強制 `remediate`。

## Files Inspected
- `core/adaptive/session_engine.py`
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- `core/adaptive/routing.py`
- `core/adaptive/remediation_retriever.py`
- `core/adaptive/rag_diagnosis_mapping.py`

## Files Changed
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- `core/adaptive/session_engine.py`
- `tests/test_phase5b_fix_e_b4_remediation_mapping_bridge.py`

## QA Commands / Result
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py`
- `python -m pytest -q tests/test_phase5b_fix_e_b4_remediation_mapping_bridge.py`
- 預期驗證：
  - repeated wrong 後可出現 non-empty remediation candidate
  - threshold 後可進入 remediation（含 safety override）
  - remediation target 為 deterministic allowlisted
  - excluded problem type blocking 仍由既有機制覆蓋
  - non-B4 行為不變

## Manual Browser Smoke Recommendation
- 路徑：`數學B4 -> 1 排列組合 -> 單元練習`
- 手動連續答錯（>=3）觀察：
  - 是否進入補救狀態（`in_remediation=true`）
  - 補救題是否切到較基礎 B4 deterministic 技能
  - 補救後是否能返回主線
  - 仍不出現 excluded problem types
