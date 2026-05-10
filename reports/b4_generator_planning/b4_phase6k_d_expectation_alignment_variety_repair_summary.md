# B4 Chapter 2 Phase 6K-D — Expectation Skill Textbook Alignment & Variety Repair Summary

**Status:** READY_FOR_MANUAL_SMOKE
**Phase template:** Template D — Small Repair Phase
**Scope (locked):** 只修 Phase 6K 中兩個 expectation 相關 problem_type
- `vh_數學B4_ApplicationsOfExpectation` → `expectation_word_problem_profit_fairness`
- `vh_數學B4_MathematicalExpectation` → `expectation_assessment_numeric`

ProbabilityOperations 與 BasicConceptsOfSets 在本輪完全未動。

---

## 1) Manual smoke failure reason

Phase 6K automated tests passed，但手動 smoke 對下列兩個 skill 標記為 NEEDS_REPAIR：

- **ApplicationsOfExpectation：** `expectation_word_problem_profit_fairness` 幾乎只出「彩券售出 N 張、獎額分布」一種題型，多 seed 觀感太單調，與課本原意不符。
- **MathematicalExpectation：** `expectation_assessment_numeric` 大量產生「抽卡／圓盤／抽獎活動」分布題，語境偏向通用「離散隨機變數」描述，不夠貼近高職 B4 課本第 2-3 節「數學期望值」例題口吻。

因此本輪只做 Template D 的「最小修復」：擴充 scenario 模板 + 重新對齊課本語境，不重做 Phase 6K，不動其他 skill。

---

## 2) Textbook evidence summary (`vh_數學B4_ApplicationsOfExpectation`)

執行內部 evidence 檢查（`textbook_examples` 表，按 `skill_id` 過濾，2-3 數學期望值範圍）。
代表性題幹摘要（來源欄位 `source_description`）：

| ID | source | Q (摘要) | A |
|----|--------|----------|---|
| 3749 | textbook_example 例題3 | 校園公益彩券 2000 張，頭獎 1000 元、貳獎 500 元、參獎 100 元，售價 30 元，求每張獎金期望值 + 是否有利 | (1) 6 元 (2) 不利 |
| 3750 | textbook_example 例題4 | 60 歲壽險：理賠 10000、保費 1000、生存機率 0.95，求保險公司獲利期望值 | 500 元 |
| 3751 | in_class_practice 隨堂3 | 袋中紅 5、白 3、黑 2，紅 10/白 20/黑 100，付 50 元玩一次是否有利 | (1) 31 元 (2) 否 |
| 3752 | in_class_practice 隨堂4 | 機車失竊險：失竊率 0.005、理賠 50000、保費 1000，求保險公司獲利期望值 | 750 元 |
| 3753 | basic_exercise 2-3 基礎題6 | 公益彩券 1000 張，獎金 2000/1000/500 元各 5/10/20 張，售價 50 元 | (1) 30 元 (2) 不利 |
| 3756 | advanced_exercise 進階題9 | 袋中 1~34 號球，5 倍數得 20、7 倍數得 30、其他 10，求一球期望所得 | 14 元 |

對 `vh_數學B4_MathematicalExpectation` 也做同樣檢查（自評題為主）：

| ID | source | Q (摘要) | A |
|----|--------|----------|---|
| 3774 | self_assessment 第16題 | 125 張獎券分布題 | 1040 元 |
| 3775 | self_assessment 第17題 | 袋中硬幣抽 2 枚（needs_review） | 52 元 |
| 3776 | self_assessment 第18題 | 擲兩骰子點數相同得 100，否則 -20 | 0 元 |
| 3777 | self_assessment 第19題 | 箱中球抽 3 顆同色獎金（needs_review） | 25 元 |
| 3778 | self_assessment 第20題 | 4 選 1 答錯倒扣 2，期望值=0 反推答對加分 | 6 分 |

**判讀 (對應 prompt 限制)：**
- 課本主流情境：彩券獎額分布、抽球得失、骰子/硬幣得失、簡單分布表。
- 保險精算（壽險、失竊險）雖在課本，但 prompt §2 明確禁止 → 不採用。
- needs_review / 反推答案 / 大學風格組合題（袋中抽 N 枚） → 不採用。
- evidence 充足，4 種 textbook-aligned 應用模板可採；MathematicalExpectation 的 4 種自評風格模板（硬幣／骰子／兩次硬幣／已整理分布表）亦在課本範圍內。

---

## 3) Files changed

| File | Change | Notes |
|------|--------|-------|
| `core/vocational_math_b4/generators/chap2_expectation_extensions.py` | **rewrite** (in-place) | 擴充至 4 scenarios × 多 templates；統一 explanation 格式 |
| `tests/test_b4_chap2_phase6k_remaining_skill_coverage.py` | minimal patch | 移除「題幹必含『彩券』」斷言；新增 5 項 diversity / 課本語境 / explanation 對齊測試 |
| `reports/b4_generator_planning/b4_phase6k_d_expectation_alignment_variety_repair_summary.md` | new | 本檔 |

未變動：
- `core/vocational_math_b4/services/question_router.py`（router metadata 已能涵蓋新 scenario，本輪未動）
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`（allowlist 成員範圍未動）
- `core/routes/practice.py`
- `core/vocational_math_b4/domain/b4_validators.py`
- ProbabilityOperations / BasicConceptsOfSets 相關檔案
- DB schema / coverage matrix / SOP 文件

---

## 4) `ApplicationsOfExpectation` repair summary
（problem_type = `expectation_word_problem_profit_fairness`）

新增 4 種 textbook-aligned scenario，由 seed 驅動均勻輪替：

| scenario_id | 課本對應 | 範例題幹模板 | answer 角色 |
|-------------|----------|---------------|-------------|
| `lottery` | 例題3 / 基礎題6 | 「某攤位售出 N 張彩券，獎額分布為…，其餘銘謝惠顧」 | E(獎金) |
| `game_fee` | 自課本「公平 / 划算」題改寫（不含保險） | 「玩一次須付入場費 K 元，命中得 …，未命中得 0」 | E(獎金) − 入場費 (期望淨收益) |
| `fair_fee` | 公平遊戲入場費 | 「依骰子點數獲得獎金 …，求公平入場費」 | E(獎金) (= 公平入場費) |
| `ball_draw` | 隨堂3 / 進階9 | 「袋中紅 a、白 b、黑 c，分別得 …，任取一球」 | E(獎金) |

**變化度設計：**
- `lottery` 4 種 (n_total ∈ {100, 200, 500, 1000})
- `game_fee` 3 種（套圈圈、飛鏢、骰子）
- `fair_fee` 3 種（骰子分段、抽籤、兩次硬幣）
- `ball_draw` 3 種（紅白黑、紅藍綠、編號 1–10 倍數）

共 **13 個唯一 (scenario, context_id) 模板**；seed 0 進場使用 `seed % 4` 旋轉起始 scenario，確保 lottery 占比 ≤ 25%。

**Explanation 格式統一：**
```
依期望值公式：
$E(X) = \sum_x x · P(X=x) = (x1)·p1 + (x2)·p2 + ...$
逐項代入計算：$E(X) = ... = <化簡結果>$
```
`game_fee` 額外明寫「先求期望獎金，再扣除入場費」，符合 prompt §4 對「淨收益」的清楚說明。

**Answer 規格：** `expected_value` 字串，可為整數或最簡分數；`expected_value` checker 仍拒絕百分比。

---

## 5) `MathematicalExpectation` repair summary
（problem_type = `expectation_assessment_numeric`）

對齊 Phase 6F-R 已確認的高職 B4 課本「數學期望值」自評風格，全面換成 4 種模板（不再以「抽卡 / 圓盤 / 抽獎活動」為主）：

| scenario_id | 課本對應 | 範例題幹 |
|-------------|----------|----------|
| `coin_single` | 6F-R 例題模板 | 擲一枚硬幣：正面得 X、反面付 Y |
| `dice_single` | 6F-R + 自評第18題風格 | 擲一顆骰子：奇/偶或 1/234/56 三段式得失 |
| `coin_two` | 6F-R 例題模板 | 擲硬幣 2 次：2 正/1 正 1 反/2 反 各對應金額（機率 1/4, 1/2, 1/4） |
| `distribution_table` | 自評第16題 | 「某遊戲一次所得金額 X 的分布如下：$P(X=200)=1/6$；…」 |

**變化度設計：**
- 每個 scenario 內含 3–4 個 context 模板（共 13 個唯一組合）。
- seed 旋轉起始 scenario，確保 24 個 seed 中能觀察到 ≥3 種 scenario，且 4 種會均勻出現。
- 抽卡 / 圓盤 等 prompt §3 禁止主導之語境完全移除；測試以 `test_no_card_or_wheel_dominance` 監控（觀察 32 seed，card/wheel 占比 = 0 / 32）。

**Explanation 格式：** 與 ApplicationsOfExpectation 一致（公式 → 逐項代入 → 化簡）。

**Answer 規格：** `expected_value` 字串（整數或最簡分數），允許負值（付出記為 -X）；checker 拒絕百分比。

**抽象語句檢查：** 題幹一律不含 `隨機權重` / `隨機分割` / `W ∈` / `設離散隨機變數`；distribution_table 強制以 `元 / 金額 / 分數 / 得分` 之一作為語境，避免抽象 `X` 主導。

---

## 6) Scenario diversity before / after

實際以 40 個 seed (1..40) 抽樣（每 seed 為獨立新 session 呼叫，模擬不同學生第一題分布）。

### `expectation_word_problem_profit_fairness`

| Scenario | Before (Phase 6K) | After (Phase 6K-D) |
|----------|---:|---:|
| lottery | ~40/40 (~100%) | 10/40 (25%) |
| game_fee | 0 | 10/40 (25%) |
| fair_fee | 0 | 10/40 (25%) |
| ball_draw | 0 | 10/40 (25%) |
| **distinct scenarios** | 1 | 4 |

### `expectation_assessment_numeric`

| Scenario | Before (Phase 6K) | After (Phase 6K-D) |
|----------|---:|---:|
| 抽卡／圓盤 / 抽獎活動 (主導) | ~30+/40 | 0/40 |
| coin_single | 0 | 10/40 (25%) |
| dice_single | 0 | 10/40 (25%) |
| coin_two | 0 | 10/40 (25%) |
| distribution_table (金額/得分語境) | minor | 10/40 (25%) |
| **distinct scenarios** | ~1–2 (主要 1) | 4 |

抽卡 / 圓盤模板已完全自 _MATH_EXP_SCENARIOS 移除（保留為未來潛在備援，目前 0% 機率出現）。

---

## 7) Tests run

執行順序與結果：

```powershell
# A. 重整後的 Phase 6K-D 直接相關 (expectation 部分)
python -m pytest tests/test_b4_chap2_phase6k_remaining_skill_coverage.py -vv -k "ExpectationWordProblem or ExpectationAssessment"
```
→ **31 passed, 151 deselected**（含 5 項新增 6K-D diversity / 語境對齊測試）

```powershell
# B. Phase 6K full file（確認 ProbabilityOperations / BasicConceptsOfSets 未受影響）
python -m pytest tests/test_b4_chap2_phase6k_remaining_skill_coverage.py -q
```
→ **182 passed**

```powershell
# C. Phase 6F (expected value) + 6J (teacher audit visibility) + router canonical
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py tests/test_b4_chap2_phase6j_teacher_audit_visibility.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```
→ **114 passed**

```powershell
# D. 其餘 Chap2 (6C1 / 6C1R / 6C1R2 / 6C2 / 6C2R / 6D / 6E / 6G-0 / 6I) + Chap1 regression
python -m pytest tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chap2_phase6c1r_practice_route_integration.py tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chap2_phase6c2_probability_second_batch.py tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py tests/test_b4_chap2_phase6d_conditional_probability.py tests/test_b4_chap2_phase6e_independent_events.py tests/test_b4_chap2_phase6g0_skill_availability_ux.py tests/test_b4_chap2_phase6i_visibility_audit_logging.py tests/test_b4_chapter1_adaptive_allowlist.py -q
```
→ **683 passed**

合計 Phase 6K-D 完成後：**(182 + 114 + 683) = 979 passed**，0 failed。

---

## 8) Manual smoke checklist

- [ ] `/practice?skill=vh_數學B4_ApplicationsOfExpectation`
  - 連按 8 次，題幹至少出現 3 種 scenario（彩券、遊戲收費、公平入場費、抽球）。
  - 任何題幹皆不含「保險 / 保費 / 投資報酬」語句。
  - 「淨收益」題的 explanation 有清楚扣除入場費的步驟。
- [ ] `/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_ApplicationsOfExpectation`（encoded）效果一致。
- [ ] `/practice?skill=vh_數學B4_MathematicalExpectation`
  - 連按 8 次，題幹至少出現 3 種 scenario（硬幣、骰子、兩次硬幣、分布表）。
  - 不再出現「從一副已洗勻的卡片中抽出一張」「轉動圓盤」主導樣板。
  - distribution_table 題型用「某遊戲一次所得金額 $X$ 的分布如下…」語境，而非抽象「設離散隨機變數 X」。
- [ ] `/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectation`（encoded）效果一致。
- [ ] explanation 在所有 scenario 下皆含「公式 → 逐項代入 → 化簡」三段。
- [ ] `/check_answer`：
  - 整數 / 最簡分數 / 等值未化簡分數 / 等值有限小數 → 判對。
  - 百分比形式 → 仍判錯（`expected_value` checker）。

---

## 9) Remaining limitations

- 課本中保險精算 / 反推答案題型（self_assessment 第20題）刻意未實作，符合 prompt §2/§3 禁止保險精算與大學機率論的範圍。需要時應另開新 phase 並重新評估 SOP 是否允許此類題型。
- 保留少量「抽卡 / 圓盤」備援的選項目前未啟用（_MATH_EXP_SCENARIOS 不含 card/wheel）。如未來課本範圍變更，可在不破壞 4-scenario 主架構下，新增 weighted minor scenario，但本輪不動。
- adaptive scoring / mastery / APR / fail_streak / remediation 仍維持 Phase 6L 規畫狀態，本輪未啟用。

---

## 10) Final confirmation

- 是否只修 expectation 相關兩個 problem_type：**是**（`expectation_word_problem_profit_fairness` + `expectation_assessment_numeric`）
- 是否修改 ProbabilityOperations：**否**
- 是否修改 BasicConceptsOfSets：**否**
- 是否新增 handwriting / free-response：**否**
- 是否修改 adaptive scoring / mastery / APR / remediation：**否**
- 是否修改 DB schema：**否**
- 是否修改 coverage matrix：**否**
- 是否新增 SOP：**否**
- 是否大改 routes / templates：**否**（router metadata 維持 Phase 6K 狀態）
- 是否更動 deterministic allowlist 成員範圍：**否**
- 是否啟動下一 phase：**否**

完成狀態：**READY_FOR_MANUAL_SMOKE**
