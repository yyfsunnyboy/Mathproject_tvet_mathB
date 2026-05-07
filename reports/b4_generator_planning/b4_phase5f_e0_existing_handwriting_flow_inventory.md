# Phase 5F-E0: Existing Handwriting Flow Inventory

## 背景
本報告盤點系統中現有的「手寫作答 / AI 檢查」流程，評估將 B4 Chapter 1「樹狀圖」整合至現有手寫作答流程的可行性與實作方向。

## 盤點結果與問題回答

### 1. 現有手寫作答區在哪個 template？
系統中存在多處手寫作答區（`#handwriting-canvas`），主要位於以下 Templates：
- **`templates/adaptive_review_simple.html`**: 具有完整的手寫版、工具列與「AI 檢查手寫」按鈕。
- **`templates/index.html`**: 主要練習頁，也包含了 `<canvas id="handwriting-canvas">` 與 `analyze-handwriting-button`，並由 `data.answer_type === 'handwriting'` 觸發顯示。
- **`templates/adaptive_practice_v2.html`**: 包含手寫版結構，作為輔助計算紙。

### 2. 現有手寫 AI 檢查打哪個 endpoint？
根據不同的前端頁面，會打不同的 endpoint：
- `adaptive_review_simple.html` 呼叫 **`POST /api/adaptive-review/check-handwriting`**。
- `index.html` 呼叫 **`POST /analyze_handwriting`**。

### 3. 後端 endpoint 是否存在？
**是的，完全存在。**
- **`/api/adaptive-review/check-handwriting`** 定義在 `adaptive_review_api.py` 的 Line 1013。
- **`/analyze_handwriting`** 定義在 `core/routes/analysis.py` 的 Line 2393。

### 4. 若不存在，最小補法是什麼？
由於 endpoint 已存在，無需新建。但現有 `/api/adaptive-review/check-handwriting` 直接呼叫 `core.ai_analyzer.analyze`（底層用 Gemini Vision 評分），可能缺乏對樹狀圖特定的 `judge_tree_diagram_text_answer` 規則防護。若要針對樹狀圖特化，最少需要在現有 route 內根據 `skill_id` 分流。

### 5. tree_diagram_listing 要接入時，應該在哪裡分流 grading_mode=ai_judged_free_response？
如果學生真正使用「畫筆」畫樹狀圖，那麼應該讓這個 skill 的 `input_type` 設為 `handwriting`。
在後端收到圖片後（例如 `/analyze_handwriting`），我們可以在該 endpoint 內針對 `skill_id == "vh_數學B4_TreeDiagramCounting"` 或 `problem_type == "tree_diagram_listing"` 進行分流，不再直接走通用 Vision 評分，而是進入專屬的樹狀圖辨識與判斷邏輯。

### 6. 能否沿用 Phase 5F-B 的 `judge_tree_diagram_text_answer` 作為文字列舉判斷？
**完全可以且強烈建議。**
由於 AI 視覺模型直接進行邏輯計數容易出現幻覺（Hallucination），最佳做法是將任務拆分：
1. **Vision 任務**：先請 Gemini Vision 將學生的手寫樹狀圖轉換為文字形式（路徑列舉，即 `detected_paths`）。
2. **Logic 任務**：將辨識出的文字路徑交由 `judge_tree_diagram_text_answer` 進行確定性的正確/偏誤判定。

### 7. 手寫圖像判斷是否應先轉成 detected_paths，再交給 judge？
**是的。** 這是最穩健的做法。
藉由 Vision 模型提取結構化資料（如 `["正反", "正反"]`），再由原有的 Python 邏輯（即 `judge_tree_diagram_text_answer`）計算是否符合 `early_stopping_game` 或其他 variant 的期望路徑集合。這樣能最大化重用已測試完畢的 P5F-B 邏輯，並保證回饋的精準度。

### 8. 是否應保留 /free_response_practice 作為 teacher preview，而學生入口改走原手寫頁？
**是的。**
- **Teacher Preview/Debug**: `/free_response_practice`（文字輸入框）是非常好的快速測試工具，能直接驗證生成器邏輯與判定 API，不需要每次都用滑鼠畫圖，也方便教師預覽。
- **學生入口**: 在 dashboard 的技能卡片應該指向標準的 `practice` 或 `adaptive_review` 頁面，並透過設定該技能為 `handwriting`，讓學生直覺地「畫」樹狀圖，從而享有流暢且統一的體驗。

## 目前手寫傳遞資料格式
### 前端 Payload (`/api/adaptive-review/check-handwriting`)
- `image_base64`: 學生手動畫布的 Base64 圖像
- `question_text`: 題目本文
- `correct_answer`: 正確答案（作為評分參考）

*(若為 `index.html` 的 `/analyze_handwriting`，則 payload 包含 `problem_type`, `skill_id`, `image_data`, `question_text` 等更豐富欄位)*

### AI 回傳格式 (`check-handwriting`)
- `status`: 'success' / 'error'
- `reply`: 評語、分析或提示 (字串)
- `is_process_correct`: 布林值 (True / False)

*(注意：目前通用 endpoint 不一定會回傳 `analysis` 或 `feedback` 等 P5F-B 需要的欄位，若前端需要顯示這些資訊，可針對樹狀圖擴充後端回傳格式並修改前端處理邏輯)*
