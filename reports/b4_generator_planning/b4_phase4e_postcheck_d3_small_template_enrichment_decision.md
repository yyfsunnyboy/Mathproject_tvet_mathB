# B4 Phase 4E Postcheck-D3 Small Template Enrichment Decision

## 1. 本階段目的

本階段目的是針對 Phase 4E deterministic runtime closure 後，部分 skill 雖已可正常出題但題型體感偏單調的情況，進行小範圍 template / parameter enrichment 決策。

本階段只做決策文件，不修改程式、不修改 router、不新增 generator、不新增 wrapper、不修改 coverage matrix。

分析目標是判斷：

- 哪些 skill 需要在 Phase 4F adaptive route 前先做小幅補強。
- 哪些 skill 可接受為 narrow skill，延後處理。
- 哪些 skill 剛完成語義修正，應先觀察。
- enrichment 問題是否影響 Chapter 1 deterministic runtime closure 結論。

## 2. 目前狀態摘要

Chapter 1 deterministic int-answer runtime 已完成實質收尾：

- 原始 problem_type 總數：28。
- runtime_ready：25 / 28。
- planned_only：0。
- manual_review / excluded-like：3。
- manual_review / excluded-like 題型為：
  - `binomial_expansion_basic`
  - `tree_diagram_listing`
  - `pascal_triangle_derivation`

Postcheck 階段已處理下列 runtime 體驗問題：

- Postcheck-B：manual_review skill 進入 practice page 時改為 friendly unavailable / gating，不再出現 missing module error。
- Postcheck-C：補上 `vh_數學B4_PermutationOfNonDistinctObjects` 的 wrapper / router mapping，終止 `No module named`。
- Postcheck-D2 / D2-Connect：新增並接入真正語義對齊的 `non_distinct_objects_arrangement`，使 `PermutationOfNonDistinctObjects` 不再只依賴 repeated choices surrogate。

目前剩下的問題是 enrichment 問題，不是 runtime failure：

- 部分 skill 只有單一 problem_type，題型自然較窄。
- 部分 generator template / context 偏少，學生體感容易重複。
- 部分二項式 depth 題型已接入，但 difficulty=1 參數與題幹變化仍偏保守。
- 這些問題不推翻 Chapter 1 deterministic runtime closure。

## 3. Skill enrichment 分析表

| skill_id | runtime 可用 | 主要問題 | 初步分類 | 是否建議 adaptive 前處理 | 建議處理 |
|---|---|---|---|---|---|
| `vh_數學B4_RepeatedPermutation` | 是 | 單一 problem_type；題幹固定為可重複使用數字排位數；context/template 偏少 | `A_adaptive_before_enrichment` | 是 | 先做 template enrichment，不改公式、不改 problem_type |
| `vh_數學B4_CombinationDefinition` | 是 | 單一 problem_type；但屬於定義型 narrow skill | `narrow_skill_accept` | 否 | 可接受目前 narrow；adaptive 後再補 context template |
| `vh_數學B4_BinomialTheorem` | 是 | depth 題型已接入，但 difficulty=1 參數偏簡單，題幹變化仍可補強 | `A_adaptive_before_enrichment` | 是 | 小幅 parameter/template enrichment；不接 `binomial_expansion_basic` |
| `vh_數學B4_BinomialCoefficientIdentities` | 是 | 分布大致可用；可見度與題幹變化仍可補強 | `B_after_adaptive_enrichment` | 否 | adaptive 後再做 identities template / visibility 補強 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 是 | D2-Connect 後剛完成語義對齊；不宜連續改動 | `C_observe` | 否 | 先觀察；後續再視需要增加 context |

## 4. 各 skill 詳細分析

### 4.1 RepeatedPermutation

現況：

- runtime 可用。
- router 目前主要對應 `repeated_permutation_digits`。
- D1 sampling 顯示 seed 1 到 30 皆產出同一個 problem_type。
- 常見題型為「有若干可用數字，每個數字可重複使用，排成若干位數，共有多少種排法？」。

問題原因：

- 主要原因是 `single_problem_type` 與 generator template 偏少。
- 目前題幹集中在數字位數排列，學生容易感覺重複。
- 這不是 router failure，因為該 skill 本身目前只掛單一 problem_type。
- 也不應將它和 `non_distinct_objects_arrangement` 混用；repeated choices 是每一位置可重複選，非相同物排列是固定多重集合排列。

建議分類：

- `A_adaptive_before_enrichment`

可能補強方向：

- 增加情境模板，但保持 answer 為 $m^{n}$ 的 int。
- 可加入：
  - 密碼設定：每位可重複使用。
  - 車牌號碼：每格可重複。
  - 座號碼 / 編碼：每一碼可重複。
  - 顏色序列：每格可選同一組顏色。
  - 投擲結果序列：每次結果可重複。
- 不改 problem_type。
- 不改 answer formula。
- 不改 wrapper / route / frontend。

是否影響 coverage matrix：

- 不影響。
- 這是既有 runtime_ready 題型的 template enrichment，不改原始 28 題 coverage 狀態。

### 4.2 CombinationDefinition

現況：

- runtime 可用。
- router 目前主要對應 `combination_definition_basic`。
- D1 sampling 顯示 seed 1 到 30 皆產出同一個 problem_type。
- 常見題型為「從若干件不同作品中選出若干件展示，共有多少種選法？」。

問題原因：

- 這是 narrow skill。
- `CombinationDefinition` 本質上是組合定義入門題，單一 problem_type 並不一定代表設計錯誤。
- 若學生體感單調，主要是 context template 偏少，而不是 router selection policy 問題。

建議分類：

- `narrow_skill_accept`
- 可視為 `B_after_adaptive_enrichment`

可能補強方向：

- adaptive 後再補 context template：
  - 選作品。
  - 選學生。
  - 選委員。
  - 選餐點。
  - 選代表。
- 保持 answer 為 int。
- 不需要在 adaptive 前優先改。

是否影響 coverage matrix：

- 不影響。
- 即使未補強，也不影響 runtime closure。

### 4.3 BinomialTheorem

現況：

- runtime 可用。
- 已接入多個 int-answer depth 題型。
- D1 sampling 顯示 `binomial_specific_term_coefficient`、`binomial_middle_term_coefficient`、`binomial_specific_coefficient_with_negative_term` 皆有出現。
- router distribution 初步不是主要問題。

問題原因：

- 主要是 parameter / template enrichment 問題。
- difficulty=1 的參數較保守，常見 `a = 1`、`b > 0` 或題幹格式接近。
- 使用者體感上會覺得 depth 題型不夠明顯，或題型仍偏薄。
- 不應用 `binomial_expansion_basic` 補這個缺口，因為完整展開題 answer 是 list / polynomial free-response，不適合目前 deterministic int-answer runtime。

建議分類：

- `A_adaptive_before_enrichment`

可能補強方向：

- 小幅增加參數與題幹變化：
  - 增加 $a \ne 1$ 的出現比例。
  - 增加 $b < 0$ 的可見度，但維持可控難度。
  - 增加中間項題幹變化。
  - 指定項係數題加入不同文字模板。
  - 讓 explanation 更清楚標示使用第 $r+1$ 項或特定次方係數。
- 保持 answer 為 int。
- 不接 `binomial_expansion_basic`。
- 不改 free-response / parser / normalization。

是否影響 coverage matrix：

- 不影響。
- 這是既有 runtime_ready / depth runtime 的 enrichment，不改原始 closure 分母。

### 4.4 BinomialCoefficientIdentities

現況：

- runtime 可用。
- 目前包含：
  - `binomial_coefficient_sum`
  - `binomial_equation_solve_n`
  - `binomial_odd_even_coefficient_sum`
- D1 sampling 顯示三類 problem_type 都有出現，分布大致可接受。

問題原因：

- 主要不是 router failure。
- 可見度與模板變化仍可補強。
- 某些 identity 題型在 practice 中可能因題幹相似而不容易被學生辨識為不同能力。

建議分類：

- `B_after_adaptive_enrichment`

可能補強方向：

- adaptive 後再做 template enrichment：
  - 係數和題：更明確說明令 $x=1$ 的意義。
  - 奇偶項係數和題：清楚區分奇次項與偶次項。
  - 解 $n$ 題：增加 $C^{n}_{1}$ / $C^{n}_{2}$ 的題幹變化。
  - 增加題目文字中的判斷提示，但不降低數學要求。
- 可搭配 debug visibility 顯示 problem_type，方便教師 QA。

是否影響 coverage matrix：

- 不影響。
- 這是 enrichment，不是 closure 修正。

### 4.5 PermutationOfNonDistinctObjects

現況：

- runtime 可用。
- Postcheck-C 先用 wrapper / router mapping 修正 missing module。
- Postcheck-D2-Fix 新增真正語義對齊的 `non_distinct_objects_arrangement`。
- Postcheck-D2-Connect 已將 `non_distinct_objects_arrangement` 接入 `vh_數學B4_PermutationOfNonDistinctObjects`，並保留 `repeated_permutation_digits` fallback。
- 目前已不應再視為單純 temporary surrogate。

問題原因：

- D2-Connect 後，主要問題已不是語義錯位。
- 未來仍可增加 context，但本 skill 剛完成語義對齊，短時間內連續改動會增加 regression 風險。

建議分類：

- `C_observe`

可能補強方向：

- 後續若需要，可增加：
  - 字母排列。
  - 彩球排列。
  - 路徑排列。
  - 固定多重集合數字排列。
- 但建議先觀察 D2-Connect 後的實際使用情況。
- 不建議在 D3-Fix-A 立即再處理。

是否影響 coverage matrix：

- 不影響。
- D2 系列是 postcheck enrichment，不改 Chapter 1 原始 28 題 runtime closure 統計。

## 5. 不建議做的事

- 不改 coverage matrix。
- 不接 `binomial_expansion_basic`。
- 不把 repeated choices 和 non-distinct objects 混為一談。
- 不為了單調問題大改 route / frontend。
- 不在 wrapper 寫題型邏輯。
- 不一次補太多 generator。
- 不把 narrow skill 的自然單調誤判為 runtime failure。
- 不用 dashboard skill rename 解決 template richness 問題。
- 不在 Phase 4F 前引入 list[int] / list[str] / free-response 判分。

## 6. 後續方案比較

| 方案 | 做法 | 優點 | 缺點 | 建議 |
|---|---|---|---|---|
| Option 1：先做 A 類 enrichment，再進 adaptive | 先補強所有建議 adaptive 前處理的 skill，再啟動 Phase 4F | adaptive 初期體感較好；能降低學生反覆看到相似題的機率 | 會延後 Phase 4F；若範圍擴大，可能重新打開太多穩定 runtime | 不採完整版本，避免 scope 擴大 |
| Option 2：先進 Phase 4F adaptive MVP，再補 B/C 類 enrichment | 直接進 adaptive route，enrichment 全部延後 | 主線推進最快；不再延長 Phase 4E | adaptive 初期可能推薦到題型單調 skill；教師 QA 時可能再回報體感問題 | 可行但不是最佳 |
| Option 3：折衷，先做一個小型 enrichment phase | 只先處理 `RepeatedPermutation` template enrichment 與 `BinomialTheorem` parameter/template enrichment，完成後進 Phase 4F | 控制範圍；改善最明顯單調點；保留主線推進速度 | Phase 4F 仍會略延後；需嚴格限制 D3-Fix-A 範圍 | 建議採用 |

建議採用 Option 3。

理由：

- `RepeatedPermutation` 的單調感最明顯，且補強 template 風險低。
- `BinomialTheorem` 是 Chapter 1 核心能力，adaptive 前稍微補強參數與題幹可見度有價值。
- `CombinationDefinition` 屬 narrow skill，可接受 adaptive 後再補。
- `BinomialCoefficientIdentities` 分布已有基本覆蓋，可後補。
- `PermutationOfNonDistinctObjects` 剛完成語義對齊，應先觀察。

## 7. 建議下一步

建議下一階段為：

Postcheck-D3-Fix-A：small enrichment for RepeatedPermutation + BinomialTheorem

範圍 1：`RepeatedPermutation` template enrichment

- 不改 answer formula。
- 不改 problem_type。
- 不改 wrapper。
- 不改 route / frontend。
- 增加 context / template。
- 保持 deterministic int-answer。
- 明確維持 repeated choices 語義，不混入 non-distinct object permutation。
- 候選 context：
  - 密碼設定。
  - 車牌號碼。
  - 編碼 / 座號。
  - 顏色序列。
  - 投擲結果序列。

範圍 2：`BinomialTheorem` parameter/template enrichment

- 不接 `binomial_expansion_basic`。
- 不改成 free-response。
- 不做 polynomial parser。
- 保持 answer 為 int。
- 增加 $a \ne 1$ 的可見度。
- 增加 $b < 0$ 的可見度。
- 增加中間項與指定項係數題幹變化。
- 保持 existing output contract 與 choices / explanation 規格。

不建議現在處理：

- `vh_數學B4_CombinationDefinition`
- `vh_數學B4_BinomialCoefficientIdentities`
- `vh_數學B4_PermutationOfNonDistinctObjects`

## 8. 進 Phase 4F 前的建議門檻

進入 Phase 4F adaptive route 前，建議至少確認：

1. D3-Fix-A 已完成，或已明確決定略過。
2. manual_review skill friendly gating 已完成。
3. `PermutationOfNonDistinctObjects` semantic alignment 已完成。
4. 不可用 skill 不應進入 adaptive skill pool。
5. manual_review / future_ai_judged 題型不得混入 deterministic adaptive pool。
6. adaptive 初期應先選 3 到 5 個穩定且題型不太單調的 skill。
7. adaptive coverage matrix 應另建，不與 deterministic runtime coverage matrix 混淆。

## 9. 結論

Postcheck-D3 判斷目前問題是 template / parameter enrichment，不是 runtime failure。

建議採用 Option 3：先做小型 D3-Fix-A，再進 Phase 4F。

adaptive 前建議優先補強 `RepeatedPermutation` 與 `BinomialTheorem`。

`CombinationDefinition` 與 `BinomialCoefficientIdentities` 可 adaptive 後補強。

`PermutationOfNonDistinctObjects` 已完成語義對齊，建議先觀察，不再立即連續修改。

本階段不修改任何程式、不修改 router、不修改 wrapper、不修改 generator、不修改 coverage matrix。
