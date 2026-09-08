# Gencode × AgentSkillV3 完整執行手冊 (Complete Master SOP)

> **版本**：v1.12-Master  
> **建立日期**：2026-09-08  
> **文件定位**：本文件為 AI Agent、自動化管線與工程師進入 Gencode × AgentSkillV3 體系的第一閱讀入口與唯一端到端完整執行手冊。本手冊將既有規範權威、流程權威、檢核原則與已封板實證案例整合成可直接執行的 Master SOP。

---

## 目錄

- [0. Document Purpose / Authority Map](#0-document-purpose--authority-map)
- [1. Gencode Hard Rules (不可違反鐵律)](#1-gencode-hard-rules-不可違反鐵律)
- [2. Core Mental Model (西堤選餐架構模型)](#2-core-mental-model-西堤選餐架構模型)
- [3. Authority and Data Ownership (權威歸屬與責任矩陣)](#3-authority-and-data-ownership-權威歸屬與責任矩陣)
- [4. End-to-End Pipeline (端到端管線與狀態流動)](#4-end-to-end-pipeline-端到端管線與狀態流動)
- [5. Textbook Example → Component Contract (一題一元件契約)](#5-textbook-example--component-contract-一題一元件契約)
- [6. Source Evidence / Ground Truth Gate (教材證據閘門)](#6-source-evidence--ground-truth-gate-教材證據閘門)
- [7. Skill-Fixed Domain / Capability / Operation (領域與能力層次)](#7-skill-fixed-domain--capability--operation-領域與能力層次)
- [8. Generator Responsibility Boundary (生成器責任邊界)](#8-generator-responsibility-boundary-生成器責任邊界)
- [9. Data Presentation / Answer Type / UI Contract (呈現與作答契約)](#9-data-presentation--answer-type--ui-contract-呈現與作答契約)
- [10. Answer Contract / Checker (答案契約與檢核系統)](#10-answer-contract--checker-答案契約與檢核系統)
- [11. Verification & 20-Seed Protocol (驗證與 20-Seed 協定)](#11-verification--20-seed-protocol-驗證與-20-seed-協定)
- [12. Component Lifecycle (元件生命週期)](#12-component-lifecycle-元件生命週期)
- [13. Domain / Capability Lifecycle (領域與能力生命週期)](#13-domain--capability-lifecycle-領域與能力生命週期)
- [14. Phase 3 Package / Partial Publish (封裝與部分發布)](#14-phase-3-package--partial-publish-封裝與部分發布)
- [15. Runtime Contract (執行期契約)](#15-runtime-contract-執行期契約)
- [16. Error Routing Table (錯誤代碼與分流矩陣)](#16-error-routing-table-錯誤代碼與分流矩陣)
- [17. Recovery / Repair Decision Tree (故障排除與修復決策樹)](#17-recovery--repair-decision-tree-故障排除與修復決策樹)
- [18. AI Implementation Contract (AI 實作與回報契約)](#18-ai-implementation-contract-ai-實作與回報契約)
- [19. SOP Compliance Checklist (自我檢核清單)](#19-sop-compliance-checklist-自我檢核清單)
- [20. Final Seal Criteria (章節/單元封板準則)](#20-final-seal-criteria-章節單元封板準則)
- [21. Anti-Patterns (反模式與常見陷阱)](#21-anti-patterns-反模式與常見陷阱)
- [22. B1 Proven Cases (B1 實證案例與修復經驗)](#22-b1-proven-cases-b1-實證案例與修復經驗)
- [23. Known Issues / Technical Debt (已知技術債宣告)](#23-known-issues--technical-debt-已知技術債宣告)
- [24. Current / Planned / Deprecated Matrix (狀態成熟度矩陣)](#24-current--planned--deprecated-matrix-狀態成熟度矩陣)
- [25. Quick Start for Agents (Agent 極速開工手冊)](#25-quick-start-for-agents-agent-極速開工手冊)

---

## 0. Document Purpose / Authority Map

### 0.1 文件定位
本文件（`SOP_Gencode_AgentSkillV3_Complete.md`）整合既有各獨立規範與實務紀錄，作為日常開發、除錯、生成、審核與封板的單一完整行動手冊。任何參與本系統之工程師或 AI Agent，皆須以本手冊作為第一行動指南。

### 0.2 權威層級與衝突裁決 (Authority Hierarchy)
當不同文件之間出現描述差異或衝突時，**嚴禁自行融合或猜測**，必須嚴格依照以下優先權判定：

```text
[層級 1：核心規範權威]
└── SOP_Gencode_AgentSkillV3_Specification.md
    職責：欄位定義、合約契約、Answer Type、Checker 規格、Gate 判斷、錯誤代碼定義。

[層級 2：流程與時序權威]
└── SOP_Gencode_AgentSkillV3_PipelineFlow.md
    職責：端到端時序、Phase 1~3 動線、狀態轉移、自癒修復路徑 (Recovery Path)、隔離邊界。

[層級 3：答案檢核細則]
└── 數學答案檢核原則_v1.12_20260908.md
    職責：Specification §8.4 之實作補充、正規化與等價比對細則、required-form 約束。

[層級 4：實證案例與上線紀錄]
└── B1_3-1_Gencode_重建與上線紀錄_20260907.md / B1_3-2_Gencode_重建與上線紀錄_20260908.md
    職責：已成功驗證之上線案例與迴歸證據，提供具體修復範例，不可覆寫層級 1~2。

[層級 5：已知技術債宣告]
└── KnownIssues_TechnicalDebt.md
    職責：宣告已被識別但暫緩處理之技術債（如特定 local check），明確禁止被視為新開發標準。
```

---

## 1. Gencode Hard Rules (不可違反鐵律)

以下 10 條鐵律為系統絕對剛性邊界，任何 violation 將直接導致 Gate 拒絕，不得有任何例外：

### HARD RULE 1 — 一題一 Component
* 每一道教材題目（`textbook_example_row`）對應唯一元件識別碼：`component_id = src_<textbook_example_id>`。
* 擁有獨立實體目錄：`agent_skills_v3/<skill_id>/components/src_<textbook_example_id>/`。
* 包含獨立的原始碼檔案：`generate.py`、`metadata.py`、`get_hint.py`。
* 擁有獨立的 tracker 紀錄。
* 永遠保持全等式：**`textbook_examples count == components count`**。
* 嚴禁將多題合併為單一 generator 或單一 component。

### HARD RULE 2 — Component 存在性與 Publish 資格分離
* 只要資料庫中存在教材例題，就必須建立對應的 component 目錄與骨架，不可因為題目破損或缺乏答案而直接省略。
* 當題目條件或解答證據不足時：
  * `component exists = YES`
  * `verified = NO`
  * `wrapper inclusion = NO`
  * `publish = NO`
* `blocked`、`missing_ground_truth`、`source_incomplete` 屬於 **Policy eligibility condition / reason**（資格條件與阻斷原因標籤）。
* 若 production tracker 目前無對應正式 enum：
  * **不得擅自新增 production enum**。
  * **不得在 Master SOP 中擅自指定另一 lifecycle status（例如 `needs_human_review`）作替代映射**（`needs_human_review` / `ready_for_human_review` 在流程中有既有特定 lifecycle 語意，不可挪用）。
  * 政策原因應儲存於 production 現有可用之 `metadata.py`、payload extra 或 error reason 欄位。
  * 若 tracker 強制需要某 Current status，必須依 production code 真實語意判定，並在文件標示：`[Gap: production alignment required]`，不得假裝已有正式 missing_ground_truth lifecycle state。

### HARD RULE 3 — 教材 Ground Truth 證據閘門 (Textbook Ground Truth Gate)
* **Generator 自己算出的答案，絕對不得作為教材 ground truth 證據。**
* **20-seed 隨機生成 PASS，僅代表演算法自洽，絕對不等於教材證據。**
* **Reliable Textbook Ground Truth Evidence** 必須同時滿足：
  1. **可追溯 (Traceable)**：具備明確出處或來源紀錄。
  2. **屬於教材或正式 source**：源自教科書、教師手冊、正式解答或經審核之教材資產。
  3. **能支持 canonical answer**：證據內容足以直接確認 canonical answer 之正確性。
* 可接受的來源證據包括：
  1. `textbook_examples.correct_answer`。
  2. `textbook_examples.detailed_solution` 中明確存在的正式答案。
  3. 原始教材正式答案／解答頁（原書對照）。
  4. 已有清晰 provenance 且經核准的 source-answer artifact（如已查核之勘誤對照表）。
* **明確禁止以下項目作為 ground-truth evidence**：
  * AI / LLM 自行解題推導。
  * Generator 內部運算或自行推導。
  * Domain Function 計算結果。
  * Checker 反推答案。
  * 20-seed 隨機測試 PASS。
  *(以上各項僅能驗證 implementation correctness，絕不能建立教材 ground truth。)*
* 元件要取得 `VERIFIED` 狀態，必須滿足：
  $$\text{VERIFIED} = \text{Reliable Source Evidence} \land \text{Exact Capability Readiness} \land \text{Executable Component} \land \text{Per-component Validator PASS} \land \text{Valid Answer Contract} \land \text{Shared Checker Validation PASS}$$
* 若題目缺乏可靠答案證據，即使 AI 或程式能推導出唯一解，**亦嚴禁標記 VERIFIED，嚴禁進入 wrapper**。

### HARD RULE 4 — Domain Function 與 Operation 架構
* 行政歸屬（`skill_id`）$\rightarrow$ 路由映射（`fixed_domain_key`）$\rightarrow$ 共享數學能力（`operation`）。
* 數學運算核心必須抽取為可跨題重用的 shared Domain operation（置於 `core/domain/`），嚴禁建立 per-example Domain Function。
* **禁止 per-example Domain Function 不等於可以把數學公式複製貼上至多個 `generate.py` 中。**
* 嚴禁在程式碼中依據 `skill_id`、`example_id` 寫死特例判斷或專屬分支。
* 嚴禁跨領域借用不相干的 Nearest-Template 算子。

### HARD RULE 5 — Generator 單一職責邊界
* Generator 僅負責：
  1. 參數合法範圍抽樣（Parameter Sampling）。
  2. 依教材拓撲組裝題幹（Question Construction）。
  3. 呼叫 shared Domain operation 取得數值解答。
  4. 輸出視覺與圖片契約（Visual / Image Contract）。
  5. 宣告作答與評分契約（Answer Contract Metadata）。
* Generator 絕不是數學演算法定義中心、絕不是學生批改評分者、絕不是教材標準答案自證者。

### HARD RULE 6 — Checker 評分權威與 Local Check 邊界
* 正式 grading authority 必須是：
  $$\text{answer\_contract} \longrightarrow \text{runtime dispatch} \longrightarrow \text{core.checkers}$$
* 數學比對原則：`safe parse → normalize → mathematical equivalence → optional required-form validation`。
* 針對 component-local `check()` 函式之規範：
  * **A. 禁止 Local Grading Authority**：若 component-local `check()` 自行進行 parse、mathematical equivalence、regex grading、string equality、required-form grading，則一律禁止，必須移除或改寫。
  * **B. 允許相容轉發 Facade**：若 component-local `check()` 僅作為 compatibility facade / thin forwarding wrapper，內部完全委派正式 shared checker（如 `check_answer`），則允許存在。
* **文件核心明定：禁止的是 local grading authority，不是單純禁止名為 `check()` 的函式存在。**
* 嚴禁純字串比對（`student == correct`）作為數學批改。
* 嚴禁使用 `"pi" in answer` 或正則表達式作為正式形式驗證器。
* 嚴禁選項題只對比 `A`/`B`/`C`/`D` 字元位置（必須走 semantic choice mapping）。
* KnownIssues 中 `CartesianCoordinateSystem` 之 technical debt 屬暫緩修正之技術債，**絕對不得被當成可仿效的新模式**。

### HARD RULE 7 — 作答拓撲不可篡改性
* 依教材原始作答拓撲決定 Answer Type：
  $$\text{table\_fill} > \text{multi\_part} > \text{drawing} > \text{single\_choice} > \text{short\_answer}$$
* 嚴禁因答案數量、數學領域或是否有配圖而自行變更 Answer Type。
* 嚴禁建立 Fake `multi_part`（單一任務卻拆成兩個輸入框，或將多個值強行串成字串）。
* `Presentation Mode`（輸入外觀元件）絕對不等於 `Answer Type`（作答合約套餐）。

### HARD RULE 8 — 獨立驗證隔離性
* 每個 component 必須獨立通過驗證，嚴禁以同一個 capability 底下某一題通過來代表其他題目通過。
* 驗證必須涵蓋：20-seed 穩定度、固定種子可再現性、數學不變量成立、正解接受、代表性錯解拒絕、數學等價異構形式接受、required-form 違規形式拒絕。

### HARD RULE 9 — 封裝發布唯 verified 原則與部分發布 (Partial Publish)
* 只有標記為 `VERIFIED` 的組件才能寫入 `GENERATOR_SPECS` 並編譯進技能 wrapper。
* 系統全面支援 Partial Publish：未驗證或政策資格不足（`missing_ground_truth` / `source_incomplete` / `source_corrupt`）的題目排除在外，絕不可阻斷已通過 verified 的組件發布。`blocked` 不是 Current production tracker enum。
* 數量恆等關係：
  $$\text{published} \le \text{verified} \le \text{components} \equiv \text{textbook\_examples}$$

### HARD RULE 10 — AI 嚴禁擅自補洞
* 缺乏 evidence 時：
  * 停止自動 VERIFIED
  * 停止 package
  * 停止 publish
  * 保留 policy reason（如 `missing_ground_truth` / `source_incomplete` / `source_corrupt`）
* 是否需要人工審核：依實際責任層與 Current production flow 決定。
* **不得**將 `missing_ground_truth` 自動映射到 `needs_human_review` 或 `ready_for_human_review`。
* 嚴禁自行揣摩或猜測教材答案。
* 嚴禁自行修改 `skill_id` 或 `fixed_domain_key`。
* 嚴禁為了提高 published 數量而人為調降 Gate 門檻。

---

## 2. Core Mental Model (西堤選餐架構模型)

本系統採用經典的「西堤選餐法」將教學、題型、元件、批改進行多層解耦：

```text
┌──────────────────────────────────────────────────────────┐
│                   西堤選餐模型架構層次                    │
├───────────────────┬─────────────┬────────────────────────┤
│ 概念層級           │ 餐廳比喻     │ 系統真實對應實體        │
├───────────────────┼─────────────┼────────────────────────┤
│ Textbook Source   │ 原始食材採購 │ 教材題庫與真實解答依據    │
│ Skill             │ 餐廳品牌分店 │ 行政課程歸屬 (skill_id)  │
│ Routing Domain    │ 菜單大分類   │ fixed_domain_key       │
│ Operation         │ 廚師烹飪菜色 │ Shared Domain Function │
│ Component         │ 每一張獨立訂單│ src_<textbook_example> │
│ Data Presentation │ 盛盤盤飾     │ 題幹資料呈現 (text/img)│
│ Answer Type       │ 享用套餐規格 │ 作答合約五套餐 (5 types)│
│ Presentation Mode │ 用餐餐具     │ 前端輸入元件外觀       │
│ Checker           │ 衛生檢核標準 │ core.checkers 批改器   │
└───────────────────┴─────────────┴────────────────────────┘
```

> **核心口訣**：  
> **Skill 決定餐廳，Registry 決定菜單。AI 只能在菜單內選菜。**  
> **教材原始作答拓撲決定套餐，答案型態決定餐具，Checker 決定如何驗收。**  
> **每一張訂單（Component）獨立製作，嚴禁合併烹飪！**

---

## 3. Authority and Data Ownership (權威歸屬與責任矩陣)

在多階段管線中，各環節的資料權威與所有權明定如下，跨層存取必須遵守邊界：

| 資料 / 欄位項目 | 唯一持有權威 (Authority) | 次要/相容參考 (Fallback) | 違規操作 (Forbidden) |
| :--- | :--- | :--- | :--- |
| `textbook_examples.skill_id` | 教材資料庫（唯讀） | 無 | AI 嚴禁改派或手動修正分類 |
| `fixed_domain_key` | `core/registry/taxonomy_registry.py` | 無 | 嚴禁因缺乏算子改指派其他 domain |
| `allowed_operations` | Domain Registry 定義檔 | 無 | 嚴禁在未登錄情況下於 generator 調用 |
| `Domain Function` | `core/domain/*.py` 共享模組 | 無 | 嚴禁在 component 目錄內撰寫 domain 運算 |
| `Source Ground Truth` | 可追溯之教材正式來源 (DB `correct_answer` / `detailed_solution` / 原始解答頁 / 核准 artifact) | 經核准勘誤表 | 嚴禁 generator、AI、Domain 算子或 20-seed 自算充當證據 |
| `Answer Contract` | `component/generate.py` 的 `answer_contract` | legacy 外層欄位 | 嚴禁使用外層字串比對欄位取代 |
| `Component Tracker` | SQLite Tracker DB / Service | JSON Tracker Report | 嚴禁以 capability 分組狀態取代單題狀態 |
| `Wrapper / Publish` | `core/gencode/phase3_skill_codegen.py` | drafts 快照 | 嚴禁手動編輯正式 `skills/<skill_id>.py` |

---

## 4. End-to-End Pipeline (端到端管線與狀態流動)

系統主流程由 Phase 1、Phase 2（Component 級）、Capability 自動生長閉環、與 Phase 3（Skill 級）組成：

```mermaid
flowchart TD
    subgraph S1["Phase 1: Classification & Onboarding"]
        TE[Textbook Example Row] --> P1Resolve{Resolve Domain}
        P1Resolve -->|Success| P1Entry[Fixed Domain & Allowed Ops]
        P1Resolve -->|Missing / Unregistered| P1Review[SKILL_ONBOARDING_NEEDS_REVIEW]
    end

    subgraph S2["Phase 2: Component Generation & Verification"]
        P1Entry --> P2CheckCap{Exact Capability Readiness Gate}
        P2CheckCap -->|Incomplete / Missing| CapGrow[Capability Growth Loop]
        P2CheckCap -->|Ready| P2Scaffold[Build Component Scaffold: generate, metadata, hint]
        P2Scaffold --> P2CheckGT{Textbook Ground Truth Gate}
        P2CheckGT -->|Missing / Corrupted| CompBlocked["Policy eligibility NO (missing_ground_truth / source_incomplete / source_corrupt)"]
        P2CheckGT -->|source_evidence_eligible YES| P2Test[Run 20-Seeds as implementation validation only]
        P2Test -->|Validation Fail| CompFailed[Mark FAILED]
        P2Test -->|All VERIFIED AND conditions Pass| CompVerified[Mark VERIFIED]
    end

    subgraph SG["Capability Growth Loop (Repair Path)"]
        CapGrow --> Prop[Proposal Creation & Deduplication]
        Prop --> Triage[Auto Triage & Scaffolding]
        Triage --> IsoImpl[Isolated Workspace Implementation]
        IsoImpl --> ExecGate{Executable Workspace Gate}
        ExecGate -->|Fail| IsoRepair[Healer Repair / Max Retries]
        IsoRepair --> ExecGate
        ExecGate -->|Pass| HumRev[Human Review Gate]
        HumRev --> Promo[Atomic Production Promotion]
        Promo --> P2CheckCap
    end

    subgraph S3["Phase 3: Package & Publish"]
        CompBlocked -.->|Excluded from wrapper| P3Filter
        CompFailed -.->|Excluded from wrapper| P3Filter
        CompVerified -->|Included| P3Filter[Verified Components Filter]
        P3Filter --> P3Compile[Compile Skill Wrapper Code]
        P3Compile --> PubGate{Publish Eligibility Gate}
        PubGate -->|Pass| ProdSkills[Publish to skills/<skill_id>.py]
        PubGate -->|Smoke Fail| P3Repair[Phase 3 Self-Healing]
    end

    subgraph S4["Runtime Student Practice"]
        ProdSkills --> RunSample[Dynamic Parameter Sampling]
        RunSample --> RunUI[Frontend UI Contract Rendering]
        RunUI --> RunDispatch[Runtime check_answer Dispatch]
        RunDispatch --> CoreCheckers[core.checkers Mathematical Grading]
    end
```

---

## 5. Textbook Example → Component Contract (一題一元件契約)

### 5.1 目錄結構契約
所有 component 必須坐落於所屬 skill 的 `components/` 目錄中，並以 `src_<textbook_example_id>` 命名：

```text
agent_skills_v3/
  └── <skill_id>/
        ├── manifest.json
        ├── facade.py
        └── components/
              ├── src_11606/
              │     ├── generate.py      # 參數取樣、題幹組裝、答案合約
              │     ├── metadata.py      # 元件中繼資料、分類、能力標記
              │     └── get_hint.py      # 漸進式提示 (Step 1, Step 2, ...)
              ├── src_11607/
              │     ├── generate.py
              │     ├── metadata.py
              │     └── get_hint.py
              └── ...
```

### 5.2 必要檔案內容標準
1. **`generate.py`**：
   - generate payload 必須符合 Current runtime/component contract。
   - `answer_contract` 等正式欄位依 Specification。
   - Master SOP 不額外創造 mandatory field（不得把 `math_core` 寫成 Current 必填欄位）。
   - 內部必須調用 shared Domain operation。
   - **若定義 `check()` 僅能作為轉發至正式 shared checker 的相容 facade，嚴禁實作本機自審 grading 邏輯。**
2. **`metadata.py`**：
   - 記錄 `textbook_example_id`、`problem_type_id`、`answer_type`、`presentation_mode`、`generation_mode` 等。
   - 包含政策狀態標籤（如 `GENERATOR_READINESS = "verified"` 或 `"blocked"`，以及阻斷原因 `BLOCK_REASON`）。
3. **`get_hint.py`**：
   - 實作 `get_hint(step, question_payload)`，提供至少 2 階引導提示。

---

## 6. Source Evidence / Ground Truth Gate (教材證據閘門)

本章節為杜絕「AI 自算自嗨冒充教材真理」的核心安全網。

### 6.1 雙軌驗證原則
系統嚴格劃分兩種不同的驗證維度：
- **維度 A：Textbook Ground-Truth Validation（教材真實性審查）**：查核教材正式來源是否存在可追溯之權威答案依據。
- **維度 B：Generator Mathematical Validation（演算法自洽性校驗）**：查核 20 seeds 運算是否無異常、答案是否等價、評分器是否運作正常。

**絕對禁止以維度 B（20 seeds PASS）反向推導或冒充維度 A！**

### 6.2 Reliable Textbook Ground Truth Evidence 標準
Reliable Textbook Ground Truth Evidence 必須同時具備：
1. **可追溯 (Traceable)**：具備明確出處、頁碼、欄位或核准記錄。
2. **屬於教材或正式 source**：源自教科書正本、官方教師用書、原書詳解或正式 source 資產。
3. **能支持 canonical answer**：證據內容可明確直接支撐題目的標準答案。

#### 可接受之證據來源包括：
1. `textbook_examples.correct_answer` 非空且正確。
2. `textbook_examples.detailed_solution` 中明確存在的正式解答。
3. 原始教材正式答案／解答頁（原書對照）。
4. 已有清晰 provenance 且經核准的 source-answer artifact（如正式勘誤表）。

#### 明確禁止以下列項目充當 Ground Truth 證據：
- AI / LLM 自行解題推導之結果。
- Generator 內部運算或隨機抽樣得出之答案。
- Domain Function 計算結果。
- Checker 反推答案。
- 20-seed 隨機生成 PASS。
*(以上各項僅能證明 implementation correctness，絕不能建立教材 ground truth。)*

因此，元件要取得 `VERIFIED` 狀態之充要條件為：
$$\text{VERIFIED} = \text{Reliable Source Evidence} \land \text{Exact Capability Readiness} \land \text{Executable Component} \land \text{Per-component Validator PASS} \land \text{Valid Answer Contract} \land \text{Shared Checker Validation PASS}$$

### 6.3 Source Evidence 矩陣與處置

> **硬性區分**：有可靠教材 ground-truth evidence → `source_evidence_eligible = YES`。  
> **不得**把「有 `correct_answer` / `detailed_solution`」直接寫成 `VERIFIED`。  
> 20-seed 只能作為 **implementation validation**，不能取代教材 evidence。

元件要取得 `VERIFIED`，必須同時滿足：

`Reliable Source Evidence`  
AND `Exact Capability Readiness`  
AND `Executable Component`  
AND `Per-component Validator PASS`  
AND `Valid Answer Contract`  
AND `Shared Checker Validation PASS`

| 來源狀況 (Source Scenario) | `source_evidence_eligible` | Component 處置 | 20-Seed（僅 implementation validation） | VERIFIED | Wrapper | Publish |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **完整題幹 + 正確 correct_answer** | **YES** | 建立完整元件 | 可執行；不得取代教材 evidence | 僅當全部 AND 條件通過 | 僅 VERIFIED 後 **YES** | 僅 VERIFIED 後 **YES** |
| **完整題幹 + 正確 detailed_solution 解答** | **YES** | 建立完整元件 | 可執行；不得取代教材 evidence | 僅當全部 AND 條件通過 | 僅 VERIFIED 後 **YES** | 僅 VERIFIED 後 **YES** |
| **完整題幹 + 經核准教材解答頁/artifact** | **YES** | 建立完整元件 | 可執行；不得取代教材 evidence | 僅當全部 AND 條件通過 | 僅 VERIFIED 後 **YES** | 僅 VERIFIED 後 **YES** |
| **題幹完整但無上述可靠答案來源** | **NO** | 建立元件骨架 | 可測但不作證據 | **NO**（policy reason: `missing_ground_truth`） | **NO** | **NO** |
| **公式解析損毀 ([MATH_PARSE_FAILED])** | **NO** | 建立元件骨架 | 停用 | **NO**（policy reason: `source_corrupt`） | **NO** | **NO** |
| **題目依賴配圖但缺少圖檔資產** | **NO** | 建立元件骨架 | 停用 | **NO**（policy reason: `source_incomplete`） | **NO** | **NO** |
| **AI 自算有解，但教材原書無可靠依據** | **NO** | 建立元件骨架 | 僅供除錯，不作 evidence | **NO**（policy reason: `missing_ground_truth`） | **NO** | **NO** |

---

## 7. Skill-Fixed Domain / Capability / Operation (領域與能力層次)

### 7.1 核心三層體系
1. **Skill 歸屬**：`textbook_examples.skill_id` 決定教學行政大綱。
2. **Fixed Domain**：`core/registry/taxonomy_registry.py` 將 `skill_id` 綁定至單一數學 Domain（如 `trigonometry.angle_measurement`）。
3. **Domain Operation**：實作於 `core/domain/*.py` 的共享純函式。實際 domain module 與 operation **必須**來自 `fixed_domain_key` + Current operation registry；本手冊舉例名稱不得直接照抄。

### 7.2 Exact Capability Readiness Gate (就緒剛性檢查)
只有當以下 8 項條件**全部成立**時，該 Capability 才算 Ready，才允許對 Component 進行 rebuild：
1. `capability declaration`：已正式宣告於白名單。
2. `operation registry spec`：已登錄於 `taxonomy_registry` 或對應 domain spec。
3. `executable implementation`：`core/domain/*.py` 具備可執行程式碼，通過單元測試。
4. `adapter route`：具備將運算結構轉為 component payload 的適配器。
5. `presentation / answer contract`：合約格式完全定義。
6. `checker`：對應 checker 已登錄且可調用。
7. `component validator`：每題具備獨立驗證邏輯。
8. `selected operation ≡ required operation`：選定算子與需求算子完全一致。

**任何 `partial_capability`（部分滿足）皆禁止重建 generator！**

---

## 8. Generator Responsibility Boundary (生成器責任邊界)

### 8.1 職責規範表

| 項目 | Generator 應當做 (SHOULD) | Generator 嚴禁做 (MUST NOT) |
| :--- | :--- | :--- |
| **數學計算** | 呼叫 `core.domain.*` 函式傳入參數並接收結果 | 自行在 `generate.py` 內編寫幾何、三角、微積分計算 |
| **隨機抽樣** | 依據題型特徵隨機抽樣合理數字，設定 seed | 寫死單一固定數值，或允許產生分母為 0 等非法參數 |
| **答案契約** | 填寫標準 `answer_contract` 與 `canonical_answer` | 自行實作本機 local grading authority 進行答案批改（僅允許純轉發至 shared checker 之相容 facade） |
| **提示引導** | 在 `get_hint.py` 拆解兩步驟以上邏輯指引 | 提供完全無意義的空提示或直接洩漏完整答案 |
| **錯誤自證** | 在題目無法生成時 raise 明確異常 | 捕捉所有異常並回傳預設空字典 `{}` 冒充成功 |

### 8.2 對照範例

#### ❌ 錯誤範例 (Bad: Duplicate Domain Logic & Local Grading Authority)
```python
# Bad: 在 component 內部重複撰寫三角換算，並自訂 local grading 比對
def generate(seed=None):
    deg = 135
    # 錯誤：重複寫入數學邏輯
    rad_val = deg * 3.14159 / 180 
    return {
        "question_text": f"將 {deg} 度換為弧度",
        "answer": "3pi/4"
    }

def check(user_ans, correct_ans):
    # 嚴重錯誤：自製 local grading authority 進行字串比對評分
    return user_ans.strip() == correct_ans.strip()
```

#### ✅ 正確範例 (Good: Shared Domain Operation & Standard Contract)
```python
# Illustrative pseudocode only.
# Actual domain module and operation MUST come from:
# fixed_domain_key + Current operation registry.

from core.domain.<resolved_domain_module> import <registered_operation>
from core.gencode.runtime_skill_wrapper import check_answer  # 若需相容 facade

def generate(seed=None):
    # 1. 抽樣
    deg = 135
    # 2. 調用共用 Domain 運算
    calc = <registered_operation>(deg)
    # 3. 裝配 Payload 與標準契約
    # Conceptual example only.
    # Actual checker_key / equivalence_type / required_form
    # must follow Specification and production registry.
    return {
        "question_text": f"試將 \({deg}^\circ\) 化為弧度。",
        "answer": calc["latex"],
        "canonical_answer": calc["latex"],
        "answer_contract": {
            "answer_type": "short_answer",
            "checker_key": "<from_specification_and_registry>",
            "equivalence_type": "<from_specification_and_registry>",
            "required_form": "<from_specification_and_registry>"
        }
    }

# 若歷史或介面相容需要 check()，僅能作為純轉發 wrapper，嚴禁自審！
def check(user_answer, correct_answer, **kwargs):
    return check_answer(user_answer, correct_answer, **kwargs)
```

---

## 9. Data Presentation / Answer Type / UI Contract (呈現與作答契約)

### 9.1 作答五套餐 (Five Formal Answer Types)

| 套餐名稱 (`answer_type`) | 適用題型與定義 | 剛性 UI 契約與規範限制 |
| :--- | :--- | :--- |
| **`short_answer`** | 單一數值、分數、方程式或單一運算式簡答 | 單一輸入框。禁止將多小題答案串成逗號字串。 |
| **`single_choice`** | 具備唯一正確選項之單選題 | 選項文字與數值不可重複。必須經語意映射評分，禁止僅比對 ABCD。 |
| **`multi_part`** | 包含 (1), (2) 兩個以上獨立子題之題型 | 每個子題具備獨立 `field_key` 與輸入框。採 All-Parts-Correct 批改。 |
| **`table_fill`** | 答案需填入表格指定儲存格之題型 | 輸入框必須直接嵌入表格 cell 內。內部 `field_key` 絕不可顯示給學生。 |
| **`drawing`** | 需在畫布 (Canvas) 上進行幾何或圖形作圖 | 禁用文字輸入框與通用提交鈕。必須強制通過 AI 視覺評分。 |

### 9.2 Presentation Mode (餐具：前端輸入元件外觀)
- `integer`：整數專用小鍵盤/輸入框
- `rational`：分數輸入框（含上下結構）
- `equation`：方程式輸入框
- `text_short`：短文字框（僅限文字名詞，如「鈍角」）
- `single_choice`：ABCD 選項按鈕
- `multiple_inputs`：多重子題輸入區
- `inline_table_input`：嵌入式表格欄位
- `canvas`：互動式幾何繪圖板

---

## 10. Answer Contract / Checker (答案契約與檢核系統)

### 10.1 批改核心四步流
所有數學類答案檢核必須遵守：
$$\text{Safe Parse} \longrightarrow \text{Normalize} \longrightarrow \text{Mathematical Equivalence} \longrightarrow \text{Optional Required-Form Validation}$$

### 10.2 核心檢核細則
1. **數值比對**：數值依浮點數誤差或整數值比對，`2` 與 `+2` 或 `2.0` 在數值合約下視為等價。
2. **分數比對**：允許等價分數（如 `1/2` = `2/4`）。是否允許轉為小數由合約定義。
3. **代數式比對**：支援隱含乘法與符號化簡。`x(x+1)` 與 `x^2+x` 具代數等價。
4. **方程式比對**：依等價方程判定。`2x = 6` 與 `x = 3` 視為等價。
5. **多小題評分**：逐 part 解構評分，嚴禁將整個答案 dictionary 轉字串後做比對。
6. **單選題評分**：學生點擊的選項 key 需映射至具體 semantic content 再行核對。
7. **解集合 (Solution Set)**：
   - *[Production Evidence]*：目前生產環境具備 `solution_set_checker.py` 與 `inequality_solution_checker.py`。
   - 當題目涉及聯立方程式解、多選項子集（如 `(1)(3)`）或區間不等式時，合約之 `checker_key` 設為 `solution_set_checker`，作答五套餐歸屬於 `short_answer`（或搭配 `multiple_inputs`），不可擅自宣告未經許可的第六種 Answer Type。
8. **Required-Form 約束驗證**：
   - 先驗證數學等價，通過後才驗證外觀形式。
   - 代數式展開與因式分解：若要求因式分解形式，即使 `x^2-3x+2` 與 `(x-1)(x-2)` 等價，仍判為 `FAIL required-form`。
   - 弧度含 $\pi$ 表達：若要求化為包含 $\pi$ 之弧度，未含 $\pi$ 的純小數近似值判為 `FAIL required-form`。

### 10.3 Component-Local `check()` 規範與邊界
正式 grading authority 必須是：
$$\text{answer\_contract} \longrightarrow \text{runtime dispatch} \longrightarrow \text{core.checkers}$$

關於 component 目錄內的 `check()` 函式：
* **A. 絕對禁止 Local Grading Authority**：
  若 component-local `check()` 自行進行 safe parse、mathematical equivalence、regex grading、string equality 或 required-form grading，則屬嚴重違背架構，**一律禁止，必須移除或改寫**。
* **B. 允許相容轉發 Facade (Thin Forwarding Wrapper)**：
  若為歷史呼叫或介面相容性需求而保留 `check()`，但其內部實作僅僅是將參數直接轉發呼叫正式的 shared checker（例如 `core.gencode.runtime_skill_wrapper.check_answer`），則**允許存在**。

> **核心界線**：  
> **「禁止的是 local grading authority，不是單純禁止名為 check() 的函式存在。」**  
> 此外，`KnownIssues_TechnicalDebt.md` 中記錄之 `CartesianCoordinateSystem` skill 內自建字串比對屬於待解決技術債，**絕對不得被當成可仿效的新模式**！

---

## 11. Verification & 20-Seed Protocol (驗證與 20-Seed 協定)

### 11.1 20-Seed 驗證的本質
- **驗證什麼**：
  1. 隨機生成 20 種不同種子，皆能順利產出題目，無例外拋出。
  2. 每一組產出的 `answer` 與 shared Domain operation 的計算一致。
  3. 共享評分器 `check_answer` 能夠正確接受 canonical 答案。
  4. 構造之錯誤答案（Wrong Answer）能被 100% 拒絕。
- **不驗證什麼**：
  - **不驗證題目與原教材是否一致**（這是教材來源證據的責任，非亂數產生的責任）。

### 11.2 VERIFIED 閘門查核清單 (Gate Checklist)
在將 Component 標記為 `verified` 前，必須逐項滿足：
- [ ] 具備可追溯且能支持 canonical answer 之教材來源證據（Hard Rule 3）。
- [ ] 呼叫共用 Domain operation，無重複 inline 數學邏輯（Hard Rule 4）。
- [ ] 無自建之 local grading 實作；若有 `check()` 必須完全委託 shared checker（Hard Rule 6）。
- [ ] 20 個 seed 連續生成成功且輸出符合規格。
- [ ] Canonical 答案與 Domain 算子輸出完全一致。
- [ ] 共享 Checker 通過 Canonical 答案。
- [ ] 構造至少 1 個錯誤答案，Checker 成功判定為錯。
- [ ] 代表性等價格式（如括號差異、分數未約分等）能正確被判對。
- [ ] 若合約具備 `required_form`，違規但等價之答案能正確被攔截判定為錯。

---

## 12. Component Lifecycle (元件生命週期)

### 12.1 Current component lifecycle
```text
Current component lifecycle：
discovered
  → classified
  → draft_written
  → compile_passed
  → smoke_passed
  → verified
  → packaged
  → published
```

`blocked` / `missing_ground_truth` / `source_incomplete` / `source_corrupt` **不是** Current production tracker enum，也不是上列 lifecycle state。

### 12.2 [Policy Eligibility Side Condition]
```text
[Policy Eligibility Side Condition]

missing_ground_truth / source_incomplete / source_corrupt
  → verified eligibility = NO
  → package = NO
  → publish = NO
```

- 以上僅屬於 **Policy eligibility condition / reason**（資格條件與阻斷原因標籤），不是 Current production lifecycle state。
- 語意核心：
  $$\text{verified} = \text{NO}, \quad \text{package} = \text{NO}, \quad \text{publish} = \text{NO}$$
- 若 production tracker 沒有正式對應 enum：
  * **不得自行新增** production enum。
  * **不得固定映射** `needs_human_review` 或 `ready_for_human_review`。
  * 標示：`[Gap: production alignment required]`

### 12.3 Tracker Status 對齊規範
1. SQLite shadow tracker 目前正式定義的 enum 狀態為：`pending`, `usable`, `generating`, `draft_written`, `smoke_passed`, `verified`, `needs_human_review`, `failed`, `unsupported_domain_operation`, `fixed_domain_violation`, `domain_operation_not_allowed`, `needs_regeneration`。
2. **嚴禁在 Master SOP 中擅自新增 production enum**。
3. **嚴禁在 Master SOP 中擅自將 `blocked` / `missing_ground_truth` 固定映射為另一生命週期狀態（例如 `needs_human_review`）**。`needs_human_review` / `ready_for_human_review` 在 PipelineFlow 中具備特定的生命週期語意（如 onboarding 或 capability promotion 前的人工審核），不得未經 production contract 證據就挪用作教材 ground truth 缺失。
4. 政策阻斷原因應保存於現有可用之 `metadata.py`（例如 `GENERATOR_READINESS` 與 `BLOCK_REASON` 等 policy 欄位）、generator payload extra 或 tracker 的 error log 欄位。此處 `"blocked"` 是 metadata policy tag，不是 tracker lifecycle enum。
5. 若 production tracker 資料庫寫入時因 schema 約束強制需要某 Current status，必須依 production code 真實語意判定，並在文件與報告中清楚標明：
   `[Gap: production alignment required]`
   嚴禁假裝 production 已有正式的 `missing_ground_truth` lifecycle state。

---

## 13. Domain / Capability Lifecycle (領域與能力生命週期)

Domain 能力依照自動生長閉環管理：

```text
proposed (建立缺口提案)
  │
  ▼
approved (自動檢核核准)
  │
  ▼
draft_scaffold_ready (隔離區骨架就緒)
  │
  ├── [未過 Executable Gate] ──> implementation_incomplete (持續修補)
  └── [通過 Executable Gate] ──> ready_for_human_review (等待人工審核)
                                    │
                                    ▼
                                 promoted (原子寫入 Production 唯讀區)
                                    │
                                    ▼
                                 verified (經各題獨立 rebuild 確認無誤)
```

---

## 14. Phase 3 Package / Partial Publish (封裝與部分發布)

### 14.1 封裝原則
- **只打包 Verified**：Phase 3 封裝編譯器遍歷 component tracker，僅萃取 `verified` 組件。
- **一題一 Spec**：在輸出之 `skills/<skill_id>.py` 中，`GENERATOR_SPECS` 陣列包含對應各 verified 題目的獨立規格物件，禁止合併。
- **部分發布 (Partial Publish)**：若某 Skill 共有 10 題，其中 3 題 verified、7 題因政策資格不足而未 verified，則編譯出的 wrapper 僅包含該 3 題，並可正常發布上線提供練習。政策資格不足的題目絕不阻礙已 verified 組件發布。

### 14.2 封裝產物模板片段
```python
# Conceptual example only.
# Do not infer Current GeneratorSpec schema from this snippet.
# Current fields are governed exclusively by:
# - Specification §6
# - production phase3_skill_codegen.py
# Master SOP 不得超越 Specification。

# skills/<skill_id>.py 由 codegen 自動產生，禁止人工手動修改
from __future__ import annotations
from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = "<skill_id>"
GENERATOR_SPECS = [
    {
        "problem_type_id": "<problem_type_id>",
        "checker_key": "<from_answer_contract>",
        "equivalence_type": "<from_answer_contract>",
        "generator_readiness": "runtime_ready",
        "answer_type": "<one_of_five_formal_types>",
        # remaining Current fields: Specification §6 only
        # Planned fields (schema_version / skill_id / example_id / component_id / ...)
        # must NOT be treated as Current production schema.
    }
]

def generate(level: int = 1, seed: int | None = None, **kwargs):
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, **kwargs)

def check(user_answer, correct_answer, **kwargs):
    return check_answer(user_answer, correct_answer, **kwargs)
```

---

## 15. Runtime Contract (執行期契約)

1. **完全無 LLM 介入**：線上學生做題、隨機參數抽樣、答案產生與評分批改，100% 由本機 Python 程式碼與數學引擎執行，禁止呼叫外部 LLM API。
2. **動態抽樣隔離**：每次呼叫 `generate_for_skill` 時傳入隨機種子，確保千人千題，且參數完全受控於定義之約束條件。
3. **安全例外處置**：
   - 學生輸入格式無法解析 $\rightarrow$ 回傳 `ANSWER_PARSE_FAILED`，引導學生修改輸入，不可扣分。
   - 評分器發生未預期 crash $\rightarrow$ 記錄系統錯誤記錄檔並回傳 `CHECKER_EXECUTION_FAILED`，絕對嚴禁靜默判定學生答錯！

---

## 16. Error Routing Table (錯誤代碼與分流矩陣)

| 錯誤代碼 (Error Code) | 發生階段 | 責任歸屬層級 | 系統標準處置作為 |
| :--- | :--- | :--- | :--- |
| `SKILL_ONBOARDING_NEEDS_REVIEW` | Phase 1 | 大綱註冊層 | 記錄於 needs_human_review，引導人工登錄 taxonomy |
| `DOMAIN_CAPABILITY_UNRESOLVED` | Phase 1 | 能力解析層 | 建立 proposal，進入自動生長閉環 |
| `DOMAIN_FUNCTION_MISSING` | Phase 2 | 數學能力層 | 進入 Capability 自動生長閉環，補充共用算子 |
| `CAPABILITY_NOT_READY` | Phase 2 | 能力閘門層 | Exact Readiness Gate 未過，嚴禁 rebuild generator |
| `EXECUTABLE_WORKSPACE_INCOMPLETE` | 生長閉環 | 程式實作層 | 阻斷 promotion，退回隔離實作環境重修 |
| `missing_ground_truth` [Policy] | 來源查核 | 教材資料層 | [Policy Condition] verified/package/publish = NO，儲存 policy reason，排除於 wrapper 之外。不得固定映射 `needs_human_review`。[Gap: production alignment required] |
| `source_incomplete` [Policy] | 來源查核 | 教材資料層 | [Policy Condition] verified/package/publish = NO，記錄缺失資源，排除於 wrapper 之外。不得固定映射 `needs_human_review`。[Gap: production alignment required] |
| `source_corrupt` [Policy] | 來源查核 | 教材資料層 | [Policy Condition] verified/package/publish = NO，記錄毀損來源，排除於 wrapper 之外。不得固定映射 `needs_human_review`。[Gap: production alignment required] |
| `ANSWER_PARSE_FAILED` | Runtime | 輸入解析層 | 提示前端輸入格式錯誤，引導學生重新輸入 |
| `CHECKER_EXECUTION_FAILED` | Runtime | 評分執行層 | 記錄嚴重系統異常記錄檔，拋出 HTTP 500 / 系統提示 |
| `SAMPLING_EXHAUSTED` | Runtime | 參數抽樣層 | 抽樣超限拋棄，自動更換 seed 重試 |

---

## 17. Recovery / Repair Decision Tree (故障排除與修復決策樹)

遇到問題時，依循決策樹定位責任層，**嚴禁一看到錯誤就改 `generate.py`**：

```text
[出現錯誤或測試失敗]
       │
       ├─ 是否為教材答案不存在或題幹破碎？
       │     └─ 是 ──> 記錄 Policy Reason (missing_ground_truth / source_incomplete / source_corrupt)，停止 VERIFIED / package / publish，退出 Wrapper (Hard Rule 2, 3)
       │
       ├─ 是否為缺少數學運算核心 (如三角換算、多項式乘除)？
       │     └─ 是 ──> 進入 Capability 生長閉環，修復/新增 core/domain/*.py (Hard Rule 4)
       │
       ├─ 是否為評分被拒絕或判定錯誤？
       │     ├─ 是否為字串比對導致 ──> 檢查 answer_contract，切換至 core.checkers 正式評分器 (Hard Rule 6)
       │     └─ 是否為 required-form 誤判 ──> 檢查 mathematical equivalence；檢查 answer_contract.required_form；修正正式 structural / AST-based required-form validator
       │
       ├─ 是否為隨機抽樣溢出或除以零？
       │     └─ 是 ──> 調整 generate.py 的參數抽樣邊界與局部防禦式約束
       │
       └─ 是否為封裝期語法或清單崩潰？
             └─ 是 ──> 觸發 Phase 3 codegen 自癒，重新比對 generator_specs 欄位
```

> **Master SOP 不得推薦 regex-only required-form grading。**

---

## 18. AI Implementation Contract (AI 實作與回報契約)

AI Agent 在修改任何程式碼之前與之後，必須完整輸出以下契約格式，缺一不可：

### 18.1 修改前回報格式 (Pre-action Report)
```text
=== AI Pre-action Implementation Contract ===
錯誤責任層：[Phase 1 / Phase 2 / Spec Contract / Answer Runtime / Sampling Runtime / Capability / Recovery]
對應 SOP 章節：[例如：Specification §8.4 / Complete SOP §6]
production code 現況：[1-3 句說明現行程式碼行為]
直接根因：[明確指出為何出錯]
預計修改範圍：[檔案名稱與函式名稱]
不修改範圍：[明示不影響的組件、skill 或題型]
局部測試方式：[測試腳本路徑與預期結果]
停止條件：[明確定義何時必須停手，不得擴大範圍]
```

### 18.2 修改後回報格式 (Post-action Report)
```text
=== AI Post-action Verification Report ===
違反的 SOP 規則：[必須為「無」]
修改檔案與函式：[列出檔案與函式]
測試結果：[通過數量 / 失敗數量]
是否新增特例分支：[必須為「否」]
是否呼叫外部 LLM：[必須為「否」]
是否影響其他 component：[必須為「否」]
SOP 與 production 是否已對齊：[必須為「是」]
```

---

## 19. SOP Compliance Checklist (自我檢核清單)

AI Agent 或開發者在宣告任務完成前，必須逐一自我檢核：

- [ ] `textbook_examples count == components count`（每題獨立元件，無漏題）。
- [ ] 無任何 per-example Domain Function，數學運算集中於 `core.domain`。
- [ ] 各 Component 內部無重複 inline 複製貼上的 shared 數學邏輯。
- [ ] Exact Capability Readiness 8 項條件全部檢查通過。
- [ ] 標記 `VERIFIED` 之元件具備可靠教材答案證據（非 generator 自算、非 LLM 推導、非 20-seed 代替）。
- [ ] 所有 Component 均無自建之 local grading authority，評分全權走 `core.checkers`（相容 `check()` 僅能純轉發）。
- [ ] 20 seeds 連續生成測試 100% 通過。
- [ ] 至少 1 個代表性錯誤答案能被 Checker 100% 拒絕。
- [ ] 代表性數學等價形式通過檢驗。
- [ ] Required-form 違規形式能正確被判定為不合格。
- [ ] 各 Component 具備獨立 tracker 紀錄，無合併追蹤。
- [ ] Phase 3 wrapper 只打包 `VERIFIED` 組件；政策資格不足的組件安全隔離（不 package、不 publish）。
- [ ] 本地 Client Runtime Smoke 測試通過，無破題或 500 錯誤。

---

## 20. Final Seal Criteria (章節/單元封板準則)

宣告一個章節（Section）或技能（Skill）封板上線的必要條件：
1. **絕不使用「100% Published」作為封板標準**（破碎題目必須不得 verified / package / publish）。
2. **所有教材例題皆已建立 Component**，且數量完全一致。
3. **所有已發布（Published）之組件皆為 VERIFIED**。
4. **所有未發布之組件皆具備明確政策資格歸因**（如 `missing_ground_truth`），且不得假裝已 verified。
5. **Domain Function 符合共用規範，Checker 完全符合四步流**。
6. **Skills Wrapper 經 Runtime Smoke 驗證全數通過**。
7. **本次 scope 內不得存在**：unresolved blocker、SOP violation、publish-breaking defect。已正式登錄於 KnownIssues、明確 deferred、且不影響本次 scope 的 technical debt：**不阻止本次 section / skill seal**。

---

## 21. Anti-Patterns (反模式與常見陷阱)

在歷次開發與修復中總結出之重大禁忌：
1. **「自算自嗨」反模式**：Generator 自己計算出解答，就將其填入作為 Ground Truth 證據並標記 VERIFIED。
2. **「假性等價」反模式**：把 20-seed 生成無 crash 當作教材驗證通過。
3. **「自立門戶」反模式**：在 `generate.py` 旁自建 local grading authority（自行以字串或正則比對），規避共用評分器。
4. **「代碼搬運工」反模式**：因為禁建 per-example domain function，就將相同數學程式碼整段複製到各題 `generate.py`。
5. **「因噎廢食」反模式**：因為教材原題缺少圖片或答案，就完全不替該例題建立 component 目錄。
6. **「盲目衝高」反模式**：為了達到 100% 發布率，人為猜測填補教材答案。
7. **「大鍋炒」反模式**：看到同一個 capability 就把 3 道教材題硬塞在同一個 component 資料夾。

---

## 22. B1 Proven Cases (B1 實證案例與修復經驗)

### 22.1 B1 3-1 多項式運算案例
- **經驗**：35 題教材題中，33 題具備完整題幹與詳解成功 VERIFIED；2 題表格題因原書表格缺失而標記為 SKIPPED / BLOCKED。
- **結論**：嚴格實施 Partial Publish，33 題成功發布上線，不強求 100% 發布，維持系統高可靠性。

### 22.2 B1 3-2 因式定理 (FactorTheorem) 答案契約修復
- **問題**：原先共用 fallback 將「已知根求一次因式」誤包裝為 Fake `multi_part`（`part_1 = x-r`, `part_2 = x-r`），且未給予 `parts` 合約，導致評分器恆判定錯誤且鎖死作答狀態。
- **修復**：回歸原始單一任務本質，將 `answer_type` 修正為 `short_answer`（搭配 `expression_checker`），標準答案訂為 `x-r`，成功解鎖正常評分與 40/40 runtime smoke。

---

## 23. Known Issues / Technical Debt (已知技術債宣告)

### 23.1 CartesianCoordinateSystem skill-local `check()`
- **位置**：`skills/vh_數學B1_CartesianCoordinateSystemEstablishment.py`
- **現況**：仍存在舊式 skill-local 字串比對邏輯，尚未完全遷移至共用數學等價評分器。
- **政策**：狀態為 `deferred`。本手冊明令：**此為已知技術債，絕對不得被任何 Agent 視為新功能的設計範例！**

---

## 24. Current / Planned / Deprecated Matrix (狀態成熟度矩陣)

| 功能模組 / 機制 | 狀態標籤 | 說明與約束 |
| :--- | :--- | :--- |
| 一題一最小生成單位 (`src_<id>`) | **`[Current]`** | 現行唯一標準，嚴格執行 |
| 5 種作答套餐 (Answer Type) | **`[Current]`** | short_answer, single_choice, multi_part, table_fill, drawing |
| 數學等價四步評分流 | **`[Current]`** | safe parse → normalize → equivalence → required-form |
| Exact Capability Readiness Gate | **`[Current]`** | 8 項條件未齊全嚴禁 rebuild |
| 獨立 Component Tracker DB | **`[Current]`** | SQLite 追蹤各題狀態 |
| 宣告式變數二元約束引擎 (`ConstraintPolicy`) | `[Planned]` | 規劃於 M3 引進，現階段由 generator 內部抽樣控制 |
| 強型別規格檢核驗證模型 (Pydantic / Dataclass) | `[Planned]` | 規劃於 M1 引進 |
| 全域 Nearest-Template Fallback | **`[Deprecated]`** | **已全面廢除，嚴禁跨 Domain 相似度借用** |
| Per-example 專屬 Domain Function | **`[Deprecated]`** | **已全面廢除，能力必須收斂至可共用算子** |
| 依 `fixed_domain_key` 存在推斷 ready | **`[Deprecated]`** | **已全面廢除，必須過 Exact Readiness Gate** |
| 多題合併為單一 Generator | **`[Deprecated]`** | **已全面廢除，違反 Hard Rule 1** |

---

## 25. Quick Start for Agents (Agent 極速開工手冊)

AI Agent 進入任務時，請直接依循此 10 步極速流程：

1. **READ SOP**：精讀本手冊 §1 鐵律與 §18 回報契約。
2. **INSPECT SOURCE**：查詢教材正式來源（DB `correct_answer`、`detailed_solution`、原書解答頁或核准 artifact）。
3. **GROUND TRUTH GATE**：確認是否有可靠教材證據。無可靠證據 $\rightarrow$ 停止自動 VERIFIED / package / publish，保留 policy reason，停手不入 wrapper、不發布。是否人工審核依實際責任層與 Current production flow 決定；不得把 `missing_ground_truth` 固定映射到 `needs_human_review`。
4. **DOMAIN CHECK**：檢查 `core/domain/*.py` 是否具備共用算子。若無 $\rightarrow$ 先擴充共用算子並單元測試。
5. **BUILD COMPONENT**：建立獨立 `src_<id>`，撰寫 `generate.py`，配置標準 `answer_contract`。
6. **NO LOCAL GRADING**：移除本機自審 `check()`；若有 `check()` 僅能作為純轉發至 `check_answer` 之相容 facade。
7. **RUN 20 SEEDS**：執行 20 種隨機 seed，驗證輸出與算子自洽，測試正解與錯解。
8. **UPDATE TRACKER**：更新單題 tracker 紀錄（`verified` 或依 production 語意記錄 blocked 政策原因 `[Gap: production alignment required]`）。
9. **COMPILE WRAPPER**：執行 Phase 3 codegen，僅打包 `verified` 組件進入 wrapper。
10. **RUNTIME SMOKE & REPORT**：執行本機端到端抽題與評分測試，輸出標準回報並封板。
