# B4 Chapter 1 Missing Skill Wrapper / Generator Coverage Plan

## 1. 問題背景

目前系統 dashboard 上有多個 B4 Chapter 1 的 skill_id 按鈕可供點擊，但由於部分對應的 `skills/{skill_id}.py` wrapper 檔案尚未建立，當請求派發至舊版 runtime 時，會導致系統拋出 `No module named 'skills.xxx'` 的錯誤。為維持系統穩定擴充，本階段旨在盤點這些缺失的 wrapper，並擬定後續的實作與接入策略。

## 2. 目前已完成 wrapper

系統中已成功建立、接入 question_router 且通過 web smoke test 的 wrapper 如下：
- `vh_數學B4_CombinationDefinition`
- `vh_數學B4_CombinationApplications`
- `vh_數學B4_MultiplicationPrinciple`
- `vh_數學B4_PermutationOfDistinctObjects`
- `vh_數學B4_RepeatedPermutation`
- `vh_數學B4_FactorialNotation`

## 3. 目前已知缺少 wrapper 的 skill_id

根據 Phase 2A/Phase 3 規格及線上 dashboard 盤點，已知缺少 wrapper 的 B4 Chapter 1 skill_id 包括：
- `vh_數學B4_TreeDiagramCounting`
- `vh_數學B4_AdditionPrinciple`
- `vh_數學B4_PermutationOfNonDistinctObjects`
- `vh_數學B4_PermutationWithRepetition`
- `vh_數學B4_CombinationProperties`
- `vh_數學B4_BinomialTheorem` (註：Phase 4E-3 剛完成 generator 樣題檢查，尚未建 wrapper)
- `vh_數學B4_BinomialCoefficientIdentities`
- `vh_數學B4_PascalTriangle`
- `vh_數學B4_Combination`

## 4. 每個缺少 wrapper 的處理建議

| skill_id | skill_ch_name | 對應 problem_type_id | generator_key | has_generator | in_router | 建議分類 | next_action | notes |
|---|---|---|---|---|---|---|---|---|
| vh_數學B4_BinomialTheorem | 二項式定理 | binomial_expansion_basic | b4.binomial.binomial_expansion_basic | yes | no | can_add_wrapper_now | 接入 router 並建 wrapper | Phase 4E-3 QA 已通過 |
| vh_數學B4_AdditionPrinciple | 加法原理 | add_principle_mutually_exclusive_choice | b4.counting.add_principle_mutually_exclusive_choice | no | no | needs_generator_first | 補齊 generator 後接入 | |
| vh_數學B4_CombinationProperties | 組合的性質 | combination_properties_simplification | b4.combination.combination_properties_simplification | no | no | needs_generator_first | 補齊 generator 後接入 | |
| vh_數學B4_PermutationWithRepetition | 重複選擇/排列 | repeated_choice_basic | b4.counting.repeated_choice_basic | no | no | needs_generator_first | 補齊 generator 後接入 | |
| vh_數學B4_Combination | 組合 | combination_basic_selection | b4.combination.combination_basic_selection | no | no | needs_generator_first | 補齊 generator 後接入 | |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物排列 | N/A | N/A | no | no | needs_generator_first | 待盤點題型與補 generator | |
| vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | binomial_coefficient_sum | b4.binomial.binomial_coefficient_sum | no | no | needs_generator_first | 補齊 generator 後接入 | |
| vh_數學B4_TreeDiagramCounting | 樹狀圖 | tree_diagram_listing | b4.tree_enumeration.tree_diagram_listing | no | no | defer_manual_or_visual | 暫緩實作 | 需視覺化與手動列舉呈現 |
| vh_數學B4_PascalTriangle | 巴斯卡三角形 | pascal_triangle_derivation | b4.binomial.pascal_triangle_derivation | no | no | defer_manual_or_visual | 暫緩實作 | 需人工審核排版 |

## 5. 優先補齊順序

**第一優先**：
能快速補 generator 且題型基礎的 skill。由於這類題型不依賴複雜的外部邏輯，可迅速產出：
- `vh_數學B4_AdditionPrinciple`
- `vh_數學B4_CombinationProperties`
- `vh_數學B4_PermutationWithRepetition`

**第二優先**：
需要較細 verifier 或涉及多種條件限制的排列組合題，實作難度中等：
- `vh_數學B4_PermutationOfNonDistinctObjects` (不盡相異物排列)
- `vh_數學B4_Combination` (含 restriction 或 seat assignment)

**第三優先**：
涉及視覺呈現或依賴學生圖形推理的題型，暫緩實作：
- `vh_數學B4_TreeDiagramCounting` (樹狀圖)
- `vh_數學B4_PascalTriangle` (巴斯卡三角形)

## 6. 下一批 generator 建議

建議自 planned_only 清單中挑選以下 3 個題型作為下一批 generator 實作目標：

1. **add_principle_mutually_exclusive_choice** (屬於 AdditionPrinciple)
   - **理由**：基礎加法原理是 Chapter 1 最核心的概念之一，能迅速填補基礎題型空缺，且計算簡單無複雜邊界條件。
2. **combination_properties_simplification** (屬於 CombinationProperties)
   - **理由**：組合性質簡化（如 $C(n,r)=C(n,n-r)$）在考卷中非常常見，且不需撰寫新的組合 domain function 即可快速實作。
3. **repeated_choice_basic** (屬於 PermutationWithRepetition)
   - **理由**：補充重複選擇的基礎題型，這也是基礎排列組合中常考的型態。

## 7. 不要做的事

- **不要為沒有 generator 的 skill 建空 wrapper**：否則會導致呼叫 router 時崩潰，不如讓系統正常拋出未支援訊息。
- **不要把缺少 wrapper 的 skill 全部導到不相關 generator**：這會嚴重污染 adaptive diagnostic 的資料與學生體驗。
- **不要為了消除錯誤而直接改 dashboard 隱藏 skill**：保留報錯能反映真實的 coverage 缺口，有助於追蹤進度。
- **不要跳過 sample QA**：所有新增 generator 必須產出 5 seed QA 報告。
- **不要一次補太多 generator**：維持每次最多 3 個 generator 的批次節奏，確保測試與 PRNG 唯一性穩健。

## 8. 結論

目前已穩定覆蓋 6 個 wrapper，尚有 9 個 skill_id 處於空缺狀態導致 dashboard 報錯。下一步應先將已通過 QA 的 `binomial_expansion_basic` 接入 router 與建立 wrapper，接著優先實作 `AdditionPrinciple` 與 `CombinationProperties` 的 generator，並維持小批次驗證的 SOP，避免為未完備的 skill 建立空 wrapper 掩蓋問題。
