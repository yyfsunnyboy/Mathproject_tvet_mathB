# AI自適應學習平台(技術型高中版)

> 以技術型高中數學 B 系列為核心，整合教材數位化、GenCode 題庫生成、學生練習、自適應診斷、補救路由與教師學習分析。

本專案是一套面向**技術型高中數學學習情境**的自適應學習平台。目前主要開發與驗證範圍為技高數學 **B1–B4**。

系統的目標不是只做一個能回答數學問題的聊天機器人，而是建立一條可追蹤、可測試、可持續維護的教學工程流程：

**教材 → 結構化題目 → 可執行題型生成器 → 學生作答 → 學習證據 → 自適應診斷與補救 → 教師分析**

AI 主要用於教材解析、題目生成、OCR／視覺理解、提示與診斷；學生端真正上線的題目仍必須通過 generator、validator、checker、runtime contract 與 regression tests，避免把不可控的模型輸出直接暴露給學生。

---

## 專案目標

平台目前聚焦以下五個問題：

1. **教材數位化**：把 PDF / Word 教材中的章節、小節、例題、習題、自我評量與圖形資產轉成可追蹤的結構化資料。
2. **題庫程式化**：把靜態教材題轉成可參數化、可重複生成的 Python 題型，而不是只儲存固定題目。
3. **一致的學生作答介面**：讓選擇題、填充題、代數表示式、多小題、向量、圖片題與作圖題遵循共用的 practice runtime 規範。
4. **真正的自適應學習閉環**：將學生作答歷程轉成 mastery / weakness evidence，再由 progression、routing 與 remediation 三個不同層次做下一步決策。
5. **教師可觀察性**：讓教師能從班級、學生、章節與技能層級檢視學習進度與錯題資料，而不是只看到總分。

---

## 目前功能與進度

| 模組 | 狀態 | 說明 |
| --- | --- | --- |
| 技高數學 B1–B4 curriculum | 已整合 | B1–B4 均已進入 curriculum / skill / practice 體系；各章節的 source coverage、publish 與 human acceptance 仍分章管理。 |
| 一般技能練習 | 可使用 | 依技能產生題目、提交答案、即時判定並累積練習紀錄與 mastery。 |
| 章節複習 | 可使用 | 支援題型輪替、章節 review run、作答持久化，以及中斷後續作。 |
| 選擇／填充／多小題 | 可使用 | 共用 answer contract；技高單選題固定 4 選項，多小題保留結構化標籤與語意。 |
| 數學等價判定 | 可使用 | 代數式、方程式、集合／區間等答案優先採數學語意等價，而非單純字串比對。 |
| 作圖與手寫區 | 可使用 | 支援 scratchpad、參考圖層、作圖題與部分結構化圖形判定。 |
| 教材圖形資產 | 已建立 gate | PDF crop / image asset 需經 accepted / needs_review / rejected 狀態後才可進學生端。 |
| 教師首頁 | 可使用 | `/teacher_dashboard` 顯示教師班級與學生入口。 |
| 教師分析 | 可使用 | `/teacher/analysis` 可依班級、學生、冊別、章節、技能與時間範圍查看資料。 |
| 自適應複習 API | 可使用 | AKT knowledge tracing + PPO routing；模型不可用時保留 deterministic fallback。 |
| RAG 補救 | 已整合 | 用於前置知識診斷與補救 bridge，不與 PPO routing 混成單一決策層。 |
| 公開唯讀 Demo | 可使用 | `/demo`、`/demo/practice`、`/demo/teacher-overview`，使用固定展示資料且不提供正式寫入。 |
| GenCode / healer / validator | 持續強化 | 教材題型可透過 generator、validator、AST / regex healer 與 publish gate 逐步進入正式題庫。 |

> **進度說明**：本專案不以「檔案存在」等同「章節完成」。教材 coverage、generator 能否穩定變形、checker 正確性、圖形語意與瀏覽器 human acceptance 會分開驗證，因此不同章節的成熟度可能不同。

---

## 系統架構

```text
Textbook PDF / DOCX
        │
        ▼
Textbook Import / Structure Binding
        │
        ├── curriculum / chapter / section
        ├── textbook examples
        └── visual assets
        │
        ▼
GenCode Pipeline
        │
        ├── prompt / skill specification
        ├── domain generator
        ├── validator
        ├── regex / AST healer
        └── publish gate
        │
        ▼
Executable Skills / Generators
        │
        ▼
Practice Runtime
        │
        ├── MCQ / expression / multipart
        ├── image / diagram / drawing
        ├── mathematical equivalence checker
        └── practice_attempts
        │
        ▼
Learning Evidence
        │
        ├── mastery / chapter review
        ├── AKT knowledge state
        ├── PPO routing
        └── RAG remediation
        │
        ├──────────────► Student adaptive flow
        └──────────────► Teacher analytics
```

主要程式責任分布：

- `app.py`：Flask application factory、登入、學生／教師入口與 top-level routes。
- `core/`：practice、教材匯入、adaptive、資料服務、RAG、GenCode orchestration 等核心邏輯。
- `skills/`：已發佈、可執行的題型 generator / checker。
- `generators/`：可重用的 domain generator。
- `validators/`、`core/validators/`：題目與程式碼驗證。
- `core/healers/`：生成程式的 regex / AST 修復。
- `agent_skills*`：skill 規格、family、prompt、evaluation metadata。
- `templates/`、`static/`：學生與教師 Web UI。
- `tests/`：維護中的 regression / integration / contract tests。
- `reports/`：保留的正式驗證與稽核證據。
- `docs/`：架構、runtime contract 與長期文件。

完整目錄說明見 [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)。

---

## 自適應學習設計

本專案刻意把自適應機制拆成三個責任層，不讓單一模型同時控制所有決策。

### 1. Progression — 教材進度

負責學生目前在教材中的主要學習位置、題型 progression 與章節順序。

### 2. Routing — PPO

負責在已定義的技能／子技能空間中決定下一步 route action。現有自適應複習流程可載入 PPO 模型；模型不可用時保留 deterministic fallback，避免整個練習流程失效。

### 3. Remediation — RAG

當學生出現弱點時，RAG 用於檢索前置知識、bridge family 與補救內容。RAG 的角色是**診斷與補救內容選擇**，不是取代 progression 或 PPO。

另外，AKT（Attentive Knowledge Tracing）用於估計學生的 knowledge state / mastery，提供 routing 與分析使用。

這三層的工程規範記錄於 [`AGENTS.md`](AGENTS.md)。

---

## Practice Runtime 的核心規範

技高 B1–B4 共用同一套 practice runtime contract，不為每一章重新發明 UI 或 checker。

目前的重要 invariant 包含：

- 技高 single-choice 固定 **4 個選項**。
- answer 以**數學語意**為優先，不以 presentation label 或字串相等為唯一判準。
- 向量答案接受實用的鍵盤輸入形式，不要求學生一定輸入 LaTeX。
- multipart 題保留結構化 `(1) / (2) / ...` 與每個輸入欄位的語意標籤。
- 作圖題的文字輸入區與 drawing area 有不同 contract。
- reference diagram 與 handwriting drawing layer 分離，undo / redo / clear 不應破壞參考圖。
- 一般題圖、scratchpad background 與 dynamic diagram 不混用同一種 renderer。
- `/get_next_question` 等 API 對匿名使用者回傳 JSON 401，不以 login HTML 302 取代 API contract。
- chapter review / practice session 狀態必須 bounded 並可持久化必要進度。

詳細規範見 [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md)。

---

## 使用者流程

### 學生

```text
登入
  → 技高學習首頁
  → 選擇 B1 / B2 / B3 / B4
  → 章節 / 技能
  → 一般練習或章節複習
  → 作答 / 手寫 / 作圖
  → checker 判定
  → 練習紀錄與 mastery 更新
  → 自適應診斷 / 補救 / 下一題
```

### 教師

```text
登入教師帳號
  → /teacher_dashboard
  → 班級 / 學生
  → /teacher/analysis
  → 依冊別、章節、技能、時間範圍查看學習資料
```

### 教授／評審快速查看

若只想理解系統結構，建議依序閱讀：

1. 本 `README.md`
2. [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)
3. [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md)
4. `reports/` 中保留的 architecture / acceptance evidence
5. `tests/` 中的 regression 與 contract tests

若應用已啟動，也可從以下唯讀展示頁開始：

- `/demo`
- `/demo/practice`
- `/demo/teacher-overview`

---

## 安裝與啟動

### 1. Clone

```bash
git clone https://github.com/yyfsunnyboy/Mathproject_tvet_mathB.git
cd Mathproject_tvet_mathB
```

### 2. 建立 Python 虛擬環境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. 環境設定

建立 `.env`。正式環境至少需要：

```env
SECRET_KEY=請使用至少32字元且不可為預設值的隨機字串
```

需要 Gemini 相關功能時再設定：

```env
GEMINI_API_KEY=your_google_api_key
```

可選設定：

```env
MATHPROJECT_DATABASE_URI=sqlite:///...
WAITRESS_THREADS=10
```

- `SECRET_KEY`：production 必填，且必須至少 32 字元。
- `GEMINI_API_KEY`：只有需要雲端 Gemini 功能時才需要。
- `MATHPROJECT_DATABASE_URI`：未指定時使用 `instance/kumon_math.db`。
- `WAITRESS_THREADS`：production Waitress thread 數，允許 1–16，預設 10。

### 4. 開發模式

```powershell
python app.py
```

預設：

```text
http://127.0.0.1:5000
```

### 5. Production 啟動（Windows）

```powershell
.\run_production.bat
```

Production entry point 使用 Waitress，關閉 Flask debug，預設綁定：

```text
127.0.0.1:5000
```

系統啟動時會執行必要的 database initialization / schema ensure；正式課程與班級資料仍應依專案既有資料匯入／備份流程管理，不應直接把本機 SQLite DB 提交到 Git。

### 6. Health check

```text
GET /healthz
```

正常時會回傳 application / database health 狀態。

---

## 主要技術

| 類別 | 技術 |
| --- | --- |
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| Production WSGI | Waitress |
| Database | SQLite / SQLAlchemy |
| Math rendering | MathJax 3 SVG |
| AI / multimodal | Google Gemini integration、OCR fallback |
| RAG | ChromaDB, sentence-transformers, BM25 |
| Knowledge tracing | PyTorch AKT |
| Adaptive routing | Stable-Baselines3 PPO |
| Document processing | PyMuPDF, python-docx, pypdf, pypandoc |
| Data / reporting | pandas, NumPy, openpyxl, Matplotlib |
| Testing | pytest + browser / contract / integration regression suites |

---

## 測試與品質控制

`tests/` 不是暫存資料，而是本專案的重要工程證據。正式修改通常依影響範圍跑 focused regression，再視需要擴大測試。

常用方式：

```powershell
pytest -q
```

針對 practice / vocational runtime 的修改，應先閱讀：

```text
docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md
```

GenCode 章節完成也不只看 generator 是否能執行。至少需要區分：

```text
source coverage
→ generator parameterization
→ answer/checker correctness
→ visual / multipart semantics
→ publish gate
→ browser / human acceptance
```

這也是本專案保留大量 regression test 與 acceptance evidence 的原因。

---

## Repository Hygiene

為避免研究與開發過程產生的中介檔案污染專案根目錄：

- 正式程式放在 `core/`、`scripts/`、`skills/`、`generators/` 等維護目錄。
- regression tests 放在 `tests/`。
- 正式技術文件放在 `docs/`。
- 可保留的歷史 one-off artifact 收進 `temp/archive/`。
- pytest cache、DB、WAL、備份、dry-run、probe、local export 等由 `.gitignore` 排除。
- 不將 `node_modules/`、本機 SQLite DB 或一次性測試輸出提交到 repository。

---

## 目前限制

這是一個持續演進中的教學研究／工程平台，以下事項仍刻意保留為持續工作，而不是在 README 中包裝成已完成：

- B1–B4 不同章節的教材 source coverage 與 human acceptance 成熟度不同。
- AI 生成題目仍必須經 deterministic validator / checker / publish gate；不能假設模型輸出天然可靠。
- 圖形題、教材 crop 與 multipart 題需要額外的語意驗收，單純「能顯示」不等於正確。
- AKT / PPO 屬於自適應研究模組，與 production progression / remediation 分層管理，仍持續以實際學生資料與模擬實驗驗證。
- 完整班級資料與正式 SQLite database 不應進 Git；部署端需使用既有 backup / restore 或資料初始化流程。

---

## 下一階段方向

目前優先順序不是無限制新增功能，而是把既有技高數學平台做得更可驗證：

1. 持續完成 B1–B4 章節級 source coverage 與 human acceptance closure。
2. 強化 GenCode family 的變形品質、圖形語意與 checker robustness。
3. 累積真實學生作答 evidence，改善 mastery、diagnosis 與 remediation 評估。
4. 將教師分析與章節複習資料串成更完整的 learning analytics workflow。
5. 以 simulation / ablation 與實際使用紀錄比較 progression、PPO routing、RAG remediation 的效果，而不是只以模型指標宣稱成效。

---

## 核心文件

- [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md) — repository 結構與檔案治理規則
- [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md) — 技高 B1–B4 共用 practice contract
- [`AGENTS.md`](AGENTS.md) — progression / PPO routing / RAG remediation 與工程 guardrails
- `reports/` — architecture audit、GenCode、coverage、acceptance 等驗證報告
- `tests/` — regression、integration 與 runtime contract tests

---

## 專案定位

**AI自適應學習平台(技術型高中版)** 的核心價值在於：把「教材內容」、「可執行題型」、「學生作答」、「自適應決策」與「教師可觀察性」放進同一套可追蹤的工程系統，而不是把 AI 當成無狀態的題目生成器。

專案目前以技術型高中數學 B 系列作為主要驗證場域，持續朝向可實際進入課堂使用、可重現、可稽核、可擴充的自適應學習平台發展。
