# Phase 4F-Main-C：Adaptive v2／session_engine Allowlist Unification — 總結

**日期：** 2026-05-05  
**目標：** 讓 **practice 線**（`get_adaptive_question`）與 **adaptive v2 線**（`submit_and_get_next`／`session_engine`）對 **職業數學 B4 Chapter 1** 共用同一套 deterministic allowlist 與 payload validator，消除雙規則。

---

## 曾檢視的檔案

| 檔案 | 角色 |
|------|------|
| `core/routes/adaptive_api.py` | `POST /api/adaptive/submit_and_get_next`：組 payload、`submit_and_get_next`、runtime store、`jsonify(_response_for_frontend(...))`。 |
| `core/adaptive/session_engine.py` | `submit_and_get_next`、`_select_entries`、`load_catalog`、`_generate_question_payload`、`_ensure_safe_question_payload`、`_normalize_question_payload`。 |
| `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` | Allowlist、manual_review 排除、`validate_b4_deterministic_adaptive_generator_payload`、`format_adaptive_question_audit_dict`。 |
| `reports/b4_generator_planning/b4_phase4f_main_b_adaptive_e2e_smoke_summary.md` | Main-B 對 session_engine「未對齊」之已知發現。 |

---

## 變更的檔案

| 檔案 | 摘要 |
|------|------|
| `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` | 新增 **`filter_catalog_entries_for_b4_chapter1_deterministic_adaptive(entries)`**：對具 **`skill_id`** 之 catalog 列套用與 Preflight 相同之 B4／manual_review／allowlist 規則，並輸出 audit 列。 |
| `core/adaptive/session_engine.py` | （1）`submit_and_get_next` 在 demo_safe 過濾後呼叫上述 catalog filter；無列時 **`ValueError`**（與原「無 catalog scope」一致）。（2）**`_b4_session_engine_payload_gate`**：B4 allowlisted 之「真 generator」題必備 **`problem_type_id`** 且通過 **`validate_b4_deterministic_adaptive_generator_payload`**；**`catalog_fallback`／`ultimate_safe_question`／`:same_family_safe`** 放行（無強制題型）。（3）**`_maybe_finalize_b4_validated_generator_layer`**：`micro_generator`／`script_dispatch`／`skill_module` 成功路徑先 gate，再附上 **`adaptive_audit`**（**`source_type`=`session_engine_<layer>`**）。（4）**`_normalize_question_payload`** 保留 **`problem_type_id`、`generator_key`、`router_trace`、`subskill_id`、`adaptive_audit`** 以利驗證與稽核。（5）**`_ensure_safe_question_payload`** 在第一階段接受題目前再跑 gate。（6）回應字典新增 **`b4_deterministic_catalog_audit`**（preflight 剔除列，無則為 `[]`）。 |
| `tests/test_phase4f_main_c_adaptive_v2_allowlist.py` | **新增** 7 項：catalog filter、gate 單元、`submit_and_get_next` allowlisted B4、排除題型 fallback、僅 disallow B4 時空 catalog、`/api/adaptive/submit_and_get_next` 非 B4 迴歸。 |

**未修改：** Phase 4E coverage matrix、`question_router`、B4 generators、`core/routes/practice.py`（沿用既有逻辑）、`adaptive_api.py` 本體（仍委派 `submit_and_get_next`，自動帶出新 audit 欄位）。

---

## adaptive_api／session_engine 選題／出題流程（摘要）

1. **`adaptive_api.adaptive_submit_and_get_next`**：補齊 `student_id`、runtime 批改 → **`submit_and_get_next(payload)`**。  
2. **`submit_and_get_next`**：**`_select_entries`**（`load_catalog` + skill／unit 範圍）→ **`_apply_demo_safe_family_filter`** → **`filter_catalog_entries_for_b4_chapter1_deterministic_adaptive`** → routing／PPO／remediation 決定 **`next_entry`**。  
3. **`_generate_question_payload(next_entry)`**：micro → script → skill **`generate()`** → 失敗則 **`catalog_fallback`**。  
4. **`_ensure_safe_question_payload`**：正規化後若題文／答案有效，再經 **B4 gate**；否則 same_family／ultimate safe。  
5. 回傳 **`new_question_data`**（前端經 **`_response_for_frontend`** 仍會移除 **`answer`／`correct_answer`**，但 **`adaptive_audit`／`problem_type_id`** 等會保留）。

---

## Allowlist 套用位置

| 階段 | 機制 |
|------|------|
| Catalog 進入 session_engine | **`filter_catalog_entries_for_b4_chapter1_deterministic_adaptive`**：剔除 manual_review B4、非 allowlist B4；非 B4 **不改**。 |
| 題 payload 準備展示 | **`_b4_session_engine_payload_gate`**：allowlisted B4 的真 generator 層須有可驗證之 **`problem_type_id`**；fallback／ultimate 不要求題型鍵。 |

---

## Excluded problem_type validator 套用位置

| 時機 | 行為 |
|------|------|
| **`_maybe_finalize_b4_validated_generator_layer`** | Gate 內呼叫 **`validate_b4_deterministic_adaptive_generator_payload`**（與 **`practice`** 同一函式）。若排除類型或缺 **`problem_type_id`** → 該層視為失敗，改走後備鏈（直至 **`catalog_fallback`**）。 |
| **`_ensure_safe_question_payload`** | 第一階段候選再度 gate，避免繞過。 |

---

## `adaptive_audit`／`source_type`（摘要）

通過 **`skill_module`／`script_dispatch`／`micro_generator`** 且為 **allowlisted B4** 時，**`new_question_data.adaptive_audit`** 由 **`format_adaptive_question_audit_dict`** 產生，**`source_type`** 形如：`session_engine_skill_module`、`session_engine_script_dispatch`、`session_engine_micro_generator`。

---

## QA 指令與結果

```powershell
Set-Location "d:\Python\Mathproject_tvet_mathB"
python -m pytest tests/test_phase4f_main_c_adaptive_v2_allowlist.py tests/test_phase4f_main_b_adaptive_e2e_smoke.py tests/test_phase4f_main_a_adaptive_generator_first.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -v --tb=short
```

**結果：** **53 passed**（Main-C：7；Main-B：9；Main-A：5；allowlist：8；router canonical：24）。

---

## 已知限制（known limitations）

1. **B4 generator 遭 gate 拒絕**時目前落到 **`catalog_fallback`／safe**（題文為占位語意），與 **`practice`** 線「再抽／再生」策略不同；功能正確但不一定是最佳教學體驗。  
2. **`adaptive_api`** 未獨立「薄適配檔」：規則集中在 **`session_engine`** + **`b4_chapter1_deterministic_allowlist`**；若未來要多後端入口，可再抽出共用 helper。  
3. **`completed`** 提早分支的回應未附加 **`b4_deterministic_catalog_audit`**（該分支不出新題）；影響僅限觀測一致性。  
4. **`tests/test_adaptive_m2_api.py`** 部分案例（例如 **`used_apr_for_completion`**）與本 Phase 無關且可能為環境／資料預設問題；本次 **Main-C** 以 **`submit_and_get_next`／HTTP bootstrap** 與指定迴歸包為準。

---

## Phase 4F-Main-D 建議

1. **統一拒題後鑑**：B4 generator 遭 validator 拒絕時，評估 **限定次數重試 `generate(seed=…)`** 或 **換 subskill**，減少 **`catalog_fallback`** 暴露。  
2. **前端／觀測**：文件化 **`b4_deterministic_catalog_audit`** 與 **`new_question_data.adaptive_audit`**，供營運／除錯對齊 **`practice`** 之 **`adaptive_audit=1`**。  
3. **Catalog 資料源**：若正式環境將 **B4** 納入 **`skill_breakpoint_catalog.csv`**，確認列與 **Phase 4E closure matrix** 仍分工清楚（矩陣不改策略維持）。  
4. **E2E**：可對 **`adaptive_practice_v2.html`** 走一輪「bootstrap → 填答 → 下一題」，確認 **`problem_type_id`** 與批改鏈路。

---

**結論：** adaptive v2 已在 **`session_engine`** 與 **`practice`** 共用 **`b4_chapter1_deterministic_allowlist`** 與 **`validate_b4_deterministic_adaptive_generator_payload`**；排除題型無法再以 generator 成功路徑直接輸出給學生；catalog 層級預先剔除非 allowlisted／manual_review B4；並透過 **`b4_deterministic_catalog_audit`** 與 **`adaptive_audit`** 強化可追溯性。
