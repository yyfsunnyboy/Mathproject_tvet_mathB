# B4 Phase 4E-13D Binomial Theorem Depth Expansion Plan

## 1. 本階段目的
本文件用於規劃 B4 Chapter 1 二項式題型的後續厚度擴充。  
目前已完成的是 int-answer 最小可用接入；本階段不修改任何程式、不接 router、不改前端，只定義下一步策略。

## 2. 目前二項式 runtime 狀態

| problem_type_id | skill_id | answer 型態 | runtime 狀態 | 備註 |
|---|---|---|---|---|
| binomial_coefficient_sum | vh_數學B4_BinomialCoefficientIdentities | int | runtime_ready | 已接 router / wrapper，已通過 web smoke test |
| binomial_specific_term_coefficient | vh_數學B4_BinomialTheorem | int | runtime_ready | 已接 router / wrapper，已通過 web smoke test |
| binomial_equation_solve_n | vh_數學B4_BinomialCoefficientIdentities | int | runtime_ready | 已接 router / wrapper，已通過 web smoke test |
| binomial_expansion_basic | vh_數學B4_BinomialTheorem | list[int] | planned_only（暫緩） | 未接 runtime；一般練習頁尚無穩定輸入/判分 normalization |

補充說明：
- 上述 3 個 runtime_ready 二項式題型皆為 int-answer。
- 目前二項式接入屬於「可上線的局部能力訓練」，不是完整二項式展開能力。
- `binomial_expansion_basic` 仍暫緩。

## 3. 目前題型偏薄的原因
1. **完整展開題未接入**：`binomial_expansion_basic` 的 answer 為 `list[int]`，一般練習頁不適合直接判分；學生輸入可能是係數列表，也可能是完整多項式。  
2. **目前題型偏單點能力**：現有題型多為係數和、指定項係數、由組合數求 `n`，可訓練局部概念，但無法完整驗證展開能力。  
3. **尚未支援多項式 normalization**：目前無法穩定判斷等價多項式，亦無法一致處理不同學生輸入格式。  
4. **尚未支援 free-response 題型**：當前 runtime 主軸仍是 int-answer / choices，未設計完整展開自由作答流程。

## 4. 二項式題型補強層級

| 層級 | 題型方向 | 是否適合現有 runtime | 優先程度 | 備註 |
|---|---|---|---|---|
| Layer 1 | 已上線 int-answer：係數和、指定項係數、常數項、由組合數條件求 n | 是 | 高（維持） | 既有穩定基線，繼續維持與小幅優化敘述品質 |
| Layer 2 | 可擴充 int-answer：中間項係數、奇偶次係數和、負 b、a≠1、係數比較/比值、簡單反求參數 | 是 | 高（下一批） | 不需改前端與判分主流程，可快速提升題型厚度 |
| Layer 3 | structured-answer：完整係數列表、多係數、部分展開、缺項填空 | 否（暫不接） | 中 | 可先做離線題庫與 sample QA，但不列入 runtime_ready |
| Layer 4 | free-response / symbolic：完整展開、多項式等價判分、輸入 normalization、SymPy/自訂 parser | 否（未來） | 低（長期） | 教學完整但工程牽動大，應在 Chapter 1 runtime 收尾後規劃 |

## 5. 後續策略比較

| 策略 | 說明 | 優點 | 缺點 | 短期建議 |
|---|---|---|---|---|
| 策略 A | 繼續用 int-answer 補強二項式深度 | 可穩定接入現有 runtime；不需改前端；不需改 check_answer；可快速增加 coverage 與練習量 | 仍不能完整檢查展開式；題型偏單點能力 | **建議採用** |
| 策略 B | 建立 structured-answer 題型，但暫不接一般 runtime | 可先累積完整展開能力資料；利於未來 free-response；可先用 sample QA 管理品質 | 不會立即提升 runtime_ready；仍需後續判分設計 | 可作為 A 的平行預研 |
| 策略 C | 立即改前端與 check_answer 支援多項式 | 可真正支援完整展開；教學完整度最高 | 工程風險高；牽動 route/frontend/wrapper/normalizer/sympy；不適合 Chapter 1 收尾期 | 短期不建議 |

## 6. 建議短期方案
建議短期採用策略 A。  
先以 int-answer 題型擴充二項式深度，維持小批次接入節奏；`binomial_expansion_basic` 仍暫緩，不進一般 runtime。

## 7. Phase 4E-13E 候選題型

| 候選 problem_type | answer 型態 | 教學價值 | 實作風險 | 是否建議下一批 |
|---|---|---|---|---|
| binomial_middle_term_coefficient | int | 補上「中間項/中間係數」核心概念，連接組合與展開結構 | 低 | 是 |
| binomial_odd_even_coefficient_sum | int | 強化代入法（x=1, x=-1）與係數分組思維 | 中 | 是 |
| binomial_specific_coefficient_with_negative_term | int | 補足負號與符號變化判讀，提升實戰性 | 中 | 是 |
| binomial_expansion_full_free_response_future | structured / symbolic | 可完整對齊二項式展開教學目標 | 高 | 否（future） |

## 8. 不建議現在做的事
- 不直接接入 `binomial_expansion_basic`。  
- 不改前端。  
- 不改 `check_answer`。  
- 不引入大型 polynomial parser。  
- 不把 `list[int]` 題硬塞進一般練習頁。

## 9. 給非 coding 教師的說明
- 現在二項式題目可以練「局部能力」。  
- 完整展開還不能穩定判分。  
- 先用係數、常數項、係數和等整數答案題型補強比較穩。  
- 完整展開題未來再做。

## 10. 結論
- Phase 4E-13D 建議先走「穩定擴充」路線。  
- 短期以策略 A 擴充 int-answer 題型最合適。  
- `binomial_expansion_basic` 仍應暫緩，不建議立即接入。  
- Phase 4E-13E 可先做 3 個 int-answer 候選題型。  
- 完整展開 free-response 與 normalization 留待後續階段。  
