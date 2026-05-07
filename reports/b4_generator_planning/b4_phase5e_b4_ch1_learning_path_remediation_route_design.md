# Phase 5E：B4 Chapter 1 Learning Path & Remediation Route Design

## 1. 設計目的

- Phase 5C 已解決「能否出題、題型是否足夠」的 runtime 可用性問題。
- Phase 5D-A 教師手動 smoke 顯示目前仍缺少教學順序與補救路線設計。
- Phase 5E 目標是把 B4 Chapter 1 從「可用的隨機式單元練習」整理為「符合課本進度的學習路徑」。
- 本階段僅產出設計文件，不直接修改程式與執行邏輯。

## 2. 現況摘要

已完成狀態：

- 章節入口可用。
- B4 Chapter 1 deterministic allowlist 已收斂為 13 個 runtime-ready skill。
- generator-first / synthetic catalog 路徑可穩定出題。
- D1-Fix 後新題型可曝光。
- B4-to-B4 remediation bridge 可啟動。
- 補救後可觀察到 `return_to_mainline` / `return` action。

目前限制：

- 出題順序仍偏抽樣，不是課本 progression。
- B4 synthetic families 目前是暫時 catalog 容器，不是正式知識圖譜。
- 補救邏輯仍是 coarse bridge。
- B4 YAML subskill ontology 尚未建立完成。
- adaptive core 仍透過 legacy agent skill 外殼（`selected_agent_skill=polynomial_arithmetic`）運作。

## 3. B4 Chapter 1 建議課本進度順序

以下為第一版 teacher-designed progression（可後續微調）：

1. `vh_數學B4_AdditionPrinciple`
- 加法原理
2. `vh_數學B4_MultiplicationPrinciple`
- 乘法原理
- 正因數個數
3. `vh_數學B4_FactorialNotation`
- 階乘記號
- 階乘方程
4. `vh_數學B4_PermutationOfDistinctObjects`
- 相異物排列
- 角色分派
- 相鄰／不相鄰
5. `vh_數學B4_RepeatedPermutation`
- 重複選取／重複排列
6. `vh_數學B4_PermutationWithRepetition`
- 重複排列應用
7. `vh_數學B4_PermutationOfNonDistinctObjects`
- 不盡相異物排列
8. `vh_數學B4_CombinationDefinition`
- 組合定義
9. `vh_數學B4_Combination`
- 基本組合選取
10. `vh_數學B4_CombinationProperties`
- 組合性質
11. `vh_數學B4_CombinationApplications`
- 組合應用
- 棋盤路徑
12. `vh_數學B4_BinomialCoefficientIdentities`
- 組合數恒等式
- 純組合數和
- hockey-stick
13. `vh_數學B4_BinomialTheorem`
- 二項式定理
- 指定項係數
- 二變數／Laurent 型指定係數

補充原則：

- 此順序是第一版教師設計進度，不等於最終 adaptive mastery order。
- 初期教學模式建議先靠近課本順序，再逐步提高 adaptive 混合比例。

## 4. 建議的 chapter unit practice 模式分層

### Mode A：Guided Progression / 課本順序模式

適用：

- 第一次進入單元
- 教師指定單元練習
- 學生尚未有足夠作答紀錄

特徵：

- 前 5～10 題優先依課本順序。
- 避免首題即跳到二項式或棋盤路徑。
- 每個 skill 先出 1～2 題。
- 答對穩定後再推進下一個 skill。

### Mode B：Adaptive Mixed Practice / 自適應混合練習

適用：

- 學生已有部分作答紀錄
- 章節複習情境

特徵：

- 依錯題與掌握度混合抽題。
- 可跨 skill 回補。
- 題型分布可包含 Phase 5C 新題型。

### Mode C：Remediation Focus / 補救模式

適用：

- 連錯
- 某 family 掌握度偏低
- 教師指定補救

特徵：

- 依 remediation map 退回前置 skill。
- 補救成功後回原主線或鄰近主線 skill。
- 避免完全 random 跳到不相關 skill。

## 5. B4-to-B4 remediation map 初稿

| current_skill | 常見錯誤或卡點 | recommended_remediation_skill | remediation_reason | return_condition | risk_note |
|---|---|---|---|---|---|
| `vh_數學B4_AdditionPrinciple` | 類別互斥判斷錯誤 | `vh_數學B4_AdditionPrinciple` | 本章起點，先在同 skill 穩定基本判斷 | 補救連對 2 題或 mastery>=0.75 且最近一題正確 | 若題幹語意歧義，可能誤判為乘法情境 |
| `vh_數學B4_MultiplicationPrinciple` | 多階段選擇拆解錯誤 | `vh_數學B4_AdditionPrinciple` | 先釐清加法/乘法情境分界 | 同上 | 過度回退會拖慢教學節奏 |
| `vh_數學B4_MultiplicationPrinciple` | 正因數個數計算卡住 | `vh_數學B4_MultiplicationPrinciple` | 同 skill 內加強質因數分解與指數乘法規則 | 同上 | 不建議誤退到 `FactorialNotation` |
| `vh_數學B4_FactorialNotation` | 階乘展開與約分錯誤 | `vh_數學B4_MultiplicationPrinciple` | 階乘本質為連乘 | 同上 | 若只回乘法不回階乘題，易失去遷移 |
| `vh_數學B4_PermutationOfDistinctObjects` | 公式代入或角色分派錯誤 | `vh_數學B4_FactorialNotation` | 先穩定排列公式與階乘關係 | 同上 | 需區分計算錯與建模錯 |
| `vh_數學B4_PermutationOfDistinctObjects` | 是否考慮順序混淆 | `vh_數學B4_MultiplicationPrinciple` 或 `vh_數學B4_CombinationDefinition` | 回到順序敏感概念對比 | 同上 | 雙路徑需依題型診斷，避免誤退 |
| `vh_數學B4_RepeatedPermutation` | 重複選取的分步獨立性錯誤 | `vh_數學B4_MultiplicationPrinciple` | 每步獨立選擇是核心 | 同上 | 與不盡相異物題型容易混淆 |
| `vh_數學B4_PermutationWithRepetition` | 重複排列建模錯誤 | `vh_數學B4_RepeatedPermutation` 或 `vh_數學B4_MultiplicationPrinciple` | 先回重複選取基本結構 | 同上 | 與 `RepeatedPermutation` 邊界需清楚 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 分母階乘概念錯 | `vh_數學B4_FactorialNotation` | 先補分母階乘操作 | 同上 | 可能只會機械代公式 |
| `vh_數學B4_PermutationOfNonDistinctObjects` | 不盡相異辨識錯誤 | `vh_數學B4_PermutationOfDistinctObjects` | 先建立相異物基準再引入重複元素 | 同上 | 題幹語意若不明確會持續誤判 |
| `vh_數學B4_CombinationDefinition` | 排列/組合分不清 | `vh_數學B4_PermutationOfDistinctObjects` | 透過對比釐清「是否考慮順序」 | 同上 | 若只講規則不練轉換，回主線仍易錯 |
| `vh_數學B4_CombinationDefinition` | 組合公式代入錯 | `vh_數學B4_FactorialNotation` | 公式底層依賴階乘計算 | 同上 | 單純計算修正不保證概念理解 |
| `vh_數學B4_Combination` | 基本選取數量建模錯 | `vh_數學B4_CombinationDefinition` | 先回定義層 | 同上 | 可能反覆卡在語意轉式子 |
| `vh_數學B4_CombinationProperties` | 性質化簡錯或對稱性誤用 | `vh_數學B4_CombinationDefinition` | 回到定義推導性質 | 同上 | 只記口訣可能再次出錯 |
| `vh_數學B4_CombinationApplications` | 應用建模錯 | `vh_數學B4_CombinationDefinition` | 先回純組合建模基本句型 | 同上 | 文句理解能力差異會影響穩定性 |
| `vh_數學B4_CombinationApplications` | 棋盤路徑卡關 | `vh_數學B4_Combination` 或 `vh_數學B4_CombinationDefinition` | 先回一般選路徑對應組合框架 | 同上 | 需避免直接跳到高抽象恒等式 |
| `vh_數學B4_BinomialCoefficientIdentities` | 組合數和、hockey-stick 推導錯 | `vh_數學B4_CombinationProperties` | 先穩定組合性質再上恒等式 | 同上 | 符號操作易造成假理解 |
| `vh_數學B4_BinomialCoefficientIdentities` | 純組合數符號讀寫錯 | `vh_數學B4_CombinationDefinition` | 先補符號與定義基礎 | 同上 | 過早回高階恆等式會再次失敗 |
| `vh_數學B4_BinomialTheorem` | 指定項係數錯 | `vh_數學B4_BinomialCoefficientIdentities` | 指定項依賴組合係數結構 | 同上 | 若只補計算不補項次判定仍會錯 |
| `vh_數學B4_BinomialTheorem` | 組合係數判讀錯 | `vh_數學B4_CombinationDefinition` | 回組合定義建立係數來源 | 同上 | 回退過多可能中斷二項式語境 |
| `vh_數學B4_BinomialTheorem` | 負號或次方處理錯 | `vh_數學B4_BinomialTheorem`（同 skill 內分層補救） | 多屬同主題內符號與項次訓練 | 同上 | 不建議直接退到跨章四則 |

## 6. Return-to-mainline 初稿

建議粗規則：

- 補救題連續答對 2 題，可嘗試回原 skill。
- 或補救 mastery 達到 0.75 且最近一題答對，可回原 skill。
- 回原 skill 後若再次連錯，回同 remediation skill 或更基礎 skill。
- 補救累計 5 題仍無改善，標記 `teacher_review_needed`。
- 回主線目標限制為：原 skill 或課本順序鄰近 skill，不跳無關 skill。

與現行 log 欄位的對應建議（設計層，不宣稱已實作完）：

- `return_ready=true`：表示達成回主線條件。
- `return_to_mainline` / `return` action：表示已觸發回主線決策。
- `return_target_skill`（建議新增/統一欄位）：顯示回原 skill 或鄰近 skill。

## 7. 出題順序設計建議

### First-entry strategy

學生第一次進 B4 Chapter 1：

1. starter pool 僅允許：
- `AdditionPrinciple`
- `MultiplicationPrinciple`
- `FactorialNotation`
2. 前幾題穩定後再開啟：
- `PermutationOfDistinctObjects`
- `RepeatedPermutation`
3. 中段再開啟：
- `CombinationDefinition`
- `CombinationProperties`
- `CombinationApplications`
4. 後段再開啟：
- `BinomialCoefficientIdentities`
- `BinomialTheorem`

### Mixed review strategy

- 第一輪完成後可開放全部 allowlist。
- 仍保留 weighted sampling：`current/nearby skills` 權重較高，遠端技能較低。

### Remediation strategy

- 進補救時優先依 remediation map。
- 不從全章 random 抽補救題。
- 補救成功後回原 skill 或課本鄰近 skill。

## 8. 與現行 synthetic family 的對照

說明：下表以目前 chapter bootstrap 常態路徑（`unit_skill_ids` 來自 allowlist 字典序）作為現況對照基線，用於設計討論。

| synthetic_family_id | current skill_id | proposed order index | role |
|---|---|---|---|
| `B4C1_SYN_01` | `vh_數學B4_AdditionPrinciple` | 1 | foundation_start |
| `B4C1_SYN_02` | `vh_數學B4_BinomialCoefficientIdentities` | 12 | advanced_binomial |
| `B4C1_SYN_03` | `vh_數學B4_BinomialTheorem` | 13 | advanced_binomial |
| `B4C1_SYN_04` | `vh_數學B4_Combination` | 9 | mid_combination |
| `B4C1_SYN_05` | `vh_數學B4_CombinationApplications` | 11 | mid_application |
| `B4C1_SYN_06` | `vh_數學B4_CombinationDefinition` | 8 | mid_transition |
| `B4C1_SYN_07` | `vh_數學B4_CombinationProperties` | 10 | mid_combination |
| `B4C1_SYN_08` | `vh_數學B4_FactorialNotation` | 3 | foundation |
| `B4C1_SYN_09` | `vh_數學B4_MultiplicationPrinciple` | 2 | foundation |
| `B4C1_SYN_10` | `vh_數學B4_PermutationOfDistinctObjects` | 4 | early_permutation |
| `B4C1_SYN_11` | `vh_數學B4_PermutationOfNonDistinctObjects` | 7 | early_permutation |
| `B4C1_SYN_12` | `vh_數學B4_PermutationWithRepetition` | 6 | early_permutation |
| `B4C1_SYN_13` | `vh_數學B4_RepeatedPermutation` | 5 | early_permutation |

## 9. 實作建議，但本階段不實作

後續可拆分為：

- Phase 5E-A-Fix：加入 chapter progression order 常數。
- Phase 5E-B-Fix：加入 B4 remediation map 常數。
- Phase 5E-C-Fix：chapter unit practice 初期啟用 guided progression。
- Phase 5E-D-Fix：補救完成後 `return_to_mainline` 回原 skill／鄰近 skill。
- Phase 5E-E：後續整合正式 B4 YAML subskill ontology。

## 10. Pilot 建議

判斷：

- 目前可進教師持續 QA。
- 若要給學生使用，建議先由教師監看。
- 不建議直接作為完全無人監督 adaptive pilot。

原因：

- 出題順序尚未完整對齊課本 progression。
- 補救路線尚未完成精準校準。
- B4 YAML 子技能樹尚未完成。

## 11. 停止線

本階段停止線如下：

- 不再補 generator。
- 不再擴展 must-cover 題型。
- 不處理完整二項式展開。
- 不處理樹狀圖與巴斯卡。
- 不建立完整 YAML ontology。
- 僅完成 learning path / remediation route 設計文件。
