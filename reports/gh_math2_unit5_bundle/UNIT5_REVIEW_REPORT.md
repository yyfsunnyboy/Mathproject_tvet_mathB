# 普高數學2 Unit 5（組合）GenCode V3 隔離建置 — 教師驗收資料

狀態：**ready_for_human_review**（隔離建置與驗證完成；尚未 Promotion／Publish，未寫入正式 DB、configs、`core/domain/promoted`、`skills/`、`agent_skills_v3/`）。

- Bundle：`reports/domain_operation_workspaces/capability_discrete_combinations_5ba1971d/revision_0001/promotion_bundle.json`
- Domain：`discrete.combinations`（19 operations，`agent_domains_candidate/combinations/`）
- 演練報告：`reports/gh_math2_unit5_bundle/rehearsal_unit5_report.json`；逐題樣本：`review_samples.json`

## 1. 範圍

| Skill | 正式題列 | 動態 GenCode | 固定題 |
|---|---|---|---|
| `gh_Combination` | 23 | 22 | 12834 進階題12（FIXED_GRADED，已上線） |
| `gh_BinomialTheorem` | 14 | 12 | 12838 例題9、12845 隨堂練習10（證明，ungraded 自評，已暫存） |

37 列 = 34 動態 + 3 固定；每題 1 個 Component，Generator 依題型共用 19 個 Domain Operation。

## 2. 逐題覆蓋（34 題動態）

答案欄為教材原題參數下的答案（已與課本解答及獨立暴力枚舉／sympy 核對）；「變體」為 Sandbox 收集的相異參數組數（20 seeds 抽樣）。

| ID | 教材 | Operation | 判分 | 原題答案 | 變體 |
|---|---|---|---|---|---|
| 12812 | 例題1 | combination_evaluate | 多小題／數值 | 45；45；1 | 20 |
| 12813 | 例題2 | select_with_members | 多小題／數值 | 120；56 | 20 |
| 12814 | 例題3 | mixed_group_ordered | 數值 | 54 | 20 |
| 12815 | 例題4 | group_partition | 數值 | 15 | 20 |
| 12816 | 例題5 | group_partition | 多小題／數值 | 90；15；15 | 11 |
| 12817 | 隨堂練習1 | combination_evaluate | 多小題／數值 | 210；35；120 | 20 |
| 12818 | 隨堂練習2 | select_with_members | 多小題／數值 | 21；10 | 20 |
| 12819 | 隨堂練習3 | mixed_group_ordered | 數值 | 198 | 20 |
| 12820 | 隨堂練習4 | group_partition | 數值 | 90 | 20 |
| 12821 | 隨堂練習5 | group_partition | 多小題／數值 | 35；280 | 12 |
| 12822 | 隨堂練習6 | combination_identity_select | 多選（集合） | 1, 3, 4, 5 | 20 |
| 12823 | 觀念澄清1 | combination_claim | ○× | ○ | 20 |
| 12824 | 觀念澄清2 | combination_claim | ○× | × | 20 |
| 12825 | 觀念澄清3 | combination_claim | ○× | ○ | 20 |
| 12826 | 基礎題1 | pair_count | 數值 | 1770 | 20 |
| 12827 | 基礎題2 | sequential_selection | 數值 | 210 | 20 |
| 12828 | 基礎題3 | gender_committee | 多小題／數值 | 210；460；455 | 20 |
| 12829 | 基礎題4 | paired_group_assignment | 數值 | 12 | 9 |
| 12830 | 基礎題5 | surjective_distribution | 數值 | 36 | 11 |
| 12831 | 進階題8 | pair_count（反求 n） | 數值 | 12 | 20 |
| 12832 | 進階題9 | parity_sum_selection | 數值 | 66 | 20 |
| 12833 | 進階題10 | multiset_select_arrange | 數值 | 72 | 20 |
| 12835 | 例題6 | binomial_expansion | 展開式（代數等價） | x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4+y^5 | 20 |
| 12836 | 例題7 | binomial_expansion | 展開式（代數等價） | 16x^4−32x^3y+24x^2y^2−8xy^3+y^4 | 20 |
| 12837 | 例題8 | general_term_coefficient | 數值 | 160 | 20 |
| 12839 | 例題10 | at_least_k_selection | 數值 | 1024 | 11 |
| 12840 | 觀念澄清4 | combination_claim | ○× | ○ | 20 |
| 12841 | 基礎題7 | binomial_sum_bound | 數值 | 10 | 20 |
| 12842 | 隨堂練習7 | binomial_expansion | 展開式（代數等價） | x^4+4x^3y+6x^2y^2+4xy^3+y^4 | 20 |
| 12843 | 隨堂練習8 | radical_binomial_power | 多小題（a, b） | −41；29 | 20 |
| 12844 | 隨堂練習9 | general_term_coefficient | 數值 | 60 | 20 |
| 12846 | 隨堂練習11 | at_least_k_selection | 數值 | 2036 | 20 |
| 12847 | 基礎題6 | general_term_coefficient | 數值 | 35 | 20 |
| 12848 | 進階題11 | coefficient_solve_parameter | 數值（有理數） | −1 | 20 |

變體較少的題（9–12 組）是題型本身受限：分組題需整除；12829 每組 1 師 1 生且以暴力枚舉驗證，上限 4 位教師；12839 的「至少一半」需 n 的奇偶限制。每題均 ≥ 9 組相異題面，且不以改寫題面灌水。

### 變體樣本（已人工複算）

- 12813：從 9 位手球選手中選出 6 人上場；(2) 甲、乙都不能上場 → 84；7
- 12822：五個組合恆等式（對稱、巴斯卡、差、連鎖、曲棍球棒）全為真 → 1, 2, 3, 4, 5
- 12829：4 名教師、4 名學生分 4 組到甲乙丙丁四地 → 4!×4! = 576
- 12836：寫出 (2p−2q)^3 的展開式 → 8p^3−24p^2q+24pq^2−8q^3
- 12840：(x+y)^12 中 x^10y^2 與 x^3y^9 係數相等？ → ×（66 ≠ 220）
- 12843：(√2−1)^6 = a+b√2 → a = 99，b = −70
- 12848：(1+ax)(1+x)^6 的 x^3 係數為 −10 → 20+15a = −10，a = −2

## 3. 固定題（3 題）

| ID | 教材 | 機制 | 狀態 |
|---|---|---|---|
| 12834 | 進階題12（半圓上 4+6 點） | FIXED_GRADED 教材原題＋教師核可裁切圖；(1) ③ 40 條、(2) 116 個 | 已上線（未變動） |
| 12838 | 例題9 證明 ΣC(n,k)=2^n | ungraded 自評：3 步提示＋3 步參考證明（代 x=y=1） | 暫存 `reports/gh_math2_unit5_fixed/staged_proof_entries.json` |
| 12845 | 隨堂練習10 證明 Σ(−1)^k C(n,k)=0 | ungraded 自評：3 步提示＋3 步參考證明（代 x=1, y=−1） | 同上 |

證明題的參考證明以 sympy 符號求和、n=1..39 數值、展開式代值（n=1..12）驗證；學生自評**不**產生對錯、連續答對、精熟度或錯題紀錄。

## 4. 驗證結果

| 項目 | 結果 |
|---|---|
| Checker 雙變數多項式等價（`test_gh_math2_unit5_expansion_checker.py`） | 22/22 PASS（重排、顯式乘號、上標、分數、小數係數接受；未展開、缺項、多項、符號錯、空白拒絕） |
| Sandbox Gate（`test_gh_math2_unit5_combinations_sandbox.py`，34 題 × 20 seeds） | 109/109 PASS |
| 證明題自評（`test_gh_unit5_fixed_proofs_staged.py`） | 3/3 PASS |
| 進階題12 學生端（`test_gh_unit5_fixed_advanced12.py`） | 15/15 PASS |
| 隔離 Promotion → Phase 2（Healer／Eval／Gate） | 34/34 tracker = `verified`，逐題 20 seeds 驗證 0 失敗 |
| Phase 3 沙盒發布 | 兩 Skill `production_published`；smoke／staging／production smoke 全 passed |
| 學生端 facade（80 seeds：標準答案、等價答案、錯誤答案） | 0 誤判；served 22／12 題全覆蓋 |
| 正式路徑寫入掃描 | 空（無寫入） |
| Unit 4 回歸（排列 Sandbox＋固定題與圖） | 全 PASS |

變化稽核（variation audit）：30 題 `dynamic`；4 題 ○×（12823、12824、12825、12840）因通用規則「單選須 4 選項」標 `unsafe_dynamic`，與已發布的 Unit 4 ○× 題相同，判分本身正確（facade smoke 0 誤判），不阻擋。

## 5. 正式發布時需同步（尚未執行，需授權）

1. 教師核准 Bundle → 正式 Promotion → Phase 2 寫入正式 tracker → Phase 3 Publish 兩 Skill。
2. 將 `staged_proof_entries.json` 合併入 `configs/fixed_textbook_practice.json`（以正式題列重新綁定 SHA-256）。
3. 合併後更新兩個預發布測試的斷言：`test_gh_unit5_fixed_proofs_staged.py`（「尚未在 live」）與 `test_gh_unit5_fixed_advanced12.py::test_other_unit5_rows_are_not_fixed_entries`（固定題應為 12834、12838、12845）。
4. 發布後增量驗收。依 Unit 4 部署前例，執行中的 Flask 需在下次重啟後才會載入新的 Skill 綁定；重啟由使用者自行安排，部署腳本不重啟任何服務。本輪隔離建置不需重啟。
