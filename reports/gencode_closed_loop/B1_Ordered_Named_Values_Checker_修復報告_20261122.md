# B1 有序多值答案誤判修復報告

**日期**：2026-11-22  
**Skill**：`vh_數學B1_PolynomialBasicConcepts`  
**題型／Component**：`polynomial_param_degree_constraint`／`src_4610`（同源 `src_4619`、`src_4630`）  
**Source**：textbook_example_id **4610**  
**不 commit／不 push**；B2 導入暫停；不進 B3／B4

---

## 1. Root Cause（有證據）

| 層級 | 結論 |
|---|---|
| Generator | 正常。`part_1` canonical＝`a={a},b={b}`；`part_2`＝剩餘多項式 |
| answer_contract | Multipart；part checker＝`expression_checker`／`algebraic_equivalent` |
| **失敗層** | **共用 Checker**：`expression_equivalence_checker._assignment_lists_equivalent` |
| Multipart 組合 | 正常（(2) 多項式可判對；(1) 單獨誤判） |

**機制**：舊邏輯要求學生端也必須是 `name=value` 賦值列表。`0,3`／`0 3` 無 `=` → 回傳 `None` → 落入一般代數式解析 → 誤判錯誤。  
`a=0,b=3` 原本可過，故畫面呈現「(1) 錯、(2) 對」。

---

## 2. 修復方式（最小共用）

1. 擴充 `_assignment_lists_equivalent`：當 canonical 為具名賦值列表（或 part 含 `variable_order`）時：
   - 無標籤有序列表依變數順序（`0,3`／空白／全形／括號）
   - 有標籤依變數名（可交換順序）
   - 拒絕顛倒、錯標籤、數量不對；不拆一般代數式
2. Adapter／本題 Generator 補 `variable_order`＋`answer_shape=ordered_named_values`
3. `coordinate_pair_checker` 一併接受空白分隔座標（有序 pair）
4. **未**另建平行 Checker；**未**改 B2～B4 Generator；**未**改掌握制／導航

---

## 3. 修復前後（本題）

| 學生輸入 | 修復前 | 修復後 |
|---|---|---|
| `0,3`／`0 3`／`(0,3)` | FAIL | PASS |
| `a=0,b=3`／`a=0 b=3`／`b=3,a=0` | PASS（標籤）／部分 FAIL | PASS |
| `3,0`／`3 0`／`a=3,b=0` | FAIL | FAIL |
| 與正確多項式同交 | 部分正確 | 整題正確 |

---

## 4. 測試結果

| 項目 | 結果 |
|---|---|
| `tests/test_ordered_named_values_checker.py` | **PASS** |
| `tests/test_b1_answer_equivalence_regression.py` + v1.12 + assignment quality-gate | **PASS** |
| Runtime `grade_answer_for_current_question`（`0 3` 等） | **PASS**（見 `b1_ordered_named_values_runtime_check.json`） |
| B1 題型掌握腳本 `scripts/test_b1_type_mastery.py` | **15/15 PASS**（制度未改） |
| Multipart 部分正確回饋 | PASS（標出失敗 part） |
| B2～B4 Generator | **未修改**；共用 checker 回歸見既有 assignment／unordered／coordinate 測試 PASS |
| 真人瀏覽器／iPad | **NOT_TESTED**（待人工） |

---

## 5. SOP 更新

- `docs/系統SOP/數學答案檢核原則_v1.12_20260908.md` → **v1.12.2**「有序多值答案」
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §12.3：Multipart 須 `overall_correct` 才 MASTERED

---

## 6. 修改檔案

- `core/checkers/expression_equivalence_checker.py`
- `core/checkers/coordinate_pair_checker.py`
- `core/gencode/domain_matrix_adapter.py`
- `agent_skills_v3/.../src_4610|4619|4630/generate.py`
- `tests/test_ordered_named_values_checker.py`
- 上述 SOP／契約／本報告

## 7. 停止條件

修復與自動化回歸完成；**等待人工驗收**。暫停 B2 導入；不自動進入 B3／B4。
