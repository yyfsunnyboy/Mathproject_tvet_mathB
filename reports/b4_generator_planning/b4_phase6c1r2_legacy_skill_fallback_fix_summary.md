# B4 Chapter 2 Phase 6C-1R2 — Legacy Skill Module Fallback Fix Summary

## 1. 問題根因

### 為何出現 `No module named 'skills.vh_數學B4_ProbabilityDefinition'`

`/get_next_question`（`next_question`）在完成 DB bypass 並進生成迴圈**之前**，已執行：

```825:834:core/routes/practice.py
        module_path = f"skills.{skill_id}"
        ...
            mod = importlib.import_module(module_path)
```

Phase 6C-1R 僅在迴圈內 `elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id)` 呼叫 `generate_for_chap2_skill`，但 **`import_module` 在迴圈外就對所有非樹状圖／非巴斯卡請求發生**。Chap2 P0 deterministic 技能並無對應 `skills.<skill_id>.py`，故在進入路由器前即抛錯並被 except 包装成「生成題目失敗: No module named ...」。

### 為何 Phase 6C-1R 未覆蓋

6C-1R 修了 URL decode、`skill_info` bypass、生成迴圈內路由器與批改分支，但未移除／閘控上述**前置強制載入**，故實際「下一題」仍會先載入缺失的 legacy skills 模組。

### `/check_answer`

`check_answer` 雖優先進入批改分支，但若先呼叫 `get_skill(skill_id)` 仍會觸發 `importlib`。為符合「不得在 Phase 6C-1 deterministic 題型載入缺失模組」，已將 deterministic Chap2 **提前至 `get_skill` 之前**。

### `/get_adaptive_question`

若以後端適應題池抽到 Chap2 deterministic 技能，原路徑在 `mod = get_skill(...)`、`mod.generate` 同樣會失敗。本輪一併以路由器生成與 **not enabled** gate 對齊，避免再走 legacy skills 載入。

---

## 2. 修改檔案清單

| 動作 | 檔案 |
|---|---|
| **修改** | `core/routes/practice.py` |
| **修改（支援 gate）** | `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` |
| **新增** | `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py` |
| **修改** | `tests/test_b4_chap2_phase6c1r_practice_route_integration.py`（import sanity 擴充） |
| **新增** | `reports/b4_generator_planning/b4_phase6c1r2_legacy_skill_fallback_fix_summary.md`（本報告） |

未修改：database、coverage matrix、Chap1 allowlist、templates、Phase 6C-2 題型。

---

## 3. 修正方式摘要

### A. `next_question` — 延後／跳過 legacy import

- 對 `is_b4_chapter2_phase6c1_deterministic_skill(skill_id)`：改為 `mod = None`，**不** `import_module` / `reload`。
- 生成仍由既有迴圈內 `generate_for_chap2_skill` + `validate_b4_chap2_phase6c1_generator_payload` 處理。

### B. Chap2 gate（不啟用技能）

- 在 `b4_chapter2_phase6c1_allowlist.py` 新增 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` 與 `is_b4_chapter2_skill_not_enabled_in_phase6c1`。
- 在 `next_question` 於 `get_skill_info` 之前：若命中 gate，回傳 **HTTP 422**，`error` 固定為 **`Chap2 skill not enabled in Phase 6C-1`**，**不**嘗試 `skills.<id>` import。

### C. `get_adaptive_question`

- 在取得 `skill_id_for_generate` 後：同上 **not enabled** → 422。
- 若 `is_b4_chapter2_phase6c1_deterministic_skill(skill_id_for_generate)`：改走 `generate_for_chap2_skill` + chap2 payload 驗證；其餘才 `get_skill` + `mod.generate`。
- 回應 `answer_type` 改為 `data.get("answer_type", "text")`（與 deterministic payload 對齊）。

### D. `check_answer`

- 將 deterministic Chap2 批改區塊**移到** `mod = get_skill(skill_id)` **之前**，避免載入缺失模組。

---

## 4. 測試結果

以下於本環境最近一次執行皆 **全部通過**（`203 passed`，約 **135s**，含載入 Flask app／Advanced RAG 初始化）：

```
python -m pytest tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chap2_phase6c1r_practice_route_integration.py tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

---

## 5. Manual Smoke 指引

1. `/get_next_question?skill=vh_數學B4_ProbabilityDefinition&gen_seed=1` → 200，題幹非空，`answer_type` 為 rational / integer。
2. URL：`skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition` → 同上。
3. `/get_next_question?skill=vh_數學B4_BasicConceptsOfSets` → **422**，訊息 `Chap2 skill not enabled in Phase 6C-1`，不應出現 `No module named`。
4. `problem_type=sample_space_listing`（SampleSpace skill）→ 仍 **422**，handwriting reserved。
5. `/check_answer`：先取題再送分數／小數／百分比等值、`36.0`／`36%`（integer）應為錯。
6. Chap1：`/get_next_question?skill=vh_數學B4_AdditionPrinciple`（或既有 Chap1 smoke）仍可出題。

---

## 6. Final Confirmation

| 項目 | 確認 |
|---|---|
| 是否只處理 Phase 6C-1 三個 problem_type／三個 deterministic skill：是 |
| 是否新增 Phase 6C-2 題型：**否** |
| 是否處理 BasicConceptsOfSets 出題：**否**（維持不啟用） |
| 是否讓 BasicConceptsOfSets 不再嘗試 import missing skills module：**是**（422 gate） |
| 是否加入 handwriting/free-response：**否** |
| 是否修改 database：**否** |
| 是否修改 coverage matrix：**否** |
| 是否修改 adaptive scoring / mastery / APR / remediation：**否** |
| 是否修改 Chap1 allowlist：**否** |
| 是否啟動 Phase 6C-2：**否** |

---

*Phase 6C-1R2 完成。**狀態：READY_FOR_MANUAL_SMOKE**（請以實際 /practice 「下一題」再驗一次）。*
