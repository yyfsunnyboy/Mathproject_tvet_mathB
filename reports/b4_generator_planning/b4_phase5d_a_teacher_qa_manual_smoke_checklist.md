# Phase 5D-A：B4 Chapter 1 Teacher QA Manual Smoke Checklist

## 1. 測試目的

說明本階段不是新增功能，而是教師手動檢查 Phase 5C 收斂後的 B4 Chapter 1 單元練習是否可進入小規模 pilot。

## 2. 測試前準備

- 確認 Flask server 已啟動。
- 確認資料庫為目前測試用 DB。
- 建議使用 Chrome。
- 開啟 DevTools：
  - Console
  - Network
- 建議使用無痕視窗或清除舊 session，避免舊狀態干擾。
- 若前端有快取問題，使用 Ctrl + F5。

## 3. 測試入口

Dashboard：

http://127.0.0.1:5000/dashboard?view=curriculum&curriculum=vocational&volume=數學B4

操作：

1. 進入上述 dashboard。
2. 找到「1 排列組合」。
3. 點「單元練習」。
4. 確認網址應包含：

`/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&learning_mode=teaching&practice_kind=unit_practice`

## 4. 基本流程 smoke

- [ ] 頁面可正常載入。
- [ ] 顯示 B4 Chapter 1 單元練習語意，而不是診斷結束語意。
- [ ] 按「開始診斷」或目前前端按鈕後，可載入第一題。
- [ ] Network 中 `/api/adaptive/submit_and_get_next` 回傳 200。
- [ ] 題目區顯示題幹、選項或輸入框。
- [ ] 送出答案後可取得下一題。
- [ ] 可連續作答超過 5 題。
- [ ] 不會出現「你已完成本單元自適應診斷。」這類診斷停止訊息。
- [ ] 後端 log 無 400 / 404 / 500。
- [ ] Console 無明顯 JavaScript error。

## 5. 題型覆蓋 smoke

### 5.1 基礎排列組合題型

- [ ] 加法原理互斥分類。
- [ ] 乘法原理多階段選擇。
- [ ] 正因數個數。
- [ ] 階乘計算。
- [ ] 階乘方程變形。
- [ ] 相異物排列。
- [ ] 角色分派。
- [ ] 相鄰排列。
- [ ] 不相鄰排列。
- [ ] 重複排列。
- [ ] 不盡相異物排列。
- [ ] 組合定義。
- [ ] 組合應用。
- [ ] 組合性質。

### 5.2 Phase 5C 新增／補強題型

請列為重點觀察：

- [ ] `binomial_two_variable_specific_coefficient`
  - 例如 $(2x-3y)^4$ 中 $x^2y^2$ 項係數。
- [ ] `binomial_laurent_specific_power_coefficient`
  - 例如 $\left(x-\frac{3}{x}\right)^6$ 中 $x^4$ 項係數。
- [ ] `grid_shortest_path_count`
  - 任意走／經過指定點／不經過指定點。
- [ ] `permutation_non_adjacent_arrangement`
  - 插空法，不相鄰排列。
- [ ] `factorial_equation_solve_n` 新 variants
  - $a! \times n=b!$
  - $b!+a!=n\times a!$
  - $b!=n\times a!$
- [ ] `combination_hockey_stick_sum`
  - 標準 hockey-stick 組合數和。
- [ ] small template enrichment 題幹語境有變化，不是一直同一題。

> 手動 smoke 不要求一次測到所有題型；若 20–30 題仍完全看不到 Phase 5C 題型，需記錄為 exposure concern。

## 6. 錯題補救 smoke

操作步驟：

1. 從單元練習開始。
2. 故意連續答錯 2～3 題，例如輸入 `999`。
3. 觀察畫面與 Network response。
4. 確認是否進入補救模式。

Checklist：

- [ ] 連續錯誤後，系統沒有當機。
- [ ] Network 仍回 200。
- [ ] UI 顯示進入補救或類似狀態。
- [ ] Response 或畫面中可觀察：
  - `in_remediation`
  - `remediation_skill`
  - `remediation_subskill`
  - `route_action`
  - `ppo_action`
- [ ] 題目難度或 skill 有退回較基礎 B4 skill 的跡象。
- [ ] 補救題仍為 B4 allowlisted deterministic 題型。
- [ ] 不會跳出 manual_review / excluded 題型。
- [ ] 補救過程中仍可繼續作答。

> 目前補救是 B4-to-B4 coarse bridge，不要求精準到完整子技能 ontology。若補救方向不夠精準，記錄為 calibration issue，不一定視為 blocking bug。

## 7. 補救後回主線 smoke

操作步驟：

1. 進入補救後，嘗試答對 1～3 題。
2. 觀察是否有返回主線或切回較主要 skill 的跡象。

Checklist：

- [ ] 補救題答對後流程可繼續。
- [ ] 不會卡在同一題。
- [ ] 不會無限補救。
- [ ] 若有 return_to_mainline / hasReturnedToMain / returnReady 等狀態，需記錄。
- [ ] 若目前尚未明確回主線，也需記錄為 known limitation。

## 8. 不應出現的題型

不應在 current deterministic unit practice 中出現：

- [ ] 不出現 `tree_diagram_listing`
- [ ] 不出現 `binomial_expansion_basic`
- [ ] 不出現 `pascal_triangle_derivation`

> 若出現任何一項，應判定為 No-Go。

## 9. Network / Response 檢查項目

每次 `/api/adaptive/submit_and_get_next` response 建議記錄：

- HTTP status
- `skill_id`
- `problem_type_id`
- `generator_key`
- `router_trace`
- `source_type`
- `adaptive_audit`
- `in_remediation`
- `remediation_skill`
- `route_action`
- `ppo_action`
- `correct_answer` 是否只在安全／開發模式下出現

若出現 400，請記錄 response JSON：
- `error`
- `missing_fields`
- `received_keys`
- `internal_exception_type`
- `internal_exception_message`

## 10. 手動觀察紀錄表

| 題號 | skill_id | problem_type_id | 題型簡述 | 是否 Phase 5C 新題型 | 作答結果 | 是否進補救 | 補救 skill | 教師觀察 | 問題等級 |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

問題等級建議：
- OK：正常
- Minor：題幹語氣或曝光問題
- Major：影響學生理解或流程
- Blocking：無法繼續使用、500/400、錯誤答案、excluded 題型出現

## 11. Go / No-Go 準則

### Go 條件

可進入小規模學生 pilot 若：

- [ ] 入口正常。
- [ ] 第一題可載入。
- [ ] 可連續練習超過 5 題。
- [ ] 送答案與下一題流程穩定。
- [ ] 沒有 400 / 500。
- [ ] excluded 題型未出現。
- [ ] Phase 5C 新題型至少部分可見。
- [ ] 連錯後可進入補救或至少不崩潰。
- [ ] 教師認為題型覆蓋足以代表 B4 Chapter 1 第一輪 pilot。

### No-Go 條件

不得進入學生 pilot 若：

- [ ] 單元練習無法進入。
- [ ] 第一題無法載入。
- [ ] 送答案後 400 / 500。
- [ ] 連續 5 題後仍錯誤進入 diagnostic stop。
- [ ] excluded 題型出現。
- [ ] correct_answer 錯誤。
- [ ] 大量題目無法作答或格式錯亂。
- [ ] 補救流程導致卡死。
- [ ] 教師認為題型覆蓋不足以給學生使用。

## 12. Known limitations

目前已知限制：

- 補救目前是 coarse B4-to-B4 bridge，尚不是完整 B4 YAML subskill ontology。
- 完整二項式展開仍未接入 current deterministic runtime。
- 樹狀圖與巴斯卡推導仍為 manual_review / future AI-judged。
- 組合數總和與奇偶項係數和可能仍需要 wording / exposure calibration。
- 手動 smoke 不等於正式學生學習成效驗證。
- Phase 5C 題型已支援，但實際出現率仍需教師觀察。

## 13. 建議測試紀錄格式

### 測試資訊

- 測試日期：
- 測試者：
- 瀏覽器：
- 測試帳號：
- Git commit / 版本：
- Flask 啟動模式：
- DB 檔案：
- 是否開 DevTools：

### 測試結果摘要

- 基本流程：
- 題型覆蓋：
- 補救流程：
- 回主線：
- excluded 題型：
- 主要問題：
- Go / No-Go：

### 後續處理建議

- 必修：
- 可延後：
- 不處理：
