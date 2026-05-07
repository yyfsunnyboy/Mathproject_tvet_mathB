# Phase 5G-A Closure Summary：Pascal Triangle Handwriting AI Check Integration

**Date**: 2026-05-07  
**Phase**: 5G-A  
**Status**: ✅ CLOSED

---

## 1. Closure 目的

本文件用於正式收斂 Phase 5G-A 開發範疇。

本階段目標為：將 `vh_數學B4_PascalTriangle` 從原先標記為 `MANUAL_REVIEW_SKILLS`（`future_ai_judged`）的待辦題型，推進到可在原有 `/practice` 頁使用的 **handwriting AI-judged** 題型，並完成最小可用流程（文字出題、手寫作答、AI 判斷、下一題輪替）。

**本階段收斂後，不再繼續擴充巴斯卡三角形功能。**

後續若有以下需求，請另開新 Phase：
- 有係數二項式展開（如 $(2x+1)^n$）
- Teacher review DB（教師人工複核入庫）
- Adaptive scoring 整合（APR / mastery 更新）
- Handwriting image 品質提升與辨識準確度優化
- 巴斯卡三角形推導證明題型

---

## 2. 完成範圍

本階段已完成下列項目：

- **巴斯卡三角形 skill 卡片接回原本 `/practice` 頁**（移除 `MANUAL_REVIEW_SKILLS` 中的 `vh_數學B4_PascalTriangle`）
- **題目 payload 含完整必要欄位**：
  - `problem_type_id = pascal_triangle_handwriting`
  - `skill_id = vh_數學B4_PascalTriangle`
  - `answer_type = handwriting`
  - `grading_mode = ai_judged_free_response`
  - `variant`（`pascal_row_listing` 或 `pascal_binomial_expansion`）
  - `n`（列數或次方數）
  - `expected_row`（row listing 題型用）
  - `expected_terms`（展開式各項係數）
  - `expected_expansion`（完整展開式字串，供 AI rubric 使用）
- **前端使用既有手寫作答區**（`#handwriting-canvas`），不新增獨立頁面
- **`/analyze_handwriting` 針對 `pascal_triangle_handwriting` 使用 Pascal rubric**，走 AI-judged 流程而非一般 expression 辨識流程
- **AI 檢查後可按「下一題」**（前端在 `success: true` 後顯示下一題按鈕）
- **下一題保留 `pascal_triangle_index` 參數**，自動遞增產生不同題幹
- **與 `tree_diagram_index` 分開維護**，兩套 handwriting flow 不互相干擾

---

## 3. 支援題型 variants

目前支援兩大 variant：

### 3.1 `pascal_row_listing`

**代表題**：
> 已知巴斯卡三角形第 0 列為 1，第 1 列為 1, 1，第 2 列為 1, 2, 1。請寫出第 4 列的各項數字。

**列數定義**（從第 0 列開始）：
```
第 0 列：1
第 1 列：1, 1
第 2 列：1, 2, 1
第 3 列：1, 3, 3, 1
第 4 列：1, 4, 6, 4, 1
第 5 列：1, 5, 10, 10, 5, 1
```

**`expected_row` 範例**（以 n = 4 為例）：
```
[1, 4, 6, 4, 1]
```

**判斷規則（AI rubric）**：
- 完整寫出正確列 → `correct`
- 漏項、順序錯 → `partial`
- 寫成上一列或下一列 → `partial` 或 `incorrect`
- 手寫不清 → `needs_review`

---

### 3.2 `pascal_binomial_expansion`

**代表題**：
> 請利用巴斯卡三角形展開 $(x+y)^3$。  
> 請利用巴斯卡三角形展開 $(x-y)^4$。

**支援範圍**：
- $(x+y)^n$，n = 2, 3, 4, 5
- $(x-y)^n$，n = 2, 3, 4, 5

**`expected_expansion` 範例**：
```
(x+y)^3 = x^3 + 3x^2y + 3xy^2 + y^3
(x-y)^3 = x^3 - 3x^2y + 3xy^2 - y^3
(x+y)^4 = x^4 + 4x^3y + 6x^2y^2 + 4xy^3 + y^4
(x-y)^4 = x^4 - 4x^3y + 6x^2y^2 - 4xy^3 + y^4
```

**判斷規則（AI rubric）**：
- 係數、次方、符號、項數皆正確 → `correct`
- 只寫出係數列（如 `1 3 3 1`）但未展開多項式 → `partial`
- 漏項、符號錯、次方錯 → `partial` 或 `incorrect`
- 手寫不清 → `needs_review`

---

## 4. 手動 Smoke 結果

本次手動 smoke 測試結果（透過瀏覽器操作確認）：

| `pascal_triangle_index` | Variant | 題幹摘要 |
|---|---|---|
| 0 | `pascal_row_listing` | 寫出第 3 列 |
| 1 | `pascal_binomial_expansion` | 展開 $(x+y)^3$ |
| 2 | `pascal_row_listing` | 寫出第 4 列 |
| 3 | `pascal_binomial_expansion` | 展開 $(x-y)^4$ |
| 4 | `pascal_row_listing` | 寫出第 5 列 |
| 5 | `pascal_binomial_expansion` | 展開 $(x+y)^5$ |

後續 index 仍可持續輪替（`index % len(PASCAL_VARIANT_TABLE)`）。

**Smoke 判定結果**：
- ✅ `/get_next_question` 回 `200`
- ✅ 未出現 `No module named skills.vh_數學B4_PascalTriangle`
- ✅ 題幹隨 `pascal_triangle_index` 變化
- ✅ 手寫作答區正常顯示
- ✅ 不走 int-answer `/check_answer`
- ✅ 下一題流程可用，不卡死
- ✅ 與樹狀圖 handwriting flow 不互相干擾（各自使用獨立 index 參數）

---

## 5. 測試結果

已執行以下自動化測試：

| 測試檔案 | 結果 |
|---|---|
| `python -m pytest -q tests/test_phase5g_a_pascal_triangle_handwriting_flow.py` | **7 passed** |
| `python -m pytest -q tests/test_phase5f_d_free_response_practice_route.py` | **14 passed** |
| `python -m pytest -q tests/test_phase5f_b_tree_diagram_text_answer_judge.py` | **13 passed** |
| `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py` | **8 passed** |

> **備註**：測試輸出中若有 `DeprecationWarning`，源自既有 SQLAlchemy `datetime.utcnow()` 使用方式，屬 pre-existing warning，**非本階段功能錯誤**，不影響判定。

---

## 6. Runtime 邊界

### 本階段**沒有**做：

- ❌ 新增一般 int-answer `PascalTriangle` generator（`skills/vh_數學B4_PascalTriangle.py`）
- ❌ 將 `pascal_triangle_handwriting` 加入 deterministic int-answer allowlist
- ❌ 修改 `/check_answer`
- ❌ 修改 `/api/adaptive/submit_and_get_next`
- ❌ 修改 B4 deterministic `question_router`
- ❌ 修改 B4 deterministic generators
- ❌ 修改 coverage matrix
- ❌ 接入 adaptive scoring（APR / mastery 不受影響）
- ❌ 接入 teacher review DB
- ❌ 擴充 handwriting/image recognition 架構

### 本階段**保留**：

- 原 `/practice` 頁作為主要學生入口
- `/analyze_handwriting` 作為 AI 檢查入口
- 樹狀圖 handwriting flow 原有行為（`tree_diagram_index` 不受影響）
- 一般 int-answer skill 原有行為

---

## 7. Known Limitations

1. **`expected_answer` 可能為空**：對 `pascal_triangle_handwriting` 而言，`correct_answer` 欄位刻意留空，因為此題型不靠單一字串比對，而是靠 `expected_row` / `expected_expansion` rubric 判斷。此行為是設計上預期的。
2. **`expected_row` / `expected_terms` / `expected_expansion` 須保持後端私有**：這些欄位僅供 AI rubric 使用，不應在學生端 UI 直接顯示。
3. **Gemini Vision 判斷受筆跡品質影響**：展開式的次方與係數若寫得不清晰，可能導致 `needs_review`。
4. **`needs_review` 須教師介入**：目前系統不會自動標記或入庫，需教師人工抽查。
5. **尚未寫入 teacher review DB**：`needs_review` 結果目前僅在前端顯示，無持久化記錄。
6. **尚未影響 adaptive mastery / APR**：巴斯卡三角形作答結果不會更新學生的 AKT 知識狀態。
7. **只支援 $(x+y)^n$ 與 $(x-y)^n$**：不支援有係數的展開式，如 $(2x+1)^n$ 或 $(ax-b)^n$。
8. **不處理巴斯卡三角形推導證明**：本階段僅支援「列舉列值」與「展開多項式」，不涉及歸納法或組合恆等式的推導題型。
9. **展開式等價判斷依賴 AI rubric**：尚未接入 symbolic algebra verifier（如 SymPy），AI 判斷準確率受模型能力限制。

---

## 8. Go / No-Go 判定

### ✅ Go（可以做）：
- **B4 Chapter 1 巴斯卡三角形可進教師 QA**：邀請教師使用練習頁，觀察題幹與 AI 判分品質
- **可在教師監看下進行小規模學生試用**：建議班級規模 ≤ 30 人，教師保有介入能力
- **可作為 AI-judged free-response 題型 prototype 的第二個成功案例**：與樹狀圖共同驗證此架構的可擴充性

### ❌ No-Go（不建議做）：
- **不建議直接無監督大規模使用**：AI 判分準確率尚未經過系統性評估
- **不建議立即混入 adaptive mastery scoring**：掌握度更新架構需另行設計
- **不建議現在擴充到有係數二項式展開**：需另行設計 rubric 與 expected_expansion 生成邏輯
- **不建議現在處理巴斯卡推導證明**：屬於更高難度的 free-response 題型，需獨立設計
- **不建議現在處理手寫圖像模型優化**：屬於獨立基礎設施工程，另開 Phase

---

## 9. 下一步建議

**本階段結束後，不要再改巴斯卡三角形 basic flow。**

若後續有需求，請另開以下 Phase：

| Phase | 內容 |
|---|---|
| **Phase 5G-B** | Pascal Triangle Coefficient Expansion Extension：支援 $(2x+1)^3$、$(x+2)^3$、$(2x-1)^3$ 等小範圍有係數展開 |
| **Phase 5G-C** | Teacher review log / override schema：教師複核記錄與覆寫機制 |
| **Phase 5G-D** | Handwriting image quality and low-confidence review：圖像品質分析與低信心度複核 |
| **Phase 5H** | Register AI-judged free-response skills into B4 adaptive candidate list：將 handwriting AI-judged 題型納入自適應推薦 |
| **Phase 5I** | 其他 `future_ai_judged` 題型擴充 |

---

## 10. Final Closure Statement

```
Phase 5G-A is closed.

B4 Chapter 1 PascalTriangle now supports:
  - text-based question generation
  - original practice page entry (/practice)
  - handwriting answer UI (existing canvas)
  - AI-judged Pascal rubric via /analyze_handwriting
  - next-question flow via pascal_triangle_index
  - basic parametric variation:
      - pascal_row_listing (rows 3–5)
      - (x+y)^n expansion (n = 2–5)
      - (x-y)^n expansion (n = 2–5)

All automated tests pass (7 + 14 + 13 + 8 = 42 tests).
Manual smoke confirmed 6 parametric variants cycling correctly.
No interference with tree_diagram handwriting flow or int-answer skills.

No further Phase 5G-A code changes are recommended.
```

---

*Document generated: 2026-05-07*  
*Author: AI Coding Assistant (Phase 5G-A Closure)*
