# B4 Phase 4E Postcheck-D2-Connect Freeze Summary

## 1. 本階段目的

本階段**凍結** `vh_數學B4_PermutationOfNonDistinctObjects` 之 **Postcheck-D2 enrichment／semantic alignment** 接入成果：在既有 Postcheck-C practice 可用性修補之上，將 **`non_distinct_objects_arrangement`** 接入路由／wrapper 路徑，並**保留** **`repeated_permutation_digits`** 作為 fallback。

請與 Phase 4E-Final **closure 統計**區分：

- 本階段屬 **postcheck enrichment／semantic alignment**，目標是 **dashboard skill 頁題型語義**與課本名詞一致。
- **不更新**原始 Chapter 1 **`b4_ch1_runtime_coverage_matrix.csv`**（維持 **28** 題分母 closure 視角）。
- **不改寫** Phase 4E-Final 所宣告之 deterministic runtime closure：**25／28 `runtime_ready`**、**`planned_only`=0**、**manual_review／excluded-like=3**（見 `b4_ch1_runtime_closure_report.md`、`b4_ch1_runtime_coverage_matrix_summary.md`）。
- **`non_distinct_objects_arrangement`** 為 enrichment 題型，用以修正 skill page 體驗與數學語義，**非**將原始 closure 分母擴張為 29。

**參考文件：** 撰寫時下列允許讀取之報告均存在；若後續版本控制移动檔名，請以 archive 為準。

## 2. 原問題

**Postcheck-C**（見 `b4_phase4e_postcheck_c_permutation_non_distinct_mapping_summary.md`）已修正：

- `/practice/vh_數學B4_PermutationOfNonDistinctObjects` 之 **`No module named`**。
- 新增 canonical **`skills/vh_數學B4_PermutationOfNonDistinctObjects.py`** wrapper，並在 **`question_router`** 註冊該 **`skill_id`**。

但当时為 **temporary surrogate**：

- **`problem_type_id`：** `repeated_permutation_digits`
- **`generator_key`：** `b4.counting.repeated_permutation_digits`

**問題：**

- `repeated_permutation_digits` 語意較接近 **repeated choices／每位可重複選**，公式典型為 **\(m^n\)**。
- **`PermutationOfNonDistinctObjects`**（不盡相異物排列）於教材語境應為 **固定多重集合**中相同物線性排列，公式為 **\(\dfrac{n!}{a!\,b!\,\cdots}\)**。
- 因此僅 surrogate **無法**代表完整語義（見 `b4_phase4e_postcheck_d2_permutation_non_distinct_enrichment_decision.md`）。

## 3. 本次凍結接入項目

| skill_id | problem_type_id | generator_key | role | 狀態 |
|---|---|---|---|---|
| `vh_數學B4_PermutationOfNonDistinctObjects` | `non_distinct_objects_arrangement` | `b4.permutation.non_distinct_objects_arrangement` | primary／main semantic-aligned problem_type | **connected**；**使用者人工 web smoke** 通過 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | fallback／temporary surrogate retained | **retained** |

**補充（實作紀錄，供維運對照）：** `question_router` 以 **`_REGISTRY`** 保留既有 **`repeated_permutation_digits`** entry，並以 **`_ENRICHMENT_REGISTRY`** 追加 **`non_distinct_objects_arrangement`**；**`generate_for_skill`** 將兩者合併後再做 **`seed_based_selection`** 或 **`problem_type_id`** 指定（細節見 `b4_phase4e_postcheck_d2_connect_non_distinct_objects_router_summary.md`）。

## 4. 數學語義修正

- **Repeated choices／數字可重複席位：** 典型為「每位自同一集合選取、可重複」，計數常為 **\(m^n\)**。
- **Non-distinct object permutation（不盡相異物排列）：** **給定固定個數之物件**，其中若干類彼此相同；線性排列時相同物內部互換不重複計數，公式 **\(\dfrac{n!}{a!\,b!\,\cdots}\)**。
- 本次 **`non_distinct_objects_arrangement`**（見 `b4_phase4e_postcheck_d2_fix_non_distinct_objects_generator_summary.md`）採 **後者**語義。
- **題幹語境**包含字母 multiset（如 A、A、B、C）、彩球「同色相同」、抽象物件「幾個相同、其餘相異」等（見 `b4_phase4e_postcheck_d2_qa_non_distinct_objects_sample_review.md`）。
- **不再**僅倚賴「有若干數字、每位可重複使用」類敘述作為該 skill 的唯一面貌。

## 5. 測試結果

**Postcheck-D2-Fix**（`b4_phase4e_postcheck_d2_fix_non_distinct_objects_generator_summary.md`）：

- focused pytest：**10 passed**
- regression pytest：**56 passed**

**Postcheck-D2-QA-Fix**（`b4_phase4e_postcheck_d2_qa_non_distinct_objects_sample_review.md`）：

- focused pytest：**11 passed**
- regression pytest：**67 passed**
- QA 初步判斷：**通過**

**Postcheck-D2-Connect**（`b4_phase4e_postcheck_d2_connect_non_distinct_objects_router_summary.md`）：

- focused pytest：**6 passed**
- core related pytest：**41 passed**
- **未新增** generator／wrapper（Connect 階段說明）
- Connect 報告載明：**未修改** generator／domain／route／frontend／app.py／coverage matrix（於該次 Connect patch 範圍內）

**Web Smoke Test（本 freeze 宣告時點）：**

- **`/practice/vh_數學B4_PermutationOfNonDistinctObjects`：** **通過**（使用者人工確認）
- **不再** `No module named`
- **可正常產題**
- **已出現**真正不盡相異物排列題（字母／彩球／物件 multiset 語境）
- **LaTeX** 正常
- **答對／答錯** 正常
- **terminal** 無 **500** error

## 6. 不更新 coverage matrix 的原因

- Phase 4E-Final 原始 Chapter 1 deterministic closure 統計**維持**：
  - **problem_type total：28**
  - **runtime_ready：25**
  - **planned_only：0**
  - **manual_review／excluded-like：3**
- 本接入為 **postcheck enrichment**，**不是**原始 **28** 題 closure 分母的新增「收尾項」。
- **`non_distinct_objects_arrangement`** 之目的為 **skill page 語義對齊**與題型豐富度，避免 closure 口徑被 enrichment **悄悄擴張**而與 Phase 4E-Final 報告不一致。
- 因此 **不更新** `b4_ch1_runtime_coverage_matrix.csv`。
- 若未來需追蹤 enrichment／expanded problem types，應 **另建** expanded／enrichment coverage 矩陣或欄位，**而非**改寫原始 closure matrix。

## 7. 目前狀態

`vh_數學B4_PermutationOfNonDistinctObjects` **現在**：

- **practice page 可用**。
- **無** wrapper import error。
- **具備**真正 **non-distinct object permutation** 題型（**primary**）。
- **fallback** **`repeated_permutation_digits`** **仍保留**。
- **不再**僅等同 Postcheck-D1／D1 審計意義下的 **`mapping_surrogate`**（語義主線已對齊）。
- **可視為**與 skill 中文標題一致之 **semantic alignment 已完成**（就 deterministic int-answer general practice 範圍而言）。

## 8. 尚未做

- **尚未**建立 expanded／enrichment coverage matrix。
- **尚未**做 **`vh_數學B4_RepeatedPermutation`** template enrichment。
- **尚未**做 **`vh_數學B4_CombinationDefinition`** template enrichment。
- **尚未**做 **Binomial** depth parameter／template enrichment。
- **尚未**進入 **Phase 4F adaptive route**。
- **尚未**建立 **future_ai_judged** runtime 主線。

## 9. 下一步建議

1. **Postcheck-D3：** small template enrichment **decision**（先做決策與優先序，不大改）
   - `vh_數學B4_RepeatedPermutation`
   - `vh_數學B4_CombinationDefinition`
   - `vh_數學B4_BinomialTheorem`／`vh_數學B4_BinomialCoefficientIdentities`
2. **或**直接進 **Phase 4F-1** adaptive route planning；仍建議 **先完成 D3 decision**，避免在未盤點體感／registry 前先放大 adaptive 範圍。
3. 若進 **D3**：**不要一次大改**；僅決定哪些 skill 值得 enrichment、指標為何（模板數、參數空間、router entry 數）。
4. 若進 **adaptive**：路由必須 **迴避** manual_review／import 不可用／無 registry 之 skill，並維護 **獨立 adaptive coverage**，勿與 deterministic closure 混淆。

## 10. 結論

**Postcheck-D2-Connect** 已完成：**`non_distinct_objects_arrangement`** 已接入 **`vh_數學B4_PermutationOfNonDistinctObjects`**，並與 **`repeated_permutation_digits`** fallback **並存**；使用者人工 **web smoke** 對 **`/practice/vh_數學B4_PermutationOfNonDistinctObjects`** **通過**。  
**`PermutationOfNonDistinctObjects`** 就由「僅 surrogate」提升為「**語義對齊 primary + retained fallback**」，skill page **語義對齊目標達成**。  
**Coverage matrix（原始 28／25 closure）維持未更新**，與 Phase 4E-Final **一致**。  
後續優先建議：**Postcheck-D3 enrichment decision**，再評估 **Phase 4F adaptive**；並視需要 **另開 enrichment coverage**，而非回溯修改 closure 分母。

---

## 完成後回報欄位（收件用）

1. 是否成功輸出 Postcheck-D2-Connect-Freeze summary：**是**（本檔）。
2. 是否確認 PermutationOfNonDistinctObjects semantic alignment 已完成：**是**（primary：`non_distinct_objects_arrangement`）。
3. 是否確認 repeated_permutation_digits fallback 保留：**是**。
4. 是否有更新 coverage matrix：**否**（依本 freeze 政策與 Phase 4E-Final 口徑）。
5. 是否有修改任何程式碼：**否**（僅新增本 Markdown）。
6. 下一步建議：**Postcheck-D3** 先做 **RepeatedPermutation／CombinationDefinition／Binomial** 等小範圍 **enrichment decision**；完成後再進 **Phase 4F** adaptive planning，並避免指向 manual_review／不可用 skill。
