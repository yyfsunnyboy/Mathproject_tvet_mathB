# B4 Phase 4E-15B Manual Review Coverage Update Summary

## 1. 本階段目的

本階段依 Phase 4E-15A 決策，只更新 coverage 文件，將 `tree_diagram_listing` 從一般 runtime 待辦中移出，標記為 manual_review / future visualization 類型。

本階段未修改程式、資料庫、前端、route、`app.py`、generator、wrapper 或 tests。

## 2. 更新項目

| problem_type_id | 原狀態 | 新狀態 | 原因 | next_action |
|---|---|---|---|---|
| `tree_diagram_listing` | `planned_only` | `excluded` with manual_review notes | 樹狀圖屬於視覺化/完整列舉能力；目前一般 runtime 不適合判分畫圖或 `list[str]` 列舉答案 | 暫緩 / future visualization 或 structured-answer |

說明：
- 目前 coverage matrix 既有非 runtime 類別使用 `coverage_status=excluded`。
- 為避免破壞 CSV 狀態設計，本階段採 `excluded`，並在 notes 明確標記 `manual_review / future visualization`。

## 3. 更新後 coverage 狀態

- problem_type 總數：28
- runtime_ready：25
- planned_only：1
- manual_review / excluded-like：2

更新後：
- `planned_only` 僅剩 `binomial_expansion_basic`。
- `tree_diagram_listing` 與 `pascal_triangle_derivation` 皆非目前一般練習 runtime 目標。
- `tree_diagram_listing` 沒有被標成 `runtime_ready`。

## 4. 為什麼 tree_diagram_listing 不算漏做

樹狀圖是視覺化/列舉能力，不只是單一數值答案。

目前 runtime 對 `int` answer 與 choices 支援較穩定，但不適合判斷學生是否畫出正確樹狀圖，也不適合直接判斷格式自由的 `list[str]` 答案。

若把題目改成「共有幾種結果」，實質上會變成乘法原理代理題，不能代表學生已具備畫樹狀圖或完整列舉的能力。

因此，暫緩並標記為 manual_review / future visualization，是兼顧教學準確性與工程穩定性的選擇。

## 5. 後續建議

1. Phase 4E-16A：重新確認 `binomial_expansion_basic` 是否繼續暫緩，或規劃 free-response / normalization。
2. Phase 4E-16B：若不接 `binomial_expansion_basic`，Chapter 1 一般 runtime 可視為 25 / 28 實質收尾。
3. `tree_diagram_listing` future path：
   - future visualization
   - structured-answer listing
   - teacher-only/manual review material
4. 不要硬接 `list[str]` 或繪圖題到一般練習頁。

## 6. 結論

`tree_diagram_listing` 已移出 `planned_only`。  
Chapter 1 runtime `planned_only` 目前只剩 `binomial_expansion_basic`。  
`tree_diagram_listing` 被記錄為 excluded-style manual_review / future visualization item。  
runtime_ready 維持 25 / 28。  
本階段沒有修改任何程式碼。  
