# B1 QIS Checker 修復、SubSection332 確認與健康分層

## 任務一：QIS Checker

### 根因（非硬編碼特例）

Skill：`vh_數學B1_QuadraticInequalitySolution`  
題型：`integer_reverse_quadratic_inequality_coefficients`

1. Slot／metadata／induced spec／GENERATOR_SPECS 皆正確指向 **`integer_checker` + `numeric_exact`**。
2. Component generate 產出整數答案，且設 `checker_type=integer_checker`，但**未嵌入** `answer_contract`。
3. V3 package `_merge_generator_spec` 見空 contract 後呼叫 `_minimal_answer_contract`。
4. 舊樣板對所有非選題短答**硬編碼** `linear_equation_equivalent_checker` → 整數正解被判 False。

### 修復

| 檔案 | 變更 |
|---|---|
| `core/gencode/skill_wrapper_compiler.py` | `_minimal_answer_contract` 依 SPECS／payload／`answer_type` 預設表選 Checker；禁止非方程式題型保留 linear_equation |
| `core/gencode/slot_generators.py` | `generate_from_problem_type_spec` 缺省時嵌入 induced `answer_contract` |
| 重渲 B1 7 支 package／facade | 套用新樣板（含 QIS） |

### 測試前後

| 項目 | 修復前 | 修復後 |
|---|---|---|
| reverse 4 components 正解 self-check | 4 FAIL | **4 PASS** |
| QIS 全 29 components 正解 self-check | 25/29 | **29/29** |
| `tests/gencode/test_qis_reverse_coefficient_checker.py` | — | **PASS**（正確／錯誤／等價形式／全題型） |

未將 Checker 改成一律接受；錯誤整數仍 FAIL。

## 任務二：SubSection332

| 項目 | 結果 |
|---|---|
| Skill ID | `vh_數學B1_SubSection332` |
| 中文名 | 分式 |
| category | `3-3 因式分解與分式`（**不是** outline） |
| curriculum | B1／3 式的運算／3-3／paragraph=分式／active |
| textbook_examples | **0** |
| facade / package / generate.py | **皆無** |
| 同節正式 Skill | `vh_數學B1_RationalExpressionArithmeticOperations`、`vh_數學B1_RationalEquation` |
| outline | `outline_vocational_數學B1_33`（章節大綱） |

**結論**：這是教材匯入遺留的**空殼可執行 Skill 註冊**（命名像小節容器），**不是** outline，也**沒有** Generator 誤放他處。本輪**不**建立虛假 Generator。

**後續建議**（待人工）：

1. 若「分式」應併入既有 Rational\* Skill → 停用／合併 `SubSection332` 並清理 curriculum。  
2. 若需獨立 Skill → 依 Stage 1 教材匯入後再走 Gencode V3。  
3. 在管理中心將「可執行但 0 題型」標 WARN（已於盤點函式調整）。

## 任務三：健康狀態分層（不得混用）

| 層級 | 意義 | 本輪證據範圍 |
|---|---|---|
| 靜態 Registry | facade／package／可用 `problem_type_id` | 盤點 `health` |
| Runtime 可用 Generator | 能選用並出題 | 局部 smoke |
| Checker 驗證 | 正解／錯答契約 | QIS 測試＋抽樣 |
| Promotion Gate | domain evidence／publish eligible | **未通過、未繞過** |
| 學生端驗收 | 正式學習流程 | **未做** |

盤點 `health=PASS` **只代表靜態 Registry／可用題型盤點**，不是完整出題驗收。

可執行 Skill 題型數＝0 → **不得**再標靜態 PASS（改 WARN + `executable_skill_with_zero_usable_types`／`no_generator_artifacts`）。

### B1 靜態盤點（本輪後，可執行 35）

| 靜態 health | 數量 |
|---|---:|
| PASS | **33** |
| WARN | **2**（`SubSection332` 0 題型；`NumberLine` bootstrap） |
| FAIL | 0 |

- 題型數＝0 可執行：`vh_數學B1_SubSection332` → **WARN**（不再隱藏於 PASS）  
- QIS：靜態 PASS；Checker 層 29/29 self-check PASS  

## 任務四：回歸

| 項目 | 結果 |
|---|---|
| QIS 全部可用題型／29 components | PASS |
| PointAndLine | PASS |
| ParallelLines | PASS |
| SlopeOfALine | PASS |
| src_4584 映射 | PASS（∈ PointAndLine，∉ Parallel） |
| inventory 單元測試 | PASS |

## 仍待處理

1. SubSection332 人工決策（合併／停用／正式建置）。  
2. B1 二次函數族正式 Promotion Gate（domain evidence）仍未通過。  
3. NumberLine 仍為 JH bootstrap。  
4. 學生端實機驗收未做。  
5. Flask 5001 若已載入舊 package，需受控 reload 後管理中心／Runtime 才吃到新 `__init__.py`。

**本輪停止，等待人工驗收。**
