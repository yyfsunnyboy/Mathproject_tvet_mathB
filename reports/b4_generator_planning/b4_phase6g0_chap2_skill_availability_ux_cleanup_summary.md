# Phase 6G-0 — Chap2 Skill Availability UX Cleanup Summary

**狀態：READY_FOR_MANUAL_SMOKE**

## Scope and guardrails

本輪僅修正 **未開放 Chap2 skill** 與 **reserved handwriting listing problem_type** 在 HTTP JSON 回應中的**對外錯誤文案**，並補強／修正相關測試。符合 `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` **Section 8.1**（v0.1.2）。

未新增 `problem_type`、未修改 generators / validators / database / coverage matrix / adaptive scoring / allowlist 邊界、未啟動 6G 應用題或 BasicConceptsOfSets。

## User-facing messages（固定字串）

| 情境 | HTTP | `error` 欄位 |
|------|------|----------------|
| `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` 內 skill | 422 | `此技能尚未開放自動出題。 Chap2 skill not enabled in current deterministic runtime.` |
| `sample_space_listing` / `event_set_listing` / `subset_listing` | 422 | `此題型保留為手寫／開放式作答，尚未於自動出題中開放。 This problem type is reserved for handwriting/free-response review.` |
| Chap2 payload 通過 allowlist 內部驗證失敗（對外不暴露 `deny_reason` 內的 phase6c1 代號） | 422 | 依 `_b4_chap2_public_payload_validation_message()` 映射之中性文案 |

## Production code

| 檔案 | 變更 |
|------|------|
| `core/routes/practice.py` | 新增公開常數 `B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR`、`B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR`；新增 `_b4_chap2_public_payload_validation_message()`；`next_question` / adaptive preflight 之 gate 與 Chap2 payload 驗證失敗回應改用上述文案；listing 早退不再在 JSON 中嵌入 raw `problem_type` 英文字串 |

## Tests

| 檔案 | 變更 |
|------|------|
| `tests/test_b4_chap2_phase6g0_skill_availability_ux.py` | **新增**：已開放 5 skill 200、`not-enabled` 422 + 無 legacy import、encoded URL 不迴顯、`reserved` listing 三題型、回應不含 Phase 6C-1/6D/6E、No module named、Traceback、vh_%E6、vh_%2525 |
| `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py` | 斷言改為與 `practice` 模組公開常數一致 |
| `tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py` | **與現行 allowlist 對齊**（mainline 11 題型、not-enabled 僅四 skill），避免舊「5 題型／Conditional 仍 blocked」之過時假設造成誤報 |

## Automated test run

```powershell
python -m pytest `
  tests/test_b4_chap2_phase6g0_skill_availability_ux.py `
  tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py `
  tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py `
  tests/test_b4_chap2_phase6f_expected_value.py `
  tests/test_b4_chap2_phase6e_independent_events.py `
  tests/test_b4_chap2_phase6d_conditional_probability.py `
  tests/test_b4_chap2_phase6c2_probability_second_batch.py `
  tests/test_b4_chap2_phase6c1_probability_basic.py `
  tests/test_b4_chapter1_adaptive_allowlist.py `
  tests/test_vocational_math_b4_question_router_registry_canonical.py `
  -q --tb=short
```

**結果：`700 passed`**（約 241s，環境既有 FutureWarning / DeprecationWarning 不計入本輪範圍）。

## Manual smoke checklist（請人工執行）

- [ ] 已開放 skill：`ProbabilityDefinition`、`ProbabilityProperties`、`ConditionalProbability`、`IndependentEvents`、`MathematicalExpectationDefinition` — `/get_next_question` 正常 200。
- [ ] 未開放：`ProbabilityOperations`、`ApplicationsOfExpectation`、`MathematicalExpectation`、`BasicConceptsOfSets` — 422，文案為「尚未開放自動出題」，**不**出現 Phase 6C-1 / legacy import 字樣。
- [ ] `sample_space_listing` 等三種 listing — 422，保留手寫／開放式文案。
- [ ] 瀏覽器實際點「下一題」與自動化測試一致。

## Final confirmation

| 項目 | 確認 |
|------|------|
| 是否新增 problem_type | 否 |
| 是否修改 generators | 否 |
| 是否修改 validators | 否 |
| 是否修改 database | 否 |
| 是否修改 coverage matrix | 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | 否 |
| 是否變更 allowlist 成員（skill / problem_type） | 否 |
| 是否只為 UX 與測試對齊而改 `practice.py` | 是 |
| 是否啟動下一 phase | **否** |

---

*Phase 6G-0 實作與自動化驗證完成。狀態：**READY_FOR_MANUAL_SMOKE**。*
