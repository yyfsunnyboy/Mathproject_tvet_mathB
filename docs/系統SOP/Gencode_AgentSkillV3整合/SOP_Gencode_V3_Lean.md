# Gencode V3 日常執行 SOP（v1.16-Lean）

> 本文件是唯一日常主要 SOP，涵蓋教材 Stage 1 到學生端驗收。
> 欄位、Answer Type、Checker、Gate 定義以 [Specification](./SOP_Gencode_AgentSkillV3_Specification.md) 為準。
> 時序、狀態與 recovery 以 [PipelineFlow](./SOP_Gencode_AgentSkillV3_PipelineFlow.md) 為準。
> 本文件不創建 V3.1，也不修改正式契約；衝突時停止猜測，回查相應權威。

## 一頁式管線入口

`Authoritative DOCX + 配對 PDF → Stage 1 匯入封板 → Gencode V3 → Domain Function → Generator → Canonical Oracle → Shared Checker → Sandbox / Gate → Publish → 學生端驗收`

| 看見的問題 | 先查的責任層 | PASS / FAIL / STOP |
| --- | --- | --- |
| 題幹、公式、圖、Skill 錯位 | authoritative source / Stage 1 | 來源不可信即 FAIL；Stage 1 未封板即 STOP Stage 2 |
| 數學操作錯或能力缺失 | Domain Function / Capability | 先重用；Exact Readiness 未過即 STOP rebuild |
| 出題參數、題意或 payload 錯 | 該題 Generator | 只修該元件及共用依賴，不重建整條管線 |
| canonical answer 錯或缺 | Source Oracle / verified Domain operation | Oracle Gate 未過即 FAIL VERIFIED |
| 等價答案誤判 | Answer Contract / Shared Checker | 修相應 checker；不可用答案顯示反推評分 |
| staging 或學生端失敗 | Phase 3 / runtime | Publish Gate 未過即 STOP；已發布按既有回滾流程 |

詳細 PASS 條件和狀態名稱只查 Specification、PipelineFlow 相應章節。

## 0. 開工與停止

1. 先讀 Repository 根目錄 `AGENTS.md`；依任務只讀本 SOP 的相關節。
2. 確認工作樹、現有成果、教材來源、Skill、DB tracker 與發布狀態。
3. 將項目分為 complete、partial、missing；保留有效成果，只處理缺口。
4. 根因已明時修正責任層；不得逐題補丁、無限重試或重跑已通過 Gate。
5. 工具同一操作連續失敗兩次即停止並報告證據與阻礙。
6. Gate 通過且驗收完成即結案，不自動開始下一單元。

## 1. 權威與作業邊界

- 一道教材例題對應一個獨立 component：`component_id = src_<textbook_example_id>`。
- DB 有教材紀錄不代表 authoritative Stage 1 完成；舊 tracker `verified` 不抵銷來源變更。
- 教材來源、Skill binding、公式、圖片、題幹或答案契約變更時，重新判定受影響 Gate。
- Generator、Oracle、Validator 分離；Generator 只抽樣、呼叫 Domain operation、組裝 payload 與 contract。
- 不把 `fixed_domain_key` 存在、可編譯、schema 通過或 placeholder 當 Capability ready。
- 不降低數學、來源、發布 Gate 以增加 published 數量。
- 不以歷史案例、技術債或舊 Master SOP 覆寫兩份正式權威。

## 2. Stage 1：教材匯入與封板

### 2.1 找到 authoritative source

1. 原始 DOCX 是教材文字、題目結構與順序的主要權威；配對 PDF 是圖形與視覺資訊的權威。
2. 先查 project-local 原始 DOCX／PDF 及其 provenance，再考慮外部來源。
3. 記錄來源 identity、hash／size、版本與對應學制、冊別、章節、Skill。
4. `*_Latex.docx`、converter output、temporary／staging／failed artifact 只能當中間產物。
5. 原始檔與轉換檔並存時，明確排除後者；來源不能唯一確認則 Gate FAIL。

### 2.2 結構與數學保真

1. 解析 DOCX 段落、runs、style、表格、錨點與順序；區分 section 與 skill heading。
2. Skill candidate 依教材結構抽取、去重，進行 `KEEP / MERGE / CONCEPT_ONLY` 決策。
3. Example → Skill 先依 heading span，章末題用可稽核 deterministic binding。
4. MathType/OLE、OMML、Symbol、負號與 template record 均通過共用 fidelity 檢查。
5. `MATH_PARSE_FAILED rows/tokens` 與 conversion failures 必須為 0；不可用 `FORMULA_MISSING=0` 掩蓋 parse corruption。
6. 每張 `QUESTION_REQUIRED` 圖像保留 DOCX anchor、題目 region、PDF page／bbox、文字與唯一配對證據。
7. Required visual unmatched 或錯掛均阻斷正式匯入；不要做 example-specific 修補。

### 2.3 Dry-run、匯入、封板

1. Dry-run 查題目總數、例題、隨堂練習、習題的分題與來源一致性，以及順序、公式、圖片、mapping、duplicates、學制／冊別／章節／Skill binding。
2. Dry-run 對 examples、skills、outline、mappings、assets、tracker 等所有 persistent state 寫入必須為 0。
3. 以 before/after row count、hash 或 snapshot 證明無寫入；否則 Gate FAIL。
4. 所有阻斷項 PASS 才以明確 transaction/write scope 執行正式 import。
5. 匯入後重查數量、順序、anchors、skill IDs、公式診斷、required visuals、頁面及狀態。
6. 封板記錄 authoritative source、Gate 證據與版本；Stage 1 未封板不得依舊 DB 開始新 Generator。
7. 中斷或失敗先查 transaction 與已寫入範圍，不把 half-import 宣稱完成。
8. 重匯入須明確界定 write scope 並保護正式 DB、既有有效教材與學生作答紀錄；不可用全域清空代替局部修復。
9. **WARNING**：DB 已有教材只證明曾寫入，不證明 authoritative source 已驗證；Stage 1 PASS 前不得正式進 Stage 2。

## 3. Stage 2：Gencode V3 Generator

### 3.1 盤點與重用

1. 逐題盤點 source fidelity、作答拓撲、既有 component、Domain、Operation、Capability、Oracle。
2. 優先沿用已完成且對目前來源仍有效的 Generator／Domain 能力。
3. 對已有能力檢查 Exact Capability Readiness，而非只看名稱或舊 verified 標記。
4. 只有真正缺失的共用能力才新增；先定義責任、input/output、canonical contract 與覆蓋題目。
5. 禁止逐題複製數學公式、以不相關題型映射或讓 fallback-only 進入 production。
6. **WARNING**：不得因新單元重新打造已有的數學能力；先確認舊能力對新教材來源仍有效。

### 3.1.1 Domain Function：共用數學能力

1. 依數學概念與語意設計，避免綁課本章節或單一 `example_id`。
2. 例：絕對值方程式／不等式解集、多項式運算／因式分解、函數與座標關係、數線分點／比例。
3. 每個函式說明 input、output、定義域、邊界情況與數學不變量。
4. 支援多個 Generator 重用，可提供或支援 Canonical Oracle，不複製現有共用能力。
5. Domain 負責數學計算；Generator 負責取樣與組題；Checker 依 Answer Contract 判學生答案。
6. Domain 數學正確性須有必要測試或獨立驗證依據，涵蓋代表值與邊界值。
7. **WARNING**：Generator 與 Checker 共用同一段錯誤邏輯不能互相證明正確；必要時使用獨立手算、正式來源或另一種驗證方法。

### 3.2 Capability Gate

1. 查 shared implementation、registry、taxonomy/fixed-domain、adapter、contract、validator、tests 與 invariants。
2. 缺 operation 時依 PipelineFlow 的 Extension／Bootstrap／Healer 隔離流程處理。
3. `pass`、`NotImplementedError`、固定空回傳、無 assertion、僅編譯或僅 schema 不能算 executable。
4. Exact Readiness 與 Executable Workspace Gate 均 PASS 後才能 `ready_to_rebuild`。
5. 對每題獨立 rebuild 與驗證；不得把一題成功視為整個 Capability 的發布資格。

### 3.3 Component 與答案權威

1. 每個 `textbook_example_row` 保留自己的 component、source、metadata、hint 與 tracker。
2. 有教材例題即保留 component 存在性；未通過 Gate 的 component 不進 wrapper/publish。
3. Source Fidelity 與 Answer Oracle 分開判斷；學生版無答案不自動否決 VERIFIED。
4. Oracle 僅用正式來源或通過 Exact Readiness 的 verified mathematical operation。
5. 禁止從 generator output、學生答案、LLM 猜測或前端反推 canonical answer。
6. VERIFIED 依 Specification §10.6 的完整充要條件，不以 `correct_answer` 欄位存在代替。

## 4. Answer Contract、Checker 與 UI

1. Nested `answer_contract` 是作答與批改權威；legacy 外層欄位僅供相容，衝突由 Gate 擋下。
2. 正式 Answer Type 僅依 Specification §4–§6：`short_answer`、`single_choice`、`multi_part`、`table_fill`、`drawing`。
3. Presentation mode／input widget 與 Answer Type 分開；不自行宣告第六種 Answer Type。
4. 一般填充／簡答用 `short_answer`；單選用 `single_choice`，正解 mapping 必須語義正確。
5. 多小題逐 part 保存 canonical answer 與 grading；表格填空逐 cell 保存答案。
6. 作圖題依 drawing contract 的 reference／rubric 與正式 grader；不可偽造文字答案。
7. 應用問題依實際作答拓撲選現有 Answer Type；不可憑敘述題另創分類。
8. `answer_contract → runtime dispatch → core.checkers` 是評分路徑；local `check()` 不得另立權威。
9. 等價判分遵守 Specification §8.4 與[數學答案檢核原則](../數學答案檢核原則_v1.12_20260908.md)。
10. 區分數學等價、required form、parse failure 與 checker crash；後兩者不可靜默判錯。
11. 數學等價判分與正確答案顯示分離；顯示只能從 canonical `answer_contract` 經 backend submit response。
12. 送出前不得曝露 canonical answer；答錯後依 Answer Type 顯示正解或正確格式。
13. 不等式回饋優先顯示含 `x` 的不等式；題目明確要求區間形式時依題目要求。此為待核對的 Unit 2 經驗，正式契約未明訂前不得作 Gate 規則。
14. 數線拖曳、手繪、AI 判圖只按已存在的作答契約執行；目前三者的完整分流契約待確認，不自行升格為新規範。
15. 不以 AI 判圖替代正式 drawing grader，除非正式契約明確授權。

### 4.1 Shared Checker 的已定義範圍

- 數學答案採 `safe parse → normalize → mathematical equivalence → optional required-form validation`，核心是數學語意，不是完全相同字串。
- 代數式依相應 expression checker 判等價；方程式依相應 equation checker 判等價，不比較左右文字順序。
- 解集類以相應 solution-set／inequality／interval checker 比較；不等式與區間可否互通仍以該題 `answer_contract`、required form 及 checker 支援範圍為準。
- 數值類依契約處理等價分數、小數、正負號；小數容差與表示限制必須由契約指定。
- 不同順序但語意等價的答案須由專用 checker／semantic mapping 處理；不能一律用同一字串 parser。
- `multi_part` 各 part 用自己的 contract；`single_choice` 用選項語意 mapping；`table_fill` 逐 cell；`drawing` 用正式 rubric／grader。
- 無法安全解析或可靠判定時回報 parse／checker error，不猜測為正確，也不靜默判錯。
- 禁止單題硬編答案、特殊字串、放寬判分；不得把尚未實作的智慧判分宣稱已上線。
- 正確答案顯示是提交後 feedback，來源為 canonical answer；不參與 grading authority。

## 5. 必要驗證與 Sandbox

### 5.0 Impact-Based Testing（MUST）

| 變更 | 最小必要驗證 |
| --- | --- |
| 純文字／SOP | Markdown 連結、引用、`git diff --check` |
| 單一 UI／CSS | 對應頁面及受影響互動 |
| 單一 Generator | 該元件出題、答案、必要回歸案例 |
| Domain Function | 該函式及所有已知直接依賴它的 Generator |
| Shared Checker | 受影響答案類型的等價與錯誤答案 |
| 教材匯入 | 本次範圍完整性、來源一致性、資料保護 |
| 正式 Gencode Publish | 正式契約規定的全部必要發布 Gate |

先界定直接影響、優先用現有測試、先跑最小單元；失敗只追該案例與直接依賴。
只有證實共用契約受影響才擴大至相關消費端；正式契約若要求更廣範圍不得擅自縮減，需簡述理由。
不因單一 Generator 重跑 B1–B4／所有普高單元，也不因單一 Checker 測所有無關題型。
相同測試 PASS 後，沒有新相關修改不得重跑；只記錄 PASS/FAIL 與失敗原因，不貼大量日誌。
禁止無理由全域 pytest、全技能 seed sweep 或完整瀏覽器巡檢；數量多不等於修正品質高。
Stage 1 封板、Capability Promotion、正式 Publish 仍執行所有必要 Gate，優先使用仍有效的既有證據。

### 5.1 正式 Gate

1. Stage 1 與 Stage 2 Gate 獨立保存證據；不得用 Generator 成功掩蓋教材匯入錯誤。
2. 逐 component 驗證 import/execute、canonical answer、contract、正解接受、錯解拒絕。
3. 適用時驗證等價解、required form、undefined case 與 no duplicate math。
4. 依現有 20 deterministic seeds 協定做正式 component 驗證；seeds 不能充當 Oracle。
5. 失敗時按責任層修復，再只重跑受影響驗證；已通過且未受影響的 Gate 不重跑。
6. Sandbox／staging 中驗證 wrapper、manifest、thin facade、per-component selection 與 generation。
7. 正式發布前查 Source Fidelity、Answer Oracle、Exact Readiness、Executable Workspace、Validator、Answer Contract、Shared Checker。
8. 另查 Specification 與 PipelineFlow 規定的 Phase 3 publish eligibility、runtime smoke 與人工審核位置。
9. Staging 失敗不得 promote；修正通用責任層後重新驗證 staging。

## 6. Partial Publish、DEFERRED、回滾

1. Phase 3 只封裝 VERIFIED component；failed／未 ready／來源或 Oracle 不合格者保留明確 exclusion reason。
2. Partial Publish 是合法流程，少數 DEFERRED 題目不阻擋其他已 verified 題目上線。
3. `DEFERRED` 是待辦／排除記錄；不要擅自寫成 production tracker 未定義的 enum。
4. 每個排除題保留 source、reason、責任層、後續條件及對應 tracker 證據。
5. 發布前記錄現行 manifest、wrapper、DB／教材版本與可回復點。
6. Publish 後 smoke FAIL：停止擴大發布，查明現有部署回滾機制後回復至最近已驗收版本；具體命令不由本 SOP 自創。
7. 回滾後核對 runtime selectable、manifest 與服務狀態，保存失敗證據。
8. 不因回滾或 DEFERRED 降低 Gate，也不將未驗證 component 偷放進 wrapper。

## 7. 學生端驗收與結案

1. 每個已發布 Skill 驗證 wrapper import、manifest/component count、可選取、可生成、無 fallback／duplicate。
2. 逐 Answer Type 驗證呈現、提交、正解／錯解及適用時等價解；practice HTTP 成功。
3. 提交後錯誤回饋顯示 backend canonical answer；單選顯示 label 與 option text，多小題／表格逐項顯示。
4. 作圖僅顯示 contract 所有的 reference／rubric；數學內容走共用渲染，分數按正式顯示規則。
5. 圖題驗證 required image、scratchpad background 與 clear 只清筆跡。
6. Teacher-facing ONLINE 以 production manifest、wrapper、runtime facade、component selectable 為證據。
7. 教材 Stage 1 和 Gencode Stage 2 的封板證據分別保留，記錄 published／DEFERRED 清單。
8. 所有必要 Gate 與學生端驗收通過後立即結案；未通過者只報明確 blocker 與下一條件。
9. 問題已修、直接及必要回歸 PASS、無直接 blocker 時 STOP；報告限修改範圍、測試及理由、PASS/FAIL、相關 blocker。

## 8. 依需求查閱的詳細契約

- [Specification](./SOP_Gencode_AgentSkillV3_Specification.md) §2–§10：component、Domain、正式 Answer Type、Checker、Gate。
- [PipelineFlow](./SOP_Gencode_AgentSkillV3_PipelineFlow.md) §3–§7：Phase 1–3、Capability recovery、publish、runtime、lifecycle。
- [數學答案檢核原則](../數學答案檢核原則_v1.12_20260908.md)：等價判定與 required form 補充。
- [KnownIssues](./KnownIssues_TechnicalDebt.md)：暫緩技術債，不能作新實作範例。
- [Complete Master SOP](./SOP_Gencode_AgentSkillV3_Complete.md)：歷史案例與詳細整合紀錄，僅在查證舊行為時選讀。
