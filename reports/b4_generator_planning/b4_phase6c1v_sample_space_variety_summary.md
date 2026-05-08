# B4 Chapter 2 Phase 6C-1V Sample Space Variety Summary

## 1. 問題

- `vh_數學B4_SampleSpaceAndEvents` 的 `sample_space_count_numeric` 在人工 smoke 中呈現偏單一。
- `coin_tosses` / `dice_rolls` / `sequential_choices` 沒有在小範圍 seed 下穩定曝光。

## 2. 根因

- 原本使用 `rng.choice(_SAMPLE_SPACE_COUNT_SCENARIOS)` 直接選情境，短區間 seed 可能聚集到少數情境。
- 在 `seen_parameter_tuples` 介入時，情境重抽也可能反覆落到同一類型，降低前期覆蓋。

## 3. 修改檔案

- `core/vocational_math_b4/generators/chap2_probability_basic.py`
- `tests/test_b4_chap2_phase6c1_probability_basic.py`
- `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py`
- `reports/b4_generator_planning/b4_phase6c1v_sample_space_variety_summary.md`

## 4. 修正方式

- 將 `sample_space_count_numeric` 的情境選擇改為 **seed 決定起點的 deterministic rotation**：
  - `start_idx = abs(seed) % 3`
  - `scenario_cycle = contexts[start_idx:] + contexts[:start_idx]`
  - 每次先嘗試 cycle 前段情境，若參數撞到 `seen` 再試下一個。
- 保持原 payload contract，不改 runtime 依賴；新增可選 metadata：
  - `context_type`（值為 `coin_tosses` / `dice_rolls` / `sequential_choices`）
- 強化題幹語意：
  - `coin_tosses`：明示「硬幣、正面/反面、投擲 n 次、樣本空間」
  - `dice_rolls`：明示「骰子/面骰、點數、樣本空間」，並補「兩顆骰子」版本
  - `sequential_choices`：明示「第幾階段、每階段幾種選擇」

## 5. 測試結果

執行指令：

`python -m pytest tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chap2_phase6c1r_practice_route_integration.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q`

結果：`passed`（本輪修改後回歸通過）。

新增/補強測試重點：

- `sample_space_count_numeric` 30-seed 覆蓋三種 context。
- context 對應題幹關鍵字檢查（coin/dice/sequential）。
- 題幹 forbidden token 檢查（不出現 listing / placeholder）。
- `/get_next_question` 實際 route flow（含 `gen_seed`）可觀察三種情境。

## 6. Manual smoke 指引

1. 連續測 `GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&gen_seed=1..30`：
   - 應可看到硬幣 / 骰子 / 階段選擇三類題幹。
2. 送 `POST /check_answer`：
   - 正整數答案應可判對；
   - `36.0` 與 `36%` 應判錯。
3. 確認不出現：
   - listing 題型；
   - `sample_space_listing`；
   - placeholder token。

## 7. Final confirmation

- 是否只處理 `sample_space_count_numeric` variety：**是**
- 是否新增 Phase 6C-2 題型：**否**
- 是否處理 BasicConceptsOfSets：**否**
- 是否加入 handwriting/free-response 題型：**否**
- 是否修改 database：**否**
- 是否修改 coverage matrix：**否**
- 是否修改 adaptive scoring / mastery / APR / remediation：**否**
- 是否修改 templates：**否**
- 是否啟動 Phase 6C-2：**否**
