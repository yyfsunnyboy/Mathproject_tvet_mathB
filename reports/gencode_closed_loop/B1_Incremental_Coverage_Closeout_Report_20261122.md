# 技高數學 B1 — 剩餘教材覆蓋缺口增量收尾報告

**日期**：2026-11-22  
**範圍**：B1 only（未進 B2–B4）  
**原則**：SOP 優先；消除真實覆蓋缺口；不偽造 Domain Evidence／Promotion；不重做已驗收項  
**基準報告**：
- `B1_SourceMapping_RuntimeAcceptance_Report_20261121.md`
- `B1_Fidelity_Coverage_Closeout_Report_20261122.md`

---

## 0. 本輪採用 SOP／契約

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | 最小修復、Impact testing、不 commit、5001 僅必要時重啟 |
| Lean SOP §0.2 | 覆蓋≠可用率；不強制 100%；Generator 優先＋原題 Fallback |
| Specification／PipelineFlow | Answer Contract、Checker、Promotion≠Runtime |
| `VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` | 學生端作答契約 |
| 數學答案檢核原則 | 等價判定 |

---

## 1. DB 集合核對

| 項目 | 結果 |
|---|---|
| 正式 DB B1 `textbook_examples` | **321** |
| 前次稽核集合 | **321** |
| 結論 | 同一集合；本輪採增量檢查，未重跑全冊靜態掃描 |

前次 mapping：`314 PASS / 7 WARN`；前次 fidelity HUMAN_REVIEW：7 筆。

---

## 2. 六筆多項式／餘式缺口

| Source | 判定 | 修復前 | 修復後 | 狀態 |
|---|---|---|---|---|
| src_4618 | A（映射／component 脫落，Domain 已有） | WARN | 降冪表 Generator 可出＋Checker PASS | **COVERED_VERIFIED** |
| src_4629 | A | WARN | 同上 | **COVERED_VERIFIED** |
| src_4638 | C → 新建獨立題型 | 無 component | `remainder_theorem_state_symbolic`（答案 `f(c)`） | **COVERED_VERIFIED** |
| src_4640 | C（題幹無除式清單；採同結構變體） | 無 | 同上（seed 產生兩線性除式） | **COVERED_VERIFIED**（結構覆蓋；Stage1 原題殘缺已註記） |
| src_4664 | C | 無 | 固定根 5/−6 → `f(5)`；`f(-6)` | **COVERED_VERIFIED** |
| src_4666 | C（同 4640） | 無 | 符號餘式陳述 | **COVERED_VERIFIED** |

說明：
- 不得與 `remainder_theorem_evaluate`（具體 $f(x)$ 求值）混題型；本輪新增 **`remainder_theorem_state_symbolic`**。
- 4640／4666 教材題幹殘缺，Generator 產生「同數學結構」變化題，並保留 Source Evidence 指向原 ID。

---

## 3. 七筆 HUMAN_REVIEW 逐題證據

| Source | 原題結構 | 現 Generator 代表題 | 結構對照 | 處置 | 狀態 |
|---|---|---|---|---|---|
| src_4457 | 沿河籬笆最大面積（單值） | 農夫籬笆 $L$ 參數化（強制 `farmer_fence`） | 同族二次極值面積 | 強制情境變體 | **COVERED_VERIFIED** |
| src_4465 | 團購：增加人數／單價／總額 | multi_part 三欄（例：5；7000；245000） | 同模型 $y=(P-dx)(N+x)$ | 新增多小題情境 | **COVERED_VERIFIED** |
| src_4471 | 旅行社：人數＋最多金額 | multi_part 兩欄（例：5；62500） | 同上 | 新增多小題情境 | **COVERED_VERIFIED** |
| src_4476 | 蛋糕利潤→最少整數 | `min_integer_profit` + integer_checker | 同結構 | 前輪已修；本輪回歸 PASS | **COVERED_VERIFIED** |
| src_4484 | 連續正整數積 | `consecutive_integer_product` | 同結構 | 前輪已修；回歸 PASS | **COVERED_VERIFIED** |
| src_4488 | 咖啡利潤→最少杯數 | `min_integer_profit` | 同結構 | 前輪已修；回歸 PASS | **COVERED_VERIFIED** |
| src_4517 | 直角三角形面積→四選一 | `right_triangle_area_mcq` + choice_label | 同族 MCQ | 本輪新建 MCQ 變體 | **COVERED_VERIFIED** |

---

## 4. NumberLine／`src_4401`

| 項目 | 結果 |
|---|---|
| 原題 | 不等式兩邊同乘／除之 12 格表格 |
| 既有 JH bootstrap | 點座標／距離 — **不得**標為 B1 原生 PASS |
| 本輪 | 新增原生 `inequality_operation_table`（決定性 oracle，不依賴 DB `correct_answer`） |
| Runtime | generate 12 cells；正解 PASS／錯答 FAIL |
| `skills_info.is_active` | 需人工確認是否對學生端開放（本輪**未改 DB**） |
| 狀態 | **COVERED_VERIFIED**（原生 Generator）；瀏覽器 UI **NOT_TESTED** |

JH bootstrap 僅在顯式 `bootstrap=True` 時可用，並標 `DEFERRED_MISALIGNED_BOOTSTRAP`。

---

## 5. B1 教材例題覆蓋率（增量口徑）

基準 321 筆；本輪把前次 **7 WARN + 7 HUMAN_REVIEW** 全部推進至可驗證 Generator 覆蓋。

| 口徑 | 數量 | 說明 |
|---|---|---|
| 教材例題總數 | 321 | DB 核對一致 |
| 前次 mapping PASS | 314 | 沿用有效證據 |
| 本輪新修／確認 | 14 | 6 多項式／餘式 + 7 HR + NumberLine（4401 計入 WARN） |
| 估計 mapping／結構覆蓋 | **321／321** | 皆有對應 component／原生 Generator |
| Runtime＋Checker 本輪抽驗 | **見 §8** | 非全冊 seed sweep |
| Domain Evidence／Promotion | **仍 13／45** | 見 §6；**不可**與 Runtime PASS 混報 |

> 相同 `problem_type` 可共用 Generator；上表是「來源可追溯至正確題型」，不是「321 個獨立 Generator 檔」。

---

## 6. Domain Evidence／Promotion Gate（真實狀態）

**未偽造 Evidence、未自行 Promotion／Publish。**

沿用前次稽核（仍有效）：

| promotion_gate | 數量 |
|---|---|
| PASS（含 domain evidence） | **13** |
| PARTIAL | 9 |
| FAIL_OR_BLOCKED | 13 |
| N/A_OUTLINE | 10 |

分層：
- **Runtime PASS ≠ Domain Evidence PASS ≠ Promotion PASS**。
- 本輪修復的 Remainder／NumberLine／Extremum multi／QIS MCQ：僅達 **Runtime／Checker 驗證**；正式 Domain Evidence 包與 Promotion **待人工授權**。
- Outline／空殼不計入發布完成率。

---

## 7. SubSection332 建議（未改 Skill ID）

| 證據 | 內容 |
|---|---|
| `skills_info` | `vh_數學B1_SubSection332`／中文「分式」／`is_active=1` |
| 教材例題 | **0** |
| skill 模組 | **不存在** |
| 同節 | RationalExpressionArithmeticOperations（8）、RationalEquation（14）皆有例題與 Runtime |

**建議（待人工決策，本輪未執行）**：
1. **優先停用或轉 Outline**（避免 active 空殼誤導 inventory）；或  
2. **敘事合併**至既有分式運算／分式方程 Skill；或  
3. 若 Stage 1 確認另有獨立「分式」來源 → 正式補匯入後再建 Generator。

**本輪未刪除、未改 Skill ID、未建無來源 Generator。**

---

## 8. Runtime／Checker 回歸

| 測試 | 結果 |
|---|---|
| `scripts/_tmp_b1_closeout_verify.py` | **19／19 PASS** |
| `scripts/accept_b1_fidelity_fix_regression.py` | **13／13 PASS**（含 4457 農夫、4465／4471 multi、4517 MCQ、4618／4629、4584、平行線距離、QIS） |
| PointSlopeForm `src_4542` 垂直平分線 | 回歸 PASS（**未改 Generator**；沿用使用者已確認行為） |
| Flask 5001 | 本輪**未重啟**；載入新碼需受控重啟後學生端才看得到新題型 |

證據：
- `reports/gencode_closed_loop/b1_incremental_closeout_verify_20261122.json`
- `reports/gencode_closed_loop/b1_fidelity_fix_regression_*.json`

---

## 9. 各 Skill 可用 Generator 題型數（修復前後）

| Skill | 修復前 components | 修復後 | unique problem_type | 備註 |
|---|---|---|---|---|
| PolynomialBasicConcepts | 9 | 9 | 5 | 4618／4629 已在前輪接入；本輪再驗 |
| RemainderTheorem | 20 | **24**（+4638／4640／4664／4666） | **2**（+symbolic） | 新題型非假合併 evaluate |
| NumberLine | 0 native | **1** native | 1 | bootstrap 非預設 |
| QuadraticFunctionExtremum | 13 | 13 | 3 | 4465／4471／4457 變體保真 |
| QuadraticInequalitySolution | 29 | 29 | 5 | 4517→MCQ；4476／4484／4488 維持 |

---

## 10. 前端／iPad（尚未測試）

| 項目 | 狀態 |
|---|---|
| MathJax／LaTeX 視覺 | **NOT_TESTED** |
| 多小題 UI（4465／4471／餘式符號／NumberLine 12 格） | **NOT_TESTED** |
| 選擇題 UI（4517） | **NOT_TESTED** |
| iPad 橫向／手寫 | **NOT_TESTED** |
| NumberLine 學生端是否 active | **待人工確認 DB／路由** |

建議人工抽測（重啟 5001 後）：NumberLine 表格、餘式符號 `f(c)`、團購三欄、直角三角形 MCQ、PointSlopeForm 垂直平分線（確認未回歸）。

---

## 11. Blocker／下一步／B1 結案條件

### 仍未解決
| 項目 | 標籤 |
|---|---|
| Domain Evidence／Promotion 多數 Skill 仍缺正式包 | **BLOCKED（發布）** |
| SubSection332 空殼治理 | **HUMAN_REVIEW（治理）** |
| 前端／iPad／多小題 UI | **NOT_TESTED** |
| NumberLine 是否對學生開啟 | **待人工** |
| 受控重啟 Flask 5001 以載入本輪新碼 | **待人工授權執行** |

### 本輪已消除的真實缺口
- 餘式四筆缺 component  
- NumberLine 結構不一致（改為原生表格式）  
- Extremum 多小題 arity  
- QIS 4517 MCQ  

### B1 結案條件？
- **教材例題 Generator 結構覆蓋（增量）**：已達可驗收狀態。  
- **全冊 Promotion／Publish 結案**：**尚未**（Domain Evidence 仍 13／45）。  
- **停止；等待人工驗收；不進入 B2。**

---

## 變更檔案（摘要）

- `core/gencode/remainder_theorem_symbolic.py`（新）
- `core/gencode/numberline_inequality_table.py`（新）
- `core/gencode/scenario_pool_manager.py` — 團購／旅行社 multi_part 情境
- `core/gencode/slot_generators.py` — Extremum preferred_scenario；QIS 直角三角形 MCQ；multi_part 驗證契約
- `skills/vh_數學B1_NumberLine.py` — 原生表格式為預設
- `skills/vh_數學B1_RemainderTheorem.py` + `agent_skills_v3/vh_數學B1_RemainderTheorem/*` — +4 components
- Extremum `src_4457/4465/4471`、QIS `src_4517` generate 變體
- Facade SPECS 同步（Extremum／QIS／Remainder）

**未 commit／未 push；未改 B2–B4；未重匯入教材；未批次 REBUILD；未改 Flask 5000／Cloudflare；未改 Skill ID。**
