# Codex / Cursor 專案指引（v1.17-Lean）

## 1. 預設工作模式
- **最小必要執行**：先讀本檔，再按任務選讀相關 SOP 章節；禁止起手全文讀取所有 SOP。
- 先定位 3–5 個相關檔案；不得無理由掃描整個 Repository。
- 已有 Root Cause 時直接做最小修復；不要重複分析、重做已完成的工作或衍生下一輪任務。
- 工具重複失敗兩次後停止該操作並報告；已通過的測試不得無理由重跑。

## 2. 路徑與選讀入口
- 專案根目錄以 `git rev-parse --show-toplevel` 確認，不依賴固定磁碟路徑。
- 日常 Gencode V3 唯一主要 SOP：`docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md`。
- 欄位、Answer Contract、Checker、Gate：同目錄 `SOP_Gencode_AgentSkillV3_Specification.md` 對應章節，為規範權威。
- 時序、狀態與 publish/recovery：同目錄 `SOP_Gencode_AgentSkillV3_PipelineFlow.md` 對應章節，為流程權威。
- 數學等價與 required form：`docs/系統SOP/數學答案檢核原則_v1.12_20260908.md`。
- 已知債：同目錄 `KnownIssues_TechnicalDebt.md`；Complete Master SOP 僅供歷史與案例查考，非預設必讀。
- 修改 vocational practice / generator runtime 前讀 `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`。
- 已支援 AI Tutor 的 Skill 遵循 `docs/AI_TUTOR_CONVERSATION_CONTRACT.md` 共用多輪契約，不另建不相容服務。
- 專案概觀與成熟度：`README.md`；目錄治理與 Canonical 文件表：`docs/REPOSITORY_STRUCTURE.md`；更新既有文件，不建立平行副本。
- 自適應（AKT stub／PPO 路由）規格：`docs/自適應實作/`；`docs/audits/SYSTEM_CURRENT_STATE_AUDIT.md` 為歷史快照，不代表現況。
- 單元範本：`agent_domains_candidate/polynomial_inequality/`（Domain、adapter、specs、build_sandbox、verification）、`tests/gencode/test_gh_unit11_*_sandbox.py`、`reports/gh_unit11_deploy/`（backup→promote→quarantine→rebuild→publish→verify-live→accept）、`reports/gh_unit11_repair/`（Stage 1 局部修復）。

## 3. 安全邊界
- 正式 DB、教材與資產：先確認來源、備份／transaction 與 dry-run Gate；不得把 DB 有紀錄當 Stage 1 封板。
- 網頁 V3 原始教材以匯入來源紀錄和 `textbook_import/uploaded_sources/{curriculum}/{volume}/` 永久檔為權威；Stage 1 先解析紀錄並驗證完整 SHA-256，不得假設檔案必在 `textbook_import/source/`。
- 普高教材建置期間，同單元重新匯入預設取代舊版；確認來源與範圍、備份及安全交易後，同時清理該單元舊題與無效 `skill_curriculum` 綁定，不累積過時教材；Stage 1 封板仍是進入 Gencode V3 的必要條件。
- 例題、隨堂練習、習題（含「戊.習題」）是教材來源類型，不得自動建立成 Skill（含 `gh_Exercises`）；無法可靠判定數學 Skill 時標記待確認。
- 已驗證且仍有效的 Domain Function 應重用，不隨教材版本刪除。
- 清理範圍僅限 curriculum + volume + chapter，不得只依 `skill_id` 或 ID 範圍；須保護關聯、備份並可回滾。
- 不自行啟動多個 Flask、Terminal 或瀏覽器；不任意重啟 Flask 5000/5001、停止 Cloudflare 或改動正式服務。
- 發布只在既有必要 Gate 通過後執行；Token 節約不得犧牲數學正確性、資料完整性或部署安全。
- 一般 Bug 跑局部測試；正式 Gencode 發布必須保留 Specification、PipelineFlow 規定的全部必要 Gate。

## 3.1 Impact-Based Testing（MUST）
- 先界定直接影響、使用現有測試、先跑最小單元；失敗只追案例與直接依賴，證實共用契約受影響才擴大。
- 純 Markdown：檢查連結、引用、`git diff --check`；單一 UI/CSS：對應頁面與受影響互動。
- 單一 Generator：該元件出題、答案與必要回歸；Domain Function：該函式及已知直接依賴的 Generator。
- Shared Checker：受影響答案類型的等價與錯答；教材匯入：本次範圍的完整性、來源與資料保護。
- 正式 Stage 1 封板、Capability Promotion、Gencode Publish：執行正式契約的必要 Gate，優先採用仍有效證據。
- 正式契約若要求更廣測試不得縮減，須簡述原因；不因單一修補自動全域 pytest、全技能 seed sweep 或完整瀏覽器巡檢。
- 相同測試 PASS 後，無新相關修改不得重跑；輸出只保留 PASS/FAIL 與失敗原因，不貼大量日誌。

## 4. 三層架構
- `progression` 控制教材順序與先備意圖；`routing`（PPO）控制政策動作與 skill/subskill 路由。
- `remediation`（RAG）控制診斷提示與 bridge 候選；三層職責不得合併或在例行修補中重設。

## 5. 固定 Skill 與 family
- 正式算術 Skill：`jh_數學1上_FourArithmeticOperationsOfIntegers`、`jh_數學1上_FourArithmeticOperationsOfNumbers`、`jh_數學2上_FourArithmeticOperationsOfPolynomial`。
- 不新增指數獨立 Skill；`jh_數學1上_IntegerExponentiation`、`jh_數學1上_PowerOfNumbers` 為 legacy，不得重回 runtime routing。
- family 定義留在 canonical catalog；source、family-subskill map、config catalog JSON、UI map JSON 必須一致。
- family-to-generator mapping 必須明確且題型正確；增修 family 須驗證 micro-generator coverage，不得用 placeholder/fallback-only 作正式映射。

## 6. 補救與 fallback
- 多項式補救先經 numbers-side 指數律，再依診斷接 integers-side 符號／乘方解釋；方向為 polynomial → numbers → integers。
- Power-like fallback 至少含 `signed_power_interpretation`、`same_base_multiplication_rule`、`power_of_power_rule`、`product_power_distribution`。

## 7. 評量與診斷
- 標準分基線 `100`；未覆蓋的必要 family 貢獻 `0`；核心 family 集由 configured assessment gate 固定。
- 診斷報告至少含 `score`、`APR`、`family_results`、`strengths`、`weaknesses`。

## 8. Catalog 變更
- catalog source 修改後執行 `python scripts/generate_skill_breakpoint_maps.py`。
- 核對 `configs/skill_breakpoint_catalog.json` 與 `configs/skill_breakpoint_ui_map.json`。

## 9. RAG 身份
- canonical addressing 與 Chroma/bridge identity 均為 `skill_id:family_id`；不得假設全域 `family_id` 唯一。

## 10. 完成與停止
- 先盤點一致性與影響，再最小、可逆修改，最後做與風險相稱的聚焦驗證。
- 只報告修改檔案、runtime 影響、必要驗證與未解問題；必要 Gate 通過且驗收完成即結案。
- 不做寬泛重構、不重複已通過 Gate、不自動展開後續單元。
- 問題修復、直接測試與必要回歸 PASS、無直接 blocker 時立即停止；只回報修改範圍、測試及理由、PASS/FAIL、相關 blocker。

## 11. 開始新冊（第二冊起）的起手順序
1. 確認 authoritative DOCX／PDF 與 SHA-256，完成 Stage 1 dry-run 與封板（Lean §2）。
2. 盤點可重用的 Domain／Operation（`core/domain/promoted/`、`configs/gencode_promoted_capabilities.json`），只補缺口。
3. 以單元範本建立候選套件與 specs，跑該單元 Sandbox 測試與 Domain 驗證器（Lean §3、§5）。
4. 建立 Bundle（`ready_for_human_review`）並做隔離演練；人工核准後才用部署腳本 Promotion／Publish。
5. 以增量驗收（Lean §5.2）收尾；不重啟 Flask，結案時回報是否需要重啟。
