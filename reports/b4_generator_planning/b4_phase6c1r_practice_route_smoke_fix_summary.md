# B4 Chapter 2 Phase 6C-1R：/practice Route Smoke Fix Summary

## 0. 問題原因

Manual smoke 發現以下兩個問題：

### A. URL encoded skill_id 未 decode

`/practice` route 從 query string / path 接收的 skill_id 為 URL-encoded 格式：

```
vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

但後端未執行 `urllib.parse.unquote`，導致查詢 DB 時找不到對應的 `SkillInfo` row，拋出「技能不存在或未啟用」錯誤。

### B. Chap2 Phase 6C-1 skills 未接入 /practice route

`/get_next_question` 在 `get_skill_info(skill_id)` 找不到 DB 記錄時，直接走 404，未處理 Chap2 P0 skills（這些 skills 可能在 `skills_info` 表中尚未建立 row）。

生成、答題批改均未有 Chap2 Phase 6C-1 分支。

---

## 1. 修改檔案清單

| 動作 | 檔案路徑 | 說明 |
|---|---|---|
| **修改** | `core/routes/practice.py` | Phase 6C-1R 所有修改集中在此（URL decode + Chap2 bypass + generator branch + checker branch） |
| **新增** | `tests/test_b4_chap2_phase6c1r_practice_route_integration.py` | Route integration tests |
| **新增** | `reports/b4_generator_planning/b4_phase6c1r_practice_route_smoke_fix_summary.md` | 本報告 |

**未修改的既有檔案：**
- `core/vocational_math_b4/generators/chap2_probability_basic.py`（未動）
- `core/vocational_math_b4/domain/b4_validators.py`（未動）
- `core/vocational_math_b4/services/question_router.py`（未動）
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`（未動）
- `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`（未動）
- 所有 templates（未動）
- 所有 routes 其他 route（未動）
- database（未動）
- coverage matrix（未動）

---

## 2. 修正內容

### A. URL decode

**位置：`core/routes/practice.py`**

```python
# 新增 import（line 14）
from urllib.parse import unquote as _url_unquote
```

三個位置加入 `_url_unquote()`：

1. `practice_query_entry`（`/practice` GET）：
   ```python
   skill_id = _url_unquote((request.args.get("skill") or "").strip())
   ```

2. `practice`（`/practice/<skill_id>` path param）：
   ```python
   @practice_bp.route('/practice/<path:skill_id>')
   def practice(skill_id):
       skill_id = _url_unquote(skill_id)
   ```
   注意：path converter 從 `<skill_id>` 改為 `<path:skill_id>` 確保 path segment 完整傳遞。

3. `next_question`（`/get_next_question` `skill` query param）：
   ```python
   skill_id = _url_unquote(request.args.get('skill', 'remainder'))
   ```

`urllib.parse.unquote` 是 idempotent：已 decode 的 skill_id 傳入不會改變。

### B. Chap2 Phase 6C-1 skill_info bypass

**位置：`next_question` 的 `skill_info = get_skill_info(skill_id)` 之後**

```python
elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
    # Phase 6C-1R: Chap2 P0 skills may not have a DB SkillInfo row.
    # Bypass DB lookup; generator handles everything.
    skill_info = {"input_type": "text", "skill_id": skill_id}
```

僅在 3 個 Chap2 P0 skills 觸發（`is_b4_chapter2_phase6c1_deterministic_skill` 為嚴格 frozenset 查詢）。

### C. Generator 分支

**位置：`next_question` 生成迴圈中的 `if _is_b4_tree_diagram...` 判斷後**

```python
elif is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
    # Guard: reject handwriting listing problem types immediately.
    if problem_type and is_b4_chapter2_excluded_problem_type(problem_type):
        return jsonify({"error": f"..."}), 422
    gen_seed = request.args.get("gen_seed", type=int)
    chap2_payload = generate_for_chap2_skill(
        skill_id=skill_id,
        level=difficulty_level,
        seed=gen_seed,
        problem_type_id=problem_type or None,
    )
    # Validate through allowlist gate
    ok_p, deny_r = validate_b4_chap2_phase6c1_generator_payload(skill_id, chap2_payload)
    if not ok_p:
        return jsonify({"error": f"Chap2 payload validation failed: {deny_r}"}), 422
    data = chap2_payload
```

### D. Answer checker 分支

**位置：`check_answer` 中，在 `mod = get_skill(skill_id)` 之後**

```python
if is_b4_chapter2_phase6c1_deterministic_skill(skill_id):
    ...
    if current.get("answer_type") == "integer":
        is_correct_chap2 = check_integer_answer(user_ans, int(correct_ans))
    else:
        # rational fraction (flexible mode)
        is_correct_chap2 = check_rational_answer(
            user_ans, exp_num, exp_den,
            allow_decimal=True, allow_percentage=True,
            validate_probability_range=True,
        )
```

確認通過：
- canonical fraction 正確（`"1/3"` → True）
- equivalent unreduced fraction 正確（`"2/6"` → True）
- decimal equivalent 正確（`"0.5"` → True for `"1/2"`）
- percentage equivalent 正確（`"50%"` → True for `"1/2"`）
- integer 正確（`"36"` → True for `36`）
- `"36.0"` 拒絕（False）
- `"36%"` 拒絕（False）
- negative integer 拒絕（False）

---

## 3. 測試結果

```
python -m pytest tests/test_b4_chap2_phase6c1r_practice_route_integration.py \
                 tests/test_b4_chap2_phase6c1_probability_basic.py \
                 tests/test_b4_chapter1_adaptive_allowlist.py -v
```

**168 passed in 0.21s**

- Phase 6C-1R 新測試：**73 passed**
- Phase 6C-1 原測試：**95 passed**
- Chap1 回歸測試：**8 passed** (也有額外 router canonical test)

---

## 4. Manual Smoke 指引

啟動 Flask app 後，請依序測試：

### 4.1 URL decode 修正

```
GET /practice?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

預期：進入練習頁面，不出現「技能不存在或未啟用」錯誤。

```
GET /practice?skill=vh_數學B4_ProbabilityDefinition
```

預期：同上（已 decoded 仍正常）。

### 4.2 取得題目

```
GET /get_next_question?skill=vh_數學B4_ProbabilityDefinition
GET /get_next_question?skill=vh_數學B4_ProbabilityProperties
GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents
```

預期：
- HTTP 200
- `new_question_text` 非空
- `answer_type` 為 `"rational_fraction"` 或 `"integer"`（非 `"handwriting"`）

### 4.3 URL encoded 取得題目

```
GET /get_next_question?skill=vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition
```

預期：HTTP 200（URL decode 後正常出題）。

### 4.4 送出答案

**古典機率（fraction）：**
```json
POST /check_answer
{"answer": "1/3"}
```
預期：`{"correct": true, "result": "正確！"}`（若 correct_answer 為 1/3）

**等值 decimal：**
```json
POST /check_answer
{"answer": "0.333"}
```
預期：不等值時 false，等值時 true（需搭配具體題目的 correct_answer）

**樣本空間計數（integer）：**
```json
POST /check_answer
{"answer": "4"}
```
預期：若 correct_answer 為 4 → `{"correct": true}`

**decimal 格式拒絕：**
```json
POST /check_answer
{"answer": "4.0"}
```
預期：`{"correct": false}`（integer strict）

### 4.5 handwriting listing 題型不可出現

```
GET /get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=sample_space_listing
```

預期：HTTP 422，錯誤訊息包含「handwriting reserved」。

### 4.6 BasicConceptsOfSets 維持不允許

```
GET /get_next_question?skill=vh_數學B4_BasicConceptsOfSets
```

預期：HTTP 404「技能不存在或未啟用」（Phase 6C-1R 不處理此技能）。

---

## 5. Final Confirmation

| 項目 | 確認 |
|---|---|
| 是否只處理 Phase 6C-1 三個 problem_type | ✅ 是 |
| 是否新增 Phase 6C-2 題型 | ✅ 否 |
| 是否處理 BasicConceptsOfSets | ✅ 否（維持 404） |
| 是否加入 handwriting/free-response 題型 | ✅ 否（listed types hard blocked） |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否修改 Chap1 allowlist | ✅ 否（Chap1 allowlist size 仍 13） |
| 是否啟動 Phase 6C-2 | ✅ 否 |
| 是否修改 templates | ✅ 否 |
| 是否重構 route | ✅ 否（minimal patch only） |
| URL decode 是否 idempotent | ✅ 是（unquote 對已 decoded 字串無副作用） |

---

*Phase 6C-1R 完成。停在此處，等待人工 smoke。*  
*狀態：READY_FOR_MANUAL_SMOKE*
