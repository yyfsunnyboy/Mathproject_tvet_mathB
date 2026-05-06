# Phase 5C-C：B4 Chapter 1 Must-Cover Closure Audit

## 1. Closure Audit 目的

本報告用來確認：在 Phase 5C 多輪補強後，教師人工指出的課本／統測常見題型中，

- 哪些已補齊且可於 Chapter unit practice 出現；
- 哪些雖有對應但仍可能需要曝光校準（exposure calibration）；
- 哪些仍屬真缺口（missing_generator）；
- 哪些依現行 deterministic int-answer 政策不應納入（manual_review / future_ai_judged / excluded）。

本次僅做唯讀盤點，未修改 production code、tests、generators、coverage matrix、adaptive routing。

---

## 2. 已補強題型總表

| phase | skill_id | problem_type_id | 題型說明 | 是否 int-answer | 是否 router connected | 是否 adaptive allowlisted | QA result | 備註 |
|------|----------|-----------------|----------|------------------|------------------------|----------------------------|----------|------|
| 5C-B4 | `vh_數學B4_RepeatedPermutation` | `repeated_permutation_digits` | 重複排列題幹語境擴充（template enrichment） | 是 | 是（`_repeated_permutation_digits` fallback） | 是 | `100 passed`（B4 small template batch） | 不新增新題型，僅敘述與參數語境擴充 |
| 5C-B4 | `vh_數學B4_AdditionPrinciple` | `add_principle_mutually_exclusive_choice` | 加法原理語境擴充 | 是 | 是 | 是 | 同上 | scenario/template 擴充 |
| 5C-B4 | `vh_數學B4_CombinationDefinition` | `combination_definition_basic` | 組合定義題幹語境擴充 | 是 | 是（`_combination_definition_basic` fallback） | 是 | 同上 | 單一題型但多 template_context |
| 5C-B4 | `vh_數學B4_CombinationProperties` | `combination_properties_simplification` | 組合性質 variant 擴充 | 是 | 是 | 是 | 同上 | 含 `two_term_sum` 等 |
| 5C-B4 | `vh_數學B4_PermutationOfNonDistinctObjects` | `non_distinct_objects_arrangement` | 不盡相異物語境擴充＋router 輪替可達 | 是 | 是（enrichment registry） | 是 | 同上 | 與 `repeated_permutation_digits` 輪替 |
| 5C-B3-A | `vh_數學B4_BinomialTheorem` | `binomial_two_variable_specific_coefficient` | 二變數二項式指定項係數 | 是 | 是 | 是 | `104 passed`（專測）+ 回歸通過 | 新增 deterministic generator |
| 5C-B3-A | `vh_數學B4_BinomialTheorem` | `binomial_laurent_specific_power_coefficient` | Laurent 型指定次方係數 | 是 | 是 | 是 | 同上 | 新增 deterministic generator |
| 5C-B3-B | `vh_數學B4_CombinationApplications` | `grid_shortest_path_count` | 棋盤格最短路徑（basic/via/avoid） | 是 | 是 | 是 | `107 passed`（專測）+ 回歸通過 | 新增 deterministic generator |
| 5C-B4.1 | `vh_數學B4_PermutationOfDistinctObjects` | `permutation_non_adjacent_arrangement` | 不相鄰排列（插空法） | 是 | 是 | 是 | `106 passed`（專測）+ 回歸通過 | 保留原 `permutation_adjacent_block` |
| 5C-B4.2 | `vh_數學B4_FactorialNotation` | `factorial_equation_solve_n`（variant 擴充） | 階乘方程變形（ratio/multiply/sum/product） | 是 | 是（沿用既有 entry） | 是 | `108 passed`（專測）+ 回歸通過 | 沿用既有 problem_type，不新增 id |

---

## 3. 教師 must-cover 題型 closure 對照表

| 編號 | must-cover 題型 | 原始判定 | 目前狀態 | 對應 skill_id | 對應 problem_type_id | 是否可在 chapter unit practice 出現 | 是否仍需後續處理 | 建議 |
|---:|---|---|---|---|---|---|---|---|
| 1 | 兩類各選一人（乘法原理） | supported_visible | 已支援 | `vh_數學B4_MultiplicationPrinciple` | `mult_principle_independent_choices` | 是 | 否（僅曝光校準可選） | 保持現況，可做 D1 抽樣確認曝光 |
| 2 | 質因數分解求正因數個數 | supported_visible | 已支援 | `vh_數學B4_MultiplicationPrinciple` | `divisor_count_prime_factorization` | 是 | 否（僅敘述校準可選） | 保持現況 |
| 3 | 階乘方程變形 | partially_supported | 已補完核心變形 | `vh_數學B4_FactorialNotation` | `factorial_equation_solve_n`（4 variants） | 是 | 低（題感可再微調） | 先做曝光抽樣，不急於新題型 |
| 4 | 角色分派排列 | supported_visible | 已支援 | `vh_數學B4_PermutationOfDistinctObjects` | `permutation_role_assignment` | 是 | 否 | 保持現況 |
| 5 | 相鄰排列 | supported_visible | 已支援 | `vh_數學B4_PermutationOfDistinctObjects` | `permutation_adjacent_block` | 是 | 否 | 保持現況 |
| 6 | 不相鄰排列 | partially_supported（原） | 已補完 | `vh_數學B4_PermutationOfDistinctObjects` | `permutation_non_adjacent_arrangement` | 是 | 否 | 保持現況 |
| 7 | 棋盤格最短路徑 | missing_generator（原） | 已補完 | `vh_數學B4_CombinationApplications` | `grid_shortest_path_count` | 是 | 否 | 保持現況 |
| 8 | 組合數總和 | partially_supported | 已有但題感可能偏差 | `vh_數學B4_BinomialCoefficientIdentities` | `binomial_coefficient_sum` | 是 | 是（A 類） | 做 wording/exposure 校準 |
| 9 | 奇偶項係數和 | partially_supported | 已有但題感可能偏差 | `vh_數學B4_BinomialCoefficientIdentities` | `binomial_odd_even_coefficient_sum` | 是 | 是（A 類） | 做 wording/exposure 校準 |
| 10 | 組合遞移／錯列和（hockey-stick 類） | missing_generator | 仍缺 | `vh_數學B4_BinomialCoefficientIdentities` / `vh_數學B4_CombinationProperties` | 無專屬題型 | 否 | 是（B 類） | 優先評估新增 deterministic generator |
| 11 | 二變數二項式指定項係數 | missing_generator（原） | 已補完 | `vh_數學B4_BinomialTheorem` | `binomial_two_variable_specific_coefficient` | 是 | 否 | 保持現況 |
| 12 | Laurent 型二項式指定次方係數 | missing_generator（原） | 已補完 | `vh_數學B4_BinomialTheorem` | `binomial_laurent_specific_power_coefficient` | 是 | 否 | 保持現況 |
| 13 | 完整二項式展開 | excluded_or_future_ai_judged | 維持不納入 deterministic runtime | `vh_數學B4_BinomialTheorem` | `binomial_expansion_basic`（excluded） | 否（由 gate 阻擋） | 否（按政策） | 留在 future AI-judged backlog |
| 14 | 樹狀圖列舉 | excluded/manual_review | 維持不納入 deterministic runtime | `vh_數學B4_TreeDiagramCounting` | `tree_diagram_listing`（excluded） | 否 | 否（按政策） | 留在 manual_review / AI-judged |
| 15 | 巴斯卡三角形推導 | excluded/manual_review | 維持不納入 deterministic runtime | `vh_數學B4_PascalTriangle` | `pascal_triangle_derivation`（excluded） | 否 | 否（按政策） | 留在 manual_review / AI-judged |

---

## 4. 仍未處理或不完整項目

### A. 已有但可能需要 exposure calibration

- `binomial_coefficient_sum`（純 `C(n,k)` 和式題感仍可能不足）
- `binomial_odd_even_coefficient_sum`（題幹用語與課本卷面可能有落差）
- 若教師期待更貼近課本敘事，需做 template wording／sampling 曝光檢核，而非新 generator

### B. 仍為 missing_generator，但適合 deterministic int-answer

- **組合遞移／錯列和（hockey-stick／對角和）**：目前仍為真缺口（`combination.py`、`binomial.py` 無專屬題型）

### C. 不適合 current int-answer runtime

- 完整二項式展開（`binomial_expansion_basic`）
- 樹狀圖列舉（`tree_diagram_listing`）
- 巴斯卡三角形推導（`pascal_triangle_derivation`）

以上三者仍在 `B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`，符合現行政策。

### D. 已補完，不建議再動

- `grid_shortest_path_count`
- `permutation_non_adjacent_arrangement`
- `factorial_equation_solve_n` 變形（4 variants）
- `binomial_two_variable_specific_coefficient`
- `binomial_laurent_specific_power_coefficient`
- 5C-B4 小型模板補強（5 項）

---

## 5. 對單元練習的實際影響

- Phase 5C 後，B4 Chapter 1 在 deterministic int-answer 路徑的題型覆蓋明顯提升，特別是原先明確缺口：
  - 棋盤格最短路徑（任意／經過／不經過）
  - 排列不相鄰（插空法）
  - 二變數與 Laurent 指定項係數
  - 階乘方程變形（乘積與和式）
- 學生在單元練習中理論上可看到更接近統測常見題型，而不再集中於早期較窄的基礎型。
- 仍建議做 **seed sampling smoke** 或 **manual browser smoke**，確認「有支援」已轉化為「實際可見曝光」。

---

## 6. 下一步建議（不改程式）

- **Phase 5C-D1：chapter unit practice exposure sampling smoke**
  - 以 seed 範圍與瀏覽器實際抽題，驗證新題型是否穩定可見。
- **Phase 5C-D2：combination identity / hockey-stick deterministic generator**
  - 若要補齊剩餘真缺口，優先處理組合遞移／錯列和。
- **Phase 5C-D3：binomial coefficient sum wording enrichment**
  - 若教師仍覺得純 `C(n,k)` 題感不足，做敘述層校準。
- **Phase 5C-D4：future AI-judged backlog**
  - 統整完整展開、樹狀圖、巴斯卡等非 current int-answer 題型。

---

## 7. 建議優先順序（P1 / P2 / P3）

- **P1（coverage blocking）**
  - `5C-D2`：組合遞移／錯列和 deterministic generator（目前唯一明確 must-cover 真缺口）

- **P2（題感與曝光優化）**
  - `5C-D1`：unit practice exposure sampling smoke（確認新題型實際出現）
  - `5C-D3`：組合數總和／奇偶項和 wording 與曝光校準

- **P3（非 current deterministic int-answer）**
  - `5C-D4`：完整展開／樹狀圖／巴斯卡 future AI-judged backlog

---

## 建議決策（A 或 B）

以當前 closure 狀態，建議先走：

- **A（先做 exposure sampling smoke）**：快速驗證 5C 已補題型的可見度與體感；
- 若 D1 顯示曝光已可接受，再進入 **B（補組合恒等式 generator）** 做最後真缺口收斂。  

若團隊想先封鎖唯一功能缺口，也可直接先做 B；但就教學現場可見成效而言，A 會更快提供回饋。
