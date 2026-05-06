# Phase 5B Smoke Test - Remediation Backtracking Manual Observation

## 1. 測試入口

- URL: `/dashboard?view=curriculum&curriculum=vocational&volume=數學B4`
- 路徑：進入 B4 Chapter 1 單元練習。

## 2. 測試結果摘要

目前進入 B4 Chapter 1 單元練習後，若連續答錯，系統已經可以成功觸發並進入補救教學流程。然而，觀察到目前的補救目標對應有時不夠精準，主要原因是目前使用的是粗粒度（coarse）的 B4-to-B4 remediation bridge，尚未實作完整的 B4 Chapter 1 subskill ontology。

## 3. 已通過項目

- [x] **chapter entry 成功**：可順利從章節入口進入單元練習。
- [x] **第一題載入成功**：系統能正常派發第一題。
- [x] **可連續練習**：題目能順利連續派發。
- [x] **不會 5 題診斷自停**：已正確分離模式，不會在 5 題後診斷提早結束。
- [x] **連錯後會進補救**：連續答錯後能正確路由至補救教學階段。

## 4. 觀察到的限制

- **補救目標仍不夠精準**：派發的補救題目與原錯題的知識點關聯度偶有落差。
- **目前 bridge 是 B4-to-B4 coarse mapping**：僅依賴粗粒度的橋接對應進行派題。
- **尚未建立 B4 YAML subskill ontology**：缺少完整的子技能樹來支撐精確的診斷與回溯。

## 5. 建議

- **不視為 blocking bug**：目前的行為在流程架構上已跑通，不阻礙整體測試的推進。
- **先做 Phase 5B-Fix-E1.1 bridge mapping calibration**：短期內先著重校準現有的 coarse mapping，以改善補救準確度。
- **後續 Phase 5B-Fix-E2 才設計完整 B4 子技能樹**：留待後續階段再建置完整的 YAML 子技能樹，從根本解決補救精準度問題。

## 6. 手動觀察表

| 原題 skill | 原題 problem_type | 系統補救 skill | 教師判斷應補救 skill | 評估 (合理 / 太前面 / 方向錯誤) | 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
