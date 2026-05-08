# B4 Chapter 2 Phase 6B Probability Validator Plan

## 0. Scope and Guardrails

本輪為 **validator / checker contract planning report only**。

明確聲明：
- ❌ 未修改 production code
- ❌ 未修改 tests
- ❌ 未修改 routes / templates / generators
- ❌ 未修改 database
- ❌ 未修改 coverage matrix
- ❌ 未新增 allowlist
- ❌ 未修改 adaptive scoring / mastery / APR / remediation
- ❌ 未修改 `core/vocational_math_b4/domain/b4_validators.py`
- ❌ 未新增任何 `.py` 實作
- ❌ 未啟動 Phase 6C
- ✅ 僅新增本 validator planning report

---

## 1. Evidence Sources

| 來源 | 路徑 | 用途 |
|---|---|---|
| Chap2 inventory | `reports/b4_generator_planning/b4_chap2_inventory.md` | 題數、needs_review、risk list |
| Phase 6A taxonomy | `reports/b4_generator_planning/b4_phase6a_chap2_problem_type_taxonomy.md` | 24 個 problem_type 分流與 checker 需求標記 |
| 教材匯入 SOP | `docs/系統SOP/教材匯入與技能生成SOP_v0.1.md` (v0.2) | 分流規則 |
| AI 閉環 SOP | `docs/系統SOP/AI閉環開發與驗收SOP_v0.1.md` | agent 邊界 |
| `b4_validators.py` | `core/vocational_math_b4/domain/b4_validators.py` | **只讀**，確認現有 validator 函式與命名規範 |

`b4_validators.py` 現況觀察（只讀，不修改）：
- 現有函式：`validate_positive_integer`、`validate_nonnegative_integer`、`validate_n_ge_r`、`validate_choices_unique`、`validate_answer_in_choices`、`validate_no_unfilled_placeholder`、`validate_integer_answer`、`validate_expression_answer`、`validate_polynomial_answer`、`validate_parameter_tuple_not_seen`、`validate_problem_payload_contract`
- 命名風格：`validate_*`（payload 與值驗證）
- 目前無 probability / rational / decimal / percentage / expected_value 相關 checker
- Chap2 所需 checker 全部為新增，不與現有函式衝突

---

## 2. Validator Design Principles

### 2.1 Canonical answer 與 accepted equivalent answers 分離

- **canonical answer**：generator 儲存的標準答案格式（建議：最簡分數字串 `"a/b"` 或整數字串 `"n"`）
- **accepted equivalents**：checker 在比對時可接受的等值格式（如 `0.5`、`50%`、`$\frac{1}{2}$`）
- 兩者分離：explanation 永遠顯示 canonical；checker 可彈性正規化

### 2.2 Checker normalization 與 explanation display 分離

- checker 負責：將 user_answer 正規化 → 與 canonical 比對
- explanation 負責：以 canonical 格式顯示正確答案
- 不將正規化邏輯混入 explanation 文字

### 2.3 Probability range validation 是共通層

- 所有機率類答案（rational / decimal / percentage）在比對前，先做 `probability_range_validator`
- 範圍：`0 <= P <= 1`（正規化後）
- 超出範圍：返回 `invalid_probability_range` 錯誤，不進行值比對

### 2.4 Strict mode vs Flexible mode

| mode | 說明 | 適用場景 |
|---|---|---|
| strict | 只接受 canonical 格式，不接受等值替換 | 題目明確要求「以分數表示」、「以整數回答」 |
| flexible | 接受等值等價格式（小數、百分比、未化簡分數） | 一般練習題，答對語意即可 |

- 預設：**flexible mode**
- strict mode 需由 generator 明確設定 `strict_mode=True`
- Phase 6C 首批建議使用 flexible mode

### 2.5 Deterministic 題型不得混入 handwriting listing

- `sample_space_listing`、`event_set_listing`、`subset_listing` 的 checker 標記為 `not_ready`
- 不實作對應 checker，不得進 deterministic allowlist

---

## 3. Answer Normalization Policy

| 項目 | 正規化規則 |
|---|---|
| 前後空白 | `strip()` 移除 |
| 全形數字 | 轉換為半形（`０１２...９` → `0123...9`） |
| 全形英文字母 | 選擇題轉半形大寫（`Ａ` → `A`） |
| LaTeX fraction | `$\frac{a}{b}$`、`\frac{a}{b}`、`\dfrac{a}{b}` → 提取 `a/b` |
| plain fraction | `a/b` → 保留，解析為 numerator=a, denominator=b |
| decimal | `0.5`、`.5`、`0.500` → float |
| percentage | `50%` → 移除 `%` → `50` → `/100` → `0.5` |
| unit suffix | `5元`、`$5`、`5 元` → 移除單位後綴，保留數值 |
| negative values | `-3`、`-3/5`、`-0.6` → 允許，保留負號 |
| bool guard | `True`/`False` → 拒絕，返回 `invalid_type` |
| empty / None | → 返回 `missing_answer` |
| division by zero | 分母為 `0` → 返回 `invalid_fraction` |

---

## 4. Checker Contract Table

| checker_name | intended_use | accepted_formats | rejected_formats | normalization | equality_policy | error_message_policy | notes |
|---|---|---|---|---|---|---|---|
| `integer_checker` | 樣本數、集合元素個數、容斥計數 | 整數字串 `"36"`、整數 `36` | 分數、小數、百分比、負整數（視情境） | strip → fullmatch `[0-9]+` | exact integer equality | 「請輸入整數」 | 非負整數；可依情境允許零 |
| `rational_checker` | 古典機率、補事件、聯集、條件、獨立 | `"1/2"`、`"0.5"`（flexible）、`"50%"`（flexible）、`"$\frac{1}{2}$"` | 不合法分數（分母0）、超出 [0,1] 機率 | LaTeX strip → parse fraction → 化簡比較 | 化簡後分子分母相等 | 「請輸入分數或小數」 | canonical 為最簡分數；strict mode 不接受小數 |
| `decimal_tolerance_checker` | 小數機率、命中率、有限小數期望值 | `"0.5"`、`"0.500"`、`".5"` | 百分比（strict）、非數值字串 | strip → float cast | `abs(user - expected) <= tolerance` | 「答案與正確值相差過大」 | 預設 tolerance=0.001 |
| `percentage_checker` | 百分比形式機率、命中率 | `"50%"`、`"50"`（明確題幹下） | 純分數（strict）、超出 [0,100] 範圍 | 移除 `%` → `/100 → float | `abs(norm_user - norm_expected) <= tolerance` | 「請輸入百分比，例如 50%」 | `50` 是否接受見 Q3 政策 |
| `probability_range_validator` | 所有機率共通層 | 正規化後 `[0, 1]` 的任意格式 | 超出範圍 | 依各 checker 正規化後驗證 | `0 <= P <= 1` | 「機率應介於 0 與 1 之間」 | 前置驗證層，非獨立 checker |
| `expected_value_checker` | 離散期望值、應用題 | 分數 `"3/2"`、小數 `"1.5"`、負值 `"-3"` | 百分比（除非題意為比例）、帶不認識單位 | strip unit → parse number → tolerance 比對 | `abs(user - expected) <= tolerance` | 「期望值計算有誤」 | 允許負值；tolerance=0.001 |
| `choice_answer_checker` | 選擇題（單選/多選） | `"A"`、`"a"`、`"Ａ"`、`"AB"`、`"A,B"`、`"A、B"` | 不在選項集的字母 | strip → 半形 → 大寫 → sorted join | 選項集合相等 | 「請選擇有效選項」 | 多選時排序後比對 |
| `set_count_checker` | 集合元素個數（alias of integer_checker） | 同 integer_checker | 同 integer_checker | 同 integer_checker | exact integer equality | 「請輸入集合元素個數（整數）」 | domain alias；未來可加 upper bound 驗證 |

---

## 5. Problem Type to Checker Mapping

### Phase 6C Candidates

| problem_type | primary_skill | checker | strict_or_flexible | canonical_answer_format | accepted_equivalent_formats | notes |
|---|---|---|---|---|---|---|
| `classical_probability_fraction` | ProbabilityDefinition | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 `"a/b"` | `"a/b"` 未化簡、`"0.x"`、`"$\frac{a}{b}$"` | 建議 explanation 顯示最簡分數 |
| `complement_probability` | ProbabilityProperties | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 `"a/b"` | 同上 | P(A')=1-P(A) |
| `union_intersection_probability` | ProbabilityProperties | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 `"a/b"` | 同上 | P(A∪B) 公式 |
| `sample_space_count_numeric` | SampleSpaceAndEvents | `integer_checker` | strict | 整數字串 `"36"` | 無（strict） | n(S) 唯一整數 |
| `dice_coin_probability_count` | ProbabilityDefinition | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 `"a/b"` | 同上 | 排除 image-related 2 筆 |
| `set_operation_count` | BasicConceptsOfSets | `set_count_checker` | strict | 整數字串 | 無 | 容斥計數 |
| `inclusion_exclusion_count` | BasicConceptsOfSets | `set_count_checker` | strict | 整數字串 | 無 | 可與 set_operation_count 共用 generator |

### Phase 6D Candidates

| problem_type | primary_skill | checker | strict_or_flexible | canonical_answer_format | accepted_equivalent_formats | notes |
|---|---|---|---|---|---|---|
| `conditional_probability_basic` | ConditionalProbability | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 | 等值小數 | 需條件一致性 validator |
| `without_replacement_conditional_probability` | ConditionalProbability | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 | 等值小數 | 袋取球情境 |
| `independent_joint_probability` | IndependentEvents | `rational_checker` 或 `decimal_tolerance_checker` | flexible | 最簡分數或小數 | 等值小數或分數 | 依題目形式選 checker |
| `independent_at_least_one_probability` | IndependentEvents | `rational_checker` 或 `decimal_tolerance_checker` | flexible | 最簡分數或小數 | 等值 | 1-(1-p)^n |
| `set_membership_judgement` | BasicConceptsOfSets | `choice_answer_checker` | strict | `"A"` / `"B"` / `"C"` / `"D"` | 小寫、全形 | 單選 |
| `event_relation_judgement` | SampleSpaceAndEvents | `choice_answer_checker` | strict | `"A"` 等 | 小寫、全形 | 單選 |
| `independent_event_judgement` | IndependentEvents | `choice_answer_checker` | strict | `"A"` 等 | 小寫、全形 | 部分表格題 → D 類 |
| `set_probability_word_problem` | ProbabilityProperties | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 | 等值小數 | 注意事件映射 |

### Phase 6E Candidates

| problem_type | primary_skill | checker | strict_or_flexible | canonical_answer_format | accepted_equivalent_formats | notes |
|---|---|---|---|---|---|---|
| `expectation_discrete_basic` | MathematicalExpectationDefinition | `expected_value_checker` | flexible | 分數或小數 | 等值分數/小數 | 負值允許 |
| `expectation_from_distribution` | MathematicalExpectationDefinition | `expected_value_checker` | flexible | 分數或小數 | 等值分數/小數 | 分佈表格式需先確認 |
| `expectation_word_problem_profit_fairness` | ApplicationsOfExpectation | `expected_value_checker` | flexible | 數值（含單位說明） | 等值數值 | 複雜情境先 HOLD（D 類）|
| `probability_algebra_mixed` | ProbabilityOperations | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 | 等值 | 全 needs_review，需人工確認品質 |
| `expectation_assessment_numeric` | MathematicalExpectation | `expected_value_checker` | flexible | 分數或小數 | 等值 | 全 needs_review，需人工確認 |
| `event_operation_probability` | ProbabilityOperations | `rational_checker` + `probability_range_validator` | flexible | 最簡分數 | 等值 | 同上 |

### Handwriting Reserved / not_ready

| problem_type | primary_skill | checker | not_ready_reason |
|---|---|---|---|
| `sample_space_listing` | SampleSpaceAndEvents | `not_ready` | 答案為集合列舉，非單一數值；需 handwriting AI-judged 流程 |
| `event_set_listing` | SampleSpaceAndEvents | `not_ready` | 事件子集合表示，非單一數值 |
| `subset_listing` | BasicConceptsOfSets | `not_ready` | 子集合列舉，集合之集合，非單一數值 |

---

## 6. Policy Decisions

### Q1. `1/2`、`0.5`、`50%` 是否視為等值？

| checker | `1/2` | `0.5` | `50%` |
|---|---|---|---|
| `rational_checker` (flexible) | ✅ canonical | ✅ 等值接受 | ✅ 等值接受（正規化後 0.5） |
| `rational_checker` (strict) | ✅ canonical | ❌ 不接受 | ❌ 不接受 |
| `decimal_tolerance_checker` | ✅ 等值（parse 為 0.5） | ✅ canonical | ✅ 等值接受 |
| `percentage_checker` | ✅ 等值接受（→0.5） | ✅ 等值接受 | ✅ canonical（`50%`） |
| `expected_value_checker` | ✅ 等值接受 | ✅ 等值接受 | ❌ 不建議（期望值通常非百分比） |

### Q2. 古典機率是否要求最簡分數？

- **正式顯示答案（explanation）**：使用最簡分數
- **checker（flexible mode）**：接受等值未化簡分數（`2/4` → 化簡後 `1/2` → 等值通過）
- **explanation**：建議加提示「答案應化為最簡分數」
- **canonical 儲存**：generator 儲存最簡分數字串

### Q3. `50` 在 percentage 題中代表 50% 還是 50？

**政策：ambiguity 以題幹為準，建議避免純數字輸入。**

- 若題幹明確要求「以百分率表示（如 50%）」：`50` 接受，正規化為 `0.5`
- 若題幹要求「機率」（值域 [0,1]）：`50` 不接受（超出範圍）；`0.5` 才是合法輸入
- 建議 generator 在 question_text 明確標示輸入格式要求，降低歧義

### Q4. 期望值是否可為負？

**政策：允許負值期望值。**

- 保險損益、賭局、抽獎虧損情境，期望值可為負
- `expected_value_checker` 不做符號限制
- 但 `probability_range_validator` 不適用於期望值（期望值非機率）

### Q5. 機率題是否接受小數近似？

- `rational_checker` flexible mode：接受等值小數（`0.5` ≡ `1/2`）
- `rational_checker` strict mode（題目標示「以分數表示」）：不接受小數
- `decimal_tolerance_checker`：接受容差 ±0.001
- 建議：Phase 6C 首批使用 flexible mode；strict mode 留待題目明確要求時啟用

### Q6. 如何處理答案帶單位？

**`expected_value_checker` 單位政策：**

- 接受：`5`、`5元`、`$5`、`5 元`（數值相同，單位忽略）
- 接受：`-3`、`-3元`、`-$3`（負值帶單位）
- 拒絕：單純單位字串 `元`（無數值）
- 正規化：移除已知單位後綴（元、分、美元、$、NT$），保留數值
- 若題幹有單位，explanation 顯示帶單位答案；checker 比對去單位後數值

### Q7. checker contract 是否要支援 LaTeX answer？

**支援，並以正規化層統一處理：**

- 輸入格式支援：`$\frac{1}{2}$`、`\frac{1}{2}`、`\dfrac{1}{2}` → 提取分子分母
- 正規化順序：LaTeX strip → plain fraction parse → 化簡 → 數值比對
- 建議正規化函式獨立為 `normalize_fraction_answer()`，所有 fraction-aware checker 共用

---

## 7. Validator Function Draft Specification

**注意：以下為規格描述，不寫程式碼，不建立任何 `.py` 檔，不修改任何既有檔案。**

### 共用正規化層

```
normalize_whitespace(raw: str) -> str
    去除前後空白、壓縮內部連續空白

normalize_fullwidth(raw: str) -> str
    全形數字/英文 → 半形

normalize_latex_fraction(raw: str) -> str | None
    偵測 \frac{a}{b} / \dfrac{a}{b} / $\frac{a}{b}$ 並提取 "a/b"
    失敗返回 None

normalize_fraction_answer(raw: str) -> FractionParseResult
    依序嘗試：LaTeX strip → plain fraction a/b → integer → decimal
    返回：{ type: "fraction"|"integer"|"decimal"|"invalid", numerator, denominator, float_value }

normalize_percentage_answer(raw: str, accept_bare_number: bool) -> float | None
    "50%" → 0.5；"50"（若 accept_bare_number=True）→ 0.5；"0.5" → 0.5
    超出 [0, 100] 範圍 → None

strip_unit_suffix(raw: str, known_units: list[str]) -> str
    移除已知單位後綴，返回純數值字串
```

### 機率範圍共通層

```
check_probability_range(value: float) -> bool
    0 <= value <= 1 → True；否則 raise InvalidProbabilityRange
```

### 各 Checker Contract

```
check_integer_answer(user_answer: str | int, expected: int) -> CheckResult
    正規化 → 整數解析 → 精確比對
    返回：{ correct: bool, normalized_user: int, error: str | None }

check_rational_answer(
    user_answer: str,
    expected_numerator: int,
    expected_denominator: int,
    *,
    allow_decimal: bool = True,
    allow_percentage: bool = True,
    strict_fraction: bool = False,
    check_probability_range: bool = True
) -> CheckResult

check_decimal_answer(
    user_answer: str,
    expected: float,
    *,
    tolerance: float = 0.001,
    allow_fraction: bool = True,
    allow_percentage: bool = False
) -> CheckResult

check_percentage_answer(
    user_answer: str,
    expected_percentage: float,
    *,
    accept_bare_number: bool = False,
    tolerance: float = 0.1
) -> CheckResult

check_expected_value_answer(
    user_answer: str,
    expected: float,
    *,
    unit: str | None = None,
    tolerance: float = 0.001,
    allow_fraction: bool = True,
    allow_percentage: bool = False
) -> CheckResult

check_choice_answer(
    user_answer: str,
    expected: str | list[str],
    *,
    multi_select: bool = False,
    case_insensitive: bool = True
) -> CheckResult

check_set_count_answer(user_answer: str | int, expected: int) -> CheckResult
    alias of check_integer_answer，加 domain 說明
```

### CheckResult 結構

```
CheckResult = {
    correct: bool,
    normalized_user: str | int | float,
    expected_canonical: str | int | float,
    error: str | None,   # None if correct
    error_code: str | None,  # e.g. "invalid_probability_range", "invalid_fraction", "missing_answer"
}
```

---

## 8. Risks and Open Questions

| # | 風險 / Open Question | 說明 | 建議 |
|---|---|---|---|
| R1 | strict mode 降低學生體驗 | 若 strict 要求分數，學生輸入小數被判錯，體驗差 | Phase 6C 首批全用 flexible；strict 留待課程明確要求 |
| R2 | flexible mode 接受題意不要求格式 | 題目要求「百分比」但接受分數，語意不一致 | 由 generator 控制 `allow_percentage` 旗標 |
| R3 | 百分比 `50` 的歧義 | 純數字 `50` 在機率題中是 50% 還是 50，無法自動判斷 | accept_bare_number 預設 False；題幹明確說明 |
| R4 | LaTeX 與一般輸入混用 | 學生可能輸入 `\frac{1}{2}` 或 `1/2`，需統一正規化 | normalize_latex_fraction 為共用前處理層 |
| R5 | 期望值單位多樣 | 元、分、美元、NT$，無法窮舉 | known_units 可配置；未知單位警告但不拒絕 |
| R6 | 浮點誤差 | `1/3 ≈ 0.3333...`，tolerance 設定影響判題 | rational 題優先比對最簡分數（精確）；decimal 才用 tolerance |
| R7 | needs_review 全 87 題 | 整章無人工確認，checker 設計需保守 | Phase 6C 首批只選 textbook_example / in_class_practice 題，排除自評題 |
| R8 | 負分母輸入 | `"-1/-2"` 應正規化為 `1/2` | 正規化層需處理雙負號消去 |
| R9 | 分佈表格式解析 | `expectation_from_distribution` 需題幹可機器解析分佈表 | Phase 6E 前需確認 DB 中分佈表的文字格式 |
| R10 | 多選排序歧義 | `AB` vs `BA`，多選題學生輸入順序不定 | choice_answer_checker 排序後比對 |

---

## 9. Recommended Next Phase

### Phase 6C：first deterministic probability generator batch（本輪不執行）

Phase 6C scope 建議：

**只做 P0 problem_type：**
- `classical_probability_fraction`
- `complement_probability`
- `union_intersection_probability`
- `sample_space_count_numeric`
- `dice_coin_probability_count`（排除 image-related 2 筆）
- `set_operation_count` + `inclusion_exclusion_count`（可合一 generator）

**排除：**
- image-related 題（ProbabilityDefinition 2 筆）
- handwriting listing 題（sample_space_listing / event_set_listing / subset_listing）
- 全 needs_review 自評題（ProbabilityOperations / MathematicalExpectation）

**必須：**
- 新增 generator：`core/vocational_math_b4/generators/chap2_probability_basic.py`
- 新增 tests：`tests/test_b4_chap2_phase6c_*.py`
- 更新 question_router：加 Chap2 P0 routes
- 更新 b4_validators.py：加 `check_rational_answer`、`check_integer_answer` 新函式
- manual smoke：機率值合法性、分數化簡、補事件計算
- **不改** adaptive scoring / mastery / APR / remediation

預期 report：`reports/b4_generator_planning/b4_phase6c_deterministic_batch1_summary.md`

---

## 10. Final Confirmation

| 項目 | 狀態 |
|---|---|
| 是否只新增 / 更新 validator planning report | ✅ 是 |
| 是否修改 production code | ✅ 否 |
| 是否修改 tests | ✅ 否 |
| 是否修改 routes | ✅ 否 |
| 是否修改 templates | ✅ 否 |
| 是否修改 generators | ✅ 否 |
| 是否修改 database | ✅ 否 |
| 是否修改 coverage matrix | ✅ 否 |
| 是否新增 allowlist | ✅ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ✅ 否 |
| 是否修改 `b4_validators.py` | ✅ 否 |
| 是否啟動 Phase 6C | ✅ 否 |

---

*Phase 6B validator plan 完成。停在此處，等待人工 approve。*  
*狀態：READY_FOR_REVIEW*
