# B4 Phase 4E-16B Final Runtime Closure Summary

## 1. 本階段目的

本階段依 Phase 4E-16A 決策，只更新 coverage 文件，將 `binomial_expansion_basic` 從 `planned_only` 移出，標記為 manual_review / future_ai_judged / future_free_response / normalization_required。

本階段未修改程式、資料庫、前端、route、`app.py`、generator、wrapper 或 tests。

## 2. 更新項目

| problem_type_id | 原狀態 | 新狀態 | 原因 | next_action |
|---|---|---|---|---|
| `binomial_expansion_basic` | `planned_only` | `excluded` with manual_review / future_ai_judged notes | answer 為 `list[int]`，完整展開也可能以多項式輸入；目前 int-answer runtime 若硬接會產生非數學性誤判 | 暫緩 / future_ai_judged free-response / normalization_required |

說明：
- 目前 coverage matrix 使用 `coverage_status=excluded` 表示非 deterministic int-answer runtime 目標。
- 為避免新增不一致 status，本階段沿用 `excluded`，並在 notes 寫明 `manual_review / future_ai_judged / future_free_response / normalization_required`。

## 3. 更新後 coverage 狀態

- problem_type 總數：28
- runtime_ready：25
- planned_only：0
- manual_review / excluded-like：3

更新後：
- Chapter 1 一般 runtime 待辦已歸零。
- `binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation` 皆非目前 int-answer 一般練習 runtime 目標。
- 這不代表這些題型不重要，而是改列 future_ai_judged / manual_review / free-response path。

## 4. 為什麼 binomial_expansion_basic 不算漏做

目前已有 6 個二項式 int-answer runtime 題型可用，涵蓋係數和、指定係數、反求 `n`、中間項、奇偶項係數和、含負項係數等能力。

`binomial_expansion_basic` 是完整展開題，answer 可能是 `list[int]` 或完整多項式。

學生輸入格式高度多樣，例如係數列表、空格分隔、逗號分隔、一般多項式、LaTeX 多項式。

若硬接目前 runtime，會因缺少 normalization 與 free-response 判分規格而產生非數學性誤判。

因此改列 future_ai_judged / free-response 是更合理的設計。

## 5. future_ai_judged / handwriting checked path

未來可行方向：

- textbox disabled / readonly。
- 學生以手寫區或上傳圖片作答。
- OCR / vision model 解析學生作答。
- AI 助教根據標準答案、學生作答與 rubric 判斷：
  - correct
  - incorrect
  - partially_correct
  - needs_review

適用題型：

- `binomial_expansion_basic`
- `tree_diagram_listing`
- `pascal_triangle_derivation`
- 完整列舉題
- 完整展開題
- 證明 / 推導題
- 手寫過程題

## 6. 後續建議

1. Phase 4E-Final：產出 Chapter 1 runtime closure report。
2. Phase 4F：規劃 adaptive route 接入，不急著一次全接。
3. future_ai_judged runtime 另開主線，不與目前 deterministic int-answer runtime 混在一起。
4. 不要硬接 `list[int]` 或 `list[str]` answer 到一般練習頁。
5. 若要處理完整展開，先做 answer format spec / normalization / AI 判分 rubric。

## 7. 結論

`binomial_expansion_basic` 已移出 `planned_only`。  
Chapter 1 一般 runtime `planned_only` 已歸零。  
runtime_ready 維持 25 / 28。  
本階段沒有修改任何程式碼。  
Chapter 1 deterministic runtime 可視為實質收尾。  
