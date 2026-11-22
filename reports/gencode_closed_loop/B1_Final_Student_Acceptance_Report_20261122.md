# 技高數學 B1 — 最後學生端驗收報告

**日期**：2026-11-22  
**範圍**：B1 only（未進 B2–B4）  
**依據**：`AGENTS.md`、Lean SOP、Specification、PipelineFlow、Runtime Contract  
**參考**：`B1_Incremental_Coverage_Closeout_Report_20261122.md`

---

## 0. 受控部署

| 項目 | 結果 |
|---|---|
| Git 工作樹 | `main`；有未提交 B1 修復變更（**未 commit／未 push**） |
| 其他 Agent 佔用 5001 | 僅既有本機 Flask 程序；已確認後受控替換 |
| 正式 DB 備份 | `backups/b1_final_accept_pre_flask_restart/kumon_math_20261122_010001.db` |
| SHA-256 | `12f0bc706c37651a7f0d068dfc8fe04998b6655eab85a3008907d36e5d08810b`（備份一致） |
| `PRAGMA integrity_check` | **ok** |
| B1 例題／使用者／attempts | 321／549／3144（歷程保留） |
| 停止舊 5001 | PID **28456**（僅 port 5001；結束碼不視為 Crash） |
| 新 5001 | PID **10040**（shell 父程序 37412）；`--no-reload` |
| `/healthz` | `{"status":"ok","database":"ok","app":"alive"}` |
| Flask 5000 | 仍 Listen（PID 23392）；healthz ok；**未動 Cloudflare** |

---

## 1. 分層驗收總覽（不得混報）

| 層級 | 狀態 | 說明 |
|---|---|---|
| 教材例題覆蓋 | **PASS（沿用增量報告）** | 321 例題皆可追溯正確題型／Generator；本輪未重掃全冊 |
| Generator Runtime | **PASS** | Live HTTP 12／12；學生頁可取得指定 component |
| Checker | **PASS** | 正解 PASS、錯答 REJECT（Route＋瀏覽器抽測） |
| 前端／瀏覽器 | **PASS（抽測）** | 餘式多小題、QIS MCQ、團購三欄、垂直平分線、MathJax |
| 前端／iPad 實機 | **NOT_TESTED** | 無實體 iPad；僅見桌面手寫區存在 |
| Domain Evidence | **13／45 PASS** | 未補造證據 |
| Promotion／Publish | **未達結案發布** | 未自行 Promotion／Publish |

---

## 2. 學生端 Route／瀏覽器結果

證據：`reports/gencode_closed_loop/b1_final_live_http_20261122_010044.json`  
測試帳：`b1_final_accept_20261122_010044`（正式 DB 可追溯；未刪歷程）

### 2.1 Live HTTP（12／12 PASS）

| 項目 | component | generate | structure | 正解 | 錯答 |
|---|---|---|---|---|---|
| remainder symbolic | src_4638／4640／4664／4666 | PASS | PASS | PASS | PASS |
| 農夫籬笆 | src_4457 | PASS | PASS | PASS | PASS |
| 團購多小題 | src_4465 | PASS | PASS | PASS | PASS |
| 旅行社多小題 | src_4471 | PASS | PASS | PASS | PASS |
| 直角三角形 MCQ | src_4517 | PASS | PASS | PASS | PASS |
| QIS reverse | src_4474 | PASS | PASS | PASS | PASS |
| QIS 最少整數 | src_4476 | PASS | PASS | PASS | PASS |
| 垂直平分線 | src_4542 | PASS | PASS | PASS | PASS |
| PointAndLine 回歸 | src_4584 | PASS | PASS | PASS | PASS |

### 2.2 瀏覽器實際頁面（桌面）

| 頁面 | 觀察 | 判定 |
|---|---|---|
| `/practice/...RemainderTheorem?component_id=src_4638` | 題幹 MathJax 正常；(1)(2) 雙欄；手寫區在；填 `f(-1)`／`f(2)` →「答對了」；連續答對 +1 | **PASS** |
| `/practice/...QuadraticInequalitySolution?component_id=src_4517` | A–D 選項＋MathJax；點選 A →「答對了」 | **PASS** |
| `/practice/...QuadraticFunctionExtremum?component_id=src_4465` | 三欄 (1)(2)(3) 多小題 UI；團購題幹可見 | **PASS（UI）**；瀏覽器送出正解未再重複（Route 已驗） |
| `/practice/...PointSlopeForm?component_id=src_4542` | 題幹含「垂直平分線」；MathJax 正常 | **PASS（出現＋渲染）**；未再改 Generator |
| 4457／4471／QIS reverse | Live HTTP 結構與 Checker 已 PASS | 瀏覽器未逐頁重送 → **Route PASS／瀏覽器部分抽測** |
| iPad 橫向／手寫實機 | — | **NOT_TESTED** |

---

## 3. 剩餘治理（僅建議，未改 DB／Skill ID）

### 3.1 NumberLine
| 證據 | 內容 |
|---|---|
| Generator | 原生 `inequality_operation_table` 已存在 |
| DB | `is_active=0` |
| 建議 | 瀏覽器多小題（12 格）驗收通過後，**人工授權**再啟用；啟用前再備份 DB |
| 禁止 | 把 JH bootstrap 當 B1 原生 PASS |

### 3.2 SubSection332
| 證據 | 內容 |
|---|---|
| active「分式」 | `is_active=1`、例題 0、無 `skills/` 模組 |
| 同節 | RationalExpressionArithmeticOperations（8）、RationalEquation（14） |
| 建議 | **停用或轉 Outline**，或敘事合併至既有分式 Skill；若有獨立來源再 Stage 1 補建 |
| 本輪 | **未刪除、未改 Skill ID、未停用** |

### 3.3 Domain Evidence／Promotion（13／45）

來源：`b1_source_mapping_audit_latest.json` → `b1_final_promotion_classification_20261122.json`

| bucket | 數 | 含義 |
|---|---|---|
| PASS | **13** | Domain Evidence 完整且 Promotion Gate PASS |
| PARTIAL | **9** | 可執行但證據包未完整 |
| FAIL_OR_BLOCKED | **13** | 缺證據／空殼／未就緒（含 NumberLine、SubSection332、QIS、Extremum、PointSlopeForm 等 — **Runtime 已可用 ≠ Promotion PASS**） |
| N/A_OUTLINE | **10** | Outline，不計入發布完成率 |

**Runtime PASS ≠ Domain Evidence PASS ≠ Promotion／Publish PASS。**  
本輪**未偽造** Source／Domain Evidence，**未繞過** Quality Gate，**未自行 Promotion／Publish**。

---

## 4. PASS／FAIL／BLOCKED／NOT_TESTED／人工決策

### PASS
- 受控重啟 5001＋healthz  
- Live HTTP 收尾重點 12 項  
- 瀏覽器：餘式符號多小題、QIS MCQ、團購三欄 UI、垂直平分線出現＋MathJax  
- 教材覆蓋口徑（沿用增量報告，未重掃）

### FAIL
- **無**本輪 Route／Checker FAIL

### BLOCKED（發布）
- Domain Evidence／Promotion 多數 Skill 仍缺正式包（13／45）

### NOT_TESTED
- 實體 iPad 橫向／手寫壓感  
- NumberLine 學生端啟用後完整 UI（目前 inactive）  
- 4457／4471 瀏覽器完整送出（Route 已 PASS）

### 需人工決策
1. 是否啟用 NumberLine（`is_active`）  
2. SubSection332：停用／Outline／合併  
3. 是否授權補做 Domain Evidence／Promotion／Publish  
4. 是否以本報告作為 B1「學生端 Runtime 驗收」通過依據  

---

## 5. B1 結案條件判斷

| 條件 | 是否具備 |
|---|---|
| 教材覆蓋缺口收尾（Generator／結構） | **是**（沿用增量＋本輪學生端確認） |
| 學生端 Runtime／Checker 對收尾項 | **是** |
| 前端桌面抽測 | **是** |
| iPad 實機 | **否（NOT_TESTED）** |
| Domain Evidence／Promotion／Publish | **否** |
| 進入 B2 | **否 — 停止等待人工驗收** |

---

## 6. 變更與安全聲明

- **未**重掃 B1 全冊、**未**重建已驗證 Generator、**未**改 B2–B4  
- **未** commit／push  
- **未**動 Flask 5000／Cloudflare  
- **未**刪除學生歷程；僅新增可追溯 audit 帳號作答紀錄  

**完成後停止，等待人工驗收，不自動進入 B2。**
