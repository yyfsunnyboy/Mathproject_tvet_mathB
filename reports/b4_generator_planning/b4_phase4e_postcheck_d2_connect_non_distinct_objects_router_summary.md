# B4 Phase 4E Postcheck-D2-Connect Non-Distinct Objects Router Summary

## 1. 本階段目的

本階段將真正語義對齊的 `non_distinct_objects_arrangement` 接入 `vh_數學B4_PermutationOfNonDistinctObjects` router。

目標是讓此 skill 可指定產生真正不盡相異物排列題型，同時保留 Postcheck-C 的 `repeated_permutation_digits` temporary surrogate 作為 fallback。

## 2. 接入項目

| skill_id | problem_type_id | generator_key | role |
|---|---|---|---|
| `vh_數學B4_PermutationOfNonDistinctObjects` | `non_distinct_objects_arrangement` | `b4.permutation.non_distinct_objects_arrangement` | primary / main |
| `vh_數學B4_PermutationOfNonDistinctObjects` | `repeated_permutation_digits` | `b4.counting.repeated_permutation_digits` | fallback / temporary surrogate retained |

## 3. 實作方式

- 本階段只修改 `core/vocational_math_b4/services/question_router.py`。
- 保留既有 wrapper：`skills/vh_數學B4_PermutationOfNonDistinctObjects.py`。
- 保留 `repeated_permutation_digits` fallback。
- 新增 router enrichment entry，使 `problem_type_id="non_distinct_objects_arrangement"` 可指定產題。
- default selection 仍相容 Postcheck-C 既有測試，且 seed 1-10 內可抽到 `non_distinct_objects_arrangement`。
- 未新增 generator，使用 Postcheck-D2-Fix 已存在的 `permutation.non_distinct_objects_arrangement`。

## 4. 測試結果

Focused pytest：

```text
python -m pytest tests/test_vocational_math_b4_permutation_non_distinct_postcheck_d2_connect.py -q
```

結果：

```text
6 passed
```

Core related pytest：

```text
python -m pytest tests/test_vocational_math_b4_permutation_non_distinct_postcheck_c.py tests/test_vocational_math_b4_generators_postcheck_d2_fix.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

結果：

```text
41 passed
```

確認：

- 未觀察到 `No module named`。
- 可指定 `non_distinct_objects_arrangement` 產題。
- wrapper 可透過 `problem_type_id="non_distinct_objects_arrangement"` 產出新題型。
- 可指定 `repeated_permutation_digits` fallback。
- canonical registry test 仍通過，未重新引入亂碼 alias。

## 5. 待人工 Web Smoke Test

請人工測試：

```text
/practice/vh_數學B4_PermutationOfNonDistinctObjects
```

檢查項目：

- 不再 `No module named`。
- 可正常產題。
- 有機會出現真正不盡相異物排列題。
- 題幹像 A、A、B、C 或彩球相同物排列。
- 不再只有「每位可重複使用」題。
- LaTeX 正常。
- 答對 / 答錯正常。
- terminal 無 500 error。

## 6. 不做的事

- 不新增 generator。
- 不新增 wrapper。
- 不改 domain functions。
- 不改 route/frontend/app.py。
- 不更新 coverage matrix。
- 不改 dashboard skill name。
- 不碰 TreeDiagramCounting / PascalTriangle。
- 不接 `binomial_expansion_basic`。

## 7. 結論

- `non_distinct_objects_arrangement` 已可透過 router 指定產題。
- `repeated_permutation_digits` fallback 已保留。
- wrapper 不需修改即可使用新 problem_type。
- focused pytest 與 core related pytest 均通過。
- 仍需人工 web smoke test 確認 practice page 實際體驗。
