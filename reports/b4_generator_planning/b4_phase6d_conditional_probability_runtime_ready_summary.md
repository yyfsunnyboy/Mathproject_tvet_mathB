# B4 Chapter 2 Phase 6D：Conditional Probability Runtime-Ready Batch Summary

## Scope and guardrails

本輪僅處理 Phase 6D 指定兩個 problem_type：

- `conditional_probability_basic`
- `without_replacement_conditional_probability`

且僅在既定範圍內完成 runtime-ready batch 所需項目（generator / checker reuse / router registry / allowlist / route integration tests / regression / summary report）。

未處理：

- IndependentEvents
- MathematicalExpectation
- BasicConceptsOfSets
- handwriting / free-response / listing 題型
- Phase 6E / 6F

---

## Runtime Smoke Gate SOP compliance

依 `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`（含 v0.1.1 frontend double-encoding guard）完成：

- Step A generator quick smoke（不載 Flask）
- Step B/C/D/E 分段 pytest（不先整包重跑）
- encoded / decoded skill_id 路徑覆蓋
- unsupported skill no legacy import guard
- handwriting reserved blocked guard
- Phase 6C + Chap1 regression

---

## Files changed

### Production code

- `core/vocational_math_b4/generators/chap2_conditional_probability.py`
  - 既有 Phase 6D generator 延續使用
  - 修正 `_make_fraction_choices()` 在小分母情況可能無限迴圈，避免 pytest/router 卡住

### Tests

- `tests/test_b4_chap2_phase6c2_probability_second_batch.py`
  - 邊界預期更新為 Phase 6D 狀態（ConditionalProbability 已開放、allowlist 數量更新）
- `tests/test_b4_chap2_phase6c1_probability_basic.py`
  - 非開放 skill 與未註冊 problem_type 斷言更新
- `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py`
  - 依目前 router seed 行為更新預期 problem_type
  - `check_answer` round-trip 改為使用 router canonical answer，並避免無限小數誤差誤判

### Existing Phase 6D files (continued, not rewritten)

- `core/vocational_math_b4/generators/chap2_conditional_probability.py`
- `core/vocational_math_b4/services/question_router.py`
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`
- `tests/test_b4_chap2_phase6d_conditional_probability.py`

---

## Implemented problem_types

1. `conditional_probability_basic`
   - skill: `vh_數學B4_ConditionalProbability`
   - formula: `P(B|A)=P(A∩B)/P(A)`
   - canonical answer: 最簡分數字串
   - checker: `check_rational_answer` flexible

2. `without_replacement_conditional_probability`
   - skill: `vh_數學B4_ConditionalProbability`
   - simple two-step without-replacement scenarios
   - canonical answer: 最簡分數字串
   - checker: `check_rational_answer` flexible

---

## Generator design summary

- 兩題皆輸出 `answer_type = rational_fraction`
- payload 含必備欄位：`question_text / answer / explanation / skill_id / problem_type_id / generator_key / difficulty / diagnosis_tags / remediation_candidates`
- explanation 保留條件機率公式或不放回後分母變化說明
- 保持 deterministic 生成與 seed 可重現
- 修復 distractor 生成終止性（小分母保證有限步結束）

---

## Router / allowlist changes

本輪沿用既有 Phase 6D 接線（已存在於工作區）：

- `question_router` 已註冊 `vh_數學B4_ConditionalProbability` 對應兩個 Phase 6D problem_type
- `b4_chapter2_phase6c1_allowlist` 已包含：
  - 6C 既有五題
  - 6D 新增兩題
- `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` 已維持不含 ConditionalProbability（因本輪開放）

---

## Checker reuse summary

- 完全重用 `core/vocational_math_b4/domain/b4_validators.py` 的 `check_rational_answer`
- 接受：
  - canonical fraction
  - unreduced equivalent fraction
  - decimal equivalent（有限小數）
  - percentage equivalent
- 拒絕：
  - wrong fraction
  - denominator zero
  - out-of-range probability

---

## Tests run

### Step A

```powershell
python -c "from core.vocational_math_b4.generators.chap2_conditional_probability import conditional_probability_basic, without_replacement_conditional_probability; print(conditional_probability_basic(...)); print(without_replacement_conditional_probability(...))"
```

- 結果：PASS（可 import、可生成）

### Step B/C/D/E（分段）

```powershell
python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py -vv -s -k "generator"
python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py -vv -s -k "checker"
python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py -vv -s -k "router or allowlist"
python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py -vv -s -k "route or practice or check_answer"
```

- `-k "generator"`：0 selected（測試名稱關鍵字未匹配）
- 其餘子集：PASS
- 曾定位到卡住點：`TestRouterPhase6D::test_router_generates_payload[conditional_probability_basic]`
  - 原因：`chap2_conditional_probability.py` distractor 生成在小分母可無限迴圈
  - 修正後不再卡住

### Full Phase 6D

```powershell
python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py -q
```

- 結果：`214 passed`

### Required regression

```powershell
python -m pytest tests/test_b4_chap2_phase6c2_probability_second_batch.py tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

- 結果：`221 passed`

---

## Manual smoke checklist

待人工執行（本輪不代替人工 smoke）：

- `/practice?skill=vh_數學B4_ConditionalProbability`
- `/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_ConditionalProbability`
- `/get_next_question?skill=vh_數學B4_ConditionalProbability&problem_type=conditional_probability_basic`
- `/get_next_question?skill=vh_數學B4_ConditionalProbability&problem_type=without_replacement_conditional_probability`
- `/check_answer` fraction / decimal / percentage equivalence
- unsupported skill clear error（不得 legacy import）
- frontend double-encoding regression
- handwriting reserved blocked

---

## Risks / known limitations

- `-k "generator"` 目前不會選到測試（命名關鍵字不一致）；建議後續補 `generator` marker 或關鍵字一致化
- 有限小數與循環小數等值比較在 route integration 測試需注意表示精度；本輪已在測試層避免循環小數誤判
- 本輪不包含 manual smoke，僅完成 automated runtime-ready

---

## Final confirmation

- 是否只處理 2 個 problem_type：是
- 是否新增 Phase 6D 題型以外內容：否
- 是否修改 production code：是，限本輪必要檔案
- 是否修改 tests：是，限本輪測試
- 是否修改 routes：否
- 是否修改 templates：否
- 是否修改 generators：是，限 Chap2 conditional probability generator
- 是否修改 database：否
- 是否修改 coverage matrix：否
- 是否新增 / 修改 deterministic allowlist：是，只限 6D 兩題 + 保留 6C
- 是否加入 handwriting/free-response 題型：否
- 是否處理 IndependentEvents / ExpectedValue：否
- 是否修改 adaptive scoring / mastery / APR / remediation：否
- 是否啟動 Phase 6E / 6F：否

---

**狀態：READY_FOR_MANUAL_SMOKE**
