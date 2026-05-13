# Gencode × B4 整合前盤點 Round 3：B4 Runtime / Router / Allowlist / Adaptive Gating 盤點

本報告旨在盤點 B4 (技高數 B 第四冊) 在 Runtime 環境下的取題路徑、Generator 註冊機制、Allowlist 限制以及 Adaptive Gating 現況，為後續將 Gencode 生成物整合至正式生產路由提供依據。

---

## 1. B4 Router / Registry 盤點

目前 B4 的路由真相完全硬編碼 (Hardcoded) 於 Python 檔案中，缺乏動態配置能力。

| registry_name | file_path | 資料結構類型 | key | value 包含欄位 | 支援章節 | 支援 skill 數 | 支援 problem_type 數 | 備註 |
|---|---|---|---|---|---|---|---|---|
| `_REGISTRY` | `question_router.py` | `dict[str, list[dict]]` | `skill_id` | `subskill_id`, `problem_type_id`, `generator_key`, `generator_fn` | Chapter 1 | 13 | ~28 | 主要為排列組合與二項式。 |
| `_ENRICHMENT_REGISTRY` | `question_router.py` | `dict[str, list[dict]]` | `skill_id` | 同上 | Chapter 1 | 1 | 1 | 多重集合排列的補充路由。 |
| `_CHAP2_PHASE6C1_REGISTRY` | `question_router.py` | `dict[str, list[dict]]` | `skill_id` | 同上 | Chapter 2 | 10 | 17 | 機率與期望值。 |
| `_CHAP3_PHASE7B_REGISTRY` | `question_router.py` | `dict[str, list[dict]]` | `skill_id` | 同上 | Chapter 3 | 4 | ~10 | 統計量數與線性轉換。 |

### 關鍵觀察：
1.  **映射關係**：支援 **One-to-Many** (一個 `skill_id` 對應多個 `problem_type_id` / `generator_key`)。
2.  **狀態缺失**：Registry 中 **完全沒有** `runtime_ready` 或 `manual_review` 欄位，這些狀態目前散落在 allowlist 檔案與 reports 中。
3.  **路由隔離**：Chapter 2 與 Chapter 3 的路由函數 (`generate_for_chap2_skill`) 與 Chapter 1 獨立，邏輯略有不同。

---

## 2. B4 Generator 模組盤點 (`core/vocational_math_b4/generators/`)

| generator_file | 主要支援章節 | functions/classes | generator_key 範例 | answer_type | checker_type | 是否被 router 註冊 | 備註 |
|---|---|---|---|---|---|---|---|
| `counting.py` | Ch 1 | `generate`, `factorial_equation_solve_n` | `b4.counting.repeated_permutation_digits` | numeric | `check_integer_answer` | 是 | |
| `permutation.py` | Ch 1 | `generate`, `non_distinct_objects_arrangement` | `b4.permutation.permutation_role_assignment` | numeric | `check_integer_answer` | 是 | |
| `binomial.py` | Ch 1 | `binomial_coefficient_sum`, etc. | `b4.binomial.binomial_coefficient_sum` | numeric | `check_integer_answer` | 是 | |
| `chap2_prob_basic.py` | Ch 2 | `classical_probability_fraction`, etc. | `b4.chap2.classical_probability_fraction` | rational | `check_rational_answer` | 是 | |
| `chap3_stat.py` | Ch 3 | `mean_basic_numeric`, etc. | `b4.chap3.mean_basic_numeric` | numeric | `check_integer_answer` | 是 | 檔案極大 (168KB) |

### 關鍵觀察：
*   **Payload 結構**：所有 Generator 均回傳包含 `router_trace` 的標準化字典，有利於後台稽核。
*   **Excluded Types**：Listing (列舉型) 題目如 `sample_space_listing` 被明確排除在 deterministic 路由外，保留給手寫/AI 判分。

---

## 3. B4 Validator / Checker 盤點

| validator_file | function/class | 支援 answer_type | 支援 problem_type | 被誰呼叫 | 可否作為 runtime_ready gate | 備註 |
|---|---|---|---|---|---|---|
| `b4_validators.py` | `validate_problem_payload_contract` | N/A | 所有 | Generator | 是 | 檢查 Payload 欄位完整性。 |
| `b4_validators.py` | `check_rational_answer` | rational | 機率題 | `practice.py` | 否 | 運行時判定學生答案。 |
| `b4_validators.py` | `check_integer_answer` | numeric | 排列組合/計數 | `practice.py` | 否 | |
| `b4_validators.py` | `check_expected_value_answer` | rational | 期望值 | `practice.py` | 否 | |

---

## 4. Practice Runtime 呼叫鏈盤點

| 階段 | file_path | function/route | 如何判斷 B4 | 如何選 generator | 備註 |
|---|---|---|---|---|---|
| 進入 practice 頁面 | `practice.py` | `practice()` | `skill_id.startswith("vh_")` | N/A | 檢查 `MANUAL_REVIEW_SKILLS`。 |
| get_adaptive_question API | `practice.py` | `get_adaptive_question()` | `is_pure_b4_allowlisted_adaptive_pool` | `pick_rng.choice` | **Generator-First**：純 B4 技能池不查 DB。 |
| 判斷 skill_id / volume | `practice.py` | `next_question()` | `is_b4_chapter2_phase6c1_deterministic_skill` | `generate_for_chap2_skill` | 攔截 legacy `import skills.<id>`。 |
| 取得 generator output | `question_router.py` | `generate_for_skill()` | N/A | 查 `_REGISTRY` | 透過 `seed` 決定 `problem_type`。 |
| check_answer | `practice.py` | `check_answer()` (未列出但存在) | `is_b4_chapter2_...` | N/A | 調用 `check_rational_answer` 等。 |

---

## 5. Adaptive / Remediation Gating 盤點

| component | file_path | function/class | allowlist 來源 | 支援 chapter mode | 支援 remediation | 備註 |
|---|---|---|---|---|---|---|
| Ch 1 Allowlist | `b4_chapter1_..._allowlist.py` | `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` | 硬編碼 Set | 是 | 是 | 定義了 `REMEDIATION_BRIDGE`。 |
| Ch 2 Allowlist | `b4_chapter2_..._allowlist.py` | `B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST` | 硬編碼 Set | 是 | 待確認 | 分階段開放 (6C-1, 6D, 6E...)。 |
| Gating Func | `practice.py` | `filter_skill_pool_...` | 調用上述 allowlist | N/A | N/A | 在自適應出題前過濾掉非 ready 技能。 |

---

## 6. Runtime Ready / Manual Review 狀態來源盤點

目前狀態資訊高度碎片化：

| 狀態來源 | file_path | 狀態類型 | 是否被 runtime 讀取 | 備註 |
|---|---|---|---|---|
| `b4_chapter1_deterministic_allowlist.py` | `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` | Runtime Ready | **是** | 自適應練習的最高真相。 |
| `practice.py` | `MANUAL_REVIEW_SKILLS` | Manual Review | **是** | 控制前端是否顯示「暫緩開放」。 |
| `reports/b4_generator_planning/` | `b4_ch1_runtime_coverage_matrix.csv` | 多種狀態 | 否 | 離線追蹤矩陣，包含 25/28 Ready 統計。 |
| `question_router.py` | `_REGISTRY` | 已註冊題型 | **是** | 雖然不帶狀態，但沒註冊就無法出題。 |

---

## 7. B4 與舊版 Gencode 的相容性判斷

1.  **單位對接**：舊版 Gencode 以 `skill_id` (檔案) 為單位，B4 以 `problem_type` (Router 條目) 為單位。
    *   *建議*：一個 Gencode `.py` 檔案應能對應 B4 的一個 `problem_type`。
2.  **Candidate 機制**：目前生成後直接覆蓋 `skills/{skill_id}.py` 存在風險。
    *   *建議*：Gencode 生成物應先存入 `generated_candidates/{skill_id}_{timestamp}.py`，經人工驗證後再更新 `question_router.py`。
3.  **Registry 演進**：不應立刻強攻 DB。
    *   *建議*：先建立 `configs/b4_dynamic_registry.json`，讓 `question_router.py` 具備讀取 JSON 的能力，作為硬編碼與 DB 之間的過渡。
4.  **不適合自動生成的題型**：圖形題 (Chart reading)、需要複雜佈局的表格題、以及涉及開放式邏輯證明的題目。

---

## 8. 自動化程度評分 (Levels)

| 功能 | 等級 | 依據 | 缺口 |
|---|---|---|---|
| B4 problem_type registry | Level 2 | 全部 Hardcoded 在 `question_router.py`。 | 缺乏動態新增介面。 |
| B4 generator runtime 呼叫 | Level 3 | 有完整的 Router 鏈，但狀態判斷散落。 | 狀態判斷不統一。 |
| B4 checker / validator | Level 4 | 具備標準化的 `b4_validators` 並能自動判分。 | 無。 |
| B4 runtime_ready gate | Level 2 | 依靠 `allowlist.py` 手動維護 Set。 | 缺乏資料庫標記位。 |
| B4 adaptive allowlist | Level 3 | 具備 Preflight 過濾邏輯。 | 依賴硬編碼 Set。 |

---

## 9. 總結與風險建議

### 整合最大風險前三項：
1.  **狀態不一致 (State Drift)**：Reports CSV、Allowlist Python 與 Practice Route 三者狀態可能不同步，導致已生成代碼卻無法進入學生端。
2.  **路由爆炸 (Registry Bloat)**：隨著 `problem_type` 增加，`question_router.py` 會變得難以維護，急需動態化。
3.  **Gencode 單位衝突**：舊版 `skills/{skill_id}.py` 與 B4 多題型架構的映射關係尚未在生產代碼中正式定義。

### 第一批 Gencode Prototype 建議：
優先選擇 **Chapter 2 (機率運算)** 與 **Chapter 3 (基礎量數)** 中尚未被 deterministic 覆蓋、但已有課本例題的「單純數值/分率題型」，例如：
*   `expectation_mixed_algebra` (期望值的代數混和運算)
*   `weighted_mean_context_variants` (加權平均數的場景變體)

---
*報告完成日期: 2026-05-13*
*盤點人員: Antigravity AI*
