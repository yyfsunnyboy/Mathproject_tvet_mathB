# B4 Phase 4E Postcheck-D2 PermutationOfNonDistinctObjects Enrichment Decision

## 1. 本階段目的

本階段針對 `vh_數學B4_PermutationOfNonDistinctObjects` 進行 enrichment decision。

Postcheck-C 已修正 missing wrapper / router mapping，使 `/practice/vh_數學B4_PermutationOfNonDistinctObjects` 不再出現 `No module named`。但 Postcheck-D1 sampling audit 顯示，此 skill 目前仍只重用 `repeated_permutation_digits`，屬於 `mapping_surrogate`，與「不盡相異物排列」的數學語義不完全一致。

本階段只產出決策文件，不修改程式、不新增 generator、不新增 wrapper、不修改 question_router、不修改 coverage matrix。

本階段指定參考文件均存在，未發現缺少文件。

## 2. 目前狀態

| 項目 | 狀態 |
|---|---|
| practice page 可用性 | Postcheck-C 後已可進入 practice，不再 `No module named` |
| wrapper 是否存在 | 是，`skills/vh_數學B4_PermutationOfNonDistinctObjects.py` |
| router entry 是否存在 | 是，`question_router._REGISTRY` 已有 `vh_數學B4_PermutationOfNonDistinctObjects` |
| 目前重用 problem_type | `repeated_permutation_digits` |
| 目前重用 generator_key | `b4.counting.repeated_permutation_digits` |
| 目前 generator path | `core.vocational_math_b4.generators.counting.repeated_permutation_digits` |
| Postcheck-D1 分類 | `mapping_surrogate` |
| Postcheck-D1 sampling | seed 1-30 全部為 `repeated_permutation_digits` |
| answer 型態 | `int` |
| 是否為完整「不盡相異物排列」 | 否，目前只是入口修補與 runtime surrogate |

目前問題：

- skill 中文語義是「不盡相異物的排列」。
- 現有題目偏「有若干可用數字，每位可重複使用，排成幾位數」。
- 這比較接近 repeated choices / multiplication principle。
- 不是典型「多重集合排列」或「相同物排列」。

## 3. 數學語義釐清

| 類型 | 典型題目 | 公式 | 是否等同目前 mapping |
|---|---|---|---|
| repeated choices | 有 4 個數字，每次可重複使用，排成 3 位數 | $m^{n}$ | 是，`repeated_permutation_digits` 目前本質上屬於此類 |
| repeated_permutation_digits | 有 3 到 5 個可用數字，每個數字可重複使用，排成 2 或 3 位數 | $m^{n}$ | 是，這就是目前 mapping |
| non-distinct object permutation | 用 A、A、B、C 共 4 個字母排成一列，共有多少種不同排列 | $\frac{n!}{a!b!\cdots}$ | 否，這才是「不盡相異物排列」的典型語義 |

語義差異：

- repeated choices 是「每個位置都可從同一集合中選，且可重複選」。
- non-distinct object permutation 是「給定一組固定物件，其中有部分物件相同，排列時相同物內部交換不產生新排列」。
- 重複數字題若題意是「每位可重複使用」，應歸 repeated choices。
- 重複數字題若題意是「給定固定多重集合，例如 1, 1, 2, 3 排列」，才屬 non-distinct object permutation。
- 因此目前 `PermutationOfNonDistinctObjects -> repeated_permutation_digits` 是可用性修補，不是教學語義完整接入。

## 4. 三種方案比較

| 方案 | 做法 | 優點 | 缺點 | 短期建議 |
|---|---|---|---|---|
| A：維持 mapping_surrogate | 保留目前 wrapper / router mapping，繼續重用 `repeated_permutation_digits` | 已可用；不新增工程量；不破壞 runtime | skill 名稱與題型語義不精準；學生可能混淆 repeated choices 與不盡相異物排列；題型單調 | 短期保留，但需明確視為 temporary surrogate |
| B：新增真正 `non_distinct_objects_arrangement` generator | 新增真正處理相同物排列的 generator，答案用 $\frac{n!}{a!b!\cdots}$ | 語義正確；支援真正不盡相異物排列；題型更像課本；仍可維持 int-answer runtime | 需新增 generator / tests / QA / router 接入；需避免與 repeated choices 混淆 | 建議作為下一個實作 phase |
| C：將 dashboard skill 改名或改 mapping | 若教材實際是重複排列，將 dashboard skill 合併到 RepeatedPermutation 或改更精準標籤 | 不新增題型；降低重複 skill | 牽涉 dashboard / curriculum 資料；可能影響已匯入教材 skill_id；後處理階段風險較高 | 不建議現在做 |

## 5. 建議決策

建議短期採取以下決策：

- Postcheck-C mapping 可暫時保留。
- 但應明確視為 `temporary surrogate`，不是完整完成「不盡相異物排列」教學。
- 建議後續新增真正 `non_distinct_objects_arrangement` generator。
- 不建議現在改 dashboard skill name，因為會牽涉 curriculum / dashboard 資料與既有教材 skill_id。
- 不建議改 coverage matrix，因為這是 skill enrichment / dashboard skill mapping 問題，不是 Chapter 1 原始 28 題 closure 失敗。

具體回答：

- 是否建議新增 generator：是，建議下一階段新增真正 `non_distinct_objects_arrangement` generator。
- 是否建議改 dashboard skill name：短期不建議。
- 是否建議改 coverage matrix：短期不建議。
- 是否應該把 Postcheck-C mapping 視為 temporary surrogate：是。

## 6. 下一階段實作建議

建議另開 Phase 4E-Postcheck-D2-Fix：non-distinct objects generator。

建議規格：

- `problem_type_id`：`non_distinct_objects_arrangement`
- `generator_key`：`b4.permutation.non_distinct_objects_arrangement`
- `skill_id`：`vh_數學B4_PermutationOfNonDistinctObjects`
- answer formula：`factorial(total_count) // product(factorial(each_duplicate_count))`
- answer 型態：`int`
- runtime 類型：deterministic int-answer，一般練習頁可判分

題幹模板：

1. 字母排列：
   - 「用 A、A、B、C 共 4 個字母排成一列，共有多少種不同排列？」
   - explanation 使用 $\frac{4!}{2!}$。

2. 物品排列：
   - 「有 6 個球，其中 2 個紅球相同、3 個白球相同、1 個黑球，排成一列共有多少種？」
   - explanation 使用 $\frac{6!}{2!3!1!}$。

3. 路徑排列類：
   - 「從某點到某點需向右走 3 步、向上走 2 步，共有多少種路徑？」
   - 這也是多重集合排列，可作為延伸模板；若教材未涵蓋，可暫緩。

LaTeX 規範：

- 使用 $\frac{n!}{a!b!}$ 或 $\frac{6!}{2!3!1!}$。
- 不可裸寫 `n!/(a!b!)`。
- explanation 必須說明：相同物互換不產生新排列，因此總排列數需除以相同物內部交換數。

測試重點：

- seed deterministic。
- seed 1-5 `parameter_tuple` 不重複或有明確處理。
- answer 為 `int`。
- choices 4 個唯一且包含 answer。
- `parameter_tuple` 包含 total_count 與 duplicate_counts。
- explanation 含正確 LaTeX 分式。
- 不輸出裸 `n!/(a!b!)`。
- 支援 `seen_parameter_tuples`。
- 50 次重抽失敗 raise `ValueError`。

QA 重點：

- 題幹是否明確表達「固定物件集合」而不是「每次可重複選」。
- 學生是否能看出相同物需要除以內部交換。
- 題型不要混成 multiplication principle。
- difficulty=1 使用小數字，例如 4 到 7 個物件、1 到 2 組重複。

router / wrapper 接入策略：

- 保留既有 wrapper `vh_數學B4_PermutationOfNonDistinctObjects.py`，不需新增 wrapper。
- 在 router 中將 `vh_數學B4_PermutationOfNonDistinctObjects` 加入新 entry。
- 下一階段可選策略：
  - 將新 `non_distinct_objects_arrangement` 設為此 skill 的主要/default 題型。
  - `repeated_permutation_digits` 可暫時保留作 fallback。
  - 或將 `repeated_permutation_digits` 移回只屬於 `vh_數學B4_RepeatedPermutation`，讓 `PermutationOfNonDistinctObjects` 語義更乾淨。

## 7. 不建議現在做的事

- 不直接改 dashboard skill name。
- 不大改 curriculum mapping。
- 不把 repeated choices 題型當成完整不盡相異物排列。
- 不改 coverage matrix。
- 不接 list/free-response。
- 不新增 manual_review gating，因為此題型可設計成 int-answer deterministic runtime。
- 不把 `PermutationOfNonDistinctObjects` 視為 Phase 4E closure 失敗。

## 8. 結論

- `PermutationOfNonDistinctObjects` 目前已可進 practice，Postcheck-C 已解決 missing wrapper 問題。
- 目前 mapping 重用 `repeated_permutation_digits`，可作為短期 temporary surrogate。
- 但 repeated choices / repeated digits 與 non-distinct object permutation 並非同一數學語義。
- 建議下一階段新增真正 `non_distinct_objects_arrangement` generator。
- 短期不建議改 dashboard skill name，也不建議改 coverage matrix。
- 此議題屬 skill enrichment / semantic alignment，不是 Chapter 1 deterministic runtime closure 失敗。
