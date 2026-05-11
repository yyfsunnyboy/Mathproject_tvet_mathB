# B4 SamplingSurvey Deterministic Choice Mode Repair Summary

## 1. 問題描述
在 B4 Phase B4 SamplingSurvey 的出題機制中，原本針對「母群體 / 樣本 / 母群體數 / 樣本數」的選擇題雖然是選擇題格式，但系統仍會將其標記為 `review_mode`（AI/review 判分路徑），導致學生在作答時無法由系統自動判斷正確與否。

## 2. Root Cause
原先 `SamplingSurvey` 所有的題目均封裝在 `sampling_survey_review_shell` 這個產生器（generator）內，且直接在產生器中強迫寫死了 metadata：
```python
"requires_teacher_review": True,
"runtime_mode": "teacher_review",
"check_mode": "review_mode",
"grading_mode": "teacher_review",
```
因此即使其題型為單純的選項辨識（如：population_sample_identification），仍會被當作需要老師或 AI 人工覆核的題目，觸發了 `/check_answer` API 提早返回「此題為 AI/review 判分路徑」的邏輯。

## 3. 修正方式
將原本的封裝拆分為「標準選擇題」與「未來保留的開放式說明題」：
1. **重構選擇題產生器**：將原有的 `sampling_survey_review_shell` 更名為 `sampling_survey_foundation_choice`，專門處理 `population_sample_identification`, `population_sample_size_identification`, `census_or_sample_survey_identification` 等選擇題，並修改其 metadata 為 deterministic_choice。
2. **新增開放式說明題殼（Shell）**：新建 `sampling_survey_bias_review_shell` 作為「抽樣偏誤」這類未來開放式題型的保留位置，維持其 `review_mode` 設定。
3. **更新路由對應**：在 `core/vocational_math_b4/services/question_router.py` 的 `vh_數學B4_SamplingSurvey` 設定中，同時註冊選擇題及開放題的路由。

## 4. 修正後 metadata (SamplingSurvey 選擇題)
```python
"problem_type_id": "sampling_survey_foundation_identification",
"scenario_family": "sampling_survey_foundation_identification",
"answer_input_type": "choice",
"requires_teacher_review": False,
"runtime_mode": "deterministic_choice",
"check_mode": "deterministic_auto_checked",
"grading_mode": "deterministic",
```

## 5. 修改檔案
- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
  - 將原來的 `sampling_survey_review_shell` 重構為 `sampling_survey_foundation_choice`。
  - 新增 `sampling_survey_bias_review_shell` 提供未來開放式問答使用。
- `core/vocational_math_b4/services/question_router.py`
  - 修改 `vh_數學B4_SamplingSurvey` 的註冊表，對應新的 deterministic 產生器及 review 產生器。
- `tests/test_b4_3_1_conceptual_skill_boundary_repair.py`
  - 更新測試驗證標準，將原本期待的 `sampling_survey_bias_review` 取代為 `sampling_survey_foundation_identification`。

*(註：因 `core/routes/practice.py` 主要是判斷 payload 的 `check_mode`，只要產生器正確給出 `deterministic_auto_checked`，即會自動進入正確比對流程，因此不需動到 `practice.py`。)*

## 6. 新增 tests
新增 `tests/test_b4_sampling_survey_deterministic_choice_mode_repair.py`：
- **SamplingSurvey deterministic choice metadata test**：驗證選擇題產出的各項 mode 是否為 deterministic。
- **SamplingSurvey choices test**：驗證 choices 陣列是否正常產出並包含 4 個選項。
- **SamplingSurvey check_answer test**：驗證 practice API 的檢查流程是否可正確通過（未被誤認為 AI review）。

## 7. 測試結果
所有針對本次修復及 regression 的測試指令皆順利通過：
- `pytest -q tests/test_b4_sampling_survey_deterministic_choice_mode_repair.py`
- `pytest -q tests/test_b4_choice_payload_rendering_repair.py`
- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py`
- `pytest -q tests/test_b4_3_2_review_payload_repair.py`
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py`
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py`

## 8. 是否影響 B4 final coverage count
**未影響 B4 final coverage count**。
因為 `vh_數學B4_SamplingSurvey` 此前已位於 `B4_CHAPTER3_PHASE7B_RUNTIME_ALLOWLIST`（非純 deterministic 計數範圍）。將題型在 runtime 從 `review` 修正為 `deterministic` 只是改進題型行為，並未變更涵蓋率與白名單的計算基底，也沒有大改架構。

## 9. Final Status
**READY_FOR_RECHECK**
