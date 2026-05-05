# B4 Phase 4F Adaptive Route Preflight Summary

## 1. 目的與硬性規則

本階段為 **Phase 4F Adaptive Route Preflight**：在 **不修改 Phase 4E-Final coverage matrix**、不接入 free-response／AI-judged／`binomial_expansion_basic` 的前提下，先行建立 **B4 Chapter 1 deterministic int-answer adaptive 允許技能池**，並在現有 **`get_adaptive_question`** 路徑加上 **pool gating** 與 **產題後防禦檢查**，並提供 **稽核／debug** 輸出。

**會計分帳：** adaptive readiness（本報告／程式 allowlist）與 Phase 4E deterministic closure **獨立**，不重寫 **25／28** 統計。

## 2. 已檢視檔案（未修改者列為 inspected）

| 檔案／區域 | 用途 |
|---|---|
| `core/routes/practice.py` — `get_adaptive_question` | 目前 adaptive API：`review`／`single`／`multiple` 組池 → `recommend_question`（DB `TextbookExample`）→ `skills.<skill_id>.generate()` |
| `core/adaptive_engine.py` — `recommend_question`、`select_review_skill` | RS 打分選題；review 弱點選技能 |
| `core/adaptive/session_engine.py`、`core/adaptive/routing.py`（摘要瀏覽） | 另有較完整的 adaptive session／routing；**本次未改**，Phase 4F 後續若改走 session_engine 須重用同一 allowlist |
| `reports/b4_generator_planning/b4_ch1_runtime_coverage_matrix.csv` | **唯讀**：對齊 Phase 4E runtime_ready skill 集合（不改檔） |

## 3. 現行 adaptive 技能／題目來源（發現）

1. **`review` 模式：** `SkillCurriculum` 依 **curriculum** 載入 **review_skill_pool**，再 **`select_review_skill`**。
2. **`single`／`multiple`：** 依 **chapter 名稱**查詢 `SkillCurriculum.skill_id`。
3. **題目模板：** **`recommend_question(user_id, skill_ids)`** 僅自 **`TextbookExample`**（DB）篩選；**若無題目列仍會回傳 `None` → 404**。
4. **實際题干：** 選定模板後 **`mod.generate(level=question_template.difficulty_level)`**，對 **B4 vocational wrappers** 即為 **`generate_for_skill`** 路由器路徑。

**Preflight 意義：** 即使 DB 題目模板稀疏，只要走到 **`generate()`**，本階段的 **`problem_type_id` 黑名單**仍能防止錯誤題型外洩；**技能池過濾**可防止 manual_review／不可用技能進入 adaptive 候選集合。

## 4. 本階段變更檔案

| 檔案 | 變更 |
|---|---|
| `core/vocational_math_b4/adaptive/__init__.py` | **新增** package |
| `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` | **新增** allowlist、排除題型、`filter_*`、`validate_*`、`format_*` audit |
| `core/routes/practice.py` | **`get_adaptive_question`**：`review` pool 過濾；統一過濾 `target_skill_ids`；`generate` 後 **payload 驗證**；log **`question_audit`**；可選 **`adaptive_audit=1`** JSON |
| `tests/test_b4_chapter1_adaptive_allowlist.py` | **新增** 單元測試 + **router smoke**（對 allowlist 內每一 skill **seed=11** `generate_for_skill`） |

**未變更：** `b4_ch1_runtime_coverage_matrix.csv`、任一 generator／wrapper、`question_router` registry、frontend、`app.py`（除間接透過 `practice` blueprint）。

## 5. Adaptive pool 來源（與 coverage 矩陣關係）

- **來源：** `b4_chapter1_deterministic_allowlist.py` 內 **`B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`** — 對齊 Phase 4E-Final **Chapter 1 runtime_ready** 之 **skill_id** 並集，並 **納入** Postcheck-D2 **`vh_數學B4_PermutationOfNonDistinctObjects`**（deterministic enrichment；**不在**原始 28-row matrix 分母內，但 **允許進 deterministic adaptive**）。
- **不讀取、不重寫 CSV**：矩陣仍為 closure 會計唯一權威；allowlist 為 **獨立程式常數**，避免 Phase 4F 回溯污染 closure。

## 6. 最終 Adaptive Allowlist（deterministic int-answer）

共 **13** 個 `skill_id`：

1. `vh_數學B4_AdditionPrinciple`  
2. `vh_數學B4_MultiplicationPrinciple`  
3. `vh_數學B4_FactorialNotation`  
4. `vh_數學B4_PermutationOfDistinctObjects`  
5. `vh_數學B4_RepeatedPermutation`  
6. `vh_數學B4_PermutationWithRepetition`  
7. `vh_數學B4_PermutationOfNonDistinctObjects`  
8. `vh_數學B4_CombinationDefinition`  
9. `vh_數學B4_CombinationApplications`  
10. `vh_數學B4_CombinationProperties`  
11. `vh_數學B4_Combination`  
12. `vh_數學B4_BinomialCoefficientIdentities`  
13. `vh_數學B4_BinomialTheorem`  

（程式：`B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`。）

## 7. 明確排除／不可用集合

### 7.1 Skill 層（不進 adaptive pool）

與 **`MANUAL_REVIEW_SKILLS`** 對齊之 **friendly-unavailable**／manual_review 技能：

- `vh_數學B4_TreeDiagramCounting`  
- `vh_數學B4_PascalTriangle`  

（程式：`B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS`。）

### 7.2 Problem type 層（防禦：產題後仍擋）

即使 metadata／路由器回歸錯誤，下列 **`problem_type_id` 一律視為不合格**：

- `binomial_expansion_basic`  
- `tree_diagram_listing`  
- `pascal_triangle_derivation`  

（程式：`B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`。）

### 7.3 其他 B4 `skill_id`

凡 **`vh_數學B4_*`** 但 **不在 allowlist**、且 **非**上述 manual_review 二元組者 — **一律 skip**，audit reason：`not_in_b4_chapter1_deterministic_allowlist`。

## 8. Route／Frontend 是否修改

| 層級 | 是否修改 |
|---|---|
| **`core/routes/practice.py`** | **是**（僅 `get_adaptive_question`） |
| **frontend／templates** | **否** |
| **`app.py`** | **否** |
| **coverage matrix CSV** | **否** |

**Debug：** `GET .../get_adaptive_question?...&adaptive_audit=1` 時，JSON 多 **`adaptive_audit`**（含 `skill_id`、`problem_type_id`、`generator_key`、`router_trace` 摘要）。預設仍僅 **server log** `question_audit`。

## 9. QA 指令與結果

```text
python -m pytest tests/test_b4_chapter1_adaptive_allowlist.py -q
```

結果：**8 passed**（含 allowlist 過濾、黑名單驗證、對 **13** 個 allowlisted skill **`generate_for_skill(..., seed=11)`** smoke）。

```text
python -m pytest tests/test_vocational_math_b4_question_router_registry_canonical.py -q
```

結果：**24 passed**（確認 router registry／canonical 未被本次間接破壞）。

## 10. 取樣摘要（程式級）

- **Pool filter：** TreeDiagram／Pascal／未知 `vh_數學B4_*` 被 skip，JH 等非 B4 id **原樣保留**。
- **Router smoke：** allowlist 內 **13** 個 skill 均能產題且 **`validate_b4_deterministic_adaptive_generator_payload`** 通過。
- **Excluded problem types：** 單元測試對三個黑名單 id **一律判定不通過**。

## 11. 限制與已知落差（需在 Phase 4F 主實作處理）

1. **`recommend_question` 仍依賴 DB `TextbookExample`**：若某 curriculum／章節 **無題目列**，仍會在 **`generate()` 之前**得到 **404**；Preflight **未**改成純 generator-first adaptive。
2. **Review pool** 原始 session 仍存完整 curriculum skill 列表；**每次請求**於記憶體中過濾，**未**回寫 session（避免副作用）；若需縮短 session，可於後續明確設計。
3. **`session_engine`／PPO path**：尚未接 allowlist；後續應 **import 共用模組**避免雙軌規則漂移。

## 12. 結論與建議

- **Preflight 已完成：** **deterministic adaptive allowlist**、**manual_review skill pool 過濾**、**excluded problem_type 防禦**、**稽核 log／可選 JSON** 均已到位。
- **是否立刻進入 Phase 4F「完整 adaptive 行為」：** 建議 **先完成／並行**下列項目再視為「主實作完成」：
  1. **Generator-first 或 hybrid**：降低對 **`TextbookExample`** 的空池依賴，否則 B4 deterministic 僅能在「DB 恰好有題」時進入 adaptive。
  2. 將 **同一 allowlist** 接到 **`session_engine`／adaptive v2**（若使用者入口會走到該路徑）。
- **Gate 本身：** 目前已可避免 **不可用／manual_review B4 skill** 與 **三類 excluded problem_type** 進入 deterministic adaptive 主路徑；**可繼續 Phase 4F implementation**，但應優先處理 **題源／選題策略** 與 **session_engine 對齊**。
