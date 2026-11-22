# B1 GenCode V3 教材例題映射稽核＋Runtime 實機驗收報告

**範圍**：技高數學 B1  only  
**日期**：2026-11-21  
**狀態**：稽核／驗收完成，等待人工決策；**不自動進入 B2**  
**正式 DB 備份**：`backups/b1_audit_pre_flask_restart/kumon_math_20261121_155303.db`  
**Flask 5001**：已受控重啟（僅 5001；未動 5000／Cloudflare）

---

## A. SOP 遵循報告

### 本輪採用的 SOP／Contract

| 文件 | 適用步驟 |
|---|---|
| `AGENTS.md` | 最小必要執行、B1-only、不重啟 5000、不 commit、Impact-Based Testing |
| `docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md` §0.2 / §1–§5 | Generator 優先＋原題 Fallback、不強制 100%、審核≠發布、停止條件、結案 |
| `docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md` §2/§3/§6–§9 | Answer Contract、Checker、Family／problem_type、教材保真 |
| `docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md` | Package／Promotion／Publish 時序；Registry≠Promotion |
| `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` | `/get_next_question`＋`/check_answer` 學生端契約；答案不洩漏 |
| `docs/系統SOP/數學答案檢核原則_v1.12_20260908.md` | 等價與 required form |
| `docs/系統SOP/Gencode_AgentSkillV3整合/KnownIssues_TechnicalDebt.md` | 已知債與受控重啟先例 |

### 執行結果

- 未重建平行流程、未批次 REBUILD、未改 B2–B4、未重匯入教材。
- 未偽造 `src_*` 映射；未刪除／合併／停用 `SubSection332`。
- 未繞過 Promotion／Publish Gate；未重新 Promotion／Publish。
- 離線回歸 → DB 備份 → 僅重啟 5001 → 學生端 Route／Live HTTP 驗收。

---

## B. 教材例題映射表（摘要）

**Schema（已實查）**：`textbook_examples`；B1 以 `skill_id LIKE 'vh_數學B1_%'` 識別；例題 `id` → Runtime `component_id=src_<id>`。

**證據檔**：
- `reports/gencode_closed_loop/b1_source_mapping_audit_20261121_235023.json`
- `reports/gencode_closed_loop/b1_source_mapping_audit_latest.json`

| 指標 | 數值 |
|---|---|
| B1 Skill 總數 | 45（可執行 35；Outline 10） |
| B1 `textbook_examples` | 321 |
| Mapping PASS | 314 |
| Mapping WARN | 7（有 DB 例題但無對應 component／generator） |
| Mapping FAIL | 0 |
| Fidelity PASS | 307 |
| Fidelity WARN | 7（同上覆蓋缺口） |
| Fidelity HUMAN_REVIEW | 7（關鍵字保真不足，需人工看原題／變化題） |
| 至少一筆 Mapping PASS 的 Skill | 33 |
| Generator 實作總數（component） | 314 |
| 可用 problem_type 總數 | 117 |

### Mapping WARN（7）— 有教材、無 Generator 覆蓋

| Source ID | Skill | 說明 |
|---|---|---|
| src_4618 | PolynomialBasicConcepts | DB 有例題，無 component |
| src_4629 | PolynomialBasicConcepts | 同上 |
| src_4638 | RemainderTheorem | 同上 |
| src_4640 | RemainderTheorem | 同上 |
| src_4664 | RemainderTheorem | 同上 |
| src_4666 | RemainderTheorem | 同上 |
| src_4401 | NumberLine | DB 有例題，無 V3 component；見 § NumberLine |

### Fidelity HUMAN_REVIEW（7）

- QIS：`src_4476`, `src_4484`, `src_4488`, `src_4517`
- QuadraticFunctionExtremum：`src_4457`, `src_4465`, `src_4471`

自動關鍵字無法充分證明數學結構保真；**不得標 PASS**，需人工對照原題與變化題。

### 特別回歸：`src_4584`

| 層級 | 結果 |
|---|---|
| DB `textbook_examples.id=4584` | `vh_數學B1_DistanceBetweenPointAndLine` |
| PointAndLine package／SPECS | `in_point=True` |
| ParallelLines package／SPECS | `in_parallel=False` |
| 學生端 Route（隔離 DB） | generate＋checker PASS；`problem_type_id=slope_and_point_line_distance_parameter_choice` |
| Live HTTP 5001 | generate＋checker PASS；錯答拒絕 |

**正確映射在 PointAndLine，未落到 ParallelLines。**

---

## C. Runtime 驗收報告

### C1. QIS Checker 離線回歸

| 項目 | 結果 |
|---|---|
| `test_qis_reverse_coefficient_checker.py`（含 29 components self-check） | **PASS** |
| reverse-coefficient 4 components 正解 | **PASS** |
| 錯答拒絕 | **PASS** |
| 等價整數形式（空白／`+n`） | **PASS** |
| payload `checker` | `integer_checker`（非 `linear_equation_equivalent_checker`） |

### C2. 學生端 Route（隔離 DB 複本，不寫正式學生歷程）

證據：`reports/gencode_closed_loop/b1_runtime_student_route_accept_20261121_155248.json`

| 指標 | 數值 |
|---|---|
| 可執行且嘗試出題 | 34 |
| 出題 PASS | **33** |
| 出題 FAIL | 1（`SubSection332` 無 skill 模組） |
| Checker PASS | **33** |
| Checker FAIL | 0 |
| Outline 略過 | 10 |
| 零 Generator keys 略過 | 1（`NumberLine`；JH bootstrap，無 `GENERATOR_KEYS`） |

### C3. Flask 5001 受控重啟

| 步驟 | 結果 |
|---|---|
| 前置：SECRET_KEY／DB URI 存在 | 是（未輸出秘密值） |
| 正式 DB 備份 | `backups/b1_audit_pre_flask_restart/kumon_math_20261121_155303.db` |
| 衝突 Terminal | 僅原 5001 服務 |
| 停止對象 | 僅 port 5001 擁有者 python PID（非全域 kill） |
| 重啟指令 | `.venv\Scripts\python.exe -m flask --app app:app run --debug --host 127.0.0.1 --port 5001 --no-reload` |
| `/healthz` | `{"status":"ok","database":"ok","app":"alive"}` |

### C4. Live HTTP 學生端煙測（正式 DB；可追溯測試帳）

證據：`reports/gencode_closed_loop/b1_live_http_smoke_20261121_155449.json`  
測試帳：`b1_live_audit_20261121_155449`（僅此帳；勿當真實學生）

| Skill | component | generate | checker | 錯答 |
|---|---|---|---|---|
| QIS | src_4474 | PASS | PASS | 拒絕 |
| PointAndLine | src_4584 | PASS | PASS | 拒絕 |
| ParallelLines | src_4570 | PASS | PASS | 拒絕 |
| SlopeOfALine | src_4519 | PASS | PASS | 拒絕 |

### C5. 前端／裝置

| 項目 | 狀態 |
|---|---|
| MathJax／LaTeX 視覺 | **NOT_TESTED**（需人工瀏覽器） |
| 圖形顯示 | **NOT_TESTED** |
| iPad 橫向版面 | **NOT_TESTED** |

人工步驟：以測試帳登入 5001 → 各章代表性 Skill 出題 → 檢視 MathJax／圖／答題區 → iPad 橫向確認無溢出。

---

## D. NumberLine／SubSection332／Promotion

### NumberLine（證據確認，未建新 Generator）

| 項目 | 證據 |
|---|---|
| Skill 狀態 | `is_active=False`；static_health=WARN |
| DB 例題 | `src_4401`：不等式兩邊同乘／除（表格題），**非**「數線點座標移動」 |
| Runtime | JH bootstrap：`skills/vh_數學B1_NumberLine.py` → `jh_數學1上_NumberLine`；`GENERATOR_KEYS=[]`；`SOURCE_COVERAGE_STATUS=INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES` |
| 離線 generate | 可出「數線點移動」題並 self-check |
| 與 B1 教材 | **結構不一致** → 不可視為 B1 原生驗收 PASS |
| 建議（待人工） | 依 Stage 1 建 B1 原生 Generator（對齊 4401 不等式運算表格語意），或明確標 DEFERRED／保持 inactive；**本輪不建置** |

### SubSection332（證據確認，未刪除／合併／停用）

| 項目 | 證據 |
|---|---|
| Skill | active；中文名「分式」；category `3-3 因式分解與分式` |
| 教材例題 | **0** |
| skill 模組 | **不存在**（`No module named 'skills.vh_數學B1_SubSection332'`） |
| 同節已有 | `RationalExpressionArithmeticOperations`（8 例）、`RationalEquation`（14 例）皆 Runtime PASS |
| 建議（待人工） | 高度疑似匯入空殼／與同節 Skill 重疊；建議：**停用或合併進既有分式 Skill**，或補 Stage 1 來源後再建 Generator。**本輪不改狀態** |

### Promotion Gate／Domain Evidence（分層，不可混成單一 PASS）

| promotion_gate | 數量 | 含義 |
|---|---|---|
| PASS | 13 | Domain evidence 完整且 publish_eligible>0 |
| PARTIAL | 9 | 部分 eligible／domain 未完整 |
| FAIL_OR_BLOCKED | 13 | 含 QIS、NumberLine、SubSection332、多個幾何／二次單元等 |
| N/A_OUTLINE | 10 | Outline |

- **Domain Evidence 完整**：13／45  
- **Runtime 可出題（學生端）**：33／45（另 NumberLine bootstrap 可出但未走學生端 keys；SubSection332 不可）  
- **Registry／出題可用 ≠ Promotion PASS**（例：QIS Runtime＋Checker PASS，但 promotion=`FAIL_OR_BLOCKED`，domain_evidence=false）

---

## E. 異常與處置（P0／P1／P2）

| 級別 | 項目 | 根因／重現 | 本輪處置 |
|---|---|---|---|
| P1 | NumberLine 教材語意與 JH bootstrap 不一致 | 比對 `src_4401` 與 `vh_數學B1_NumberLine.generate()` | 僅記錄；待人工決策是否 Stage 1 重建 |
| P1 | SubSection332 空殼 active | DB active + 無例題 + 無模組 | 僅記錄；待人工停用／合併／建置 |
| P2 | 6 筆多項式／餘式例題無 component | Mapping WARN src_4618/4629/4638/4640/4664/4666 | 覆蓋缺口清單；不偽造映射 |
| P2 | 7 筆 Fidelity HUMAN_REVIEW | 自動關鍵字不足 | 附原題 ID；待人工抽樣 |
| — | QIS 錯綁 linear checker | 前輪已修；本輪回歸 PASS | 維持；未重引入 |
| — | src_4584 錯落 ParallelLines | 前輪已修；本輪三層一致 PASS | 維持 |

**本輪未做**：教材語意改寫、Generator 批次重建、映射重寫、Promotion／Publish。

---

## F. 最終結論（六問）

1. **B1 45 Skill 中，有多少已完成教材來源確認？**  
   - 有教材列且 Mapping 可追溯：**33** Skill 至少一筆 PASS；**321／321** 例題皆列入稽核。  
   - Outline 10：無例題屬預期。  
   - SubSection332：確認**無來源**。NumberLine：有來源但與 Runtime **不一致**（WARN）。

2. **有多少 Generator 題型具有有效教材證據？**  
   - Mapping PASS 的 component／例題連結：**314**。  
   - 另 7 筆例題缺 Generator（WARN）。  
   - 可用 problem_type：**117**（≠ 例題數 ≠ 實作數）。

3. **有多少 Runtime 可實際出題？**  
   - 學生端 Route：**33** Skill generate PASS。  
   - Live HTTP（重啟後）：優先 4 Skill PASS。  
   - NumberLine：模組可出但 inactive／語意未驗收。SubSection332：不可出題。

4. **有多少 Checker 通過？**  
   - 學生端 Route：**33／33**（有 Generator 者）。  
   - QIS 離線：**29／29** components + reverse 4 + 錯答／等價。  
   - Live HTTP 優先 4：**全 PASS**（含錯答拒絕）。

5. **哪些仍缺 Domain Evidence？**  
   - `domain_evidence_complete=false` 共 **32**（含 10 outline + 22 可執行／空殼）。  
   - Promotion PASS 且 domain 完整：**13**。  
   - 明確缺：QIS、NumberLine、SubSection332、Cartesian、PointSlope、Quadratic* 多個、LinearFunction、FunctionConcept 等（見 audit JSON `skill_summaries`）。

6. **B1 是否具備下一階段驗收條件？**  
   - **具備「Runtime／Checker 實機驗收」條件**（33 Skill 學生端＋QIS／src_4584 回歸＋5001 已載入新碼）。  
   - **不具備「全冊 Promotion／Publish 結案」條件**（僅 13 Promotion PASS；NumberLine／SubSection332／HUMAN_REVIEW／覆蓋缺口待決策）。  
   - **前端視覺／iPad：NOT_TESTED**，需人工補驗。  
   - **建議**：人工審 NumberLine／SubSection332／7 筆 HUMAN_REVIEW → 再決定是否授權 Promotion；**停止，不進入 B2**。

---

## 產物清單

| 檔案 | 用途 |
|---|---|
| `scripts/audit_b1_source_mapping_and_runtime.py` | 映射／保真／Promotion 盤點 |
| `scripts/accept_b1_runtime_student_routes.py` | 隔離 DB 學生端 Route 驗收 |
| `scripts/accept_b1_live_http_smoke.py` | 5001 Live HTTP 煙測 |
| `reports/gencode_closed_loop/b1_source_mapping_audit_*.json` | 映射原始證據 |
| `reports/gencode_closed_loop/b1_runtime_student_route_accept_*.json` | Route 驗收 |
| `reports/gencode_closed_loop/b1_live_http_smoke_*.json` | Live HTTP |
| `backups/b1_audit_pre_flask_restart/kumon_math_20261121_155303.db` | 重啟前 DB 備份 |
| 本報告 | 結案交付 |

**未 commit／未 push。**
