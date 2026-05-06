# Phase 5C-D1-Fix：B4 Router / Sampling Exposure Calibration Summary

## 1) D1 root cause recap

Phase 5C-D1 smoke 已確認：在 B4 Chapter 1 unit practice 的 pure generator-first 路徑，外層與內層都用 `Random(gen_seed)` 的首抽，造成 skill 選取與 router entry 選取強耦合，導致多題型技能長期鎖在單一 `problem_type_id`，使 Phase 5C 新補題型大量 `not_seen`。

## 2) 修改檔案

- `core/routes/practice.py`
  - 新增 `_stable_b4_inner_seed(skill_id, gen_seed)`。
  - 僅在 `get_adaptive_question` 的 `pure_b4` 且有 `gen_seed` 時，將 `mod.generate(seed=inner_seed)`。
  - 加入 audit 欄位：`outer_gen_seed`、`inner_router_seed`、`seed_derivation`。
- `tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py`
  - 新增 D1-Fix 專屬 smoke / regression 測試（determinism、pure_b4 路徑、non-pure 路徑、exposure 可見性、excluded/validator 守門）。

## 3) Seed derivation design

外層 skill selection 保持原規則（不動 adaptive policy）：

- `pick_rng = random.Random(gen_seed)`
- `skill_id_for_generate = pick_rng.choice(target_skill_ids)`

內層（僅 pure B4 + 有 `gen_seed`）改為穩定派生：

```python
raw = f"b4-router::{skill_id}::{gen_seed}"
digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
inner_seed = (int(digest[:8], 16) % 1_000_000) + 1
```

說明：
- 使用 SHA-256（避免 Python 內建 `hash()` 的 process randomization）。
- 以固定模數做 bounded seed，避免部分 generator 在極端 seed 下出現長時間 sampling loop。
- 同一 `skill_id + gen_seed` 可重現同一題（deterministic reproducibility 保留）。

## 4) Before / After exposure comparison（seed 1–500）

| target problem_type_id | before (D1) | after (D1-Fix) | first_seen_seed (after) | status |
|---|---:|---:|---:|---|
| `binomial_two_variable_specific_coefficient` | 0 | 6 | 18 | visible |
| `binomial_laurent_specific_power_coefficient` | 0 | 10 | 87 | visible |
| `grid_shortest_path_count` | 0 | 9 | 115 | visible |
| `permutation_non_adjacent_arrangement` | 0 | 11 | 101 | visible |
| `factorial_equation_solve_n` | 0 | 17 | 9 | visible |

守門結果（before/after 一致）：
- `validate_b4_deterministic_adaptive_generator_payload`: failures = 0
- excluded hits = 0（`tree_diagram_listing`、`binomial_expansion_basic`、`pascal_triangle_derivation`）

## 5) QA commands / result

已執行並通過：

- `python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py` → `4 passed`
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py` → `13 passed`
- `python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py` → `4 passed`
- `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py` → `8 passed`
- `python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py` → `24 passed`
- `python -m pytest -q tests/test_phase5c_b3_binomial_specific_coefficient_generators.py` → `104 passed`
- `python -m pytest -q tests/test_phase5c_b3_grid_shortest_path_generator.py` → `107 passed`
- `python -m pytest -q tests/test_phase5c_b4_1_permutation_non_adjacent_generator.py` → `106 passed`
- `python -m pytest -q tests/test_phase5c_b4_2_factorial_equation_variation.py` → `108 passed`

## 6) 是否可以進 Phase 5C-D2

可以。

D1-Fix 後，D1 指定的 B3-A / B3-B / B4.1 / B4.2 核心補強題型已由 `not_seen` 轉為可見，且 validator 與 excluded gate 行為保持正確。建議進入 Phase 5C-D2（combination identity / hockey-stick deterministic generator）。
