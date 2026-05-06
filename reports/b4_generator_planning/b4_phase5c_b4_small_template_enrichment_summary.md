# Phase 5C-B4：B4 第 1 章 Runtime-ready 小型模板補強總結

**日期**：2026-05-06  
**依據**：`reports/b4_generator_planning/b4_phase5c_a_b4_ch1_unit_practice_generator_coverage_audit.md`（Phase 5C-A）

---

## 1. Phase 5C-A 缺口摘要（本階段對應）

| 觀察 | 5C-B4 處理方式 |
|------|----------------|
| `RepeatedPermutation` router 僅單一 `problem_type_id`，題幹語境易單調 | 擴充 **`template_context`** 字串集合與題幹模板（仍為 \(m^n\) 重複選擇計數） |
| `CombinationDefinition` 單一敘述 | 在**同一** `combination_definition_basic` 下增加多組課本式語境（選題、委員會、樣本等） |
| `CombinationProperties` 僅對稱／直接算 \(C(n,r)\) | 新增 **`two_term_sum`**、**`symmetry_word`** 變體（仍為 int 求值，無證明） |
| `AdditionPrinciple` 僅「社團」敘事 | 增加書架、路線、餐點、活動梯次等**互斥分類**語境（不加乘法原理） |
| `PermutationOfNonDistinctObjects` enrichment 抽樣可見度 | Router 對該 skill 使用 **`seed % len(entries)`** 輪詢；generator 增加 **`word_tiles`／`badge_strip`** 語境 |

**未處理（刻意）**

- `tree_diagram_listing`、`binomial_expansion_basic`、`pascal_triangle_derivation`：維持 excluded／manual_review 路線。
- Phase 4E **`b4_ch1_runtime_coverage_matrix.csv`**：未修改。
- DB `TextbookExample` 混入 adaptive、free-response／AI-judged 路徑、adaptive 核心策略：未變更。

---

## 2. 補強技能清單

| 技能 | 檔案 |
|------|------|
| A `vh_數學B4_RepeatedPermutation` | `core/vocational_math_b4/generators/counting.py`（`repeated_permutation_digits`） |
| B `vh_數學B4_CombinationDefinition` | `core/vocational_math_b4/generators/combination.py`（`combination_definition_basic`） |
| C `vh_數學B4_CombinationProperties` | `core/vocational_math_b4/generators/combination.py`（`combination_properties_simplification`） |
| D `vh_數學B4_AdditionPrinciple` | `core/vocational_math_b4/generators/counting.py`（`add_principle_mutually_exclusive_choice`） |
| E `vh_數學B4_PermutationOfNonDistinctObjects` | `permutation.py`（`non_distinct_objects_arrangement`）+ `question_router.py`（輪詢選項） |

---

## 3. 新增或調整的 `template_context`／`variant`／`scenario`／`context`

### A. `repeated_permutation_digits`

**`parameters.template_context`** 新增：

- `set_menu`：套餐連續選擇（可重複品項）
- `badge_pin`：員工證 PIN
- `locker_code`：轉輪置物櫃密碼

（保留既有：`password`、`license_plate`、`seat_serial`、`color_sequence`、`trial_sequence`）

### B. `combination_definition_basic`

**`parameters.template_context`**（納入 `parameter_tuple` 第 4 元，避免與同 \((n,r)\) 重複卡死）：

- `works_exhibit`、`exam_pick`、`committee`、`sample_draw`、`delegate_pick`

### C. `combination_properties_simplification`

**`parameters.variant`** 擴充：

- `symmetry_word`：白話「選 \(r\) 人與選 \(n-r\) 人方法數相同」
- `two_term_sum`：求 \(C(n,r_1)+C(n,r_2)\)（兩項皆 int 化簡）

（保留：`symmetry`、`direct`）

### D. `add_principle_mutually_exclusive_choice`

**`parameters.template_context`（原 `scenario`）**：

- `bookshelf`、`routes`、`meal_types`、`activity_tracks`（外加原有 `clubs`）

**`parameter_tuple`** 結構變更：加入 `scenario`，與舊測試／seen 集合相容性已於測試同步更新。

### E. `non_distinct_objects_arrangement`

**`parameters.context`** 新增：

- `word_tiles`：拼字字卡
- `badge_strip`：識別帶圖樣

**Router**：`vh_數學B4_PermutationOfNonDistinctObjects` 在無指定 `problem_type_id` 時，`selection_reason` 可為 **`seed_mod_router_balance`**，於 **`repeated_permutation_digits`** 與 **`non_distinct_objects_arrangement`** 間輪替。

---

## 4. 測試與 QA

### 新增測試

- `tests/test_phase5c_b4_small_template_enrichment.py`：seed 1–50 抽樣、int answer、choices、非 excluded、`template_context`／`variant` 多樣化、non_distinct 雙題型可達、direct generator 語境覆蓋。

### 調整測試

- `tests/test_vocational_math_b4_generators_phase4e6.py`：mock／seen tuple 配合加法原理與組合性質新參數形狀。
- `tests/test_vocational_math_b4_generators_phase4b2.py`：`combination_definition_basic` 阻擋集合改為含 **五種 template_context** 的 4-tuple。

### 已執行指令與結果

```text
python -m pytest tests/test_phase5c_b4_small_template_enrichment.py ^
  tests/test_vocational_math_b4_generators_phase4e6.py ^
  tests/test_vocational_math_b4_generators_phase4b2.py ^
  tests/test_vocational_math_b4_permutation_non_distinct_postcheck_d2_connect.py ^
  tests/test_b4_chapter1_adaptive_allowlist.py ^
  tests/test_vocational_math_b4_question_router_registry_canonical.py ^
  tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py ^
  tests/test_phase5b_fix_e1_b4_remediation_bridge.py -q
```

**結果**：`100 passed`（約 34.5s；Phase5b 測試有 SQLAlchemy `utcnow` DeprecationWarning，與本變更無關）。

---

## 5. Manual browser smoke 建議

1. 登入後開啟：`/dashboard?view=curriculum&curriculum=vocational&volume=數學B4&chapter=1%20%E6%8E%92%E5%88%97%E7%B5%84%E5%90%88`（或介面中等價章節）。
2. 進入 **單元練習**，連續刷題約 15–20 題，確認：
   - 仍為 **整數填答／選擇**；
   - 出現 **套餐／PIN／置物櫃**、**書展／路線／午餐梯次**、**拼字字卡／識別帶** 等敘述；
   - **不盡相異物** 與 **數字重複排列** 兩類題可交替出現（奇偶 seed 路徑下尤為明顯）。
3. 單技能頁（若使用）：`RepeatedPermutation`、`CombinationDefinition`、`CombinationProperties`、`AdditionPrinciple`、`PermutationOfNonDistinctObjects` 各抽 5 題目視檢 LaTeX 與語境。

---

## 6. 技術備註

- **未新增**任何 `problem_type_id`；**未修改** Phase 4E coverage matrix。
- `question_router` 僅新增 **單一技能** 的種子輪詢分支，其餘技能仍為 `Random(seed).choice`。
- 組合定義之 `parameter_tuple` 含 `template_context`，與「同參數不同語境」並存時之去重邏輯一致。
