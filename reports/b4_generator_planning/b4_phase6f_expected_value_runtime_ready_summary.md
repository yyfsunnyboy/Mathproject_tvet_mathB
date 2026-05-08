# B4 Chapter 2 Phase 6F — Expected Value Runtime-Ready Summary

**Status:** READY_FOR_MANUAL_SMOKE  

**SOP:** Complies with `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` (incl. v0.1.1 frontend double-encoding guard). Encoded/decoded skill_id checks and double-encoding regression are covered in `tests/test_b4_chap2_phase6f_expected_value.py`; Phase 6D double-encoding parametrization was extended with the MathematicalExpectationDefinition encoded URL fragment.

---

## 1. Scope and guardrails

**In scope (only):**

| problem_type_id | skill_id |
|-----------------|----------|
| `expectation_discrete_basic` | `vh_數學B4_MathematicalExpectationDefinition` |
| `expectation_from_distribution` | `vh_數學B4_MathematicalExpectationDefinition` |

**Explicitly out of scope (unchanged):** `expectation_word_problem_profit_fairness`, `ApplicationsOfExpectation`, `vh_數學B4_MathematicalExpectation` self-assessment, `probability_algebra_mixed`, `event_operation_probability`, `BasicConceptsOfSets`, handwriting / listing types, Chap1 allowlist edits, Phase 6G/6H.

---

## 2. Runtime Smoke Gate SOP compliance

- Deterministic generators with stable payload keys and `correct_answer == answer`.
- Chap2 gated skills: unsupported skills do not fallback to legacy `skills.<skill_id>` (tests still patch `import_module`).
- URL-encoded skill round-trip plus **frontend double-encoding** simulation for `vh_%E6%95%B8%E5%AD%B8B4_MathematicalExpectationDefinition`.
- `/practice` / `/get_next_question` / `/check_answer`: expectation items use dedicated `answer_type` and checker path (see §7).

---

## 3. Files changed

| Area | Path |
|------|------|
| Generator | `core/vocational_math_b4/generators/chap2_expected_value.py` (new) |
| Validator | `core/vocational_math_b4/domain/b4_validators.py` (`check_expected_value_answer`) |
| Router | `core/vocational_math_b4/services/question_router.py` |
| Allowlist | `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py` |
| Practice | `core/routes/practice.py` (minimal branch for `expected_value`) |
| Tests | `tests/test_b4_chap2_phase6f_expected_value.py` (new) |
| Regression | `tests/test_b4_chap2_phase6d_conditional_probability.py`, `tests/test_b4_chap2_phase6e_independent_events.py`, `tests/test_b4_chap2_phase6c2_probability_second_batch.py` |
| Report | This file |

---

## 4. Implemented problem_types

1. **`expectation_discrete_basic`** — Discrete \(E(X)=\sum x\,P(X=x)\) with 2–4 outcomes; nonnegative integer \(x_i\); random positive integer composition probabilities over common denominators \(\{6,8,12\}\); narration + \(\sum_x P(X=x)=1\).
2. **`expectation_from_distribution`** — Same distribution logic; question uses a **Markdown pipe table** of \(x\) vs \(P(X=x)\).

---

## 5. Generator design summary

- **Probabilities:** `W ∈ {6,8,12}`, random composition of \(W\) into \(k\) parts (\(k \in \{2,3,4\}\)), each \(P(X=x_i)=w_i/W\).
- **Expectation:** `Fraction`; canonical **reduced** string via `_fraction_str`; `answer_type` = **`expected_value`**.
- **Choices:** Exactly four options including the correct reduced answer; nonnegative distractors; shuffle after assembly.
- **Explanations:** Required \( \sum_x x\cdot P(X=x)\) expansion with substituted numeric chain.

---

## 6. Router / allowlist changes

- Registry key `vh_數學B4_MathematicalExpectationDefinition` with both Phase 6F generators.
- `B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES`: +`expectation_discrete_basic`, +`expectation_from_distribution`.
- `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`: removed `vh_數學B4_MathematicalExpectationDefinition` (still blocks Applications / legacy MathematicalExpectation / ProbabilityOperations / BasicConceptsOfSets).

---

## 7. Checker reuse / minimal implementation summary

**`check_expected_value_answer(user, correct_str)`** in `b4_validators.py`: wraps `check_rational_answer` with `allow_decimal=True`, **`allow_percentage=False`**, **`validate_probability_range=False`** (expectation may exceed \([0,1]\)).

`practice.check_answer`: if `answer_type == "expected_value"`, delegates to `check_expected_value_answer` instead of probability-style `allow_percentage=True`.

---

## 8. Tests run

Segmented:

```powershell
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -k "generator" -vv --tb=short
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -k "checker" -vv --tb=short
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -k "router or allowlist" -vv --tb=short
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -k "route or practice or check_answer" -vv --tb=short
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py -q
```

Combined regression (+ Phase 6F file):

```powershell
python -m pytest tests/test_b4_chap2_phase6f_expected_value.py `
  tests/test_b4_chap2_phase6e_independent_events.py `
  tests/test_b4_chap2_phase6d_conditional_probability.py `
  tests/test_b4_chap2_phase6c2_probability_second_batch.py `
  tests/test_b4_chap2_phase6c1_probability_basic.py `
  tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py `
  tests/test_b4_chapter1_adaptive_allowlist.py `
  tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

**Result:** `593 passed` on the unified run listed above (13 SQLAlchemy `utcnow()` deprecation warnings from DB-backed integration tests).

---

## 9. Manual smoke checklist

- [ ] Open `/practice?skill=vh_數學B4_MathematicalExpectationDefinition` — page loads without legacy import failure.
- [ ] Open encoded URL `%E6%95%B8%E5%AD%B8B4_MathematicalExpectationDefinition` variant — same.
- [ ] `/get_next_question` with both `problem_type` values pinned — distinct stems (list vs Markdown table style).
- [ ] `/check_answer`: correct **fraction**, **unreduced fraction**, **exact decimal when terminating** succeed; **`50%` style rejected** on expectation skill.
- [ ] Confirm handwritten listing types remain blocked (`sample_space_listing`, etc.).
- [ ] Spot-check Chap2 pooled rotation still rotates across all enabled skills/problem types as expected.

---

## 10. Risks / known limitations

- **Percentage answers** intentionally unsupported for expectation (Phase 6F spec); probability skills still accept `%` via original path.
- **Distractors** are numeric only (≥0); pedagogical realism is secondary to deterministic uniqueness.
- **`validate_b4_chap2_phase6c1_generator_payload` naming** remains “phase6c1” for historical continuity; semantics now cover phases through **6F**.

---

## 11. Final confirmation

| Item | Answer |
|------|--------|
| 是否只處理 2 個 problem_type | **是** |
| 是否新增 Phase 6F 題型以外內容 | **否** |
| 是否修改 production code | **是**，限 router / Chap2 allowlist / `practice.check_answer` 最小分支 / `b4_validators` 新增期望值 checker / 新增 generator 模組 |
| 是否修改 tests | **是**，新增 `test_b4_chap2_phase6f_expected_value.py`，並調整 Phase 6D/6E/6C-2 regression 數量断言 |
| 是否修改 routes | **是**：`practice.py` 對 `answer_type=="expected_value"` 之批改分流（除此以外 Chap2 routing 沿用既有 deterministic 路徑） |
| 是否修改 templates | **否** |
| 是否修改 generators | **是**，限 `chap2_expected_value.py` |
| 是否修改 database | **否** |
| 是否修改 coverage matrix | **否** |
| 是否新增 / 修改 deterministic allowlist | **是**，只限開放 MathematicalExpectationDefinition + 兩種題型，並保留先前 6C/6D/6E |
| 是否加入 handwriting/free-response | **否** |
| 是否處理 ApplicationsOfExpectation / MathematicalExpectation 自評題 | **否** |
| 是否修改 adaptive scoring / mastery / APR / remediation | **否** |
| 是否啟動 Phase 6G | **否** |
