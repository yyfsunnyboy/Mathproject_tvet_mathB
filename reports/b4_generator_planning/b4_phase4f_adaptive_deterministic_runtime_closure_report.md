# Phase 4F-Closure：Adaptive Deterministic Runtime Closure Report

## 1) Phase 4F 目的

Phase 4F 的核心目標是：

- 為 **B4 Chapter 1** 建立可運行的 deterministic adaptive runtime。
- 明確保持 **adaptive readiness** 與 **Phase 4E deterministic closure matrix** 分離。
- 在不擴張題型邊界、不改 coverage matrix 的前提下，完成路由、驗證、防呆與可觀測性閉環。

---

## 2) 最終架構摘要

- `core/routes/practice.py` `get_adaptive_question`
  - 實作 B4 adaptive 題源策略（`generator_first` / `db_textbook_example` / `generator_fallback`）。
  - 產題後走 shared validator，必要時拒題並回傳 audit。
- `core/routes/adaptive_api.py` `submit_and_get_next`
  - 維持為 adaptive v2 API 入口，透過 `session_engine.submit_and_get_next` 繼承 Main-C/Main-D 行為。
- `core/adaptive/session_engine.py`
  - 套用 B4 catalog allowlist 過濾。
  - 對 B4 payload 執行 shared validator。
  - Main-D 加入「validator 拒絕後 bounded B4 retry，最終 fallback safety net」。
- Shared B4 adaptive allowlist module
  - `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- Shared validator
  - `validate_b4_deterministic_adaptive_generator_payload`
  - 被 `practice.py` 與 `session_engine.py` 共用，確保一致規範。

---

## 3) 最終 B4 adaptive allowlist 來源

- 檔案：`core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- 常數：`B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`
- catalog 過濾函式：`filter_catalog_entries_for_b4_chapter1_deterministic_adaptive`

此模組是 Phase 4F 的單一 allowlist 來源，避免 practice 線與 session_engine 線規則漂移。

---

## 4) 明確排除 problem types

- `binomial_expansion_basic`
- `tree_diagram_listing`
- `pascal_triangle_derivation`

以上題型在 deterministic adaptive runtime 中明確禁止輸出。

---

## 5) Source policy 摘要

- **pure allowlisted B4 pool**：`generator_first`
- **mixed pool + DB template 命中**：`db_textbook_example`
- **mixed pool + DB empty + 有 allowlisted B4 候選**：`generator_fallback`
- **session_engine validator rejection**：bounded B4 retry（上限重試）→ 若仍失敗再 `catalog_fallback`
- **non-B4-only empty DB pool**：既有 `404` 行為保留

---

## 6) Audit / debug 欄位

Phase 4F 最終觀測欄位包含：

- `adaptive_audit`
- `b4_deterministic_catalog_audit`
- `source_type`
- `skill_id`
- `problem_type_id`
- `generator_key`
- `router_trace` 摘要（或對應 selection reason）
- rejection / fallback reason（可得時附帶）

---

## 7) QA summary table

| QA 類別 | 狀態 / 結果 |
|---|---|
| Preflight tests | 通過（已完成） |
| Main-A tests | 通過（已完成） |
| Main-B tests | 通過（已完成） |
| Main-C tests | 通過（已完成） |
| Main-D tests | **5 passed** |
| Final combined regression | **58 passed, 27 warnings, exit_code 0, runtime 約 200.56s** |

---

## 8) Phase 4F 各階段變更檔案摘要

### Preflight
- `core/vocational_math_b4/adaptive/__init__.py`
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`
- `core/routes/practice.py`
- `tests/test_b4_chapter1_adaptive_allowlist.py`

### Main-A
- `core/routes/practice.py`
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`（audit/source_type 對齊）
- `tests/test_phase4f_main_a_adaptive_generator_first.py`

### Main-B
- `tests/test_phase4f_main_b_adaptive_e2e_smoke.py`

### Main-C
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`（catalog entry filter）
- `core/adaptive/session_engine.py`（allowlist/validator/audit 對齊）
- `tests/test_phase4f_main_c_adaptive_v2_allowlist.py`

### Main-D
- `core/adaptive/session_engine.py`（bounded retry alignment + retry audit）
- `tests/test_phase4f_main_d_real_smoke_retry_alignment.py`

---

## 9) 明確「未變更」範圍

以下項目為 Phase 4F 中刻意不變：

- Phase 4E coverage matrix
- B4 generators（除既有 D3-Fix-A enrichment 之外不擴張）
- `manual_review` 狀態
- `binomial_expansion_basic` 連結策略（維持排除）
- free-response / list-answer / AI-judged runtime
- frontend redesign
- non-B4 adaptive behavior

---

## 10) Known limitations

- 前端 smoke 屬 lightweight route/app-context 驗證，非完整 browser QA。
- 真實班級 pilot 仍需人工觀測與教學現場回饋。
- 目前 warnings 仍存在，但與 Phase 4F 功能失敗無直接關聯。
- Advanced RAG 初始化較重，會拉長整包回歸時間。

---

## 11) Final conclusion

- **Phase 4F adaptive deterministic runtime 已完成 closure。**
- **B4 Chapter 1 已可進入 limited pilot / teacher QA。**
- 下一階段建議應是 **pilot checklist / deployment smoke**，而非再擴張 generator 功能面。
