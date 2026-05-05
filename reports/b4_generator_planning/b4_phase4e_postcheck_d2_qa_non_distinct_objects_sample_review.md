# B4 Phase 4E Postcheck-D2-QA Non-Distinct Objects Sample Review

## 1. 本階段目的

本階段對 `non_distinct_objects_arrangement` 產出之 **固定參數樣題**（seed 1～5，`difficulty=1`，`multiple_choice=True`）做 **品質檢查與紀錄**。**Postcheck-D2-QA-Fix** 已將 **`colored_balls`** 題幹「其中」後補上空格，本報告為修正後之重製版。

（本 QA 文件僅紀錄結果；router／wrapper／coverage 接入仍依專案後續階段。）

## 2. 檢查範圍

| generator_key | function | skill_id | subskill_id | multiple_choice |
|---|---|---|---|---|
| `b4.permutation.non_distinct_objects_arrangement` | `non_distinct_objects_arrangement` | `vh_數學B4_PermutationOfNonDistinctObjects` | `b4_ch1_perm_non_distinct_objects_01` | `True` |

## 3. 總體檢查表

| generator_key | 樣題數 | unique_parameter_tuple 數 | choices_valid | answer_valid | latex_valid | semantic_valid | metadata_complete | placeholder_free | 初步判斷 |
|---|---:|---:|---|---|---|---|---|---|---|
| `b4.permutation.non_distinct_objects_arrangement` | 5 | 5 | 是 | 是 | 是 | 是 | 是 | 是 | **通過** |

## 4. 樣題清單

### seed = 1

- **question_text:** 用 A、A、B、C 共 4 個字母排成一列，共有多少種不同排列？
- **choices:** `[11, 12, 10, 6]`
- **answer:** `12`
- **explanation:** 若先把所有物件都當作相異，共有 $4!$ 種排列。但相同物互換不產生新排列，所以要除以相同物內部交換數。本題共有 $4$ 個物件，故不同排列數為 $\frac{4!}{2!1!1!}=12$。
- **parameters:**  
  `total_count=4`, `duplicate_counts=[2]`, `singleton_count=2`, `context=letters`,  
  `parameter_tuple=('non_distinct_objects_arrangement', 4, (2,), 2, 'letters')`
- **檢查結果:**
  - **semantic_valid:** 是
  - **choices_valid:** 是
  - **answer_valid:** 是
  - **latex_valid:** 是
  - **metadata_complete:** 是
  - **placeholder_free:** 是
  - **parameter_tuple_exists:** 是
  - **notes:** 無

### seed = 2

- **question_text:** 有 5 個物件，其中 2 個相同，其餘 3 個都不同，排成一列共有多少種不同排列？
- **choices:** `[30, 120, 58, 60]`
- **answer:** `60`
- **explanation:** 若先把所有物件都當作相異，共有 $5!$ 種排列。但相同物互換不產生新排列，所以要除以相同物內部交換數。本題共有 $5$ 個物件，故不同排列數為 $\frac{5!}{2!1!1!1!}=60$。
- **parameters:**  
  `total_count=5`, `duplicate_counts=[2]`, `singleton_count=3`, `context=objects`,  
  `parameter_tuple=('non_distinct_objects_arrangement', 5, (2,), 3, 'objects')`
- **檢查結果:**
  - **semantic_valid:** 是
  - **choices_valid:** 是
  - **answer_valid:** 是
  - **latex_valid:** 是
  - **metadata_complete:** 是
  - **placeholder_free:** 是
  - **parameter_tuple_exists:** 是
  - **notes:** 無

### seed = 3

- **question_text:** 有 6 個球，其中 2 個紅球相同、2 個白球相同、1 個黑球、1 個綠球，排成一列共有多少種不同排列？
- **choices:** `[179, 180, 178, 360]`
- **answer:** `180`
- **explanation:** 若先把所有物件都當作相異，共有 $6!$ 種排列。但相同物互換不產生新排列，所以要除以相同物內部交換數。本題共有 $6$ 個物件，故不同排列數為 $\frac{6!}{2!2!1!1!}=180$。
- **parameters:**  
  `total_count=6`, `duplicate_counts=[2, 2]`, `singleton_count=2`, `context=colored_balls`,  
  `parameter_tuple=('non_distinct_objects_arrangement', 6, (2, 2), 2, 'colored_balls')`
- **檢查結果:**
  - **semantic_valid:** 是
  - **choices_valid:** 是
  - **answer_valid:** 是
  - **latex_valid:** 是
  - **metadata_complete:** 是
  - **placeholder_free:** 是
  - **parameter_tuple_exists:** 是
  - **notes:** `colored_balls` 題幹已為「其中 」後接內容（Postcheck-D2-QA-Fix 排版修正）

### seed = 4

- **question_text:** 用 A、A、A、B、C、D 共 6 個字母排成一列，共有多少種不同排列？
- **choices:** `[118, 120, 119, 240]`
- **answer:** `120`
- **explanation:** 若先把所有物件都當作相異，共有 $6!$ 種排列。但相同物互換不產生新排列，所以要除以相同物內部交換數。本題共有 $6$ 個物件，故不同排列數為 $\frac{6!}{3!1!1!1!}=120$。
- **parameters:**  
  `total_count=6`, `duplicate_counts=[3]`, `singleton_count=3`, `context=letters`,  
  `parameter_tuple=('non_distinct_objects_arrangement', 6, (3,), 3, 'letters')`
- **檢查結果:**
  - **semantic_valid:** 是
  - **choices_valid:** 是
  - **answer_valid:** 是
  - **latex_valid:** 是
  - **metadata_complete:** 是
  - **placeholder_free:** 是
  - **parameter_tuple_exists:** 是
  - **notes:** 無

### seed = 5

- **question_text:** 有 5 個球，其中 3 個紅球相同、1 個黑球、1 個綠球，排成一列共有多少種不同排列？
- **choices:** `[20, 40, 18, 10]`
- **answer:** `20`
- **explanation:** 若先把所有物件都當作相異，共有 $5!$ 種排列。但相同物互換不產生新排列，所以要除以相同物內部交換數。本題共有 $5$ 個物件，故不同排列數為 $\frac{5!}{3!1!1!}=20$。
- **parameters:**  
  `total_count=5`, `duplicate_counts=[3]`, `singleton_count=2`, `context=colored_balls`,  
  `parameter_tuple=('non_distinct_objects_arrangement', 5, (3,), 2, 'colored_balls')`
- **檢查結果:**
  - **semantic_valid:** 是
  - **choices_valid:** 是
  - **answer_valid:** 是
  - **latex_valid:** 是
  - **metadata_complete:** 是
  - **placeholder_free:** 是
  - **parameter_tuple_exists:** 是
  - **notes:** 同 seed 3，`colored_balls` 排版已修正

## 5. parameter_tuple 重複性檢查

五組 **皆不重複**：

1. `('non_distinct_objects_arrangement', 4, (2,), 2, 'letters')`
2. `('non_distinct_objects_arrangement', 5, (2,), 3, 'objects')`
3. `('non_distinct_objects_arrangement', 6, (2, 2), 2, 'colored_balls')`
4. `('non_distinct_objects_arrangement', 6, (3,), 3, 'letters')`
5. `('non_distinct_objects_arrangement', 5, (3,), 2, 'colored_balls')`

## 6. context 覆蓋檢查

| seed | context |
|---:|---|
| 1 | `letters` |
| 2 | `objects` |
| 3 | `colored_balls` |
| 4 | `letters` |
| 5 | `colored_balls` |

已涵蓋 **letters／objects／colored_balls**（≥ 2 種）。**無需** seed 6～30 補充觀察。

## 7. 與 repeated choices 的語義區隔

- 題幹**未**使用「可重複使用」「每位可重複」「每次可重複選」「有幾個可用數字」等 **repeated choices** 語意。
- 本 generator 使用 **固定多重集合**（相同物／排成一列／求相異排列數），與 **`repeated_permutation_digits`（$m^n$ 類）** 有明確區隔。

## 8. 問題與建議

- **本次樣題未發現需登記之缺失**；`colored_balls`「其中」後空格已於 **Postcheck-D2-QA-Fix** 處理。
- **選擇性後續：** 仍可依產品需求擴充模板／參數（與先前決策文件一致），非本樣題阻塞項。

## 9. 結論

- **router 接入：** 本 generator 樣題與契約 **已可進入 Connect** 階段（實際接入仍依專案排程）。
- **QA-Fix：** **colored_balls 排版已完成**；無額外 QA-Fix 阻塞項。
- **temporary surrogate：** 仍建議後續以本題型作為 **`vh_數學B4_PermutationOfNonDistinctObjects` 主要語義對齊來源**，取代長期依賴 `repeated_permutation_digits`。

---

## 完成後回報欄位（收件用）

1. 是否修正 colored_balls 題幹排版：**是**（`其中 ` + `join(descriptions)`）。
2. focused pytest：**通過**，**11 passed**。
3. regression pytest：**通過**，**67 passed**。
4. 是否重新產出 QA 報告：**是**（本檔覆寫）。
5. QA 初步判斷：**通過**。
6. 是否修改 question_router／wrapper／domain／route／frontend／app.py／coverage matrix：**否**。
