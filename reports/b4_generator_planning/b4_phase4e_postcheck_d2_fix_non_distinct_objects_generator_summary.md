# B4 Phase 4E Postcheck-D2-Fix Non-Distinct Objects Generator Summary

## 1. 本階段目的

本階段新增真正的不盡相異物排列 generator：`non_distinct_objects_arrangement`。

目的在於補足 `vh_數學B4_PermutationOfNonDistinctObjects` 的數學語義，使後續不必只依賴 Postcheck-C 的 temporary surrogate：`repeated_permutation_digits`。

本階段只新增 generator 與 generator tests，尚未接入 question_router、wrapper、web smoke 或 coverage matrix。

## 2. 新增 generator

| function | problem_type_id | generator_key | answer 型態 | router 接入 |
|---|---|---|---|---|
| `non_distinct_objects_arrangement` | `non_distinct_objects_arrangement` | `b4.permutation.non_distinct_objects_arrangement` | `int` | no |

新增位置：

- `core/vocational_math_b4/generators/permutation.py`

支援 context：

- `letters`
- `colored_balls`
- `objects`

## 3. 數學語義

本 generator 處理的是不盡相異物排列 / 多重集合排列。

它不同於 repeated choices：

- repeated choices：每個位置都可從同一集合中選，且可重複選，公式通常為 $m^{n}$。
- non-distinct object permutation：給定固定物件集合，其中有些物件相同，排列時相同物互換不產生新排列。

本 generator 使用：

```text
factorial(total_count) // product(factorial(count) for count in duplicate_counts)
```

對應數學式為：

$\frac{n!}{a!b!\cdots}$

explanation 會說明：

- 若先把所有物件都當相異，共有 $n!$ 種排列。
- 相同物互換不產生新排列。
- 因此需除以相同物內部交換數。

## 4. 測試結果

Focused pytest：

```text
python -m pytest tests/test_vocational_math_b4_generators_postcheck_d2_fix.py -q
```

結果：

```text
10 passed
```

Generator regression pytest：

```text
python -m pytest tests/test_vocational_math_b4_generators_phase4e14a.py tests/test_vocational_math_b4_generators_phase4e12b.py tests/test_vocational_math_b4_generators_phase4b2.py -q
```

結果：

```text
56 passed
```

## 5. 尚未做

- 尚未接 question_router。
- 尚未改 wrapper。
- 尚未 web smoke test。
- 尚未更新 coverage matrix。
- Postcheck-C temporary surrogate 仍存在。
- `/practice/vh_數學B4_PermutationOfNonDistinctObjects` 目前仍透過既有 router mapping 使用 `repeated_permutation_digits`。

## 6. 下一步建議

1. Postcheck-D2-QA：樣題檢查。
2. Postcheck-D2-Connect：若 QA 通過，接入 `vh_數學B4_PermutationOfNonDistinctObjects` router。
3. 接入後可考慮讓新 problem_type 成為主要/default 題型，`repeated_permutation_digits` 只作 fallback 或移回 RepeatedPermutation。

## 7. 結論

- 已新增真正的不盡相異物排列 generator。
- answer 維持 `int`，可支援 deterministic runtime。
- focused pytest 與 generator regression pytest 均通過。
- 本階段未接 router、未改 wrapper、未改 route/frontend/app.py、未改 coverage matrix。
- Postcheck-C temporary surrogate 仍存在，待後續 QA 與 Connect 階段處理。
