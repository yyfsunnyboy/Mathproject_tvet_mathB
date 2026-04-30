# MathProject 高職數學教材匯入與技能生成 SOP v0.1

- 文件版本：v0.1
- 適用專案：Mathproject_tvet_mathB
- 適用範圍：高職數學 B 版教材匯入、題庫生成、技能建模、RAG 與自適應學習流程
- 最後更新日期：2026-04-30
- 維護者：Ivan / MathProject Team

---

## 一、文件目的

本文件用於建立一份可操作、可追蹤、可交接的流程總覽，協助開發者、學生協作者與後續維護者，理解教材從匯入到可用於自適應學習的完整生命週期。  
目前系統已具備教材 PDF 匯入、PDF/OCR 文字擷取、數學式正規化、可疑公式偵測、題目圖片資產保存、AI 結構化分析、課本例題匯入、隨堂練習獨立入庫、多小題 `sub_questions`、自我評量匯入、`skill`/`subskill`/`skill_family` 建立、`domain function` 與無限出題程式生成、RAG 索引與自適應學習流程等能力，因此需要 SOP 明確定義：

- 順序：每一階段先後關係與依賴。
- 責任：各階段主要負責模組與人工複核點。
- 輸入輸出：資料格式、來源、目的地與資料表。
- 驗收點：可用於判定「可上線」、「需回滾」或「需重匯」的檢查準則。

本版為 v0.1，定位為總覽與流程文件，不等同最終完整規格書。

---

## 二、核心觀念定義

### 2.1 教材來源類型 `source_type`

| source_type | 中文名稱 | 說明 | 是否獨立題目 |
|---|---|---|---|
| textbook_example | 課本例題 | 課本中的正式例題 | 是 |
| in_class_practice | 隨堂練習 | 例題後的隨堂練習，需獨立入庫 | 是 |
| chapter_exercise | 章節習題 | 章節後方習題 | 是 |
| self_assessment | 自我評量 | 章末自我評量 / 教師用書詳解題 | 是 |
| exam_practice | 統測題 / 統測補給站 | 統測或升學考試型題目 | 是 |
| generated_question | AI 生成題 | domain function 或 AI 產生的新題 | 是 |
| student_uploaded | 學生上傳題 | 學生自行上傳或手寫辨識題 | 是 |

重點說明：

- `source_type` 是題目來源，不是 `skill`。
- `skill_id` 代表數學能力點（能力分類）。
- 不同 `source_type` 的題目可指向同一個 `skill_id`。
- `in_class_practice`（隨堂練習）是獨立題目，不是例題附屬文字。
- `self_assessment`（自我評量）不是 `skill`，而是題目來源類型。

### 2.2 `skill` / `subskill` / `domain function` 關係

| 名稱 | 說明 | 範例 |
|---|---|---|
| skill | 教材中的主要技能點 | 加法原理、乘法原理、階乘記法 |
| subskill | skill 下的細部能力 | 條件分類、乘法步驟拆解、階乘展開 |
| skill_family | 相近技能或題型家族 | counting_principle_family |
| domain function | 可控出題與解題函式 | generate_factorial_problem() |
| generated question | 由 domain function 產生的題目 | 試求 6! / 4! |

---

## 三、整體流程總覽

```text
教材 PDF / Word / 教師用書 / 自我評量
        ↓
文字擷取 + 圖片資產保存
        ↓
公式正規化 + 可疑公式偵測
        ↓
AI 結構分析
        ↓
章節 / 概念 / 例題 / 隨堂練習 / 習題 / 自我評量入庫
        ↓
skill_id 建立
        ↓
subskill 分析
        ↓
domain function 設計
        ↓
無限出題程式生成
        ↓
程式測試 / AST 檢查 / 解答驗證
        ↓
skill prerequisite / family bridge 建立
        ↓
RAG 索引
        ↓
前端練習 / 自適應學習
```

| 階段 | 主要工作 | 主要輸入 | 主要輸出 | 是否可人工複核 |
|---|---|---|---|---|
| 0 前置設定 | 模型、Prompt、範圍、備份確認 | 系統設定、DB 狀態、匯入目標 | 匯入任務配置 | 是 |
| 1 檔案匯入 | 上傳與匯入類型判斷 | PDF/Word 檔案 | import 任務與進度 | 是 |
| 2 擷取與資產 | 文字擷取、圖像保存 | 原始教材頁面 | extracted_text、image_assets | 是 |
| 3 公式處理 | 正規化與可疑偵測 | extracted_text | normalized_text、warning report | 是 |
| 4 AI 分析 | 章節與題目結構化 | normalized_text、metadata | 結構化 JSON | 是 |
| 5 DB 寫入 | 題目與技能資料入庫 | AI JSON、匯入上下文 | 各資料表紀錄 | 是 |
| 6 skill 生成 | 建立 skill 節點 | concept/section/examples | skill_id 與 skill metadata | 是 |
| 7 subskill 分析 | 細部能力拆解與橋接 | 例題、練習、錯誤型態 | subskill_nodes、bridge 資料 | 是 |
| 8 domain function | 生成可控出題邏輯 | skill/subskill 需求 | 函式規格與實作草案 | 是 |
| 9 無限出題 | 程式化產題與驗證 | domain function、模板 | 可執行產題程式與 metadata | 是 |
| 10 RAG 索引 | 建立檢索知識層 | skills、examples、notes | 向量索引與診斷素材 | 是 |
| 11 前端接軌 | 練習與自適應學習流程 | 題庫、索引、規則 | 使用者可互動學習流程 | 是 |

---

## 四、階段 0：前置設定

匯入前需先完成配置檢查，避免後續出現模型漂移、資料覆寫或範圍污染。

### 4.1 AI 模型設定

- 模型由外部 `config.py` 或後台 AI 模型設定控制。
- importer 不應硬寫模型名稱。
- 可用模型例如：
  - `gemini-3.1-flash-lite-preview`
  - `gemini-3-flash-preview`
  - `gemini-2.5-flash`
- 實際使用模型以系統設定解析結果為準。

### 4.2 Prompt template 狀態

- 若 prompt 由 DB override 控制，需先確認 DB 版本是否與部署版本同步。
- 若 `prompt_registry.yaml` 更新，需執行相對應同步流程，避免舊 prompt 影響結構化輸出。

### 4.3 DB 備份與匯入範圍

- 大規模重匯前必須先備份 SQLite DB。
- 不建議清空全資料庫；建議只清理指定範圍：
  - `curriculum`
  - `publisher`
  - `volume`
  - `chapter`
  - `section`
  - `source filename`

---

## 五、階段 1：教材檔案匯入

### 5.1 入口與支援檔案

- 入口頁面：`/textbook_importer`
- 支援檔案類型：
  - 一般課本 PDF
  - 教師用書 PDF
  - 自我評量 PDF
  - Word / 其他文字來源（若系統支援）

### 5.2 處理流程

1. 使用者上傳檔案。
2. 後端判斷 `import_content_type`。
3. 一般課本走 `textbook` 流程。
4. 自我評量走 `self_assessment` 流程。
5. 狀態頁與 stream log 顯示當前進度。

### 5.3 可能的 log

- `[IMPORT TYPE]`
- `正在從 ... 提取內容`
- `成功從 .pdf 檔案中提取了 N 頁/區塊內容`

---

## 六、階段 2：PDF / OCR 文字擷取與圖片資產保存

### 6.1 文字擷取策略

- 優先使用本機 PDF extraction。
- 此階段通常不消耗 Gemini token。
- 僅在 Gemini Vision / PDF OCR fallback 啟用時才會消耗 token。

### 6.2 正規化前常見問題

PDF 擷取常造成數學式破碎，例如：

- `3 # 3 # 5 # 2`
- `5 1 !`
- `C_0^5` 上下標錯亂
- 多小題誤合併

### 6.3 圖片資產保存設計

- 含圖題目不建議存 base64。
- 圖片以獨立檔案保存於 `uploads/question_assets`。
- `metadata_json` 記錄 `image_assets`。
- v0.1 可先存整頁截圖，`bbox` 由後續版本補強自動裁切。

`metadata_json` 範例：

```json
{
  "has_image": true,
  "needs_image_review": true,
  "image_assets": [
    {
      "asset_type": "page_image",
      "path": "uploads/question_assets/vocational_longteng_數學B4/CH1/1-1/page_004.png",
      "page_index": 4,
      "source_page": 5,
      "bbox": null,
      "needs_crop_review": true,
      "reason": "question contains 如圖",
      "image_description": "樹狀圖"
    }
  ]
}
```

---

## 七、階段 3：公式正規化與可疑公式偵測

### 7.1 主要功能

- `normalize_math_text()`
- `normalize_combination_permutation_notation()`
- `normalize_operator_artifacts()`
- `detect_suspicious_formula()`

### 7.2 處理範例

| 原始抽取 | 正規化 / 處理 |
|---|---|
| `3 # 3 # 5 # 2` | `3 × 3 × 5 × 2` |
| `C_0^5` | `C(5,0)` 或保留為可顯示 LaTeX |
| `P_3^5` | `P(5,3)` |
| `5 1 !` | 標記 `suspicious_factorial` |
| `3!!!!` | 標記 `suspicious_factorial` |
| `C_0^5 + C_1^5 + C_2^6` | 標記 `combination_upper_index_inconsistent` |

### 7.3 警示策略

可疑公式不一定在本階段直接修正；可先標記 `needs_review` 或寫入 warning report，交由人工複核或後續 AI 結構分析階段處理。

---

## 八、階段 4：AI 結構分析

### 8.1 AI 結構分析輸入

- `extracted_text`
- `normalized_text`
- `formula warnings`
- `page metadata`
- `image hints`

### 8.2 AI 輸出 JSON 必要欄位

- `chapters`
- `sections`
- `concepts`
- `examples`
- `practice_questions`
- `sub_questions`
- `source_type`
- `skill_id`
- `linked_example_title`
- `source_page`
- `has_image`
- `image_description`

### 8.3 JSON 範例（例題 + 隨堂練習 + 多小題）

```json
{
  "concept_name": "階乘記法",
  "concept_en_id": "FactorialNotation",
  "examples": [
    {
      "example_title": "例題5",
      "source_type": "textbook_example",
      "problem": "試求下列各式之值：",
      "skill_id": "vh_數學B4_FactorialNotation",
      "sub_questions": [
        {"label": "1", "problem": "3!", "answer": "6"},
        {"label": "2", "problem": "5!", "answer": "120"},
        {"label": "3", "problem": "\\frac{8!}{6!}", "answer": "56"}
      ]
    }
  ],
  "practice_questions": [
    {
      "practice_title": "隨堂練習5",
      "source_type": "in_class_practice",
      "linked_example_title": "例題5",
      "skill_id": "vh_數學B4_FactorialNotation",
      "problem": "試求下列各式之值：",
      "sub_questions": [
        {"label": "1", "problem": "4!", "answer": "24"},
        {"label": "2", "problem": "6!", "answer": "720"},
        {"label": "3", "problem": "\\frac{10!}{8!}", "answer": "90"}
      ]
    }
  ]
}
```

重點規範：

- 隨堂練習是獨立題目。
- `sub_questions` 不可被合併為單一公式字串。
- LaTeX 反斜線需符合 JSON escape 規則。
- `safe_load_gemini_json` 負責修復 Gemini 回傳中的 LaTeX escape 問題。

---

## 九、階段 5：資料庫寫入

### 9.1 主要資料表（依專案現況）

- `skills_info`
- `skill_curriculum`
- `textbook_examples`
- `skill_family_bridge`
- `skill_prerequisites`
- 其他現有表（依實作版本與 migration 結果）

### 9.2 `textbook_examples` 的來源覆蓋

`textbook_examples` 可同時保存下列來源，並以 `source_type` 區分：

- `textbook_example`
- `in_class_practice`
- `chapter_exercise`
- `self_assessment`
- `exam_practice`

### 9.3 去重（dedupe）原則

建議 dedupe key：

`curriculum + publisher + volume + section_title + skill_id + source_type + title + normalized_problem_hash + sub_questions_hash`

必要說明：

- 不可僅使用 `skill_id` 去重，否則不同題目會被誤判重複並被誤刪。

---

## 十、階段 6：skill 生成

### 10.1 生成邏輯

`skill` 由 `concept / section / examples` 推導建立，應維持命名一致、語意單一、可被前端與 RAG 共用。

輸入：

- `concept_name`
- `concept_en_id`
- `concept_description`
- `section_title`
- `examples`

輸出：

- `skill_id`
- `skill_name`
- `skill_ch_name`
- `skill_en_name`
- `curriculum`
- `volume`
- `chapter`
- `section`

### 10.2 範例對照

| concept | skill_id |
|---|---|
| 樹狀圖 | vh_數學B4_TreeDiagramCounting |
| 加法原理 | vh_數學B4_AdditionPrinciple |
| 乘法原理 | vh_數學B4_MultiplicationPrinciple |
| 階乘記法 | vh_數學B4_FactorialNotation |

---

## 十一、階段 7：subskill 分析

`subskill` 用於表示技能底下更細的可診斷能力，來源可包含例題、隨堂練習、常見錯誤型態與解題步驟。

### 11.1 拆解示例

- 乘法原理可拆：
  - 步驟拆解
  - 每步方法數判斷
  - 總方法數相乘
  - 條件限制處理
- 階乘記法可拆：
  - 階乘展開
  - 階乘約分
  - `n!` 方程
  - 多小題辨識

### 11.2 主要輸出

- `subskill_nodes`
- `skill_family_bridge`
- `RAG skill notes`

---

## 十二、階段 8：domain function 生成

`domain function` 的目的不是讓 AI 每次自由出題，而是為各 `skill/subskill` 提供可控、可測試、可驗證的出題與解題邏輯，支援無限題庫與自適應練習品質控管。

### 12.1 建議函式介面

- `generate_question()`
- `solve_question()`
- `check_answer()`
- `explain_solution()`
- `validate_question()`

### 12.2 範例

```python
def generate_factorial_quotient_problem():
    ...
```

---

## 十三、階段 9：無限出題程式生成

### 13.1 輸入

- `skill_id`
- `domain function`
- 題型模板
- 難度參數
- `constraints`

### 13.2 輸出

- Python 出題程式
- `expected_answer`
- `solution_steps`
- `metadata`

### 13.3 生成後檢查

- `py_compile`
- AST parse
- Sympy 驗證
- sample generation
- answer consistency
- difficulty distribution

---

## 十四、階段 10：技能連結與 RAG 索引

### 14.1 技能連結

- `skill_prerequisites`：前置技能、主線技能、補救技能關係。
- `skill_family_bridge`：將 skill 與 family/subskill 進行橋接，支援診斷與路徑回推。

### 14.2 RAG 索引內容

- `concept description`
- `examples`
- `common mistakes`
- `hints`
- `subskill notes`

### 14.3 主要用途

- 錯誤診斷
- 補救教學
- RAG tutor 回答引導
- adaptive learning path 推薦

---

## 十五、階段 11：前端練習與自適應學習接軌

題庫入系統後可應用於：

- 課本例題展示
- 隨堂練習
- 自我評量
- AI 生成題
- 手寫批改
- 錯誤診斷
- 補救教學
- 回到主線

### 15.1 模式區分

#### Assessment mode

- 依主線技能進行測驗。
- 不啟動補救流程。
- 輸出 `mastery` / `breakpoint` / `learning path suggestion`。

#### Teaching mode

- 主線 + 補救並行。
- 依 `fail_streak` / `mastery` / `frustration` 觸發補救。
- 透過 RAG 找補救 skill 與提示內容。
- 補救完成後回到主線。

---

## 十六、匯入後驗收清單

### 16.1 教材匯入驗收

- [ ] PDF 頁數正確
- [ ] `import_content_type` 判斷正確
- [ ] 章節 `section` 正確
- [ ] `concepts` 正確
- [ ] 例題數量正確
- [ ] 隨堂練習數量正確
- [ ] 多小題沒有被合併錯
- [ ] `source_type` 正確
- [ ] `skill_id` 正確
- [ ] LaTeX 顯示正常
- [ ] 有圖題目已保存 `image_assets`
- [ ] suspicious formula 有 log / report
- [ ] dedupe 沒有誤刪
- [ ] RAG 索引可查
- [ ] 前端練習可正常出題

### 16.2 特別檢查 1-1 範例

- [ ] 例題5 正確保留三個小題
- [ ] 隨堂練習5 正確獨立入庫
- [ ] 例題6 正確保留兩個小題
- [ ] 隨堂練習6 正確獨立入庫
- [ ] 不再出現「3! + 6! / 8!」錯誤合併

---

## 十七、常見錯誤與處理

| 問題 | 可能原因 | 檢查位置 | 修正方式 |
|---|---|---|---|
| Gemini JSON 解析失敗 | LaTeX 反斜線未 escape | `safe_load_gemini_json` log | 啟用 sanitizer |
| 公式出現 `3!!!!` | PDF 抽取破碎 | `[FORMULA CHECK]` log | `needs_review` / fallback |
| 隨堂練習漏抓 | prompt 或 parser 未支援 | `[PRACTICE IMPORT]` log | 更新 prompt / parser |
| 圖形題沒圖 | `source_page` 缺失 | `[QUESTION IMAGE]` log | 補 `source_page` / 手動複核 |
| 題目重複 | dedupe key 不完整 | dedupe log | 增加 `source_type + hash` |
| skill 錯誤 | AI 分類錯誤 | `skill_id` / `concept` 對照 | 加入 candidate skill 限制 |
| 模型不正確 | 後台設定或 DB override | `[AI CONFIG RESOLVE]` log | 修正系統設定 |

---

## 十八、重要 log 關鍵字

| 關鍵字 | 用途 |
|---|---|
| `[AI CONFIG RESOLVE]` | 顯示模型與 prompt 的最終解析結果，確認是否有 override。 |
| `[AI MODEL]` | 記錄實際呼叫模型名稱與版本。 |
| `[IMPORT TYPE]` | 顯示匯入內容類型判斷（textbook/self_assessment 等）。 |
| `[FORMULA NORMALIZE]` | 記錄公式正規化前後差異。 |
| `[FORMULA CHECK]` | 輸出可疑公式檢測結果與警示標記。 |
| `[TEXTBOOK IMPORTER]` | 記錄教材匯入主流程執行狀態。 |
| `[PRACTICE IMPORT]` | 記錄隨堂練習與習題抽取、解析與寫入狀態。 |
| `[QUESTION IMAGE]` | 記錄題目圖像資產保存、路徑與 metadata。 |
| `[IMPORT VALIDATION WARNING]` | 匯入驗證異常警示（缺欄位、數量不一致等）。 |
| `[FACTORIAL FALLBACK]` | 階乘類公式解析 fallback 觸發與結果。 |
| `[MULTIPART FIX]` | 多小題修復與拆分策略觸發記錄。 |

---

## 十九、附錄：建議目錄與檔案

目前可能相關檔案如下：

- `app.py`
- `config.py`
- `core/textbook_processor.py`
- `core/math_formula_normalizer.py`
- `core/question_image_assets.py`
- `core/ai_settings.py`
- `core/ai_analyzer.py`
- `templates/textbook_importer.html`
- `templates/ai_prompt_settings.html`
- `tests/test_textbook_gemini_json.py`
- `tests/test_math_formula_normalizer.py`
- `tests/test_textbook_practice_import.py`
- `tests/test_question_image_assets.py`
- `docs/系統SOP/`

---

## 二十、下一版 v0.2 待補

- 自我評量匯入完整 SOP
- OCR Vision fallback SOP
- 圖形自動裁切 bbox
- domain function 生成標準模板
- subskill 命名規則
- RAG 索引重建 SOP
- DB 清理與重匯 SOP
- 實驗報表生成 SOP

