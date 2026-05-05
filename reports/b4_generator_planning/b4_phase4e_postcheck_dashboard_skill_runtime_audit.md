# B4 Phase 4E Postcheck Dashboard Skill Runtime Audit

## 1. 本階段目的

說明：

- **Phase 4E-Final**（見 `b4_ch1_runtime_closure_report.md`）收斂的是 **problem_type** 層級：28 題型中 **25** 個 `runtime_ready`、**0** 個 `planned_only`、**3** 個 manual_review／excluded-like，並將 Phase 4E-13F 三個二項式 depth 題型界定為 **matrix 外補強**。
- **本報告**為 **skill 練習頁／dashboard 點擊路徑** 之 **postcheck**：對照 `skills/` wrapper 是否存在、`question_router._REGISTRY` 是否有該 `skill_id`、`get_next_question` 如何載入模組，以找出 **「coverage 閉環」與「使用者實際可練」之落差**。
- **本階段不修改程式**，僅整理落差與下一階段建議。

**方法與限制（符合 Phase 4E-Postcheck-A 允許範圍）：**

- 已讀：`b4_ch1_runtime_closure_report.md`、`b4_ch1_runtime_coverage_matrix.csv`、`b4_ch1_runtime_coverage_matrix_summary.md`、`b4_phase4e16b_final_runtime_closure_summary.md`、`core/vocational_math_b4/services/question_router.py`（`_REGISTRY` 與 `_select_entry`／`generate_for_skill`）、`core/routes/practice.py`（`/practice/<skill_id>`、`get_next_question` 模組載入）、`skills/` 目錄下 `vh_數學B4_*.py` 清單及示例 wrapper。
- **未**做全專案掃描；**未**讀取 `app.py` 內文（僅以精確搜尋確認存在 `@app.route('/dashboard')`）。
- **Dashboard 完整 skill 清單**：通常綁 **資料庫**（如 `SkillInfo`／`SkillCurriculum`）與模板；本報告**無法在不查 DB／不大範圍掃描前提下**列舉「儀表板上全部 Chapter 1 技能」。以下以 **coverage matrix 出現之 skill_id 並集** 加上 **使用者實測 7 項**，並註記 **`vh_數學B4_PermutationOfNonDistinctObjects`** 未出現在 `b4_ch1_runtime_coverage_matrix.csv`。

## 2. 使用者實測問題摘要

| skill_id | practice 狀態 | 使用者觀察 | 初步判斷 |
|---|---|---|---|
| `vh_數學B4_BinomialTheorem` | 可顯示、可出題（例：指定項係數） | 不易感受到「depth」或分數／多題型輪替 | Router 對此 skill 有 **3** 筆 entry；wrapper **未**傳 `problem_type_id`，採 seed 抽樣。若僅短時間抽題，主觀上可能偏窄；另 **generator 模板／參數**仍可能相近（見 §6.3）。 |
| `vh_數學B4_BinomialCoefficientIdentities` | 可顯示、可出題（例：奇數次項係數和） | 覺得缺少部分題型或覆蓋不足 | Router 有 **3** 筆（係數和、求 `n`、奇偶係數和）；與 matrix 一致。**未**涵蓋「矩陣外」題型屬預期；感受不足時宜查 **抽題種子、前端是否固定 seed** 與 **模板多樣性**（§6.4）。 |
| `vh_數學B4_TreeDiagramCounting` | **錯誤**：`No module named 'skills.vh_數學B4_TreeDiagramCounting'` | 不應當作一般 deterministic 練習 | **`skills/` 無對應 `.py`**；`question_router` **無**此 `skill_id`。`tree_diagram_listing` 在 matrix 為 **excluded／manual_review**。屬 **skill 頁可進但 runtime 未支援** + **不應硬補 deterministic wrapper**（§5.1）。 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | **錯誤**：`No module named 'skills.vh_數學B4_PermutationOfNonDistinctObjects'` | 需判斷缺 wrapper／alias／canonical 對應 | **`skills/` 無此檔**；`question_router` **無**此 key。該 skill_id **未**列於 `b4_ch1_runtime_coverage_matrix.csv`，屬 **課程／dashboard 與 closure 矩陣脫鉤**（§5.3）。 |
| `vh_數學B4_RepeatedPermutation` | 可顯示 | 題型單調（重複數字排列敘述） | Router 中此 skill **僅 1 筆** `repeated_permutation_digits` → `_select_entry` 永遠 **single_entry**，**非**抽樣分布問題（§6.2）。`repeated_permutation_assignment` 掛在 **`vh_數學B4_PermutationWithRepetition`**。 |
| `vh_數學B4_CombinationDefinition` | 可顯示 | 題型單調（基本選取敘述） | Router 中此 skill **僅 1 筆** `combination_definition_basic`，與「定義頁」定位一致；單調感來自 **單一 problem_type**（§6.1）。 |
| `vh_數學B4_PascalTriangle` | **錯誤**：`No module named 'skills.vh_數學B4_PascalTriangle'` | 不應直接 deterministic 出題 | **無 wrapper**；router **無**此 skill。`pascal_triangle_derivation` 為 **excluded／manual_review**（§5.2）。 |

## 3. problem_type coverage 與 skill page availability 的差異

說明：

- **Coverage matrix** 以 **problem_type_id** 為列，對應 **generator／router／wrapper／smoke**；歸檔的是「題型是否接上最小 deterministic runtime」。
- **Dashboard／搜尋／課程表** 以 **skill_id** 為單位；同一 skill 可對應 **多個** problem_type（router 多筆 entry），也可能 **矩陣内有題型但 skill 頁根本無模組**（矩陣未追「瀏覽器能否 import skills.xxx」）。
- **`runtime_ready` 的 problem_type** 不代表 **每個 curriculum 掛名的 skill 頁** 都已做 **gating**；若 DB 仍連到 **無 wrapper** 或 **manual_review 專屬 skill**，使用者會看到 **No module named** 或誤入 **非 deterministic** 目標頁。
- **manual_review／excluded** 題型若仍能點入 **`/practice/<skill_id>`**，因 `get_next_question` 會 `importlib.import_module(f"skills.{skill_id}")`，在 **缺檔**時即拋出 **`No module named 'skills.xxx'`**（與「generator 是否存在」無必然關係）。

## 4. Skill audit table

**欄位說明**

- **wrapper_exists**：`skills/vh_數學B4_<SkillName>.py` 是否存在（目錄掃描結果：**12** 個檔；見下列）。
- **router_entry_exists**：`core/vocational_math_b4/services/question_router.py` 之 `_REGISTRY` 是否含該 `skill_id`。
- **coverage／manual_review**：依 `b4_ch1_runtime_coverage_matrix.csv` 關聯之題型狀態（該 skill 列至少一列為 excluded 則註記）。

**`skills/` 現有 B4 wrapper 檔（12）：**  
`vh_數學B4_AdditionPrinciple`、`vh_數學B4_BinomialCoefficientIdentities`、`vh_數學B4_BinomialTheorem`、`vh_數學B4_Combination`、`vh_數學B4_CombinationApplications`、`vh_數學B4_CombinationDefinition`、`vh_數學B4_CombinationProperties`、`vh_數學B4_FactorialNotation`、`vh_數學B4_MultiplicationPrinciple`、`vh_數學B4_PermutationOfDistinctObjects`、`vh_數學B4_PermutationWithRepetition`、`vh_數學B4_RepeatedPermutation`。

| skill_id | wrapper_exists | router_entry_exists | coverage／manual_review 關聯 | 目前狀態 | 建議處理 |
|---|---|---|---|---|---|
| `vh_數學B4_BinomialTheorem` | yes | yes（3 筆，含 middle／negative term） | `binomial_expansion_basic` excluded；其餘為 runtime_ready（矩陣） | **ok** + **router_distribution_review_needed**（主觀覆蓋感） | 下一階段檢視 **前端／seed** 與 **模板 enrichment**；**不要**用接入 `binomial_expansion_basic` 補單調。 |
| `vh_數學B4_BinomialCoefficientIdentities` | yes | yes（3 筆） | runtime_ready + depth 題型（odd-even） | **ok** + **router_distribution_review_needed**（若仍覺不足） | 同上做 **抽題可觀測性**（例如 log `router_trace`）與 **模板**檢討。 |
| `vh_數學B4_TreeDiagramCounting` | **no** | **no** | `tree_diagram_listing` **excluded** | **manual_review_should_be_disabled** + **missing_wrapper**（政策面：**不補** deterministic wrapper） | **Gating**／替代頁說明（Postcheck-B）；勿為 closure 補假 int wrapper。 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | **no** | **no** | **未**見於 `b4_ch1_runtime_coverage_matrix.csv` | **missing_wrapper** + **alias_or_mapping_needed** | Postcheck-C：**對應 RepeatedPermutation／新增 router 條目／獨立開發** 三選一決策；避免長期 No module named。 |
| `vh_數學B4_RepeatedPermutation` | yes | yes（**僅 1 筆**） | `repeated_permutation_digits` runtime_ready | **ok** + **enrichment_needed**（體感單調） | Router **必為**同一題型；可將 **assignment** 合併至此 skill 或加强 **模板／敘述變體**（§6.2）。 |
| `vh_數學B4_CombinationDefinition` | yes | yes（**僅 1 筆**） | `combination_definition_basic` runtime_ready | **ok** + **enrichment_needed** | 屬「窄技能頁」；可導向 **Combination** 或擴 **模板**。 |
| `vh_數學B4_PascalTriangle` | **no** | **no** | `pascal_triangle_derivation` **excluded** | **manual_review_should_be_disabled** | 同 TreeDiagram：**gating**，不建 deterministic wrapper（§5.2）。 |
| `vh_數學B4_PermutationOfDistinctObjects` | yes | yes（5 筆） | 多題型 runtime_ready | **ok** | 維持；Phase 4F 再接 adaptive 時納入映射檢查。 |
| `vh_數學B4_Combination` | yes | yes（3 筆） | runtime_ready | **ok** | 同上。 |
| `vh_數學B4_MultiplicationPrinciple` | yes | yes（3 筆） | runtime_ready | **ok** | 同上。 |
| `vh_數學B4_CombinationApplications` | yes | yes（3 筆） | runtime_ready | **ok** | 同上。 |
| `vh_數學B4_CombinationProperties` | yes | yes（1 筆） | runtime_ready | **ok** + **enrichment_needed**（僅一題型） | 可接受或後續加第二題型／模板。 |
| `vh_數學B4_AdditionPrinciple` | yes | yes（1 筆） | runtime_ready | **ok** | 同上。 |
| `vh_數學B4_FactorialNotation` | yes | yes（2 筆） | runtime_ready | **ok** | 兩筆 entry → seed 抽樣。 |
| `vh_數學B4_PermutationWithRepetition` | yes | yes（2 筆） | `repeated_choice_basic`、`repeated_permutation_assignment` | **ok** | 與 **RepeatedPermutation** 分工造成使用者混淆時，宜 **UX／命名／映射** 檢討（§6.2）。 |

**互動行為摘要（回答「wrapper／router 錯配會怎樣」）：**

| 情境 | 預期行為（依現行程式結構） |
|---|---|
| **無 wrapper，有／無 router** | `/get_next_question` 執行 `importlib.import_module("skills.<skill_id>")` 失敗 → **`No module named 'skills.<skill_id>'`**（與 router 是否有 entry 無關，因尚未進入 `generate_for_skill`）。 |
| **有 wrapper，router 無 `skill_id`** | `generate_for_skill` 對未知 skill 拋 **`ValueError: Unsupported skill_id.`**（與 import 錯誤訊息不同）。 |
| **有 wrapper，router 有 entry** | 正常產題（若 generator 與參數無誤）。 |

## 5. No module named 問題分析

### 5.1 TreeDiagramCounting

- **根因**：**缺 `skills.vh_數學B4_TreeDiagramCounting` 模組**（非僅缺 generator）；`question_router` 亦**無**該 key。
- **政策**：Phase 4E-15A／15B — `tree_diagram_listing` 為 **manual_review／future visualization**，**不應**為「closure」補 **deterministic int wrapper**。
- **建議**：**Dashboard／練習入口 gating**（Postcheck-B）：標示暫緩、導向未來 visual／AI；**勿**以假計數題硬接。

### 5.2 PascalTriangle

- **根因**：同樣 **缺 wrapper**、**router 無註冊**；matrix 上 `pascal_triangle_derivation` 為 **excluded**。
- **建議**：**不要**直接補 deterministic wrapper；應 **gating** 或靜態說明頁（Postcheck-B）。

### 5.3 PermutationOfNonDistinctObjects

- **根因**：**缺 wrapper** 且 **router 無**該 skill；且 **未**納入 Chapter 1 closure CSV，代表 **課程／UI 仍暴露一個「矩陣未覆蓋」的 skill 名稱**。
- **決策選項（下一階段，本報告不裁定）**：
  - **A**：視為 **不盡相異物** 獨立主題 → 未來 **補 generator／router／wrapper**（非本階段）。
  - **B**：與 **`vh_數學B4_RepeatedPermutation` 或 `PermutationWithRepetition`** 做 **canonical alias**（redirect 或共用 wrapper），避免 **No module named**。
  - **C**：若教材以 **圖形／開放題** 為主，可能改列 **manual_review**，與 closure 策略一致。
- **共通結論**：**不應**長期維持 dashboard 可點但 **import 失敗**。

## 6. 題型單調／分布不足分析

### 6.1 CombinationDefinition

- `_REGISTRY["vh_數學B4_CombinationDefinition"]` **僅** `combination_definition_basic` 一筆 → **永遠 single_entry**，非 seed 偏見。
- **結論**：單調感符合設計（窄技能）；若希望豐富體感，應 **加題型／模板** 或引導至 **`vh_數學B4_Combination`**（多筆 entry）。

### 6.2 RepeatedPermutation

- `vh_數學B4_RepeatedPermutation` 在 router 中 **只有** `repeated_permutation_digits`，故 **不可能** 輪出 `repeated_permutation_assignment`（該項註冊在 **`vh_數學B4_PermutationWithRepetition`**）。
- **結論**：使用者若只進 **RepeatedPermutation** 頁，體感會集中在「數字重複排列」；屬 **skill 切割與 router 註冊策略**，非僅 generator 模板數少（雖模板 enrichment 仍有幫助）。

### 6.3 BinomialTheorem

- Router **有 3 筆**（指定項、中間項、負項係數）；`_select_entry` 在多筆且 **未**指定 `problem_type_id` 時，以 **`random.Random(seed).choice`** 抽樣；`seed` 為 `None` 時 Python 會使用系統預設種子化行為。
- **為何仍覺「depth 不明」**：可能包含 —（1）**三類題在 UI 上敘述相近**；（2）**參數範圍窄**（Phase 4E-13F 文件亦提及）；（3）**未顯示** `router_trace.selected_problem_type_id`；（4）短時間抽樣的統計波動。
- **重申**：**不可**靠接入 `binomial_expansion_basic` 來「變豐富」，因其為 **list／free-response** 路線。

### 6.4 BinomialCoefficientIdentities

- Router **3 筆**與 matrix／closure 一致；若使用者仍覺「缺題型」，需區分 — **matrix 未承諾之題型** vs **抽樣／模板**問題。
- **建議下一階段**：記錄每次作答之 **`router_trace`**，確認三類是否均有出現；再決定 **模板 enrichment** 或 **documented** 抽題政策。

## 7. 建議下一階段修正項目

### Phase 4E-Postcheck-B：manual_review skill gating

**目標技能：** `vh_數學B4_TreeDiagramCounting`、`vh_數學B4_PascalTriangle`

**行為建議：**

- Dashboard／章節清單標示 **暫緩／future_ai_judged／非一般練習**。
- 若仍允許 URL 直達 **`/practice/<skill_id>`**，應顯示 **說明頁**或 **友善錯誤**，而非 **`No module named`**。
- **不**建立 deterministic wrapper（與 Phase 4E-15／16 決策一致）。

### Phase 4E-Postcheck-C：PermutationOfNonDistinctObjects mapping

**目標：** 結束 **No module named**

**行為建議：**

- 產品上確認該技能定義：是否等價 **Repeated／PermutationWithRepetition** 某子集合，或需 **獨立** generator 路線。
- 選定後：**wrapper＋router** 或 **alias redirect**；並更新 **課程資料與文件**，避免矩陣與 dashboard 再度脫鉤。

### Phase 4E-Postcheck-D：router distribution／enrichment review

**目標技能：** `vh_數學B4_BinomialTheorem`、`vh_數學B4_BinomialCoefficientIdentities`、`vh_數學B4_RepeatedPermutation`、`vh_數學B4_CombinationDefinition`

**行為建議：**

- **Binomial**：確認 **預設抽題**（seed 來源、`problem_type_id` 是否被前端固定）與 **題幹可辨識度**；必要時 **模板／參數** enrichment。
- **RepeatedPermutation**：確認是否要 **合併 assignment** 至同一 skill 或改善 **導覽文案**，否则 **單一 entry** 將始終單調。
- **CombinationDefinition**：**模板 enrichment** 或 **導向 Combination**。

### Phase 4F：adaptive route

**前提：**

- 完成 Postcheck-B／C（至少 **gating** + **無孤兒 skill import 失敗**）後再大量接 adaptive，避免 **指向不可用 skill**。

## 8. 優先順序

1. **先修 gating／入口體驗** — 使 **manual_review** 技能**不再**以 **No module named** 呈現（TreeDiagram、PascalTriangle）。
2. **再修 PermutationOfNonDistinctObjects** — **mapping 或新增路線**，消除 **長期 import 失敗**。
3. **再處理題型單調與分布** — Binomial 抽樣可觀測性、RepeatedPermutation 與 PermutationWithRepetition **分工**、窄 skill **模板**。
4. **最後**進入 **Phase 4F adaptive route**（含獨立 adaptive coverage 追蹤，避免與 deterministic 混淆）。

## 9. 結論

Chapter 1 在 **problem_type** 層的 **deterministic int-answer runtime**（25／28、`planned_only`=0）已由 Phase 4E-Final **正式閉環**；目前使用者於 **skill 頁**遇到的 **No module named**、**manual_review 仍可進頁**、以及 **部分頁面題感單調**，主要來自 **（1）dashboard／DB 仍指向無 `skills` 模組或矩陣未涵蓋之 skill_id**、**（2）router 對同一 skill 僅掛 **一筆** entry 時必然無「題型輪替」**、**（3）二項式雖多筆 entry，仍可能受 **模板相近／參數窄／可觀測性不足** 影響**。這些屬 **skill 層／產品入口／registry 切割** 問題，**並不推翻** Phase 4E 在 **coverage matrix** 上的 closure 結論。下一步應優先 **Postcheck-B／C**（**gating** 與 **PermutationOfNonDistinctObjects** 映射），再進行 **enrichment／distribution** 檢視，最後才銜接 **Phase 4F adaptive**。

---

## 完成後回報欄位（供收件確認）

1. 是否成功輸出 dashboard skill runtime audit report：**是**（本檔）。  
2. 是否確認為 skill page 層問題而非 problem_type closure 失敗：**是**（見 §3、§9）。  
3. 優先修正前三項：**（1）manual_review 技能 gating／替代頁**（TreeDiagram、PascalTriangle）**（2）PermutationOfNonDistinctObjects** 映射或獨立接入決策 **（3）RepeatedPermutation／CombinationDefinition／Binomial** 之 **registry／模板／抽題可觀測性** 複查。  
4. 是否修改任何程式碼：**否**（僅新增本 Markdown）。
