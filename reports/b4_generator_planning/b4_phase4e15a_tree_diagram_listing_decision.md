# B4 Phase 4E-15A Tree Diagram Listing Decision

## 1. 本階段目的

本階段僅針對 `tree_diagram_listing` 做 runtime 收尾決策，產出可執行的策略文件；不修改程式、不接 router、不改前端、不引入新判分機制。

## 2. 目前 coverage 狀態

- runtime_ready：25 / 28
- planned_only：2
- excluded：1
- planned_only 剩餘：
  - binomial_expansion_basic
  - tree_diagram_listing
- excluded：
  - pascal_triangle_derivation

## 3. tree_diagram_listing 的核心問題

`tree_diagram_listing` 的教學本體是「分支展開與完整列舉」，但現有一般練習頁主要是文字題幹 + 單一答案（多為 `int`）+ choices。這造成三個直接落差：

1. 樹狀圖是視覺化表示，目前頁面與判分流程不支援「畫圖作答」。
2. 若改要求「列出所有可能」，答案型態會接近 `list[str]`，會遇到順序、分隔符、符號、同義表示等 normalization 問題。
3. 若只問「總共有幾種」，會退化為乘法原理計數，與既有 counting 題型高度重疊，題型名稱易名實不符。

因此 `tree_diagram_listing` 不適合直接硬接現行一般練習頁。

## 4. 三種方案比較

| 方案 | 做法 | answer 型態 | 是否相容現有 runtime | 教學準確性 | coverage 影響 | 風險 |
|---|---|---|---|---|---|---|
| A：暫緩 / manual_review | 不接一般練習頁；維持 planned_only 或轉 manual_review/excluded，留待教材或未來視覺模組 | N/A | 高（不新增 runtime 變更） | 高（不假裝已評量畫圖/列舉能力） | 不提升（維持 25/28，或視其他題型到 26/28） | 低 |
| B：文字列舉 structured answer | 題目要求列出全部組合 | `list[str]` | 低 | 中高 | 可提升但不穩定 | 高（判分格式歧義、normalization 成本高） |
| C：int-answer 計數替代 | 題幹保留樹狀圖語境，只問總數 | `int` | 高 | 中（偏代理題） | 可提升（可標 runtime_ready） | 中（題型語義偏移） |

## 5. 建議方案

短期建議採 **方案 A（暫緩 / manual_review）**。

原因：目前 Phase 4E 是 runtime 收尾，核心目標是穩定與可維運；`tree_diagram_listing` 若不做前端/判分升級，無法真實評量「畫樹狀圖」與「完整列舉」能力。方案 C 雖可補 coverage，但語義漂移明顯，會把題型實質改成 multiplication-principle counting；方案 B 則在現階段風險過高。

## 6. 若採建議方案，後續如何落地

1. coverage matrix 將 `tree_diagram_listing` 由 `planned_only` 轉為 `manual_review`（或 `excluded`，建議 `manual_review`）。
2. 在 planning 報告層新增 future item：`tree_diagram_visual_free_response`（未來視覺化/structured-answer 能力）。
3. Chapter 1 runtime 目標改為「實質可達上限」：
   - 若 `binomial_expansion_basic` 未解：25 / 28
   - 若 `binomial_expansion_basic` 後續以可接受方式解：26 / 28
4. 在報告 notes 明確註記：`tree_diagram_listing` 非 runtime 練習頁題，避免後續被誤解為漏接。

## 7. 不建議現在做的事

- 不要求學生畫樹狀圖
- 不接 `list[str]` answer
- 不改前端繪圖
- 不改 `check_answer` 做複雜列舉 normalization
- 不把視覺題硬塞進一般練習頁

## 8. 給非 coding 教師的說明

- 樹狀圖是「表示方法」，不是單純一個數字答案。
- 系統目前能穩定判斷整數答案，但不能判斷學生畫的圖。
- 若短期改成問總數，是借用樹狀圖語境做計數練習，不等於學生真的會畫樹狀圖。
- 真正的樹狀圖能力需要未來視覺化或 structured-answer 支援。

## 9. 結論

`tree_diagram_listing` 在目前 runtime 架構下不適合直接接入一般練習頁。  
短期應以穩定性優先，採方案 A，轉為 `manual_review` / future visualization。  
不建議現在做 list 列舉判分（方案 B）。  
方案 C 可作 coverage 衝刺備案，但會弱化題型教學語義。  
Chapter 1 實際 runtime 上限建議按 25/28 或 26/28 管理。  
