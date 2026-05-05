# B4 Phase 4E Postcheck-C PermutationOfNonDistinctObjects Mapping Summary

## 1. 本階段目的

本階段修正 dashboard skill_id `vh_數學B4_PermutationOfNonDistinctObjects` 進入 practice 頁時的 missing wrapper 問題。

目標是終止 `No module named 'skills.vh_數學B4_PermutationOfNonDistinctObjects'`，並讓此 skill 進入既有 deterministic int-answer runtime。

## 2. 問題原因

- dashboard 已存在 skill_id：`vh_數學B4_PermutationOfNonDistinctObjects`。
- `skills/` 下原本沒有對應 wrapper。
- `question_router` 原本也沒有此 canonical skill_id entry。
- 因此使用者進入 `/practice/vh_數學B4_PermutationOfNonDistinctObjects` 時，practice 頁嘗試 import missing wrapper，導致 `No module named`。
- 這是 skill page mapping 問題，不是 generator coverage closure 失敗。

## 3. 實作方式

- 新增 wrapper：`skills/vh_數學B4_PermutationOfNonDistinctObjects.py`。
- 在 `core/vocational_math_b4/services/question_router.py` 新增 skill_id entry：`vh_數學B4_PermutationOfNonDistinctObjects`。
- 重用既有 problem_type：`repeated_permutation_digits`。
- 重用既有 generator_key：`b4.counting.repeated_permutation_digits`。
- 重用既有 generator function path：`core.vocational_math_b4.generators.counting.repeated_permutation_digits`。
- 未新增 generator。
- 未新增新的 problem_type。
- 未修改 route、frontend、app.py、domain functions 或 coverage matrix。

## 4. 測試結果

- Focused pytest：
  - 指令：`python -m pytest tests/test_vocational_math_b4_permutation_non_distinct_postcheck_c.py -q`
  - 結果：`6 passed`
- Core router/wrapper pytest：
  - 指令：`python -m pytest tests/test_vocational_math_b4_question_router_registry_canonical.py tests/test_vocational_math_b4_question_router_phase4e14b.py tests/test_vocational_math_b4_skill_wrappers_phase4e14b.py -q`
  - 結果：`32 passed`
- Flask route smoke in focused test：
  - `GET /practice/vh_數學B4_PermutationOfNonDistinctObjects` 回傳 `200`
  - response 不包含 `No module named`
  - response 不包含 `生成題目失敗`
- 目前未觀察到 `No module named`。

## 5. 不做的事

- 不新增 generator。
- 不修改 generator。
- 不修改 domain functions。
- 不改 route、frontend 或 app.py。
- 不更新 coverage matrix。
- 不改 manual_review 題型。
- 不接 `binomial_expansion_basic`。
- 不新增不相干 alias。

## 6. 結論

- `PermutationOfNonDistinctObjects` 已新增 canonical wrapper。
- `question_router` 已新增 canonical skill_id entry。
- 此 skill 重用 `repeated_permutation_digits` / `b4.counting.repeated_permutation_digits`。
- focused pytest 與 core router/wrapper pytest 均通過。
- 本階段未新增 generator，未修改 generator/domain/route/frontend/app.py/coverage matrix。
