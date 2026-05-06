# Phase 5C-D1：B4 Chapter 1 Chapter Unit Practice Exposure Sampling Smoke

## 1. Smoke 目的

本報告要確認：Phase 5C 已補強並接入 router／allowlist 的題型，在 **與線上 `get_adaptive_question` 等價的 generator-first 抽樣** 下，是否真的會出現在 **B4 Chapter 1 章節單元練習**（vocational／數學B4／chapter_id=1／`practice_kind=unit_practice`）的出題分佈中。

本次為唯讀觀察與統計，未修改 production code、tests、generators、coverage matrix、adaptive routing，亦未新增 `problem_type_id` 或接入 manual_review／future_ai_judged。

---

## 2. 抽樣方法

| 項目 | 說明 |
|------|------|
| **Seed 範圍** | `gen_seed`（與 generator `seed`）= **1–500**（含端點），共 500 次。 |
| **技能池** | `sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)`，共 13 個 `skill_id`（與 `_resolve_b4_chapter_adaptive_entry` 的 `unit_skill_ids` 一致）。 |
| **模擬的 HTTP 入口行為** | 對齊 `core/routes/practice.py` 中 `get_adaptive_question` 的 **pure B4 allowlist** 分支：`pick_rng = random.Random(gen_seed)`，`skill_id_for_generate = pick_rng.choice(target_skill_ids)`，再以同一 `gen_seed` 呼叫技能模組的 `generate(**{"level": 1, "seed": gen_seed})`，其內部等同 `generate_for_skill(..., seed=gen_seed)`。 |
| **是否模擬 chapter mode URL** | 是。上述池即 chapter bridge 解析後的 **unit_skill_ids**；未模擬 DB `TextbookExample`（generator-first 路徑下跳過）。對應查詢概念：`/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&learning_mode=teaching&practice_kind=unit_practice`，且請求題目時帶 `gen_seed`。 |
| **是否經過 validator** | 每次產生後呼叫 `validate_b4_deterministic_adaptive_generator_payload(skill_id, payload)`，與 production preflight 一致。 |
| **manual_review／future_ai_judged** | 技能池僅含 allowlist；`TreeDiagramCounting`、`PascalTriangle` 等未納入池，故本抽樣自然 **未接入** 該類技能。 |

### 2.1 根因備註（抽樣結構）

外層與內層皆使用**同一整數 seed 重新建構** `random.Random(seed)`：

- 外層：`Random(seed).choice(13 個技能)`  
- 內層（多題型技能）：`generate_for_skill` 內 `Random(seed).choice(registry_entries)`（見 `question_router._select_entry`）

兩次 `Random(seed)` **各自從相同初始狀態取第一個 `choice`**，導致「抽到某技能」與「該技能下 registry 索引」之間出現 **強耦合**（對 MT19937 首抽而言，首個 `randbelow(13)` 與首個 `randbelow(n)` 的組合高度鎖定）。因此：**只要某技能在抽樣中被選中，其子題型幾乎永遠落在固定一個 `problem_type_id`**，Phase 5C 新掛在 registry **後段** 的題型在現行 seed 協定下 **無法被抽到**。

相關程式位置（僅供對照，本次未修改）：

```470:522:core/routes/practice.py
        gen_seed = request.args.get("gen_seed", type=int)
        pick_rng = random.Random(gen_seed) if gen_seed is not None else random.Random()
        ...
        if pure_b4:
            skill_id_for_generate = pick_rng.choice(target_skill_ids)
            source_type = "generator_first"
        ...
        gen_kwargs: dict = {"level": difficulty_level}
        if gen_seed is not None:
            gen_kwargs["seed"] = gen_seed
        data = mod.generate(**gen_kwargs)
```

```318:345:core/vocational_math_b4/services/question_router.py
def _select_entry(
    skill_entries: list[dict[str, object]],
    seed: int | None,
    problem_type_id: str | None,
    *,
    skill_id: str | None = None,
) -> tuple[dict[str, object], str]:
    ...
    rng = random.Random(seed)
    return rng.choice(skill_entries), "seed_based_selection"
```

---

## 3. Skill / problem_type 分布表

統計維度：**(skill_id, problem_type_id)**，500 次抽樣。`generator_key` 取自 `payload["router_trace"]["selected_generator_key"]`。`selection_reason` 多為 `seed_based_selection`；`vh_數學B4_PermutationOfNonDistinctObjects` 上出現 `seed_mod_router_balance`（與 enrichment 輪替設計一致）。

| skill_id | problem_type_id | count | percentage | first_seen_seed | generator_key | 備註 |
|----------|-----------------|------:|-----------:|----------------:|---------------|------|
| vh_數學B4_Combination | combination_basic_selection | 48 | 9.6% | 3 | b4.combination.combination_basic_selection | |
| vh_數學B4_BinomialCoefficientIdentities | binomial_coefficient_sum | 46 | 9.2% | 14 | b4.binomial.binomial_coefficient_sum | |
| vh_數學B4_PermutationOfDistinctObjects | permutation_digit_parity | 42 | 8.4% | 5 | b4.permutation.permutation_digit_parity | 同技能下僅見此題型（見 §2.1） |
| vh_數學B4_RepeatedPermutation | repeated_permutation_digits | 41 | 8.2% | 6 | b4.counting.repeated_permutation_digits | |
| vh_數學B4_FactorialNotation | factorial_evaluation | 40 | 8.0% | 9 | b4.counting.factorial_evaluation | 未見 `factorial_equation_solve_n` |
| vh_數學B4_CombinationApplications | combination_group_selection | 40 | 8.0% | 13 | b4.combination.combination_group_selection | 未見 `grid_shortest_path_count` |
| vh_數學B4_AdditionPrinciple | add_principle_mutually_exclusive_choice | 39 | 7.8% | 2 | b4.counting.add_principle_mutually_exclusive_choice | |
| vh_數學B4_CombinationDefinition | combination_definition_basic | 38 | 7.6% | 7 | b4.combination.combination_definition_basic | |
| vh_數學B4_MultiplicationPrinciple | mult_digits_no_repeat | 38 | 7.6% | 17 | b4.counting.mult_digits_no_repeat | |
| vh_數學B4_BinomialTheorem | binomial_middle_term_coefficient | 37 | 7.4% | 1 | b4.binomial.binomial_middle_term_coefficient | 未見 B3-A 兩題型 |
| vh_數學B4_CombinationProperties | combination_properties_simplification | 35 | 7.0% | 25 | b4.combination.combination_properties_simplification | 僅見 `two_term_sum` variant |
| vh_數學B4_PermutationOfNonDistinctObjects | non_distinct_objects_arrangement | 16 | 3.2% | 19 | b4.permutation.non_distinct_objects_arrangement | |
| vh_數學B4_PermutationWithRepetition | repeated_permutation_assignment | 15 | 3.0% | 24 | b4.counting.repeated_permutation_assignment | |
| vh_數學B4_PermutationOfNonDistinctObjects | repeated_permutation_digits | 13 | 2.6% | 38 | b4.counting.repeated_permutation_digits | `seed_mod_router_balance` |
| vh_數學B4_PermutationWithRepetition | repeated_choice_basic | 12 | 2.4% | 20 | b4.counting.repeated_choice_basic | |

**僅列上表 15 種 (skill, problem_type) 組合**；其餘 registry 題型在 1–500 內 **count = 0**。

---

## 4. Phase 5C 題型曝光檢查表

### A. Phase 5C-B3-A（`vh_數學B4_BinomialTheorem`）

| phase | expected problem_type_id / variant / template_context | observed? | count | first_seen_seed | status | comment |
|-------|--------------------------------------------------------|-----------|------:|----------------:|--------|---------|
| 5C-B3-A | binomial_two_variable_specific_coefficient | 否 | 0 | — | **not_seen** | 與 §2.1 seed 耦合：該技能僅命中 `binomial_middle_term_coefficient`。 |
| 5C-B3-A | binomial_laurent_specific_power_coefficient | 否 | 0 | — | **not_seen** | 同上。 |

### B. Phase 5C-B3-B（`vh_數學B4_CombinationApplications`，`grid_shortest_path_count`）

| phase | expected | observed? | count | first_seen_seed | status | comment |
|-------|----------|-----------|------:|----------------:|--------|---------|
| 5C-B3-B | variant `basic` | 否 | 0 | — | **not_seen** | 該技能僅命中 `combination_group_selection`。 |
| 5C-B3-B | variant `via_point` | 否 | 0 | — | **not_seen** | 同上。 |
| 5C-B3-B | variant `avoid_point` | 否 | 0 | — | **not_seen** | 同上。 |

### C. Phase 5C-B4.1（`vh_數學B4_PermutationOfDistinctObjects`）

| phase | expected problem_type_id | observed? | count | first_seen_seed | status | comment |
|-------|--------------------------|-----------|------:|----------------:|--------|---------|
| 5C-B4.1 | permutation_non_adjacent_arrangement | 否 | 0 | — | **not_seen** | 該技能僅命中 `permutation_digit_parity`。 |

### D. Phase 5C-B4.2（`vh_數學B4_FactorialNotation`，`factorial_equation_solve_n`）

| phase | expected variant | observed? | count | first_seen_seed | status | comment |
|-------|------------------|-----------|------:|----------------:|--------|---------|
| 5C-B4.2 | ratio_basic | 否 | 0 | — | **not_seen** | 該技能僅命中 `factorial_evaluation`。 |
| 5C-B4.2 | multiply_factorial_equation | 否 | 0 | — | **not_seen** | 同上。 |
| 5C-B4.2 | factorial_sum_linear_equation | 否 | 0 | — | **not_seen** | 同上。 |
| 5C-B4.2 | factorial_product_ratio | 否 | 0 | — | **not_seen** | 同上。 |

### E. Phase 5C-B4 small template enrichment

| phase | expected | observed? | count（題次） | first_seen_seed | status | comment |
|-------|----------|-----------|--------------:|----------------:|--------|---------|
| 5C-B4 | repeated_permutation_digits：`set_menu` / `badge_pin` / `locker_code` | 是 | 4 / 9 / 9 | 6+ | **visible** | 另見既有語境如 `password`、`seat_serial`、`trial_sequence` 等。 |
| 5C-B4 | add_principle：`bookshelf` / `routes` / `meal_types` / `activity_tracks` | 是 | 8 / 13 / 1 / 9 | 2+ | **visible**（`meal_types` **low_exposure**） | 另出現 `clubs`（8）— 非本次清單列名，屬額外语境。 |
| 5C-B4 | combination_definition_basic：`works_exhibit` / `exam_pick` / `committee` / `sample_draw` / `delegate_pick` | 是 | 9 / 6 / 5 / 10 / 8 | 7+ | **visible** | 五種 template_context 皆有命中。 |
| 5C-B4 | combination_properties_simplification：`two_term_sum` | 是 | 35 | 25 | **visible** | |
| 5C-B4 | combination_properties_simplification：`symmetry_word` | 否 | 0 | — | **not_seen** | 500 次內 generator 未給出該 variant。 |
| 5C-B4 | combination_properties_simplification：basic／既有 | 否 | 0 | — | **not_seen** | 同上（僅 `two_term_sum`）。 |
| 5C-B4 | non_distinct_objects_arrangement：`word_tiles` / `badge_strip` | 是 | 2 / 4 | 19+ | **visible**（偏低） | 另見 `objects`、`colored_balls`、`letters` 等。 |

---

## 5. Validator / gate 結果

| 項目 | 結果 |
|------|------|
| `validate_b4_deterministic_adaptive_generator_payload` | **500／500 通過**，無擋下紀錄。 |
| 期望 **未出現** 的 excluded `problem_type_id` | **`tree_diagram_listing`、`binomial_expansion_basic`、`pascal_triangle_derivation` 皆 0 次**（與 allowlist／gate 政策一致）。 |

---

## 6. 結論

1. **Phase 5C-B3-A、B3-B、B4.1、B4.2 核心補強題型**：在與線上相同的 `gen_seed` 協定下，於 seed **1–500** 的 chapter unit practice 抽樣中 **皆不可見（not_seen）**。原因已非 generator 品質單一問題，而是 **外層技能選取與內層 `generate_for_skill` 共用同一 `Random(seed)` 首抽** 造成的 **registry 子題型鎖死**。
2. **Phase 5C-B4 小模板擴充**：多數 **template_context 可見**；`combination_properties_simplification` 在樣本內 **僅見 `two_term_sum`**，`symmetry_word` 與 basic 類 variant **not_seen**（可能需另開 generator 內部抽樣或更長 seed 窗確認，但與 B3/B4.1/B4.2 的「結構性 not_seen」層級不同）。
3. **是否需要 sampling calibration**：**是（強烈）**。建議列為 **Phase 5C-D1-Fix：router／sampling exposure calibration**（例如：內層改用 `hash((skill_id, gen_seed))` 或 `gen_seed * P + Q` 等 **與外層解耦** 的派生 seed，或分離 `pick_seed`／`gen_seed` 參數），否则 Phase 5C 新增題型在 **實際 chapter unit practice** 中仍形同不可達。
4. **是否可進入 Phase 5C-D2（組合遞移／hockey-stick）**：**不建議在修正 D1-Fix 前進入**。closure audit 已標示 hockey-stick 仍缺 generator；在現行曝光結構下，即使新增 generator，**多題型技能仍可能長期鎖在單一子題型**，應先修正抽樣可達性。

---

## 7. 下一步建議

- **若目標為「Phase 5C 補強題型在 unit practice 可見」**：優先執行 **Phase 5C-D1-Fix（router／sampling exposure calibration）**，再重跑本 smoke（同 seed 窗或 1–5000）驗證 B3-A／B3-B／B4.1／B4.2 是否轉為 **visible** 或至少 **low_exposure**。
- **若 D1-Fix 後主要題型皆 visible**：再依 closure audit 進入 **Phase 5C-D2：combination identity／hockey-stick deterministic generator**。
- **combination_properties** 若 Fix 後仍長期缺 `symmetry_word`／basic：**另做 generator 內部 variant 抽樣審計**（仍屬 exposure／機率設計，非本報告 seed 窗可單獨證成）。

---

*報告產出：唯讀抽樣腳本於本機執行（Python，`core` 模組 import），統計窗 seed 1–500。對照 closure audit：`reports/b4_generator_planning/b4_phase5c_c_b4_ch1_must_cover_closure_audit.md`。*
