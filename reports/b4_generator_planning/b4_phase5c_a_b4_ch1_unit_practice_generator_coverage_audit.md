# Phase 5C-A：B4 第 1 章「單元練習」Generator 覆蓋率稽核（唯讀）

**稽核日期**：2026-05-06  
**範圍**：技高（`curriculum=vocational`）數學 B4 第 1 章「1 排列組合」— 儀表板章節頁 →「單元練習」→ deterministic adaptive 產題鏈  
**限制**：未修改任何 production code、tests、generators、coverage matrix、adaptive routing；本檔為 read-only 盤點結論。

---

## 1. Audit 目的

本報告回答：

1. **課本／DB 層**：B4 第 1 章在課綱與匯入資料中，有哪些技能與題目（含 `source_type` 分布）？哪些帶有品質旗標（如 `needs_review`）？
2. **自動生題鏈**：每個技能是否有 `skills` 包裝層、`question_router` 註冊、以及（若適用）enrichment 題型？產出是否為 int-answer 友善的 deterministic `problem_type_id`？
3. **單元練習入口**：使用者從章節頁點「單元練習」後，**實際進入的技能池**為何？與 DB 章節內全部技能、以及 Phase 4E `runtime_ready` 口徑是否一致？
4. **缺口歸因**：缺題感來自「根本沒 generator／沒接到 router／沒進 allowlist／generator-first 不吃 DB 例題／manual_review 排除／模板過窄」中哪幾類？

---

## 2. B4 Chapter 1 DB 題型盤點

### 2.1 資料來源與查詢條件

- **SkillCurriculum**：`curriculum='vocational'`、`volume='數學B4'`、`chapter LIKE '1%'`（實際章名為 **`1 排列組合`**）。
- **TextbookExample**：同上冊章，以 `source_description` 內嵌字串判讀 `source_type=*`（與匯入管線一致）；並統計 `needs_review=true` 等旗標。

### 2.2 章節內技能清單（SkillCurriculum，共 15 筆）

| skill_id | 中文技能名稱（SkillInfo） | 小節（section） |
|----------|---------------------------|-----------------|
| vh_數學B4_TreeDiagramCounting | 樹狀圖 | 1-1 加法原理與乘法原理 |
| vh_數學B4_PermutationOfDistinctObjects | 相異物的排列 | 1-2 直線排列 |
| vh_數學B4_PermutationWithRepetition | 重複排列 | 1-3 重複排列 |
| vh_數學B4_RepeatedPermutation | 重複排列 | 1-3 重複排列 |
| vh_數學B4_CombinationDefinition | 組合的定義與計算 | 1-4 組合 |
| vh_數學B4_PascalTriangle | 巴斯卡三角形 | 1-5 二項式定理 |
| vh_數學B4_AdditionPrinciple | 加法原理 | 1-1 加法原理與乘法原理 |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 1-2 直線排列 |
| vh_數學B4_Combination | 組合 | 1-4 組合 |
| vh_數學B4_CombinationProperties | 組合的性質 | 1-4 組合 |
| vh_數學B4_BinomialTheorem | 二項式定理 | 1-5 二項式定理 |
| vh_數學B4_MultiplicationPrinciple | 乘法原理 | 1-1 加法原理與乘法原理 |
| vh_數學B4_CombinationApplications | 組合的應用 | 1-4 組合 |
| vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | 1-5 二項式定理 |
| vh_數學B4_FactorialNotation | 階乘記法 | 1-1 加法原理與乘法原理 |

### 2.3 TextbookExample：`source_type` 分布、題數、代表摘要、旗標

（題數為 `textbook_examples` 列筆數；`source_type` 由 `source_description` 內嵌標記加總，一列僅歸一類。）

| skill_id | 中文名稱 | textbook_example | in_class_practice | self_assessment | 總題數 | needs_review 列數 | 代表題目摘要（各 skill 取最小 `id` 一列之前 90 字） | 題型特徵／是否像重要課本題型 |
|----------|----------|------------------:|------------------:|----------------:|-------:|-------------------:|-----------------------------------------------------|-------------------------------|
| vh_數學B4_AdditionPrinciple | 加法原理 | 1 | 1 | 1 | 4 | 1 | 書櫃選一本中文／日文／英文書的選法 | 典型互斥分類加法；重要 |
| vh_數學B4_MultiplicationPrinciple | 乘法原理 | 2 | 2 | 3 | 10 | 4 | 兩科各選一人派駐的多階段選法 | 乘法原理核心；重要 |
| vh_數學B4_FactorialNotation | 階乘記法 | 2 | 2 | 0 | 4 | 2 | 求 3!、5!、8!/6! | 階乘計算；重要 |
| vh_數學B4_TreeDiagramCounting | 樹狀圖 | 1 | 1 | 0 | 4 | 0 | 拔河先贏兩場—**試以樹狀圖描述**所有可能 | **列舉／作圖**導向；與 int-answer 計數題不同 |
| vh_數學B4_PermutationOfDistinctObjects | 相異物的排列 | 5 | 5 | 7 | 18 | 10 | 6 人排成一排合照 | 直線排列典型；重要 |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 2 | 2 | 2 | 6 | 3 | 數字 3939889 重排成不同七位數 | 重複元素排列；重要 |
| vh_數學B4_PermutationWithRepetition | 重複排列 | 0 | 0 | 2 | 2 | 2 | 四人各選三種套餐之一（選擇題敘述） | n^m 語境；重要 |
| vh_數學B4_RepeatedPermutation | 重複排列 | 3 | 3 | 0 | 10 | 1 | 0–4 五數字可重複排三位數 | 數位重複排列；重要 |
| vh_數學B4_CombinationDefinition | 組合的定義與計算 | 1 | 1 | 0 | 2 | 0 | 10 題取 8 題作答方法數 | C(n,r) 基本；重要 |
| vh_數學B4_CombinationApplications | 組合的應用 | 3 | 3 | 0 | 7 | 0 | 8 人選 3 人—含必選／不可選條件 | 條件組合；重要 |
| vh_數學B4_CombinationProperties | 組合的性質 | 1 | 1 | 0 | 2 | 2 | 求 C(5,2)+C(5,3) | 性質／恒等式；重要 |
| vh_數學B4_Combination | 組合 | 0 | 0 | 7 | 7 | 7 | 四色顏料兩兩調色（選擇題） | 自我評量比重高；題幹偏應用 |
| vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | 1 | 1 | 0 | 3 | 3 | 組合數和 C(5,0)+…+C(5,5) 等 | 賦值型係數和；重要 |
| vh_數學B4_BinomialTheorem | 二項式定理 | 3 | 3 | 3 | 12 | 5 | **試利用二項式定理展開** (x+2)^4 | **展開／多項**導向；與單一 int 填答不完全同型 |
| vh_數學B4_PascalTriangle | 巴斯卡三角形 | 1 | 0 | 0 | 1 | 0 | **填寫並推導**巴斯卡三角形列 | **推導／填表**；非典型 int-only |

**備註**

- 本機 DB **未**在 `source_description` 中觀察到 `needs_formula_review`／`needs_image_review` 字樣（可能為 0 或匯入未標）；`needs_review` 如上表。
- `reports/b4_generator_planning/b4_skill_source_summary.csv` 與本次 SQL 題數大致對齊，可作交叉參考。

---

## 3. Generator／wrapper／router 對照表

### 3.1 章節頁「單元練習」入口（A）

- **路由**：`GET /adaptive_practice`，`practice.adaptive_practice_page`（`core/routes/practice.py`）。
- **儀表板條件**：`templates/dashboard.html` 中，僅當 `curriculum == 'vocational'` 且 `volume == '數學B4'` 且章節顯示字串 **`ch.display.startswith('1')`** 時，「單元練習」連結改為  
  `mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&learning_mode=teaching&practice_kind=unit_practice`；否則仍為舊式 `mode=single&skill_ids=<章節 raw 字串>`。
- **章節解析**：`_resolve_b4_chapter_adaptive_entry` 在 `mode=chapter` 且冊別為數學 B4、`chapter_id=1` 時，將單元技能池設為 **`sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)`**，並以 **`starter_b4_candidates`**（受 `B4_CHAPTER_1_ADAPTIVE_STARTER_SKILL_ORDER` 限制）決定首題技能。

### 3.2 Router 註冊摘要（`core/vocational_math_b4/services/question_router.py`）

- 主表 **`_REGISTRY`**：鍵為 `skill_id`，值為多筆 `{ subskill_id, problem_type_id, generator_key, generator_fn }`。
- **Enrichment**：**`_ENRICHMENT_REGISTRY`** 僅見 **`vh_數學B4_PermutationOfNonDistinctObjects`** → `non_distinct_objects_arrangement`（與主表合併後再抽樣）。

### 3.3 對照表（B4 第 1 章 15 個 curriculum 技能）

| skill_id | generator exists? | wrapper (`skills/vh_*.py`) | router `_REGISTRY` | enrichment `_ENRICHMENT_REGISTRY` | 代表性 `problem_type_id`（router 內） | Phase 4E CSV `runtime_ready`？ | adaptive allowlist？ | chapter 單元練習可達？ | 備註 |
|----------|--------------------|----------------------------|----------------------|-------------------------------------|--------------------------------------|-------------------------------|----------------------|-------------------------|------|
| vh_數學B4_AdditionPrinciple | 是 | 是 | 是（1 筆） | 否 | `add_principle_mutually_exclusive_choice` | 是 | 是 | 是 | 單一題型列—易顯單調（見 Phase 4E postcheck） |
| vh_數學B4_MultiplicationPrinciple | 是 | 是 | 是（3 筆） | 否 | `divisor_count_prime_factorization`, `mult_principle_independent_choices`, `mult_digits_no_repeat` | 是 | 是 | 是 | |
| vh_數學B4_FactorialNotation | 是 | 是 | 是（2 筆） | 否 | `factorial_equation_solve_n`, `factorial_evaluation` | 是 | 是 | 是 | |
| vh_數學B4_PermutationOfDistinctObjects | 是 | 是 | 是（5 筆） | 否 | 含 `permutation_role_assignment`, `permutation_formula_evaluation`, `permutation_full_arrangement`, `permutation_adjacent_block`, `permutation_digit_parity` | 是 | 是 | 是 | |
| vh_數學B4_RepeatedPermutation | 是 | 是 | 是（**1 筆**） | 否 | `repeated_permutation_digits` | 是 | 是 | 是 | **Router 僅單 entry** → 無題型輪替；另見 `PermutationOfNonDistinctObjects` 亦掛同型 |
| vh_數學B4_PermutationWithRepetition | 是 | 是 | 是（2 筆） | 否 | `repeated_choice_basic`, `repeated_permutation_assignment` | 是 | 是 | 是 | |
| vh_數學B4_PermutationOfNonDistinctObjects | 是 | 是 | 是（1 筆，同上） | **是** | `repeated_permutation_digits` + **`non_distinct_objects_arrangement`** | **CSV 無此 skill 列**（矩陣未收錄） | 是 | 是 | Postcheck-D2 enrichment；矩陣口徑外 |
| vh_數學B4_CombinationDefinition | 是 | 是 | 是（1 筆） | 否 | `combination_definition_basic` | 是 | 是 | 是 | 單 entry |
| vh_數學B4_CombinationApplications | 是 | 是 | 是（3 筆） | 否 | `combination_polygon_count`, `combination_required_excluded_person`, `combination_group_selection` | 是 | 是 | 是 | |
| vh_數學B4_CombinationProperties | 是 | 是 | 是（1 筆） | 否 | `combination_properties_simplification` | 是 | 是 | 是 | 單 entry |
| vh_數學B4_Combination | 是 | 是 | 是（3 筆） | 否 | `combination_basic_selection`, `combination_restricted_selection`, `combination_seat_assignment` | 是 | 是 | 是 | |
| vh_數學B4_BinomialCoefficientIdentities | 是 | 是 | 是（**3 筆**） | 否 | `binomial_coefficient_sum`, `binomial_equation_solve_n`, **`binomial_odd_even_coefficient_sum`** | CSV 僅 2 列／與現況**可能不同步** | 是 | 是 | 第三題型在 **live router**；CSV 未單列列全 |
| vh_數學B4_BinomialTheorem | 是 | 是 | 是（**3 筆**） | 否 | `binomial_specific_term_coefficient`, `binomial_middle_term_coefficient`, `binomial_specific_coefficient_with_negative_term` | CSV 僅 1 列 runtime + 1 列 excluded | 是 | 是 | **`binomial_expansion_basic` 有 generator 但未接 router**（CSV 註 excluded） |
| vh_數學B4_TreeDiagramCounting | **否（矩陣 N/A）** | **否（無 `skills` 模組）** | **否** | 否 | — | **excluded**（`tree_diagram_listing`） | **否**（manual_review 集合） | **否** | `practice.MANUAL_REVIEW_SKILLS` + allowlist 排除 |
| vh_數學B4_PascalTriangle | **否** | **否** | **否** | 否 | `pascal_triangle_derivation`（矩陣：無 generator） | **excluded** | **否** | **否** | 推導題；deterministic 不接入 |

**int-answer／deterministic runtime**

- Allowlist 內技能產題後，會經 `validate_b4_deterministic_adaptive_generator_payload` 擋下 **`binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation`** 等 `problem_type_id`（`b4_chapter1_deterministic_allowlist.py`）。

### 3.4 Phase 4E coverage matrix／reports 對照（稽核項目 D）

| 項目 | 本機盤點結果 |
|------|----------------|
| `b4_ch1_runtime_coverage_matrix.csv` | **28 列**；`coverage_status` 為 **`runtime_ready` 25**、`excluded` 3；列上共 **14 個**相異 `skill_id` |
| `b4_ch1_runtime_coverage_matrix_summary.md` | 與 CSV 一致之摘要敘述；並列 **25** 個 `runtime_ready` 的 `problem_type_id` |
| `runtime_ready`／`manual_review`／`excluded-like` | 三個 **excluded**：`tree_diagram_listing`、`pascal_triangle_derivation`、`binomial_expansion_basic`（理由見該 summary 與 CSV `notes`） |
| **CSV 與 live `question_router` 脫節** | **`vh_數學B4_PermutationOfNonDistinctObjects` 未出現在 CSV**（屬 Postcheck-D2 後 allowlist／router enrichment，**closure 矩陣未擴列**）；**二項式系**在 router 的 entry **多於** CSV 以「單列 skill」呈現的粒度—若稽核只讀 CSV 會**低估**已接題型 |

### 3.5 儀表板：單元練習實際技能池與 coverage 涵蓋（稽核項目 E）

點選「單元練習」並完成 B4 章節橋接後：

- **`unit_skill_ids`（排序後）** 等同 **`B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`**，共 **13** 個 `skill_id`（**不含** `TreeDiagramCounting`、`PascalTriangle`）。
- **與「CSV 上全部 `runtime_ready`」的涵蓋關係**  
  - **skill 粒度**：CSV 所涉 **14** 技能中，**12** 個在 allowlist；缺 **樹狀圖、巴斯卡**（屬 **manual_review／excluded** 政策，非遺漏）。  
  - **problem_type 粒度**：技能即使在池內，仍可能因 **router 單 entry**、**seed 抽樣**、或 **gate 擋特定 `problem_type_id`**，導致部分 runtime 題型**出現率低或長期不可見**。
- **DB 有匯入、但單元練習「自動產題體感」不一定出現**  
  - **`get_adaptive_question`** 在 **純 allowlist B4 池**時註解為 **generator-first、略過 `TextbookExample` 推薦**（`core/routes/practice.py`）。  
  - **Adaptive v2** 以 **catalog／generator** 為主並套用 B4 session gate；**不以逐題還原課本 `problem_text` 為目標**。  
  - 因此被排除技能（樹狀圖、巴斯卡）以及「展開／畫樹」等課本敘述，**不會**以原貌進入目前 deterministic 單元練習池。

---

## 4. 缺口分類

### A. DB 有題，但完全沒有 generator（或無可接之 deterministic 題型）

- **樹狀圖**：DB 有列舉／畫圖敘述；矩陣標 `tree_diagram_listing` **無 generator**、無 router、無 `skills` wrapper。
- **巴斯卡三角形**：DB 為填表推導；`pascal_triangle_derivation` 矩陣標 **無 generator**。

### B. 有 generator，但沒有 wrapper／router

- **`binomial_expansion_basic`**（屬 `vh_數學B4_BinomialTheorem` 概念）：CSV 標 **has_generator=yes**，但 **in_question_router=no**、**has_skill_wrapper=no**—不進現行練習鏈。

### C. 有 generator／router，但「單元練習敘事」與課本題感不一致（含未吃 DB）

- **Legacy `get_adaptive_question`（Phase 4F-Main-A）**：若目標池為 **純 allowlist B4**，註解明確為 **generator-first，略過 `TextbookExample` 推薦**（`core/routes/practice.py`）。亦即：**課本匯入的細緻敘述與子題**，不一定會出現在該路徑。
- **Adaptive v2（`session_engine`）**：以 catalog／generator 層為主，並有 B4 gate；同樣**不以「還原每一道課本敘述」為目標**。

### D. 有 `runtime_ready`，但沒進 adaptive allowlist

- 無（在 **第 1 章 15 技能**範圍內）：**未**出現「CSV runtime_ready 但 allowlist 漏列」之技能。  
- 反向案例較顯著：**`vh_數學B4_PermutationOfNonDistinctObjects` 進 allowlist 與 router，但未收錄於 `b4_ch1_runtime_coverage_matrix.csv`**（文檔口徑與 runtime 脫節）。

### E. 已進 allowlist，但 starter／抽樣邏輯偏窄

- **首題**：`B4_CHAPTER_1_ADAPTIVE_STARTER_SKILL_ORDER` 僅 5 個技能；章節入口首屏體感集中在加法／乘法／階乘／相異排列／組合定義。
- **多技能隨機**：`pure_b4` 時 `pick_rng.choice(target_skill_ids)` 對技能維度均勻，**對「同一技能下多 problem_type」**仍受 router「單 entry 直接回傳」限制（見 G）。

### F. 重要題型屬 manual_review／future_ai_judged（不應硬接）

- **樹狀圖列舉**、**巴斯卡推導**、**二項式完整展開**（係數列／多項式自由答）。

### G. 有 generator，但 template／router entry 過窄

- **`vh_數學B4_RepeatedPermutation`**：router **僅一筆** `repeated_permutation_digits` → 無輪替。
- **`vh_數學B4_CombinationDefinition`**、**`vh_數學B4_CombinationProperties`**、**`vh_數學B4_AdditionPrinciple`**：各 **單一** `problem_type_id`。
- **`vh_數學B4_PermutationOfNonDistinctObjects`**：主表與 `RepeatedPermutation` 共用數字重排題型 + enrichment；**抽樣結構**仍可能讓使用者覺得「不盡相異物」課本語境出現不足（Phase 4E postcheck 已討論）。

---

## 5. 高優先補強清單（5–10 項，僅建議、不改程式）

| # | skill_id／題型 | 為何重要 | 目前缺在哪一層 | 建議處理方式（Phase 5C-B 方向） |
|---|----------------|----------|----------------|----------------------------------|
| 1 | **樹狀圖** `vh_數學B4_TreeDiagramCounting` | 課本 1-1 核心表徵，DB 有完整「畫樹」敘述 | **無 deterministic int generator／未進 allowlist** | 保留 **manual_review**；未來 **AI-judged／結構化列舉** 路徑；若只做 int 替身題會失去評量意義（4E-15A 已決策） |
| 2 | **巴斯卡** `vh_數學B4_PascalTriangle` | 課本與組合性質銜接 | **無 generator／未進 allowlist** | 保留 **future_ai_judged／教師批改**；不建議硬接 int runtime |
| 3 | **二項式展開** `binomial_expansion_basic` | DB 大量「展開 (x+2)^4」類敘述 | **有 generator 但未接 router／wrapper；且被 deterministic gate 排除** | **free-response／正規化** 後再接；**不要**為了題感接入 int-only |
| 4 | **`vh_數學B4_RepeatedPermutation`** 單一 router entry | 課本與自我評量常見數位／球取箱語境 | **Router 結構過窄（G）** | **Small template enrichment** 或 **合併／拆分 skill 策略**（文件層先決策） |
| 5 | **`vh_數學B4_CombinationDefinition`** 單一題型 | 組合章起手式 | **單 entry（G）** | Template／參數 enrichment；或導向 `Combination` 大池 |
| 6 | **`vh_數學B4_PermutationOfNonDistinctObjects` vs CSV** | allowlist／router 已接，但 **官方矩陣未列** | **文檔／矩陣口徑與 runtime 脫節（D 類反向）** | Phase 5C-B：**另開 enrichment coverage 帳**（不回溯改 closure 分母之原則見 postcheck 文件） |
| 7 | **DB `Combination` 全為 self_assessment 且 needs_review 高** | 影響若走 DB-first 路徑時的可用性 | **資料品質／非 generator** | 匯入清洗與標記 review；與 generator 池分開治理 |
| 8 | **單元練習 generator-first 與課本題文本脫鉤** | 使用者預期「像課本那題」 | **產品路徑（C）** | 若要「課本對齊」需另規畫 **RAG／例題引導** 或 **混合池政策**—非單純加 generator |

---

## 6. 不應立即硬接的題型（範例）

| 代表 | 原因 |
|------|------|
| `tree_diagram_listing` | 非單純 int；需列舉或圖示；硬改 int 會折疊成乘法原理計數，失去評量焦點。 |
| `binomial_expansion_basic` | 答案型態為係數列／多項式；無正規化易造成假錯（Phase 4E-16A）。 |
| `pascal_triangle_derivation` | 推導／填表；非現行 deterministic 合約。 |

---

## 7. Phase 5C-B 建議（不改程式，僅路線）

1. **Phase 5C-B1（單元練習池政策）**：決定是否要讓「章節單元練習」在 **教學模式**下 **混合 DB 例題與 generator**（需產品規格與 gate／評分一致），而非預設完全略過課本列。
2. **Phase 5C-B2（wrapper／router）**：對 **已 runtime_ready 但未接** 的類型（典型：`binomial_expansion_basic`）**維持不接**，改走 **free-response backlog**；對 **窄 router** 技能做 **第二筆 entry** 或 **敘述 enrichment** 的**規格化**（實作留待後續 phase）。
3. **Phase 5C-B3（缺 generator 的真缺口）**：僅針對 **仍堅持 int deterministic** 的教學目標補 **新題型**；樹狀圖／巴斯卡應歸 **AI judged** 而非硬補 generator。
4. **Phase 5C-B4（template 窄）**：優先 **`RepeatedPermutation`、`CombinationDefinition`、二項式深度參數** 的小幅 enrichment（與 Phase 4E Postcheck-D3 決策對齊）。
5. **Phase 5C-B5（backlog）**：整理 **`future_ai_judged`**：`binomial_expansion_basic`、樹狀圖列舉、巴斯卡推導、以及 DB 中 **高 needs_review** 列之人工處理隊列。

**附錄：稽核觸及之唯讀來源**

| 區塊 | 路徑或查詢 |
|------|------------|
| 章節頁模板 | `templates/dashboard.html` |
| 單元練習解析 | `core/routes/practice.py`（`_resolve_b4_chapter_adaptive_entry`、`get_adaptive_question` 註解） |
| Allowlist／gate | `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` |
| Router／enrichment | `core/vocational_math_b4/services/question_router.py` |
| Adaptive API 橋接 | `core/routes/adaptive_api.py` |
| Session gate | `core/adaptive/session_engine.py`（`_b4_session_engine_payload_gate`） |
| DB | `instance/kumon_math.db` — `skill_curriculum`、`skills_info`、`textbook_examples` |
| Phase 4E 矩陣 | `reports/b4_generator_planning/b4_ch1_runtime_coverage_matrix.csv`、`b4_ch1_runtime_coverage_matrix_summary.md` |
| 匯入彙總 CSV | `reports/b4_generator_planning/b4_skill_source_summary.csv` |

---

**結論（一句話）**：第 1 章「單元練習」在工程上被設計為 **13 個 allowlisted 技能上的 deterministic generator 池**，**刻意不包含**樹狀圖與巴斯卡，且 **generator-first 路徑本來就不還原每一道課本匯入敘述**；因此使用者感到「課本很多重要題型沒出現」，**同時來自（1）政策排除與 non-int 題型、（2）DB 與自動產題鏈解耦、（3）部分技能 router 結構偏窄／矩陣文件與 live router 不同步**—不全然是 adaptive sampling 單一因素。
