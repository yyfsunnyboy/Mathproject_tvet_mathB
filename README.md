# MathProject — Verified AI Code Generation for Adaptive Mathematics Learning

具備**可驗證 AI 程式生成**、**數學判分**與**適性學習**能力的數學教學平台。

> **▶️ 公開 Demo（唯讀）：<https://mathb.math-adaptive.org/review-demo>** — 展示模式僅開放技高課綱、不寫入正式資料（`core/guest_demo.py`）。

## 專案概觀

多數 AI 教學網站直接請 LLM 即時產生題目與答案，結果無法保證數學正確，也難以重現與稽核。MathProject 處理的工程問題是：

> **如何讓 AI 產生的「出題程式」，在進入學生端之前，通過明確的數學驗證、題型契約與受控發布流程，並可追溯到教材來源。**

本系統不是單純呼叫 LLM API 產生題目，而是一套完整的**數學題型程式生成、驗證與受控發布流程**：

| 核心貢獻 | 實作重點 |
| --- | --- |
| **AI-assisted Code Generation** | GenCode V3 以教材例題為起點，產生參數化的 Generator；數學答案由 Domain 的精確運算決定，而非由 LLM 輸出。 |
| **Mathematical Verification** | SymPy／Fraction 精確運算＋**獨立 Validator**＋數學等價 Checker；測試以手算標準答案、錯答與等價寫法驗證。 |
| **Safe Deployment and Traceability** | Sandbox → 人工審核 Bundle → hash 鎖定的 Promotion → Publish；每題保留教材來源錨點與 SHA-256。 |

此外整合了 Parameterized Question Generation、Multimodal Handwriting Assessment 與 Adaptive Learning Architecture（成熟度見[實作現況](#實作現況)）。

> **關於「Verified」**：指通過本專案定義的 Validator、Answer Contract、Sandbox 與發布檢查（見 [SOP](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md)），**不等同於**已對所有題目做形式化證明。

---

## System at a Glance

### 教材與動態出題規模

| 已發布 Generator 範圍 | 元件數量 |
| --- | ---: |
| 技術型高中數學 B 系列 | 487 |
| 普通型高中數學第一冊 | 398 |
| **正式發布合計** | **885** |

系統已建置技高數學 B1～B4 及普高數學第一冊教材。以上統計為正式發布的參數化 Generator 元件，不代表固定題庫數量。

> **Published** ＝ 已編入正式 production manifest、具對應 wrapper（`skills/`），且通過驗證並記錄於 `gencode_component_tracker` 的元件（截至 2026-10-24，核對自 `instance/kumon_math.db` 與 `agent_skills_v3/*/component_manifest.json`）。

### 五個不同的指標

| 指標 | 意義 | 目前可證實的數字與說法 |
| --- | --- | --- |
| Published Generator Components | 已正式發布的出題元件 | 885（見上表） |
| Configured Parameter Variants | 元件內嵌、可被種子選取的參數設定 | 普高 398 個元件合計 **9,663 組**（中位數 20／元件）。這是**設定數**，不是已證實互異的題目數；技高 B1／B2／B4 由 Domain 依種子取樣，沒有可計數的清單，不做估計 |
| Questions per Invocation | 呼叫一次 `generate()` 產生的題目數 | 1 題（多小題為單一題目 payload 的多個 part） |
| Validated Seed Samples | 元件通過的生成驗證樣本 | 正式協定：每元件 20 組確定性種子（Lean SOP §5.1）；是驗證樣本數，不是題目上限 |
| Observed Distinct Questions | 實際觀察到互不重複的題目 | Unit 10／11 的沙盒測試要求 20 組種子至少產生 18 種不同題面；其餘單元未逐一統計，不外推 |

參數選取為 `seed % len(variants)`：種子超過參數組數量時會**循環回到既有參數組**。因此本系統的重點是**參數化與可重現的生成能力**，而非題目總量；增加變化需新增參數組或擴大 Domain 的取樣範圍。

其他規模（`core/` 約 25 萬行 Python、約 5,300 個測試函式、13 個已 Promotion 的 Domain、121 個 Operation）來自 `core/`、`tests/`、`configs/gencode_promoted_capabilities.json` 的靜態統計。

---

## System Demonstration

學生練習與題型管理畫面取自本機測試環境（資料庫副本；使用者帳號與姓名已匿名化）；教師分析為公開 Demo 的固定假資料頁。

**學生練習介面** — 數學公式渲染、由題目參數即時產生的函數圖形（含根的標示）、多小題輸入、手寫畫布與 AI 助教（普高 Unit 11）。
![學生練習介面](docs/assets/readme/student-practice.png)

**GenCode V3 教材／題型管理介面** — 例題管理中心顯示各題的 Gencode V3 狀態（「已上線」）與公式診斷計數（普高 Unit 11，38 題）。
![例題管理中心與 GenCode V3 狀態](docs/assets/readme/gencode-admin.png)

**教師分析介面（Demo 固定假資料）** — 公開展示模式 `/demo/teacher-overview` 的唯讀頁，以固定的示範學生與錯題資料呈現教師總覽；正式教師端另有班級與個別學生分析頁（`/teacher/analysis`）。
![教師分析 Demo](docs/assets/readme/teacher-analysis.png)

---

## System Architecture

```mermaid
flowchart LR
    subgraph OFF["離線建置：教材到受控發布"]
        SRC["教材來源<br/>DOCX / PDF / MathType"] --> IMP["教材匯入 V3<br/>解析 · 來源追溯"]
        IMP --> DB[("SQLite<br/>教材 · Skill · Tracker")]
        DB --> GEN["GenCode V3<br/>Domain · Generator · Validator"]
        GEN --> PUB["受控發布<br/>Sandbox · 人工審核 · Promotion"]
    end
    subgraph ON["線上 Runtime"]
        RT["Practice Runtime<br/>題目 · 動態圖形 · 作答"]
        CHK["判分<br/>Answer Contract · 數學 Checker"]
        LOG[("作答與診斷紀錄")]
        TEA["教師端<br/>學習分析 · 診斷"]
    end
    PUB --> RT
    STU["學生端"] <--> RT
    RT --> CHK
    RT --> LOG
    LOG --> TEA
    AI["AI 服務<br/>Gemini · 本機 Qwen"] -. 輔助生成 .-> GEN
    AI -. 手寫／作圖特徵抽取 .-> CHK
    LOG -. 適性模式，限定範圍 .-> ADP["AKT stub · PPO 路由"]
    ADP -. 推薦題目 .-> RT
```

主要目錄：`core/`（匯入、GenCode、checker、adaptive、routes）· `agent_skills_v3/` 與 `skills/`（已發布題型）· `templates/`、`static/` · `tests/` · `docs/`。完整說明見 [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)。

---

## Engineering Challenges & Technical Implementation

### 系統模組與核心工程課題（System Modules & Engineering Challenges）

| 系統模組 | 核心技術 | 關鍵工程課題 | 實作與驗證 |
| --- | --- | --- | --- |
| 1. 教材解析與匯入 | DOCX、PDF、MathType／MTEF、LaTeX、來源錨點、圖片關聯 | 從含公式與圖形的非結構化教材建立結構化題目，並保留來源追溯 | `core/textbook_importer_v3_*.py`、`core/mtef/`、`core/textbook_pdf_visual.py`；來源 SHA-256 與 `question_anchor`；`tests/` 中的 DOCX／MathType 測試；[Stage 1 SOP](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md) |
| 2. GenCode V3 | AI Code Generation、Domain Function、Operation、Generator、Healer、Validator | 讓 AI 產生可執行、可重用、符合數學與題型契約的出題程式 | `core/gencode/`、`core/gencode/domain_bootstrap/`、`agent_skills_v3/`；`tests/gencode/`（182 個檔案）；[PipelineFlow](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md) |
| 3. 數學 Oracle 與判分 | SymPy、Fraction、答案正規化、數學等價 Checker | 區分表示不同但數學等價的答案，並讓題目、標準答案與 Checker 一致 | `core/domain/promoted/`、`core/checkers/`；[數學答案檢核原則](docs/系統SOP/數學答案檢核原則_v1.12_20260908.md)；`tests/domain/` |
| 4. AI 手寫與作圖批改 | Gemini Vision（雲端）、筆跡特徵抽取、Drawing Checker、Evaluator | 處理手繪誤差與不確定結果：模型只抽取特徵，**由確定性 evaluator 判定**，而非像素比對 | `core/services/drawing_answer_analysis_service.py`（直線、拋物線、三次函數、不等式區域、直方圖）；`tests/test_drawing_vision_analyzer.py`、`tests/test_cubic_graph_drawing_evaluator.py` |
| 5. 動態數學視覺化 | JavaScript Canvas、Visual Spec、MathJax 3（SVG 輸出） | 讓隨機生成的函數、圖形、標籤與答案保持一致 | `static/js/visual_spec.js`；圖形由題目參數即時建立；`tests/test_practice_visual_spec_rendering.py`、`tests/test_practice_layout_shared_contract.py` |
| 6. 適性學習 | Knowledge Tracing（AKT 研究原型）、PPO、學習路徑 | 依表現估計學習狀態，決定練習、補救或返回主線 | `core/adaptive/`；`models/adaptive/phase2_policy.pt`；`tests/test_adaptive_phase*_policy.py`（範圍見[實作現況](#實作現況)） |
| 7. 知識圖譜 | Skill、Prerequisite、Knowledge Graph | 建立技能間依賴供診斷與補救使用 | `kg_outputs/`（24 個國中知識圖譜 JSON）、`/knowledge-graph` 頁、`skill_family_bridge`（67 筆）；先備關係管理與查詢已實作，目前資料庫尚未填入先備資料 |
| 8. 教師與學生學習分析 | 學習歷程、錯題本、班級分析、診斷 | 整合不同練習來源與歷史作答，提供可解釋的學習狀態 | `core/teacher_analysis_service.py`、`core/diagnosis_analyzer.py`、`core/mistake_notebook_service.py`；`/teacher/analysis`、`/student/diagnosis` |
| 9. Web 系統與資料管理 | Flask、SQLAlchemy／SQLite、Flask-Login、角色（學生／教師／管理員） | 整合教材、使用者、練習、批改與分析服務 | `app.py`、`models.py`、`core/routes/`；乾淨 Clone 啟動會自動建立 34 張表並通過 `/healthz` |
| 10. 驗證與發布管線 | Sandbox、Validator、Promotion、SHA-256、Bundle、Revision、Regression Tests | 讓 AI 產生的程式經驗證、人工核准與隔離測試後才進入學生端 | `core/gencode/reviewed_capability_promotion.py`、`core/gencode/v3_production_publish_service.py`；`reports/gh_unit*_deploy/`（backup→promote→rebuild→publish→verify-live→accept） |

---

## GenCode V3 Architecture

GenCode V3 以「**Domain 決定數學、Generator 組題、Validator 獨立檢查、Checker 判學生答案**」分工：

```mermaid
flowchart TD
    A["Authoritative 教材<br/>DOCX / PDF · Stage 1 封板"] --> B["Source Fidelity Gate<br/>題幹 · 公式 · 圖形 · 來源 SHA-256"]
    B --> C{"Capability 盤點<br/>既有 Domain／Operation 可重用？"}
    C -->|可重用，無需新 Promotion| G
    C -->|缺口| D["Domain Extension / Bootstrap<br/>candidate 隔離區新增 Operation"]
    D --> V{"獨立 Validator"}
    V -->|FAIL| H["Domain Healer<br/>最多 3 輪，僅限 candidate"]
    H -->|修復後重新驗證| V
    H -->|未修復或達上限| X["停止：維持 candidate<br/>不 Promotion、不發布"]
    V -->|PASS| S{"Sandbox<br/>20 組種子 · 正解／錯解／等價解"}
    S -->|FAIL，修正後重試| D
    S -->|PASS| R{"人工審核 Bundle<br/>revision · SHA-256"}
    R -->|Reject，退回修正| D
    R -->|Approve| P["Promotion<br/>hash 鎖定 · 寫入正式 registry"]
    P --> G["Phase 2 逐題元件重建<br/>Validator · Checker · 20 seeds"]
    G -->|未通過| N["該元件不發布"]
    G -->|VERIFIED| K["Phase 3 封裝 · Publish Gate"]
    K --> RT["Practice Runtime（學生端）"]
```

流程依 [PipelineFlow](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md) 與實際部署腳本繪製：既有 Domain 可重用時只需重建元件，**新增 Domain／Operation 才需要 Promotion**；Domain Healer 最多 3 輪（`MAX_HEALER_ROUNDS`），不保證修復成功。三個核心設計：

**A. Separation of Concerns** — Generator（`agent_skills_v3/<skill>/components/src_<id>/generate.py`）只負責參數化與組題；精確數學運算在 Domain（`core/domain/promoted/<package>/`）；Validator 另行驗證；學生作答由 `core/checkers/` 依 Answer Contract 判分。AI 不決定正確答案。

**B. Independent Verification** — 每個 Operation 同時有 `build_*_matrix`（求解）與 `validate_*_matrix`（驗證）。兩者盡量走不同路徑，例如 Domain 以符號號誌表求不等式解集，Validator 以 SymPy `solve_univariate_inequality`、取樣點檢查或回代驗證。這降低同一錯誤被兩邊同時接受的風險，但仍是有限測試，不是形式化證明。

**C. Controlled Promotion** — 新 Domain／Operation 必須先在 candidate 與 Sandbox 通過，再產生 **Bundle**（`promotion_bundle.json`）：其中列出套件每個檔案的 **SHA-256**、涵蓋的 Operation 與測試案例，以及 `review` 區塊。只有人工將 `review.status` 設為 `human_approved` 後才能 Promotion；已 Promotion 的套件以 digest 鎖定，後續新增 Operation 必須建立新的 **Revision**（`revision_0002`…）與新 Bundle，重新審核，不可就地修改。範例：`reports/domain_operation_workspaces/capability_polynomial_inequality_*/`。

---

## Parameterized Question Generation

MathProject 不是儲存固定題庫，而是由教材建立**可參數化的出題程式**。

**執行路徑**（`agent_skills_v3/gh_*/components/src_<id>/generate.py`）：`seed` → 選取內嵌的 variant 參數組（`seed % len(variants)`，超出清單長度即循環）→ Domain Operation 以精確運算求解並建立題幹、答案契約與圖形規格（`visual_spec`）→ 回傳一題 payload。題幹、答案與圖形使用一致的參數來源，並透過 Domain 驗證、Checker 契約與圖形一致性測試降低內容不一致的風險（有限測試，非形式化證明）。呼叫路徑為 `core/gencode/registered_operation_dispatch.py`。

### 案例一：Unit 10 三次函數（`gh_GraphsOfCubicFunctions`）

- **工程問題**：隨機參數的三次函數，圖形、對稱中心與答案必須一致；作圖題需要可靠的批改。
- **設計**：6 個 Operation（對稱中心式、由條件求函數、敘述判斷、圖形配對等，`agent_domains_candidate/function_cubic/`）；圖形曲線由同一組係數取樣；作圖題由視覺模型抽取特徵，再由 `evaluate_cubic_graph` 判定（`core/services/drawing_answer_analysis_service.py`）。
- **驗證**：沙盒測試逐點檢查圖形曲線與答案描述的函數誤差小於 0.002；Evaluator 對正確、鏡像、位移、拋物線、空白圖形分別判定；另有真實視覺模型檢查腳本（`reports/gh_unit10_grader/`）。已發布 26 個元件。

### 案例二：Unit 11 多項式不等式（`gh_PolynomialInequalities`、`gh_PolynomialFunctionGraphs`）

- **工程問題**：同一組數學能力要支援解集（含重根、無實根、根號端點）、由解反求參數、應用題與由函數圖形讀解集；答案的寫法多樣（`x≠2`、`1<x<3 或 x>5`、含 `√` 的端點）。
- **設計**：單一 Domain `inequality.polynomial` 提供 5 個 Operation，涵蓋 38 題；以因式分解與符號號誌表精確求解；共用 `inequality_solution_checker` 擴充支援單點與 `≠` 解集；應用題的示意圖與函數圖由參數即時產生。
- **驗證**：Domain 測試 81 項（含竄改答案與退化輸入）；每個元件的沙盒閘門與手算標準答案（例如 `(1±√5)/2`、`3≤x≤1+√7`）；Phase 2 隔離演練後，經人工核准才 Promotion（revision 1：35 題；revision 2：另外 3 題）。

---

## Practice & Assessment Pipeline — 學生作答與判分流程

不是每一題都交給 LLM 判分。結構化題型由數學 Checker 以確定性方式判分；AI Vision 只用於手寫與作圖題的**特徵抽取**，最後仍由 Evaluator 判定。

```mermaid
flowchart TD
    G["Published Generator<br/>generate(seed)"] --> Q["Parameterized Question<br/>題幹 · Answer Contract · Visual Spec"]
    Q --> RT["Practice Runtime<br/>題目呈現 · 動態圖形 · 作答介面"]
    RT --> R["Student Response"]
    R --> T{"Answer Type 路由"}
    subgraph STR["A. 結構化作答（不經 LLM）"]
        C1["選擇 · 填充 · 多小題<br/>方程式 · 不等式 · 代數式"] --> C2["對應 Checker<br/>安全解析 → 正規化 → 數學等價（SymPy）"]
    end
    subgraph HW["B. 手寫與作圖"]
        D1["畫布影像"] --> D2["AI Vision 特徵抽取"] --> D3["Drawing Evaluator<br/>對照 expected spec"]
    end
    T -->|結構化| C1
    T -->|drawing| D1
    C2 --> F["判分結果 · Feedback<br/>正解顯示來自 canonical answer"]
    D3 --> F
    D3 -.->|分析失敗或低信心：不計入答錯| U["不確定狀態"]
    F --> L[("作答紀錄<br/>practice_attempts · 錯題本")]
    L --> TA["學生診斷 · 教師分析"]
    L -.->|僅適性模式| AD["適性推薦"]
```

- **路由依據**：Answer Contract 的 Answer Type（`short_answer`、`single_choice`、`multi_part`、`table_fill`、`drawing`），評分路徑為 `answer_contract → runtime dispatch → core/checkers`（[Lean SOP §4](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md)）。
- **作圖不確定狀態**：視覺分析逾時、失敗或信心不足時回報系統錯誤，不計入答錯（`core/services/drawing_answer_analysis_service.py`）。
- **範圍說明**：適性推薦只在適性模式啟用；適性模式中少數 B4 第 1 章自由作答題另由 AI 判定（`core/vocational_math_b4/adaptive/`），屬有限範圍。

---

## Adaptive Learning & Student Analytics

- **學生狀態**：`core/adaptive/akt_adapter.py` 是**啟發式 Local APR 更新（AKT stub）**，程式內明文標示並非真實 AKT 模型。
- **策略路由**：PPO 策略（`core/adaptive/ppo_adapter.py`、`models/adaptive/phase2_policy.pt`）輸入 8 維狀態，輸出 `stay`／`remediate`／`return`，目前只適用 5 個算術 Skill（整數、分數、根式、多項式、一次式）。
- **補救與診斷**：以 family／subskill 目錄（`skill_breakpoint_catalog`）對應錯誤型態；RAG 補救已自 Phase 1 runtime 移除，僅保留實驗資料。
- **分析**：`practice_attempts`、`learning_diagnosis`、`mistake_notebook_entries` 等資料表支援錯題本、班級與個別學生分析頁。
- **限制**：目前沒有以真實學生資料驗證學習成效的研究結論；`Simulated_student/` 為模擬實驗工具。

---

## 實作現況

| 狀態 | 項目 |
| --- | --- |
| **已實際運作（Production）** | 教材匯入 V3 與來源追溯；GenCode V3 已發布題型（見上表）；Practice Runtime（單選、填充、多小題、作圖）；共用 Checker；動態圖形；教師端管理與分析頁；Waitress 部署與公開 Demo。 |
| **已測試（範圍有限）** | AI 手寫／作圖批改（單元與 evaluator 測試）；PPO 路由（5 個算術 Skill）；AI Tutor 多輪對話契約（[`docs/AI_TUTOR_CONVERSATION_CONTRACT.md`](docs/AI_TUTOR_CONVERSATION_CONTRACT.md)）。 |
| **研究原型** | AKT（heuristic stub）；RAG 補救；知識圖譜視覺化與先備關係；模擬學生實驗。 |

**限制**：Published 範圍以上表為準，其餘教材與普高第二冊以後的 GenCode 覆蓋持續擴充；自適應模型尚未以大規模學生資料驗證學習成效；測試依變更範圍執行，不以單次全量測試作為唯一品質依據。

---

## Development & Contributions

以下依倉庫內可查證的成果說明。

- **系統需求與架構設計**：題型 Answer Contract、Domain／Generator／Checker 分工與 GenCode V3 流程，記錄於 [`AGENTS.md`](AGENTS.md) 與 [`docs/系統SOP/`](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md)。
- **教材處理與 GenCode V3 整合**：教材匯入（`core/textbook_importer_v3_*.py`）、Domain 與 Operation（`core/domain/promoted/`），以及各單元的 Stage 1、Sandbox 與發布紀錄（`reports/gh_unit*_*/`）。
- **數學驗證與品質控制**：獨立 Validator、Sandbox 測試、[數學答案檢核原則](docs/系統SOP/數學答案檢核原則_v1.12_20260908.md)與 `tests/`；GenCode 元件的 Promotion 需人工核准（Bundle 的 `review` 區塊）。
- **Web Runtime、前後端整合與部署**：Flask 應用、Practice Runtime 與前端、Waitress 部署與唯讀 Demo。
- **AI Agent 輔助開發**：開發過程使用 Cursor、Claude 等 AI 編碼工具輔助，Agent 的作業邊界與驗證要求見 [`AGENTS.md`](AGENTS.md)。AI 輔助產生的程式並非全部由人工逐行撰寫；GenCode V3 的 Sandbox／Promotion Gate 針對其規範的生成元件，一般程式變更依測試與審查處理。
- **教材與教學需求來源**：以技高與普高數學教材（DOCX／PDF）及其練習情境作為需求來源。

---

## Getting Started

需求：Python 3.11 以上（生產環境使用 3.14）。

```powershell
git clone https://github.com/yyfsunnyboy/Mathproject_tvet_mathB.git
cd Mathproject_tvet_mathB
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000，GET /healthz 為健康檢查
```

乾淨 Clone 會自動建立空的資料庫結構；**教材與題庫資料、正式資料庫不在倉庫內**（由 `.gitignore` 排除），因此需自行匯入教材，或直接使用公開 Demo。

選用 `.env`（不要提交）：

```env
SECRET_KEY=正式環境必填，至少 32 字元的隨機字串
GEMINI_API_KEY=選填，僅 AI 功能需要
MATHPROJECT_DATABASE_URI=選填
```

正式部署：`.\run_production.bat`（Windows，Waitress）。測試：`pytest -q`，建議依變更範圍執行（[SOP §5.0](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md)）。AI 功能預設使用 Gemini（雲端），亦可設定本機 Qwen 模型（`core/ai_settings.py`）。

---

## Documentation

| 想了解 | 閱讀 |
| --- | --- |
| 專案結構與檔案治理 | [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md) |
| GenCode V3 日常 SOP（匯入→生成→發布→驗收） | [`SOP_Gencode_V3_Lean.md`](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_V3_Lean.md) |
| 題型契約、Checker、Gate 規格 | [`Specification`](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md)、[`PipelineFlow`](docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md) |
| 數學等價與 required form | [`數學答案檢核原則`](docs/系統SOP/數學答案檢核原則_v1.12_20260908.md) |
| 技高 Practice Runtime 契約 | [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md) |
| 自適應規格與 AKT stub 說明 | [`docs/自適應實作/`](docs/自適應實作/ADAPTIVE_PRODUCT_SPEC_v1.md) |
| 各單元發布證據與測試 | `reports/gh_unit*_deploy/`、`reports/gh_unit*_stage1/`、`tests/gencode/` |
| Agent 作業規範 | [`AGENTS.md`](AGENTS.md) |

本倉庫不包含教材原檔（DOCX／PDF）、正式資料庫與學生資料（由 `.gitignore` 排除）；教材內容之權利歸原權利人，展示與使用授權以權利人條件為準。請勿提交金鑰或 `.env`。
