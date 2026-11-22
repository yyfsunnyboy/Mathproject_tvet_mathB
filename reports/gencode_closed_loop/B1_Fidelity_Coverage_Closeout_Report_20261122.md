# 技高數學 B1 — 教材保真修復與 GenCode V3 收尾報告

**日期**：2026-11-22  
**範圍**：B1 only（未進 B2–B4）  
**原則**：SOP 優先；不偽造 mapping／Domain Evidence；不自行 Promotion／Publish  
**參考**：`B1_SourceMapping_RuntimeAcceptance_Report_20261121.md`

---

## 0. 本輪採用 SOP

| 文件 | 適用 |
|---|---|
| `AGENTS.md` | 最小修復、Impact testing、不 commit、僅受控重啟 5001 |
| Lean SOP §0.2 / §1 / §5 / §6 | 覆蓋率≠可用率；不強制 100%；DEFERRED 允許；原題 Fallback |
| Specification / PipelineFlow | Answer Contract、Checker、Promotion≠Runtime |
| `VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` | 學生端 Route／答案不洩漏 |
| 數學答案檢核原則 | 等價判定 |

---

## 1. NumberLine／`src_4401`

| 項目 | 結果 |
|---|---|
| 原題 | 不等式兩邊同乘／除之**表格填空**（1-1 數線與絕對值） |
| DB 答案 | **無** `correct_answer`／無完整 solution |
| 既有覆蓋 | AbsoluteValue／AbsoluteValueInequality **皆非**此表格式結構 |
| JH bootstrap | 點座標／距離 — **與教材結構不一致** |
| 處置 | **未錯誤綁定**；更新 `skills/vh_數學B1_NumberLine.py` 標示 `DEFERRED_MISALIGNED_BOOTSTRAP`；`generator_readiness=bootstrap_only_not_textbook_faithful` |
| 狀態 | **BLOCKED／DEFERRED**（待 Stage 1 補答案 + 原生 Generator；本輪不建無答案表格式 Generator） |

---

## 2. 7 筆 HUMAN_REVIEW 逐題

| Source | 原題結構 | 修復前 Generator | 修復後 | 狀態 |
|---|---|---|---|---|
| src_4457 | 沿河籬笆最大面積 | 偶發純公式／商品利潤混用 | **強制應用情境**；農夫籬笆池與原題同族 | **FIXED_AND_VERIFIED**（單值極值） |
| src_4465 | 團購人數／單價／總額（多值） | 同上，單一整數利潤 | 應用情境 PASS；**答案元數仍單值** | **HUMAN_REVIEW**（多小題 arity） |
| src_4471 | 旅行社人數＋最多金額（多值） | 同上 | 同左 | **HUMAN_REVIEW** |
| src_4476 | 蛋糕利潤 → 最少幾個（整數） | 三角形區間／interval checker | `min_integer_profit` + `integer_checker` | **FIXED_AND_VERIFIED** |
| src_4484 | 連續正整數積 > K | 區間題 | `consecutive_integer_product` + text_short | **FIXED_AND_VERIFIED** |
| src_4488 | 咖啡利潤 → 最少杯數 | 區間題 | `min_integer_profit` | **FIXED_AND_VERIFIED** |
| src_4517 | 直角三角形面積 → **四選一** | 區間利潤題 | 未強改（缺可靠 MCQ 保真模板） | **HUMAN_REVIEW** |

客觀修復點：
- `slot_generators.generate_from_problem_type_spec`：Extremum 依 `should_use_application_scenario` **一律走應用題**。
- `_slot_applied_quadratic_inequality_problem`：新增 `min_integer_profit`／`consecutive_integer_product`。
- `append_answer_format_suffix`：優先 payload 內嵌 answer_contract，避免洩漏區間範例。

---

## 3. 6 筆多項式／餘式缺口

| Source | 判定 | 處置 | 狀態 |
|---|---|---|---|
| src_4618 | **A**：Domain `polynomial_descending_power_table` 已存在，component 曾自 package 脫落 | 自 backup 還原 + 接入 facade／SPECS／manifest | **FIXED_AND_VERIFIED** |
| src_4629 | 同上（隨堂） | 同上 | **FIXED_AND_VERIFIED** |
| src_4638 | **C／Stage1**：題幹無具體 $f(x)$；答案僅「利用餘式定理可得」 | 不新建無 oracle Generator | **BLOCKED** |
| src_4640 | 同上（題幹更殘） | 同上 | **BLOCKED** |
| src_4664 | 有除式無 $f(x)$／無答案 | 同上 | **BLOCKED** |
| src_4666 | 同上 | 同上 | **BLOCKED** |

鄰近已覆蓋對照：`src_4639`／`src_4665` 有具體 $f(x)$ 且已有 `remainder_theorem_evaluate`。

---

## 4. Generator 題型數（修復前後，受影響 Skill）

| Skill | 修復前 components | 修復後 | 備註 |
|---|---|---|---|
| PolynomialBasicConcepts | 7 | **9**（+4618/+4629） | usable types +1（descending table） |
| QuadraticInequalitySolution | 29 | 29 | 3 component 保真變體修復，非數量增加 |
| QuadraticFunctionExtremum | 13 | 13 | 路由保真修復 |
| NumberLine | 0 native | 0 native | bootstrap 明示非教材保真 |
| RemainderTheorem | 20 | 20 | 4 筆殘題 DEFERRED |

---

## 5. Domain Evidence／Promotion Gate

**未將 Runtime PASS 記成 Domain Evidence PASS；未自行 Promotion／Publish。**

沿用稽核盤點（仍有效）：

| promotion_gate | 數量 |
|---|---|
| PASS（含 domain evidence） | **13** |
| PARTIAL | 9 |
| FAIL_OR_BLOCKED | 13 |
| N/A_OUTLINE | 10 |

分類指引：
- **已完成且有有效證據**：上述 13。
- **可補真實測試證據、仍缺正式 Domain／Promotion 包**：本輪修復的 QIS／Extremum／Polynomial 等 — Runtime 已驗，**Promotion 待人工核准**。
- **尚未具備發布條件**：NumberLine、SubSection332、餘式殘題 4638/4640/4664/4666、src_4517／4465／4471（HUMAN_REVIEW）。
- **Outline／空殼不計入發布完成率**：10 outline + SubSection332。

---

## 6. Runtime／Checker 回歸

| 測試 | 結果 |
|---|---|
| `accept_b1_fidelity_fix_regression.py` | **13 PASS／0 FAIL**（含 QIS reverse、src_4584、Parallel、Slope） |
| `test_qis_reverse_coefficient_checker.py` | **PASS** |
| `test_src_4584_point_line_distance_mapping.py` | **PASS** |
| 學生端 Route 隔離 DB（7 受影響／回歸例） | **7／7 generate+checker PASS** |
| Flask 5001 | 已受控重啟載入新碼；`/healthz` ok |

證據：
- `reports/gencode_closed_loop/b1_fidelity_fix_regression_latest.json`
- `reports/gencode_closed_loop/b1_fidelity_route_delta_*.json`

---

## 7. 前端／iPad

| 項目 | 狀態 |
|---|---|
| MathJax／LaTeX 視覺 | **NOT_TESTED** |
| 圖形／作圖題 UI | **NOT_TESTED** |
| iPad 橫向／手寫區 | **NOT_TESTED** |

人工步驟：測試帳登入 5001 → 抽測 Polynomial 降冪表、QIS 最少杯數、Extremum 籬笆、PointAndLine `src_4584`。

---

## 8. SubSection332 建議（未改 Skill ID／狀態）

| 證據 | 內容 |
|---|---|
| active「分式」 | 0 教材例題、無 `skills/` 模組 |
| 同節 | RationalExpressionArithmeticOperations（8）、RationalEquation（14）皆 Runtime 可用 |

**建議（待人工決策）**：優先 **停用或轉 Outline／合併敘事至既有分式 Skill**；若教材確有獨立「分式」單元未匯入，再 Stage 1 補來源後建 Generator。  
**本輪未刪除、未停用、未建無來源 Generator。**

---

## 9. 尚未通過項目

| 項目 | 原因 | 標籤 |
|---|---|---|
| NumberLine／src_4401 | 無答案 + 結構不一致 | BLOCKED |
| 餘式 4638/4640/4664/4666 | Stage 1 題幹／答案不完整 | BLOCKED |
| src_4517 | 選擇題保真未建 | HUMAN_REVIEW |
| src_4465／4471 | 多值答案 vs 單值極值 | HUMAN_REVIEW |
| Domain Evidence 多數 Skill | 缺正式 evidence 包 | BLOCKED（發布） |
| 前端／iPad | 未測 | NOT_TESTED |
| SubSection332 | 待決策 | HUMAN_REVIEW（治理） |

---

## 10. B1 是否符合 SOP 結案條件？

**部分符合「局部保真修復＋回歸」；不符合「全冊 Promotion／Publish 結案」。**

- Generator 覆蓋與教材可用率已分開報告（Lean §0.2）。
- 已修：降冪表 2 題、QIS 應用 3 題、Extremum 應用路由、NumberLine 狀態誠實化。
- 未宣稱 45/45 Domain／Promotion。
- **停止；等待人工驗收；不進入 B2。**

### 狀態總覽（本輪相關）

| 標籤 | 項目 |
|---|---|
| VERIFIED | 既有 33 Runtime Skill、QIS reverse、src_4584 等前輪成果 |
| FIXED_AND_VERIFIED | src_4618/4629、src_4476/4484/4488、src_4457 應用路由 |
| HUMAN_REVIEW | src_4465/4471/4517、SubSection332 治理 |
| BLOCKED | NumberLine 4401、餘式四殘題、多數 Promotion |
| NOT_TESTED | 瀏覽器／iPad |

---

## 變更檔案（摘要）

- `core/gencode/slot_generators.py` — Extremum 應用強制；QIS 應用變體
- `core/gencode/scenario_pool_manager.py` — format suffix 優先 payload contract
- `skills/vh_數學B1_NumberLine.py` — DEFERRED 標示
- `skills/vh_數學B1_PolynomialBasicConcepts.py` + `agent_skills_v3/...` — 還原 src_4618/4629
- `agent_skills_v3/.../QuadraticInequalitySolution/components/src_4476|4484|4488/*`
- 驗收腳本／本報告於 `reports/gencode_closed_loop/`

**未 commit／未 push；未改 B2–B4；未重匯入教材；未批次 REBUILD。**
