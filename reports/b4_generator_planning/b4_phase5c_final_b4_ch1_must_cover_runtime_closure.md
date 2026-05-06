# Phase 5C-Final：B4 Chapter 1 Must-Cover Runtime Closure

## 1. Closure 目的

Phase 5C 目標是補齊 **技術型高中 B4 Chapter 1** 在 **章節單元練習（deterministic、int-answer）** 路徑下，教師指出的 **課本／統測常見題型** 缺口，並確保題型在 router、validator 與實際抽樣中可達；**不**將完整展開、樹狀圖、巴斯卡推導等納入現行 int-answer runtime。

---

## 2. Phase 5C 已完成項目總表

| 階段 | skill_id（代表） | problem_type_id（代表／重點） | 題型說明 | Router | Validator | Unit practice 曝光（D1-Fix 後） | QA |
|------|------------------|-------------------------------|----------|--------|-----------|----------------------------------|-----|
| **5C-B4** small template enrichment | `vh_數學B4_RepeatedPermutation` 等 | `repeated_permutation_digits`、`add_principle_mutually_exclusive_choice`、`combination_definition_basic`、`combination_properties_simplification`、`non_distinct_objects_arrangement` 等 | 語境／template／variant 擴充，不新增核心題型 id | 是 | 通過 | **visible**（D1 smoke 已觀察多 template_context／variant） | 既有 small template batch 與 allowlist smoke |
| **5C-B3-A** | `vh_數學B4_BinomialTheorem` | `binomial_two_variable_specific_coefficient`、`binomial_laurent_specific_power_coefficient` | 二變數指定項係數、Laurent 型指定次方係數 | 是 | 通過 | **visible**（seed 1–500：6／10） | 專測 + 回歸 |
| **5C-B3-B** | `vh_數學B4_CombinationApplications` | `grid_shortest_path_count` | 棋盤格最短路徑（basic／via／avoid） | 是 | 通過 | **visible**（9） | 專測 + 回歸 |
| **5C-B4.1** | `vh_數學B4_PermutationOfDistinctObjects` | `permutation_non_adjacent_arrangement` | 不相鄰排列（插空） | 是 | 通過 | **visible**（11） | 專測 + 回歸 |
| **5C-B4.2** | `vh_數學B4_FactorialNotation` | `factorial_equation_solve_n`（多 variant） | 階乘方程變形 | 是 | 通過 | **visible**（17） | 專測 + 回歸 |
| **5C-D1-Fix** | 全 allowlist 技能池 | （沿用既有 `problem_type_id`） | 解耦外層 `gen_seed` 選技能與內層 router 選子題型，避免多題型鎖死 | 是 | 通過 | **由 not_seen → visible**（見 §4） | `test_phase5c_d1_fix_b4_router_sampling_exposure.py` 等 |
| **5C-D2** | `vh_數學B4_BinomialCoefficientIdentities` | `combination_hockey_stick_sum` | 標準 hockey-stick：$C(r,r)+\cdots+C(n,r)=C(n+1,r+1)$ | 是 | 通過 | **visible**（seed 1–500：13，first_seen 14） | `test_phase5c_d2_combination_hockey_stick_generator.py` + 回歸 |

---

## 3. 教師 must-cover 題型 closure 對照

| 題型意涵 | 狀態 |
|----------|------|
| 兩類各選一人（乘法原理） | **已支援** |
| 質因數分解求正因數個數 | **已支援** |
| 階乘方程變形 | **已補**（`factorial_equation_solve_n`） |
| 角色分派排列 | **已支援** |
| 相鄰排列 | **已支援** |
| 不相鄰排列 | **已補**（`permutation_non_adjacent_arrangement`） |
| 棋盤格最短路徑 | **已補**（`grid_shortest_path_count`） |
| 組合數總和 | **已有**（`binomial_coefficient_sum`）；**可能仍需 wording calibration** |
| 奇偶項係數和 | **已有**（`binomial_odd_even_coefficient_sum`）；**可能仍需 wording calibration** |
| hockey-stick／組合遞移和 | **已補標準型**（`combination_hockey_stick_sum`）；**shifted／複雜錯列和本階段不做** |
| 二變數二項式指定項 | **已補** |
| Laurent 型指定次方係數 | **已補** |
| 完整二項式展開 | **保留 future AI-judged**（excluded policy） |
| 樹狀圖列舉 | **保留 manual_review／future AI-judged** |
| 巴斯卡三角形推導 | **保留 manual_review／future AI-judged** |

---

## 4. Unit practice exposure 結論

- **D1 前**：外層與內層共用同一 `Random(gen_seed)` 首抽，Phase 5C 新補之多題型技能下 **B3-A／B3-B／B4.1／B4.2 等近乎全部 not_seen**。
- **D1-Fix 後**：內層改為穩定派生 `inner_router_seed`，同窗 seed 1–500 下上述題型 **皆轉為 visible**；`combination_hockey_stick_sum` 在 D2 後同條件下 **visible**。
- **excluded 題型**：抽樣中 **0 次**（與 allowlist／validator 一致）。
- **validator**：**failures = 0**。

---

## 5. 仍未處理項目與停止線

- **shifted／complex staggered 組合和**：**暫不做**（D2.1 不開；避免未經嚴格驗證的公式一般化）。
- **完整二項式展開**：**不進**現行 int-answer deterministic runtime。
- **樹狀圖／巴斯卡**：**不硬接**；維持 manual_review／future AI-judged。
- **`binomial_coefficient_sum`／`binomial_odd_even_coefficient_sum`**：可列 **P2 題感／wording 優化**，**不列為 Phase 5C blocking**。

---

## 6. Pilot readiness 判斷

B4 Chapter 1 目前已達成：

- chapter entry 可用（含 vocational／數學B4／chapter_id=1 橋接）。
- teaching mode 可連續練習；答錯可進補救（既有 remediation 設計未在本階段破壞）。
- must-cover **int-answer** 題型大多已支援並可經 router 產生。
- D1-Fix 後，新題型可在 **unit practice 抽樣** 中出現；D2 hockey-stick 亦已可見。

**結論：可進入教師 QA／pilot manual smoke。**

---

## 7. 下一階段建議

1. **Phase 5D-A**：B4 Chapter 1 **Teacher QA Manual Smoke**（課本對照、用語、難度窗、錯題路徑）。
2. 或 **Phase 5D-B**：小規模學生 pilot（觀察曝光與疲勞度）。
3. **AI-judged 題型** 與 **B4 YAML subskill ontology** 等大面積工作：**暫列後續大階段**，不與 Phase 5C closure 混線。

---

*本檔為 Phase 5C 正式收斂之唯讀 closure 報告；未修改 production code、tests、generators、coverage matrix 或 adaptive routing。*
