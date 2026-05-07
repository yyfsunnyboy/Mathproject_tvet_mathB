# Phase 5F-E Closure Summary：Tree Diagram Parametric Handwriting Practice Flow

**Date**: 2026-05-07  
**Phase**: 5F-E  
**Status**: ✅ CLOSED

---

## 1. Closure 目的

本文件用於正式收斂 Phase 5F-E 開發範疇。

本階段目標為：將 `tree_diagram_listing` 從原先標記為 `future_ai_judged` 的待辦題型，推進到可在原有 `/practice` 頁使用的 **handwriting AI-judged** 題型，並完成最小可用流程（端對端可操作、AI 可判分、支援下一題輪替）。

**本階段收斂後，不再繼續擴充樹狀圖功能。**

後續若有以下需求，請另開新 Phase：
- Handwriting image 品質提升與辨識準確度優化
- Teacher review DB（教師人工複核入庫）
- Adaptive scoring 整合（APR / mastery 更新）
- 複雜樹狀圖結構支援

---

## 2. 完成範圍

本階段已完成下列項目：

- **樹狀圖 skill 卡片接回原本 `/practice` 頁**（移除 MANUAL_REVIEW_SKILLS 中的 `vh_數學B4_TreeDiagramCounting`）
- **題目 payload 含完整必要欄位**：
  - `problem_type_id = tree_diagram_listing`
  - `answer_type = handwriting`
  - `grading_mode = ai_judged_free_response`
  - `variant`（`early_stopping_game` 或 `fixed_stage_binary_tree`）
  - `expected_count`
  - `expected_paths`（供後端 AI rubric 使用，不在前端顯示）
  - `path_labels`
- **前端使用既有手寫作答區**（`#handwriting-canvas`），不新增獨立頁面
- **`/analyze_handwriting` 針對 `tree_diagram_listing` 使用 `expected_paths` rubric**，走 AI-judged 流程而非一般 expression 辨識流程
- **AI 檢查後可按「下一題」**（前端在 `success: true` 後顯示下一題按鈕）
- **下一題保留 `tree_diagram_index` 參數**，自動遞增產生不同題幹
- **參數化題目支援 labels / stages / index 變化**（從 `build_tree_diagram_listing_payload` 延伸）

---

## 3. 支援題型 variants

目前支援兩大 variant：

### 3.1 `early_stopping_game`

**代表題**：
> 甲、乙兩隊比賽，每場沒有平手，先贏兩場者勝。試問共有多少種勝負情形？請用樹狀圖或完整列舉方式描述所有可能情形。

**支援 label 變化**：
- 甲 / 乙
- 紅 / 藍
- A / B

**`expected_paths` 範例**（以甲乙為例）：
```
甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙
```
共 6 種路徑（`expected_count = 6`）。

**關鍵判斷規則**：若學生列出固定三場 8 種，須回饋「先贏兩場即停止」錯誤。

---

### 3.2 `fixed_stage_binary_tree`

**代表題**：
> 投擲一枚均勻硬幣連續三次，試用樹狀圖或完整列舉方式描述所有可能情形。

**支援 label / stage 變化**：
- 正 / 反（三次）
- 成 / 敗（兩次或三次）
- 甲 / 乙（兩次或三次）
- 紅 / 藍（三次）

**`expected_paths` 自動產生**：由 `labels` 與 `stages` 以笛卡兒積生成。例如三次正/反 → 8 種，兩次成/敗 → 4 種。

---

## 4. 手動 Smoke 結果

本次手動 smoke 測試結果（透過瀏覽器操作確認）：

| `tree_diagram_index` | Variant | Labels |
|---|---|---|
| 0 | `early_stopping_game` | 甲 / 乙 |
| 1 | `fixed_stage_binary_tree` | 正 / 反（三次）|
| 2 | `early_stopping_game` | 紅 / 藍 |
| 3 | `fixed_stage_binary_tree` | 成 / 敗（兩次）|
| 4 | `early_stopping_game` | A / B |
| 5 | `fixed_stage_binary_tree` | 紅 / 藍（三次）|

後續 index 仍可持續輪替（`index % len(VARIANT_TABLE)`）。

**Smoke 判定結果**：
- ✅ `/get_next_question` 回 `200`
- ✅ 未再出現 `No module named skills.vh_數學B4_TreeDiagramCounting`
- ✅ 題幹隨 index 變化
- ✅ 手寫作答區正常顯示
- ✅ 不走 int-answer `/check_answer`
- ✅ 下一題流程可用，不卡死

---

## 5. 測試結果

已執行以下自動化測試：

| 測試檔案 | 結果 |
|---|---|
| `python -m pytest -q tests/test_phase5f_b_tree_diagram_text_answer_judge.py` | **13 passed** |
| `python -m pytest -q tests/test_phase5f_d_free_response_practice_route.py` | **14 passed** |
| `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py` | **8 passed** |

> **備註**：測試輸出中的 `DeprecationWarning` 源自既有 SQLAlchemy `datetime.utcnow()` 使用方式，屬 pre-existing warning，**非本階段功能錯誤**，不影響判定。

---

## 6. Runtime 邊界

### 本階段**沒有**做：

- ❌ 新增 `skills/vh_數學B4_TreeDiagramCounting.py`
- ❌ 將 `tree_diagram_listing` 加入 deterministic int-answer allowlist
- ❌ 修改 `/check_answer`
- ❌ 修改 `/api/adaptive/submit_and_get_next`
- ❌ 修改 B4 deterministic `question_router`
- ❌ 修改 B4 deterministic generators
- ❌ 修改 coverage matrix
- ❌ 接入 adaptive scoring（APR / mastery 不受影響）
- ❌ 接入 teacher review DB
- ❌ 擴充 handwriting/image recognition 架構

### 本階段**保留**：

- `/free_response_practice` 保留作為 teacher preview / fallback 路徑
- 原 `/practice` 頁作為主要學生入口
- `/analyze_handwriting` 作為 AI 檢查入口

---

## 7. Known Limitations

1. **`expected_answer` 可能為空**：對 `tree_diagram_listing` 而言，`correct_answer` 欄位刻意留空，因為此題型不靠單一字串比對，而是靠 `expected_paths` rubric 判斷。此行為是設計上預期的。
2. **`expected_paths` 須保持後端私有**：前端 payload 中仍可能包含 `expected_paths` 欄位，應確保學生端 UI 不直接顯示這些路徑（目前前端未顯示）。
3. **Gemini Vision 判斷受圖片品質影響**：手寫圖像品質差（如筆跡潦草、背景雜訊）可能導致 `needs_review`。
4. **`needs_review` 須教師介入**：目前系統不會自動標記或入庫，需教師人工抽查。
5. **尚未寫入 teacher review DB**：`needs_review` 結果目前僅在前端顯示，無持久化記錄。
6. **尚未影響 adaptive mastery / APR**：樹狀圖作答結果不會更新學生的 AKT 知識狀態。
7. **只支援二分支樹狀圖**：目前不處理三分支或更複雜的樹狀圖結構（如三隊循環賽、多事件組合）。

---

## 8. Go / No-Go 判定

### ✅ Go（可以做）：
- **B4 Chapter 1 樹狀圖可進教師 QA**：邀請教師使用練習頁，觀察題幹與 AI 判分品質
- **可在教師監看下進行小規模學生試用**：建議班級規模 ≤ 30 人，教師保有介入能力
- **可作為 AI-judged free-response 題型 prototype**：為後續其他 free-response 題型整合提供架構參考

### ❌ No-Go（不建議做）：
- **不建議直接無監督大規模使用**：AI 判分準確率尚未經過系統性評估
- **不建議立即混入 adaptive mastery scoring**：掌握度更新架構需另行設計
- **不建議立即擴充到所有 free-response 題型**：應依題型特性逐一評估 rubric 設計
- **不建議現在處理手寫圖像模型優化**：屬於獨立基礎設施工程，另開 Phase

---

## 9. 下一步建議

**本階段結束後，不要再改樹狀圖功能。**

若後續有需求，請另開以下 Phase：

| Phase | 內容 |
|---|---|
| **Phase 5G** | B4 Chapter 1 teacher QA / pilot readiness cleanup（教師 QA 準備與介面精修）|
| **Phase 5F-F** | Teacher review log / override schema（教師複核記錄與覆寫機制）|
| **Phase 5F-G** | Handwriting image quality and low-confidence review（圖像品質分析與低信心度複核）|
| **Phase 5H** | 其他 `future_ai_judged` 題型：完整二項式展開、巴斯卡三角形推導等 |

---

## 10. Final Closure Statement

```
Phase 5F-E is closed.

B4 Chapter 1 tree_diagram_listing now supports:
  - text-based question generation
  - original practice page entry (/practice)
  - handwriting answer UI (existing canvas)
  - AI-judged expected_paths rubric (/analyze_handwriting)
  - next-question flow (tree_diagram_index parametric cycling)
  - parametric question variation (labels / stages / index)

All automated tests pass (13 + 14 + 8 = 35 tests).
Manual smoke confirmed 6 parametric variants cycling correctly.

No further Phase 5F-E code changes are recommended.
```

---

*Document generated: 2026-05-07*  
*Author: AI Coding Assistant (Phase 5F-E Closure)*
