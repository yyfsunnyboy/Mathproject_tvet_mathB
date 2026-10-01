# AI自適應學習平台(技術型高中版)

> ## ▶️ [評審／教授請點此進入公開 Demo](https://mathb.math-adaptive.org/review-demo)
>
> **https://mathb.math-adaptive.org/review-demo**  
> 可直接進入唯讀展示模式，快速了解目前系統的教材、練習介面與教師端整合成果；展示模式不提供正式資料寫入。

## 專案定位

**AI自適應學習平台(技術型高中版)** 是一個以技術型高中數學 B 系列為核心的長期教學研究與工程專案。

專案最終目標是建立一套能根據學生學習證據進行診斷、推薦與補救的 AI 自適應學習平台；但目前開發進度仍在基礎建設階段，**尚未把自適應學習架構視為已完成成果**。

目前已完成的主要里程碑是：

> **Phase 1 — 技術型高中數學 B 教材數位化與系統化導入**

也就是先把教材內容、章節結構、例題、習題、圖形與題型資料整理成系統可以持續使用、驗證與擴充的基礎資料層。

---

## 目前開發階段

### Phase 1 — 技術型高中數學 B 教材導入

目前已將技術型高中數學 **B1–B4** 納入同一套 curriculum / skill / textbook import 體系，重點工作包括：

- 建立 B1–B4 的冊別、章節、小節與技能結構。
- 匯入 PDF / DOCX 教材內容。
- 解析例題、隨堂練習、習題與章節自我評量。
- 保存題目來源與教材定位資訊，避免教材內容失去可追溯性。
- 處理數學公式、向量符號、特殊字元與 LaTeX 表示。
- 對需要圖形的教材題目建立 image / PDF crop 資產流程。
- 將教材內容整理成後續可供 generator、checker 與 practice runtime 使用的結構化資料。
- 透過測試、人工驗收與 runtime contract 持續檢查匯入品質。

這個階段的核心不是「先做推薦模型」，而是先建立可靠的教材與題庫基礎。

```text
Textbook PDF / DOCX
        │
        ▼
教材解析與結構化
        │
        ├── Curriculum
        ├── Volume / Chapter / Section
        ├── Textbook Examples
        ├── Exercises / Self-assessment
        └── Visual Assets
        │
        ▼
可追蹤、可驗證的教材資料層
        │
        ▼
Generator / Checker / Practice Runtime 驗證基礎
```

---

## 為什麼先做教材工程

真正的自適應學習不能只靠一個推薦模型。

在進入學生知識狀態建模與個人化推薦之前，系統至少必須先知道：

- 學生正在學哪一本教材、哪一章、哪一節。
- 每一題對應哪個技能與教材來源。
- 題目能否穩定顯示、作答與判分。
- 數學答案是否能以語意而非單純字串判定。
- 圖形、圖片、多小題與作圖題是否有一致的 runtime 規範。
- 學生作答紀錄是否能形成後續研究可使用的 learning evidence。

因此目前先完成：

**教材 → 結構化資料 → 題型／判分／練習基礎**

之後才進一步研究：

**學生作答 → Learning Evidence → Knowledge / Mastery Modeling → Adaptive Decision → 個人化學習與補救**

---

## 目前系統成果

| 項目 | 目前狀態 | 說明 |
| --- | --- | --- |
| 技高數學 B1–B4 curriculum | Phase 1 已導入 | 已納入冊別、章節、小節、技能與教材資料體系。 |
| 教材 PDF / DOCX 匯入 | 已建立 | 支援教材內容解析與結構綁定。 |
| 例題／習題／自我評量 | 已導入 | 依教材來源建立可追蹤的結構化題目資料。 |
| 數學公式與特殊符號 | 已建立處理流程 | 包含 LaTeX、向量、特殊數學符號與異常字元處理。 |
| 教材圖形資產 | 已建立流程 | 可由教材 PDF 擷取必要圖形並掛接到題目資料。 |
| 題型 generator / checker 基礎 | 持續驗證 | 用於確認教材題目能否轉成可執行、可判分的練習內容。 |
| Practice runtime | 持續驗證 | 用於檢查選擇、填充、多小題、圖片、作圖等題型的實際呈現與作答。 |
| 教師／學生展示介面 | 可展示 | 提供目前整合成果的實際操作介面。 |
| 自適應知識狀態模型 | **尚未列為完成成果** | 屬於後續階段。 |
| 個人化 routing / remediation | **尚未列為完成成果** | 屬於後續階段。 |

> **重要說明**：本專案不把「檔案存在」或「程式可以執行」直接視為教材完成。不同章節仍會分別檢查 source coverage、題意正確性、圖形語意、checker 與瀏覽器實際呈現。

---

## Phase 1 系統架構

```text
教材來源
PDF / DOCX
    │
    ▼
Textbook Import Pipeline
    │
    ├── 章節與小節辨識
    ├── 題目文字與數學式解析
    ├── 例題／練習／自評分類
    ├── Curriculum Binding
    └── Visual Asset Extraction
    │
    ▼
結構化教材資料
    │
    ├── curriculum / chapter / section
    ├── skill metadata
    ├── textbook examples
    ├── source traceability
    └── image assets
    │
    ▼
題庫工程驗證
    │
    ├── GenCode / generator
    ├── validator
    ├── checker
    └── practice runtime
```

主要程式責任分布：

- `app.py`：Flask application factory 與主要 Web 入口。
- `core/`：教材匯入、資料服務、practice、GenCode 等核心邏輯。
- `textbook_import/`：教材匯入相關流程與資產。
- `skills/`：已整理／發布的題型與 checker。
- `generators/`：可重用的題型生成邏輯。
- `validators/`、`core/validators/`：題目與程式驗證。
- `core/healers/`：生成程式的 regex / AST 修復。
- `agent_skills*`：skill / family / prompt / evaluation metadata。
- `templates/`、`static/`：學生與教師 Web UI。
- `tests/`：regression、integration 與 runtime contract tests。
- `reports/`：教材匯入、GenCode、coverage、acceptance 等驗證紀錄。
- `docs/`：架構、SOP、runtime contract 與長期技術文件。

完整目錄說明見 [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)。

---

## Practice Runtime 驗證原則

教材匯入完成後，仍需要確認題目在實際學生介面中可以正確使用。

目前技高 B1–B4 共用 practice runtime 規範，主要檢查：

- 單選題、填充題與多小題的作答格式。
- 數學式與方程式的等價判定。
- 向量與特殊數學符號的輸入與顯示。
- 教材圖片與動態圖形的掛接。
- 作圖題與手寫區的互動規則。
- reference diagram 與學生 drawing layer 分離。
- chapter / skill 與題目來源的對應關係。

詳細規範見 [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md)。

---

## 教授／評審快速查看

### 1. 直接看 Demo

▶️ **https://mathb.math-adaptive.org/review-demo**

這是最快了解目前成果的方式，可瀏覽目前教材、學生練習與教師端整合畫面。

### 2. 看工程結構

建議依序閱讀：

1. 本 `README.md`
2. [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md)
3. [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md)
4. `reports/` 中保留的教材匯入、coverage、GenCode 與 acceptance evidence
5. `tests/` 中的 regression 與 contract tests

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

需要雲端 AI 功能時再設定：

```env
GEMINI_API_KEY=your_google_api_key
```

可選：

```env
MATHPROJECT_DATABASE_URI=sqlite:///...
WAITRESS_THREADS=10
```

### 4. 開發模式

```powershell
python app.py
```

預設：

```text
http://127.0.0.1:5000
```

### 5. Production（Windows）

```powershell
.\run_production.bat
```

### 6. Health check

```text
GET /healthz
```

---

## 主要技術

| 類別 | 技術 |
| --- | --- |
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| Production WSGI | Waitress |
| Database | SQLite / SQLAlchemy |
| Math rendering | MathJax 3 SVG |
| AI / multimodal | Google Gemini integration、OCR / vision related utilities |
| Document processing | PyMuPDF, python-docx, pypdf, pypandoc |
| Data / reporting | pandas, NumPy, openpyxl, Matplotlib |
| Testing | pytest + browser / contract / integration regression suites |

---

## 測試與品質控制

`tests/` 是目前教材工程的重要品質證據，不是暫存檔案。

常用測試：

```powershell
pytest -q
```

教材與題型進入正式學生端前，至少需要區分：

```text
source coverage
→ curriculum binding
→ formula / symbol correctness
→ visual asset correctness
→ generator / checker validation
→ runtime rendering
→ browser / human acceptance
```

這也是本專案保留 regression tests、runtime contract 與 acceptance evidence 的原因。

---

## Repository Hygiene

為避免教材研究與開發過程產生的中介檔案污染 repository：

- 正式程式放在 `core/`、`scripts/`、`skills/`、`generators/` 等維護目錄。
- regression tests 放在 `tests/`。
- 長期技術文件放在 `docs/`。
- 正式驗證證據集中於 `reports/`。
- pytest cache、DB、WAL、local backup、probe、export 等由 `.gitignore` 排除。
- 不將本機 SQLite database、IDE cache 或一次性測試輸出提交到 repository。

---

## 後續研究與開發方向

Phase 1 完成教材基礎後，後續預計依序進行：

1. **Learning Evidence** — 整理學生作答紀錄、錯誤型態、作答時間與章節進度等可用證據。
2. **Knowledge / Mastery Modeling** — 定義可以反映學生學習狀態的表示方式與評估方法。
3. **Adaptive Decision** — 研究下一題、下一技能與補救內容的個人化決策策略。
4. **Remediation** — 建立前置知識診斷與補救路徑。
5. **Evaluation** — 透過模擬實驗與實際學生使用資料評估自適應策略是否真的改善學習。

上述項目屬於**後續 roadmap**，不是目前 README 所宣稱的已完成功能。

---

## 核心文件

- [`docs/REPOSITORY_STRUCTURE.md`](docs/REPOSITORY_STRUCTURE.md) — repository 結構與檔案治理規則
- [`docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`](docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md) — 技高 B1–B4 practice runtime contract
- `reports/` — 教材匯入、GenCode、coverage、acceptance 等驗證紀錄
- `tests/` — regression、integration 與 runtime contract tests

---

## 專案目前的核心價值

目前 **AI自適應學習平台(技術型高中版)** 最重要的成果，是先把技術型高中數學 B1–B4 從原始教材轉成可追蹤、可驗證、可持續擴充的系統化教材資料與題庫基礎。

這個 Phase 1 基礎將作為後續 learning evidence、knowledge modeling 與真正自適應決策研究的起點。