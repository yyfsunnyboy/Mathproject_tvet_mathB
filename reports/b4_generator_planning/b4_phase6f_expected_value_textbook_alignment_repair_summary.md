# B4 Chapter 2 Phase 6F-R — Expected Value Textbook Alignment Repair Summary

**Status:** READY_FOR_MANUAL_SMOKE

## 1) manual smoke failed 原因
- Phase 6F 生成題幹雖數學正確，但主體語境偏「抽象離散隨機變數分布」，不夠貼近高職 B4 課本在 2-3「數學期望值」常見的例題敘事。
- 手動 smoke 反饋重點：題幹需回到「擲硬幣 / 擲骰子 / 所得金額(得分)」的課本情境，不宜以 `W`、隨機分割式語句主導。

## 2) textbook evidence summary
先做 DB 證據檢查（`textbook_examples`，`skill_id=vh_數學B4_MathematicalExpectationDefinition`，`source_chapter=2 機率`，`source_section=2-3 數學期望值`）。代表題幹摘要如下：

1. 擲骰子一次：1 點得 12 元、2/3/4 點付 20 元、5/6 點得 60 元，求一次所得金額期望值。
2. 袋中 10 元與 5 元硬幣若干枚，任取數枚，求所得金額期望值。
3. 擲均勻硬幣一次：正面得 20 元、反面付 10 元，求一次所得金額期望值。
4. 擲公正骰子一次：奇數點得 100 元、偶數點付 50 元，求一次所得金額期望值。
5. 擲均勻硬幣 2 次：2 正面得 400 元、1 正 1 反得 100 元、2 反面付 500 元，求所得金額期望值。

結論：課本語境明確偏向「簡單遊戲 + 金額(得失)」或「已整理分布表」，非抽象理論敘述。

## 3) 修正前問題
- 題幹常以「設離散隨機變數 X...」+ 公分母權重敘述為主。
- 內文帶有不自然生成語言（例如 common denominator 的建構式說法）。
- manual smoke 觀感上不像高職課本例題口吻。

## 4) 修正後題型語境
僅修正原兩個 problem_type：

- `expectation_discrete_basic`
  - 改為課本風格模板：硬幣得失、骰子得失、兩次硬幣得失。
  - 題幹改為「玩一次所得到金額」「所得金額的期望值」等語句。
  - 允許正負報酬（付出記負值），符合課本例題呈現。

- `expectation_from_distribution`
  - 改為「已整理好的 X / P(X) 表格」題幹。
  - 表格欄位明確為 `X` 與 `P(X)`。
  - 題幹用語維持課本練習風格，避免抽象理論導向。

兩題 explanation 均統一：
1. 先列 `E(X)=Σ x·P(X=x)`
2. 再逐項代入
3. 最後化簡得到答案

## 5) 修改檔案
- `core/vocational_math_b4/generators/chap2_expected_value.py`
- `tests/test_b4_chap2_phase6f_expected_value.py`
- `reports/b4_generator_planning/b4_phase6f_expected_value_textbook_alignment_repair_summary.md`（本檔）

## 6) 測試結果
依分段策略執行：

```powershell
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -vv -s -k "generator"
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -vv -s -k "checker"
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -vv -s -k "router or allowlist"
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -vv -s -k "route or practice or check_answer"
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -q
```

結果：`77 passed`

必要 regression：

```powershell
python -m pytest tests/test_b4_chap2_phase6e_independent_events.py tests/test_b4_chap2_phase6d_conditional_probability.py tests/test_b4_chap2_phase6c2_probability_second_batch.py tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

結果：`517 passed, 12 warnings`

## 7) manual smoke checklist
- [ ] `/practice?skill=vh_數學B4_MathematicalExpectationDefinition` 題幹為金額/得分語境。
- [ ] encoded skill URL 同樣可出題，且語境一致。
- [ ] `expectation_discrete_basic` 題幹不出現抽象隨機分割語句。
- [ ] `expectation_from_distribution` 表格含 `X` / `P(X)` 欄位。
- [ ] explanation 含公式、逐項代入、化簡結論。
- [ ] `/check_answer`：等值分數/小數可判對；百分比在期望值題型仍拒絕。

## 8) final confirmation
- 是否只修正 Phase 6F 兩個 problem_type：**是**
- 是否新增新題型：**否**
- 是否修改 database：**否**
- 是否修改 coverage matrix：**否**
- 是否修改 adaptive scoring / mastery / APR / remediation：**否**
- 是否修改 templates：**否**
- 是否啟動 Phase 6G：**否**
- 是否已避免超出高職 B4 範圍：**是**
- 是否已依課本例題語境修正：**是**
