# B4 Chapter 2 Phase 6C-1 Deterministic Probability Minimal Batch Summary

## 0. Scope and Guardrails

本輪只處理 3 個 problem_type：
1. `classical_probability_fraction` → `vh_數學B4_ProbabilityDefinition`
2. `complement_probability` → `vh_數學B4_ProbabilityProperties`
3. `sample_space_count_numeric` → `vh_數學B4_SampleSpaceAndEvents`

明確聲明：
- ✅ 未修改 database
- ✅ 未修改 coverage matrix
- ✅ 未修改 adaptive scoring / mastery / APR / remediation
- ✅ 未處理 handwriting / free-response 題型
- ✅ 未加入 `sample_space_listing` / `event_set_listing` / `subset_listing` 到 deterministic allowlist
- ✅ 未修改 templates
- ✅ 未修改 unrelated routes 或 generators
- ✅ 未啟動 Phase 6C-2 / 6D / 6E

---

## 1. Files Changed

| 動作 | 檔案路徑 | 說明 |
|---|---|---|
| **新增** | `core/vocational_math_b4/generators/chap2_probability_basic.py` | 3 個 problem_type generator |
| **修改（追加）** | `core/vocational_math_b4/domain/b4_validators.py` | 新增 `check_rational_answer`、`check_integer_answer`、`check_probability_range`、私有 helper |
| **修改（追加）** | `core/vocational_math_b4/services/question_router.py` | 新增 `_CHAP2_PHASE6C1_REGISTRY` 與 `generate_for_chap2_skill`（隔離於 Chap1 `_REGISTRY`）|
| **新增** | `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` | Chap2 Phase 6C-1 deterministic allowlist（3 skills，排除 handwriting listing）|
| **新增** | `tests/test_b4_chap2_phase6c1_probability_basic.py` | 95 個測試案例 |
| **新增** | `reports/b4_generator_planning/b4_phase6c1_deterministic_probability_minimal_summary.md` | 本報告 |

**未修改的既有檔案：**
- `b4_chapter1_deterministic_allowlist.py`（未動）
- 所有 Chap1 generator（未動）
- 所有 templates / routes（未動）

---

## 2. Implemented Problem Types

| problem_type | skill_id | generator function | checker | answer format | notes |
|---|---|---|---|---|---|
| `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` | `classical_probability_fraction()` | `check_rational_answer` (flexible) | 最簡分數字串 `"a/b"` | 3 種情境：colored_balls / integer_range / card_draw |
| `complement_probability` | `vh_數學B4_ProbabilityProperties` | `complement_probability()` | `check_rational_answer` (flexible) | 最簡分數字串 `"a/b"` | 2 種情境：direct_given_pa / colored_balls_complement |
| `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` | `sample_space_count_numeric()` | `check_integer_answer` (strict) | 非負整數 | 3 種情境：coin_tosses / dice_rolls / sequential_choices；不要求學生列出樣本空間 |

---

## 3. Checker Implementation Summary

### `check_rational_answer`
- 接受：`"1/2"`、`"2/4"`（等值未化簡）、`"0.5"`（flexible）、`"50%"`（flexible）、`\frac{1}{2}`、`\dfrac{1}{2}`、`$\frac{1}{2}$`
- strict_fraction=True 時只接受 plain fraction 或 integer，拒絕小數/百分比
- 機率範圍守衛：expected 答案超出 [0,1] 時 raise ValueError
- 防 denominator=0、防 None/空白
- 支援全形數字轉半形

### `check_integer_answer`
- 接受：整數字串 `"36"`、int `36`、帶空白 `" 36 "`、全形 `"３６"`
- 拒絕：`"36.0"`（小數）、`"72/2"`（分數）、`"36%"`（百分比）、負整數（預設）
- allow_negative=True 時允許負整數

### `check_probability_range`
- 接受：`[0, 1]` 範圍內的數值（含邊界）
- 超出範圍：raise ValueError with "probability must be between 0 and 1"

---

## 4. Router / Allowlist Changes

### Router（`question_router.py` 追加）
- 新增 `_CHAP2_PHASE6C1_REGISTRY`（與 Chap1 `_REGISTRY` 完全隔離）
- 新增 `generate_for_chap2_skill()` 入口點
- 只接受 3 個 Chap2 P0 skill/problem_type

### Allowlist（新增 `b4_chapter2_phase6c1_allowlist.py`）
- `B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST`：3 個 skills
- `B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES`：3 個 problem_types
- `B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES`：`sample_space_listing` / `event_set_listing` / `subset_listing`（hard excluded）
- `validate_b4_chap2_phase6c1_generator_payload()`：payload 驗證
- Chap1 allowlist（`b4_chapter1_deterministic_allowlist.py`）**完全未修改**

確認：Chap2 3 個 skills **不在** Chap1 allowlist 中（測試確認無 overlap）。

---

## 5. Tests Run

```
python -m pytest tests/test_b4_chap2_phase6c1_probability_basic.py -v
```

**95 passed in 0.22s**

```
python -m pytest tests/test_b4_chapter1_adaptive_allowlist.py \
                 tests/test_vocational_math_b4_question_router_registry_canonical.py -v
```

**32 passed in 0.04s（Chap1 回歸全通過）**

測試涵蓋：
- checker tests：rational（等值/strict/range/invalid）、integer（格式/值/邊界）、probability_range
- generator tests：payload 完整性、answer 格式、probability range、分數化簡、choices 含答案、question 不含 listing 要求
- router tests：3 個 P0 skills 可生成、不支援 skill raise ValueError、Chap1 不受影響
- allowlist boundary tests：handwriting excluded、未開放 skill 不在 allowlist、validate_payload 各種邊界
- multi-seed smoke：6 個 seed × 3 個 skills = 18 案例全通過

---

## 6. Manual Smoke

Manual smoke 未執行（需 Flask app 啟動）。

建議手動確認項目：
- `GET /practice?skill=vh_數學B4_ProbabilityDefinition&problem_type=classical_probability_fraction` 能抽到古典機率題
- 送出正確答案（如 `1/3`）→ correct
- 送出等值答案（如 `0.333...`）→ flexible mode 下 correct
- `GET /practice?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=sample_space_count_numeric` 能抽到計數題
- 送出 `36.0` → 不應判 correct（integer strict）
- listing 題（`sample_space_listing`）不應出現在 deterministic flow

---

## 7. Risks / Known Limitations

| # | 限制 | 說明 |
|---|---|---|
| L1 | 尚未處理 `union_intersection_probability` | Phase 6C-2 |
| L2 | 尚未處理 `dice_coin_probability_count` | Phase 6C-2 |
| L3 | 尚未處理 `set_operation_count` / `inclusion_exclusion_count` | Phase 6C-2 |
| L4 | 尚未處理 handwriting listing | Phase 6F |
| L5 | 尚未處理 adaptive scoring / mastery / APR / remediation | 需另開 phase |
| L6 | needs_review 87 題全待人工確認 | DB 資料品質問題；本輪 generator 使用獨立參數化生成，不依賴 DB 題目 |
| L7 | `classical_probability_fraction` integer_range 情境固定只出奇數/偶數 | 未來可擴充更多情境 |
| L8 | `generate_for_chap2_skill` 尚未接入現有 `/practice` route | 需確認 practice.py 是否需要路由 Chap2；未在本輪修改 |
| L9 | manual smoke 未執行 | 需環境啟動確認 |

---

## 8. Final Confirmation

| 項目 | 狀態 |
|---|---|
| 是否只處理 3 個 problem_type | ✅ 是 |
| 是否修改 production code | ✅ 是，限於本輪必要檔案（b4_validators.py 追加、question_router.py 追加） |
| 是否修改 tests | ✅ 是，限本輪新測試檔 |
| 是否修改 routes | ✅ 否（未修改 routes/practice.py） |
| 是否修改 templates | ✅ 否 |
| 是否修改 generators | ✅ 是，限新增 chap2_probability_basic.py |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否新增 deterministic allowlist | ✅ 是，只限 3 個 P0 題型（b4_chapter2_phase6c1_allowlist.py） |
| 是否加入 handwriting/free-response 題型 | ✅ 否（`sample_space_listing` 等明確 excluded） |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否啟動 Phase 6C-2 / 6D / 6E | ✅ 否 |
| 是否有越界修改 | ✅ 否 |

---

## 9. Recommended Next Phase

**Phase 6C-2：Chap2 second deterministic probability batch**

建議 scope：
- `union_intersection_probability`（ProbabilityProperties）
- `dice_coin_probability_count`（ProbabilityDefinition，排除 image-related 2 筆）
- `set_operation_count` + `inclusion_exclusion_count`（BasicConceptsOfSets，可合一 generator）

前提：
- 本 Phase 6C-1 manual smoke 通過
- 人工確認至少 1 筆每個 problem_type 的題目品質

---

*Phase 6C-1 完成。停在此處，等待人工 approve。*  
*狀態：READY_FOR_REVIEW*
