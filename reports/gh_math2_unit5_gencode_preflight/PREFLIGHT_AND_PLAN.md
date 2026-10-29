# 普高數學2 Unit 5「組合」— GenCode V3 Preflight 與執行計畫

前提：正式 Stage 1 已封板（`reports/gh_math2_unit5_stage1_formal/SUMMARY.md`，Gate READY，37 題）。

流程照 Unit 4 的 SOP（`reports/gh_math2_unit4_bundle/UNIT4_REVIEW_REPORT.md`）：

1. 候選 Domain 套件與 specs
2. Sandbox 測試
3. Bundle 達到 `ready_for_human_review`
4. 隔離發布演練
5. 教師核准後，依序執行 backup、promote、fixed、quarantine、rebuild、publish、verify-live、accept

本輪只做 Preflight，不建置，也不做 Promotion 或 Publish。

## 1. 正式 Skill 與題目覆蓋
| Skill | 題數 | ID | 目前 runtime |
|---|---|---|---|
| `gh_Combination` | 23 | 12812–12834 | 沒有 `skills/`、`agent_skills_v3/`；以教材原題出題（`no_generator_serve_textbook_example`）；12834 走固定題 |
| `gh_BinomialTheorem` | 14 | 12835–12848 | 同上 |

- 37 題都有 anchor，`source_order` 為 1–37。
- 教材沒有附答案（`correct_answer` 全為空），所以答案必須由 Domain 的獨立 oracle 計算，做法與 Unit 4 相同。

## 2. 可重用資產
- `core/domain/promoted/permutations`（Unit 4 已發布）：
  - 可當函式庫直接 import：`_falling`、`_multinomial`、`_sequential_binomials`、`_multiset_patterns`。
  - 「○× 敘述判斷」（`counting_claim`）的題型與驗證模式。
  - 多重集合排列（適用 snoopy 題）。
- `core/domain/promoted/counting_sets`：選取／分組的列舉驗證寫法。
- `core/domain/promoted/algebra_multiplication_formulas`：多項式的建立、乘冪與序列化（`poly_pow`、`serialize_polynomial`），用來計算展開式答案。
- `core/domain/promoted/algebra_radical_operations`：計算 \((\sqrt2-1)^5=a+b\sqrt2\)。也可以直接用整數對 \((a,b)\) 精確運算。
- 共用 Checker：
  - `integer_checker`、`multi_part_answer_checker`、`choice_label_checker`、`unordered_set_checker`
  - `expression_equivalence_checker`（展開式）
  - `rational_checker`
- 沒有可以直接重用的 Generator：兩個 Skill 都還沒有 V3 component。

## 3. 新增 Domain、Family 與 component 分工
- 新 Domain：`discrete.combinations`，新套件 `combinations`，同時涵蓋兩個 Skill，做法與 Unit 4 一個 Domain 涵蓋三個 Skill 相同。
- 37 題的分工：34 題動態出題、1 題固定題可判分（12834）、2 題固定題自評（12838、12845，待教師確認）。

| 題目（ID） | Family／problem type | 方式 | Checker |
|---|---|---|---|
| 例題1、隨堂練習1（12812、12817） | `combination_value`（\(C^n_k\) 計算、\(P/C\) 比值） | 動態 | multi_part＋integer |
| 例題2、隨堂練習2（12813、12818） | `select_with_inclusion`（指定人恰選一人／都選） | 動態 | multi_part＋integer |
| 例題3、隨堂練習3（12814、12819） | `mixed_group_ordered`（各組都要有人＋排序，用排容原理） | 動態 | integer |
| 例題4、隨堂練習4（12815、12820） | `labeled_partition`（分房、分班） | 動態 | integer |
| 例題5、隨堂練習5（12816、12821） | `unlabeled_partition`（相同袋子、平分要除以重複數） | 動態 | multi_part＋integer |
| 隨堂練習6（12822） | `combination_identity_select`（對稱性、巴斯卡定理） | 動態多選 | unordered_set／choice |
| 觀念澄清1–3（12823–12825）、觀念澄清4（12840） | `combination_claim`（○×） | 動態 | choice_label |
| 基礎題1、2（12826、12827） | `pair_count`、`sequential_selection` | 動態 | integer |
| 基礎題3（12828） | `gender_committee`（恰好／至少／各至少） | 動態 | multi_part＋integer |
| 基礎題4（12829） | `paired_group_assignment` | 動態 | integer |
| 基礎題5（12830） | `surjective_distribution`（每處至少 1 人） | 動態 | integer |
| 進階題8（12831） | `round_robin_solve_n`（由 \(C^n_2\) 反求 n） | 動態 | integer |
| 進階題9（12832） | `parity_sum_selection` | 動態 | integer |
| 進階題10（12833） | `multiset_select_arrange`（snoopy） | 動態（重用 permutations） | integer |
| 進階題12（12834） | — | **固定題，可判分（已發布）** | multi_part（choice＋integer） |
| 例題6、隨堂練習7、例題7（12835、12842、12836） | `binomial_expansion` | 動態 | expression_equivalence |
| 隨堂練習8（12843） | `radical_binomial_power`（\(a+b\sqrt2\)） | 動態 | multi_part＋integer |
| 例題8、隨堂練習9、基礎題6（12837、12844、12847） | `general_term_coefficient`（指定次方項係數、常數項） | 動態 | integer |
| 例題10、隨堂練習11（12839、12846） | `at_least_k_selection`（二項式係數和） | 動態 | integer |
| 基礎題7（12841） | `binomial_sum_bound`（\(2^n-1\) 介於範圍內，求 n） | 動態 | integer |
| 進階題11（12848） | `coefficient_solve_parameter` | 動態 | integer／rational |
| 例題9、隨堂練習10（12838、12845） | 證明題 | **建議固定題、自評**（先例：12731、12735） | — |

## 4. Domain Function、Checker 與 Visual Contract
- 每個 Operation 都要有：生成器、與生成器分開實作的 oracle（暴力列舉或 `math.comb` 直接計算）、驗證器防竄改、拒絕退化輸入，並對教材原題做重算比對。標準與 Unit 4 的 119 項測試相同。
- 展開式：
  - 標準答案是係數完整的多項式。
  - `expression_equivalence_checker` 對雙變數多項式的等價判斷，需要先在 sandbox 測試中驗證。
  - 送出前的 `answer_format_example` 不得洩漏答案，依 Lean SOP 的 Answer Contract 規定逐 seed 檢查。
- ○× 題沿用 Unit 4 的處理：variation audit 預期會因「四選項」規則標為 `unsafe_dynamic`，與 Unit 1–4 先例相同，不構成阻擋。
- Visual Contract：
  - 除 12834 外，36 題都不需要圖。
  - 動態變體一律不附圖，題幹不得出現「如圖／右圖／下圖」，由圖形守門測試強制。
  - 12834 不要求 Generator 重畫半圓圖。

## 5. 固定題與動態出題的分工
- 固定題可判分：12834（已在 live `configs/fixed_textbook_practice.json`）。
- 固定題自評：12838、12845，建議做法，需教師確認。
- 動態出題：其餘 34 題的 component。

## 6. 執行計畫（下一輪，需要教師下令開始）
1. 建立 `agent_domains_candidate/combinations/`：domain、adapter、specs、build_sandbox、verification、sandbox_harness，以 `permutations` 為範本。
2. 新增 `tests/gencode/test_gh_math2_unit5_combinations_sandbox.py`：每個 component 20 個 seed，涵蓋 Answer Contract、oracle、題幹語意重算、圖形守門。
3. 新增 12838、12845 的自評固定條目，先放 staged，不寫入 live。
4. 建立 Bundle（`ready_for_human_review`），執行隔離發布演練：所有 component tracker 都要 verified，學生端 facade problems 為 0，正式路徑寫入掃描為空。
5. 產出審核報告，等待教師核准後，才用部署腳本執行 Promotion 與 Publish。

## 7. Blocker 與待確認事項
- 沒有 Blocker。
- 待教師確認：證明題 12838、12845 是否採用固定題自評（建議採用）。
- 待 sandbox 驗證：展開式 Checker 對雙變數多項式的等價判斷。
