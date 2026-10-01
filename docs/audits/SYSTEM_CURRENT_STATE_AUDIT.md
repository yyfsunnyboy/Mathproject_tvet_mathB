# AI 自適應學習系統 (Mathproject TVET Math B)｜系統現況與開發進度技術盤點稽核報告

> **審核基準時間**：2026 年 8 月  
> **系統定位**：結合生成式 AI（LLM/Vision）、強化學習（PPO/AKT 知識追蹤）、向量檢索（Hybrid RAG）、程式自動修復（AST Healer）與領域數學規則引擎的國高中/技高數學自適應學習平台。  
> **稽核原則**：本報告依據真實程式碼（Templates、Routes、Models、DB Tables、Tests、Config、Scripts）逐項追蹤驗證，**絕不美化、不把程式骨架誤判為已完成、不因 UI 存在按鈕即認定功能可用**。

---

## 摘要與系統全貌統計

### 1. 核心代碼與資源規模（實體統計）
* **資料庫表格**：`instance/kumon_math.db`（33 張資料表，檔案大小 4.56 MB）
  * 使用者數 (`users`)：408 人（學生 394、教師 13、管理員 1）
  * 技能主檔 (`skills_info`)：496 筆（啟用中 482 筆）
  * 課綱節點 (`skill_curriculum`)：507 筆（橫跨 14 個冊別）
  * 題庫範例 (`textbook_examples`)：4,228 筆教材結構化題目
  * 自適應學習執行日誌 (`adaptive_learning_logs`)：344 筆
  * 斷點家族橋接 (`skill_family_bridge`)：67 筆
  * 自動生成題型代碼組件追蹤 (`gencode_component_tracker`)：243 筆
* **後端路由與架構**：
  * 註冊 Flask 路由：80+ 端點（涵蓋 practice, admin, analysis, classroom, exam, live_show, demo, free_response, knowledge_graph 等 9 大模組/Blueprint）
* **測試套件規模**：
  * 測試檔案數：448 個測試檔（覆蓋適應性路徑、B4題型生成、符號批改、RAG檢索、AST修復、手寫辨識等）
* **微生成器與腳本庫**：
  * `agent_skills_v3/`：733 個自動化題型生成腳本
  * `core/vocational_math_b4/`：28 個專用領域生成與路由模組
  * 知識圖譜節點 JSON：26 個國中/高中結構化知識圖譜檔案 (`kg_outputs/`)

---

## 一、系統成熟度統計與分佈表

| 領域 | ✅ 已完成 (Production Ready) | 🟡 半完成 (Demo/局部閉環) | 🔵 開發中 (WIP Pipeline) | ⚪ 規劃中／骨架 (Stub/Skeleton) | 合計項目 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A. 學生端 (Student UX & Learning)** | 8 | 4 | 2 | 2 | 16 |
| **B. 教師端 (Teacher & Management)** | 6 | 4 | 1 | 2 | 13 |
| **C. 教材與題庫系統 (Curriculum & Bank)** | 5 | 2 | 1 | 1 | 9 |
| **D. AI / LLM / RAG 功能** | 5 | 3 | 2 | 1 | 11 |
| **E. 自適應學習與認知模型 (Adaptive & RL)** | 4 | 3 | 2 | 1 | 10 |
| **F. 系統工程與部署運維 (Engineering & Scale)** | 4 | 3 | 2 | 3 | 12 |
| **總計** | **32** | **19** | **10** | **10** | **71** |

---

## 二、使用者功能逐項深度盤點（附真實代碼與資料庫證據）

### A. 學生端功能 (Student UX)

#### 1. 使用者帳號與身分認證 (Authentication)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/login.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/login.html), [templates/register.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/register.html)
  * 後端：[app.py](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L98-L105), [core/routes/auth.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/auth.py)
  * 資料庫：`users` 表（目前 408 筆，儲存 `username`, `password_hash`, `role`, `email`）
  * 測試：[tests/test_core_backup_users_classes.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_core_backup_users_classes.py)
* **實際行為**：支援學生/教師/管理員登入、註冊密碼加鹽雜湊（Werkzeug Security）、Session 狀態維持與 `@login_required` 保護。
* **限制**：目前尚未實作忘記密碼/Email 重設驗證信機制；無 OAuth/Google 快速登入。

#### 2. 課綱導航與單元選擇 (Curriculum Navigation)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/dashboard.html), [templates/unit_view.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/unit_view.html)
  * 後端：[app.py](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L467-L705), [core/utils.py](file:///c:/Projects/Mathproject_tvet_mathB/core/utils.py)
  * 資料庫：`skill_curriculum` 表（507 筆，含國中7-9年級、高中、技高B1~B4自然排序）
  * 測試：[tests/test_admin_skill_display_order.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_admin_skill_display_order.py)
* **實際行為**：學生可在 Dashboard 依學制（國中/高中/技高）、冊別、章節自然遞增階層展開各節技能卡片，並即時讀取連續答對次數與等級。
* **限制**：若切換為全部分類 (`view=all`) 時，部分跨冊別重複技能之進度彙整是以單一 `skill_id` 為鍵，非多對多映射。

#### 3. 核心題目練習區與動態題目渲染 (Interactive Practice)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/index.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/index.html) (7,093 行)
  * 後端：[core/routes/practice.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/practice.py#L1-L300)
  * 靜態腳本：[static/js/choice_math.js](file:///c:/Projects/Mathproject_tvet_mathB/static/js/choice_math.js), [static/js/visual_spec.js](file:///c:/Projects/Mathproject_tvet_mathB/static/js/visual_spec.js)
  * 測試：[tests/test_practice_question_session.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_practice_question_session.py), [tests/test_practice_visual_spec_rendering.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_practice_visual_spec_rendering.py)
* **實際行為**：支援單選題、整數填答、分數、根式、多項式、區間表示法、座標數對與向量運算，支援 MathJax 3 數學公式渲染與 SVG/Canvas 動態幾何/統計圖表（直方圖、折線圖、樹狀圖）。
* **限制**：前端 JS 邏輯過度集中於 `index.html` 內嵌 script（單檔超過 7,000 行），未進行模組化打包（如 Vite/Webpack）。

#### 4. 領域數學答案即時自動批改 (Symbolic Math Auto-Grading)｜✅ 已完成
* **Evidence**:
  * 後端：[core/domain_functions.py](file:///c:/Projects/Mathproject_tvet_mathB/core/domain_functions.py), [core/fraction_domain_functions.py](file:///c:/Projects/Mathproject_tvet_mathB/core/fraction_domain_functions.py), [core/polynomial_domain_functions.py](file:///c:/Projects/Mathproject_tvet_mathB/core/polynomial_domain_functions.py), [core/math_formula_normalizer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/math_formula_normalizer.py)
  * 路由：`POST /check_answer` ([core/routes/practice.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/practice.py))
  * 測試：[tests/test_gencode_expression_equivalence_checker.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_gencode_expression_equivalence_checker.py), [tests/test_integer_phase1_regression.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_integer_phase1_regression.py)
* **實際行為**：非簡單字串比對，而是具備符號等價性運算（Symbolic Evaluation、分數約分寬容判斷、多項式展開等價檢驗、商式與餘式分解、小數誤差容忍）。
* **限制**：高階微積分或立體幾何複合證明題型目前不支援自動符號證明，僅限於代數/解析幾何與機率統計規範型填答。

#### 5. 電子計算紙與觸控手寫支援 (Scratchpad Canvas)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/index.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/index.html#L56-L69)
  * 樣式與事件：`touch-action: none !important;`、Pointer/Touch 事件監聽、橡皮擦/筆刷寬度/清空畫布。
  * 測試：[tests/test_adaptive_practice_drawing_frontend.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_adaptive_practice_drawing_frontend.py)
* **實際行為**：在 Surface Pro / iPad 觸控筆及滑鼠環境下，學生可在畫面直接計算並即時截圖/提交手寫過程。
* **限制**：筆跡僅儲存於前端 Canvas Base64 或記憶體中，未將每道題目的完整書寫軌跡以向量向量格式（如 InkML/Stroke JSON）永續儲存。

#### 6. AI 手寫拍照/畫布辨識批改 (Handwriting AI Check)｜✅ 已完成
* **Evidence**:
  * 前端：`index.html` 內的手寫識別按鈕與畫布傳送
  * 後端：[core/handwriting_ai_check.py](file:///c:/Projects/Mathproject_tvet_mathB/core/handwriting_ai_check.py), [core/routes/analysis.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/analysis.py#L59-L120)
  * 路由：`POST /api/practice/ai-check-handwriting`
  * 測試：[tests/test_ai_check_handwriting.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_ai_check_handwriting.py)
* **實際行為**：將 Canvas 筆跡轉成 PNG Base64，發送至後端調用 Gemini Vision 或本地模型，提取 LaTeX 數學式並比對答案，回傳結構化辨識結果與批改建議。
* **限制**：依賴有效之雲端 Gemini API Key 或本機 Vision 模型；連線失敗時會觸發 fallback 但無法進行複雜草寫辨識。

#### 7. 蘇格拉底式 AI 助教對話與漸進式提示 (Socratic Tutor Chat)｜✅ 已完成
* **Evidence**:
  * 前端：`templates/index.html` (AI 助教抽屜與即時對話面板)
  * 後端：[core/ai_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/ai_analyzer.py), [core/rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/rag_engine.py), [core/advanced_rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/advanced_rag_engine.py)
  * 路由：`POST /chat_ai`, `POST /api/rag_chat`, `GET /get_suggested_prompts/<skill_id>`
  * 測試：[tests/test_chat_follow_up_prompts.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_chat_follow_up_prompts.py), [tests/test_adaptive_rag_hint.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_adaptive_rag_hint.py)
* **實際行為**：學生卡關時，AI 助教遵循 Prompt 限制，不直接公佈最終答案，而是利用 RAG 檢索同單元先備觀念與定理，進行分步驟提問引導（Scaffolding），並動態給出 3 個追問建議氣泡。
* **限制**：當使用者發送完全無關的閒聊時，雖然有 system prompt 防護，但在純本地小模型模式下可能偶有漂移。

#### 8. 非選題與樹狀圖繪圖作答 (Free Response & Tree Diagram Practice)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/free_response_practice.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/free_response_practice.html)
  * 後端：[core/routes/free_response_practice.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/free_response_practice.py)
  * 路由：`GET /free_response_practice`, `GET /api/free_response/tree_diagram/question`, `POST /api/free_response/tree_diagram/submit`
  * 測試：[tests/test_phase5f_d_free_response_practice_route.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_phase5f_d_free_response_practice_route.py), [tests/test_free_response_drawing_checker.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_free_response_drawing_checker.py)
* **實際行為**：專為 B4 排列組合與機率設計，提供階層式樹狀圖節點繪製與非選題文字步驟驗證。
* **限制**：目前主要涵蓋 B4 第二章樹狀圖與計數原理，其他幾何作圖（如尺規作圖）尚未全面涵蓋。

#### 9. 錯題本與收藏 (Mistake Notebook)｜🟡 半完成 (功能可用但資料流有雙軌歷史)
* **Evidence**:
  * 前端：[templates/mistake_notebook.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/mistake_notebook.html)
  * 後端：[core/routes/analysis.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/analysis.py#L400-L550), [core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py)
  * 資料庫：`mistake_notebook_entries`（3 筆），但 `mistake_logs` 為 0 筆
  * 測試：[tests/test_b4_3_2_review_payload_repair.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_b4_3_2_review_payload_repair.py)
* **狀態說明**：學生可在練習介面將錯題存入錯題本，並於 `/mistake-notebook` 檢視、篩選科目與複習。但資料庫存在 `mistake_logs` 與 `mistake_notebook_entries` 兩張歷史表，目前系統只寫入 `mistake_notebook_entries`，常規練習未自動強制將每一道答錯題目寫入錯題本（需主動收藏或於特定模式觸發）。

#### 10. 學生診斷雷達圖與弱點分析 (Student Diagnosis & Radar Chart)｜🟡 半完成 (前端有展示，依賴即時計算而非持久化報告)
* **Evidence**:
  * 前端：[templates/student_diagnosis.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/student_diagnosis.html)
  * 後端：[core/routes/analysis.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/analysis.py#L200-L350), [core/diagnosis_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/diagnosis_analyzer.py)
  * 資料庫：`learning_diagnosis` 表為 0 筆（診斷結果由前端透過 `/student/analyze_weakness` 即時從 `progress` 與 session 計算生成並渲染 Chart.js 雷達圖，未寫回 `learning_diagnosis` 表）
* **狀態說明**：介面可即時呈現五大維度（計算、觀念、符號、邏輯、應用）之雷達圖與 AI 建議，但歷史診斷歷程未自動持久化歸檔。

#### 11. 試卷拍照上傳與 OCR 診斷 (Exam Paper Upload & Analysis)｜🟡 半完成 (單張可用，缺乏大量批次管理)
* **Evidence**:
  * 前端：[templates/exam_upload.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/exam_upload.html)
  * 後端：[core/routes/exam.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/exam.py), [core/exam_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/exam_analyzer.py)
  * 資料庫：`exam_analysis` 表（目前 0 筆）
* **狀態說明**：支援上傳 JPG/PNG 試卷照片，透過後端進行切題與 OCR 解析，回傳答對與否及知識點歸屬。但未建立完整的「全班試卷批改作業管理系統」與多頁考卷拼合流程。

#### 12. 知識圖譜互動可視化 (Knowledge Graph Visualization)｜🟡 半完成 (國中完整，高中/技高部分檔案化)
* **Evidence**:
  * 前端：[templates/knowledge_graph.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/knowledge_graph.html)
  * 後端：[core/routes/knowledge_graph.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/knowledge_graph.py), [core/kg_data_loader.py](file:///c:/Projects/Mathproject_tvet_mathB/core/kg_data_loader.py)
  * 數據源：`kg_outputs/`（26 個單元 JSON，包含國一上到國二下完整的 nodes 與 prerequisite edges）
  * 測試：[test_kg_loader.py](file:///c:/Projects/Mathproject_tvet_mathB/test_kg_loader.py)
* **狀態說明**：可在瀏覽器透過 Vis.js / D3 互動縮放檢視技能關聯網、先備知識與斷點路徑；但技高 B3/B4 知識圖譜目前以 YAML/CSV 形式存在，尚未全數轉為 `kg_outputs/*.json` 視覺化格式。

---

### B. 教師端功能 (Teacher UX & Classroom)

#### 1. 班級建立與邀請碼機制 (Classroom & Invitation Codes)｜✅ 已完成
* **Evidence**:
  * 後端：[core/routes/classroom.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/classroom.py)
  * 路由：`POST /classes/create`, `POST /class/join`, `POST /classes/regenerate_code/<id>`, `POST /classes/delete/<id>`
  * 資料庫：`classes` 表（1 筆）、`class_students` 表（33 筆）
  * 測試：[tests/test_core_backup_users_classes.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_core_backup_users_classes.py)
* **實際行為**：教師可一鍵建立班級、自動生成英數唯一邀請碼，學生輸入邀請碼即可加入班級。

#### 2. 學生名冊 Excel 批次匯入 (Batch Excel Student Import)｜✅ 已完成
* **Evidence**:
  * 後端：[core/routes/classroom.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/classroom.py#L120-L200)
  * 路由：`POST /api/classes/<class_id>/students/upload`
* **實際行為**：教師上傳包含座號、姓名、帳號的 Excel 檔案，後端自動批次建立學生帳號並綁定至該班級。

#### 3. 教材與章節技能管理後台 (Curriculum & Skills Management)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/admin_skills.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_skills.html), [templates/admin_curriculum.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_curriculum.html)
  * 後端：[core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py)
  * 資料庫：`skills_info`, `skill_curriculum`, `skill_prerequisites`
  * 測試：[tests/test_admin_skill_display_order.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_admin_skill_display_order.py)
* **實際行為**：管理者與教師可新增/修改/刪除技能、調整排序順序 (`order_index`, `display_order`)、設定是否啟用 (`is_active`) 以及指定過關連續答對題數。

#### 4. 教科書範例題庫管理 (Textbook Examples Management)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/admin_examples.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_examples.html), [templates/admin_v3_example_preview.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_v3_example_preview.html)
  * 後端：[core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py)
  * 資料庫：`textbook_examples` 表（4,228 筆）
  * 測試：[tests/test_admin_v3_example_lifecycle.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_admin_v3_example_lifecycle.py)
* **實際行為**：可依冊別、章節檢視教材原始題目、正確答案、詳細解析與題型分類，並支援題目內容編輯與新增。

#### 5. AI Prompt 模板配置與 API Key 管理後台 (AI & Prompt Settings)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/ai_prompt_settings.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/ai_prompt_settings.html)
  * 後端：[core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py), [core/ai_wrapper.py](file:///c:/Projects/Mathproject_tvet_mathB/core/ai_wrapper.py)
  * 路由：`POST /test_api_key`, `GET /api/runtime_ai_status`
  * 測試：[tests/test_ai_config_gemini_models.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_ai_config_gemini_models.py)
* **實際行為**：支援線上填入/驗證 Gemini API Key、切換預設模型（Gemini 3.5 Flash, 3.1 Flash-Lite 等）、查看 Prompt 登錄清單與自動遮罩金鑰。

#### 6. 教師 B4 第二章可見度稽核紀錄 (B4 Chap2 Audit View)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/teacher_b4_chap2_audit.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_b4_chap2_audit.html)
  * 後端：[core/routes/b4_chap2_teacher_audit.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/b4_chap2_teacher_audit.py)
  * 資料庫：`b4_chap2_visibility_audit_logs` 表（220 筆）
  * 測試：[tests/test_b4_chap2_phase6j_teacher_audit_visibility.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_b4_chap2_phase6j_teacher_audit_visibility.py)
* **實際行為**：專供教師查閱排列組合與機率題型之出題與過濾紀錄（確定性題目派發 vs 門檻過濾紀錄）。

#### 7. 教師儀表板與班級作答概況 (Teacher Dashboard & Analytics)｜🟡 半完成 (UI完備，數據即時查詢但缺少預聚合快取)
* **Evidence**:
  * 前端：[templates/teacher_dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_dashboard.html) (1,612 行), [templates/teacher_analysis.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_analysis.html)
  * 後端：[app.py](file:///c:/Projects/Mathproject_tvet_mathB/app.py), [core/routes/classroom.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/classroom.py)
* **狀態說明**：UI 介面極度精緻完整（包含班級卡片、學生列表、近期進度、弱點警示），後端可動態撈取 `class_students` 與 `progress`。但由於尚未建立日/週分析統計匯總表（Daily Aggregations），當學生量達到數百人時，即時 SQL Join 運算會加重 SQLite 負擔。

#### 8. Word (DOCX) / MathType 教材自動解析與匯入器 (Textbook DOCX Importer)｜🟡 半完成 (底層解析器極強，UI 缺少非同步進度條)
* **Evidence**:
  * 前端：[templates/textbook_importer.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/textbook_importer.html), [templates/textbook_importer_v2.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/textbook_importer_v2.html)
  * 後端：[core/textbook_processor.py](file:///c:/Projects/Mathproject_tvet_mathB/core/textbook_processor.py) (347 KB), [core/textbook_processor_v2.py](file:///c:/Projects/Mathproject_tvet_mathB/core/textbook_processor_v2.py) (210 KB)
  * 測試：[tests/test_docx_importer.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_docx_importer.py), [tests/test_batch_mathtype_convert_docx_auto.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_batch_mathtype_convert_docx_auto.py)
* **狀態說明**：後端擁有極其完整的 MathType OLE 方程式提取、WMF/EMF 轉換、LaTeX 轉換與正則結構切分演算法；但大檔案匯入時容易超出 HTTP 請求超時時間，目前透過 Server-Sent Events (`/importer/stream/<task_id>`) 部分改善，但未串接 Redis/Celery 任務佇列。

---

### C. 教材與題庫系統 (Curriculum & Question Bank)

#### 1. 課綱覆蓋程度與現況數據 (Curriculum Coverage)｜✅ 已完成
* **真實資料庫統計**：
  * 總冊別數：**14 冊**
    * 國中：數學1 (36 技能)、數學1上 (41 技能)、數學1下 (27 技能)、數學2 (36 技能)、數學2上 (34 技能)、數學2下 (64 技能)、數學3A (37 技能)、數學3上 (38 技能)、數學3下 (10 技能)、數學4A (38 技能)
    * 技高：數學B1 (45 技能, 321 題)、數學B4 (40 技能, 253 題)
    * 高中選修：選修數學甲(上) (26 技能)、選修數學甲(下) (27 技能)
  * 總題庫範例：**4,228 題**
  * 啟用中核心技能：**482 項**

#### 2. 自動化參數題目生成器 (Algorithmic Question Generators)｜✅ 已完成
* **Evidence**:
  * 實體檔案：`agent_skills_v3/`（733 個獨立微生成器腳本）、`core/vocational_math_b4/`（28 個生成器）
  * 路由派發：[core/generator_route_resolver.py](file:///c:/Projects/Mathproject_tvet_mathB/core/generator_route_resolver.py)
  * 測試：[tests/test_generator_route_resolver.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_generator_route_resolver.py), [tests/test_b4_chap2_phase6c1_probability_basic.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_b4_chap2_phase6c1_probability_basic.py)
* **實際行為**：包含排列、組合、二項式定理、機率基本性質、條件機率、獨立事件、期望值、多項式長除法、絕對值不等式、坐標幾何等，每次請求透過 Python 隨機參數動態產出全新題目、干擾選項與詳細解析。

---

### D. AI 與生成式輔助功能 (AI & LLM Integration)

#### 1. 混合式知識檢索與斷點補救 RAG (Hybrid RAG & ChromaDB)｜✅ 已完成 (核心能力)
* **Evidence**:
  * 後端：[core/rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/rag_engine.py), [core/advanced_rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/advanced_rag_engine.py)
  * 向量快取：`configs/rag_embeddings_cache.pkl` (231 KB)
  * 索引規模：記憶體/Chroma 索引 281 筆知識節點與 67 筆斷點家族橋接 (`skill_family_bridge`)
  * 模型：`shibing624/text2vec-base-chinese` 語義嵌入模型 + BM25 關鍵字混合檢索
  * 測試：[tests/test_adaptive_rag_hint.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_adaptive_rag_hint.py)
* **實際行為**：先執行 Naive RAG 比對；若語意相似度分數超過閾值（預設 0.35），則啟動 Advanced RAG 擴展檢索先備技能與常見錯誤型態（Misconception Nodes），精準提供診斷提示。

#### 2. 題目代碼生成閉環與 AST 自動修復 (GenCode Closed-Loop & AST Healer)｜✅ 已完成 (研究/後台能力)
* **Evidence**:
  * 後端：[core/code_generator.py](file:///c:/Projects/Mathproject_tvet_mathB/core/code_generator.py), [core/prompt_architect.py](file:///c:/Projects/Mathproject_tvet_mathB/core/prompt_architect.py), [core/healers/](file:///c:/Projects/Mathproject_tvet_mathB/core/healers/)
  * 測試：[tests/test_ast_healer.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_ast_healer.py), [tests/test_gencode_pipeline_policy_gate.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_gencode_pipeline_policy_gate.py)
* **實際行為**：當 LLM 生成題目 Python 代碼時，系統會自動在隔離環境語法解析（AST），若發現未引用模組、不平衡括號、死迴圈或動態取樣失敗，自動啟動 AST 修復器與正則修復器（Self-Healing），修復通過後才標記發布。

#### 3. AI 實時題目生成與思維鏈展示 (Live Show Mode)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/live_show.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/live_show.html)
  * 後端：[core/routes/live_show.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/live_show.py), [core/routes/live_show_pipeline.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/live_show_pipeline.py)
  * 路由：`GET /live_show`, `POST /api/generate_live`, `POST /api/run_generated_code`, `GET /api/stream_thought_ab1`
  * 測試：[tests/test_run_generated_code_regression.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_run_generated_code_regression.py)
* **實際行為**：專供展示/科研使用，可即時輸入任意數學概念，系統調用 LLM 生成 Python 代碼、串流展示推理解析，並即時在畫面上安全執行並渲染題目。

---

### E. 自適應學習與認知模型 (Adaptive Learning & Policy)

#### 1. 完整自適應閉環路徑 (End-to-End Adaptive Loop)｜✅ 已完成
* **流程閉環驗證**：
  $$\text{學生答題} \xrightarrow{\text{POST /api/adaptive/submit}} \text{批改與認知狀態判定} \xrightarrow{\text{APR/Frustration更新}} \text{PPO/Progression策略選擇} \xrightarrow{\text{檢索微生成器/補救橋接}} \text{下一題派發}$$
* **Evidence**:
  * 前端：[templates/adaptive_practice_v2.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/adaptive_practice_v2.html)
  * 後端：[core/adaptive/session_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/adaptive/session_engine.py) (4,191 行), [core/adaptive/routing.py](file:///c:/Projects/Mathproject_tvet_mathB/core/adaptive/routing.py)
  * 模型權重：[models/adaptive/phase2_policy.pt](file:///c:/Projects/Mathproject_tvet_mathB/models/adaptive/phase2_policy.pt), [models/akt_curriculum.pth](file:///c:/Projects/Mathproject_tvet_mathB/models/akt_curriculum.pth)
  * 資料庫紀錄：`adaptive_learning_logs`（344 筆真實學習紀錄）
  * 測試：[tests/test_adaptive_m2_api.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_adaptive_m2_api.py), [tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py)
* **實際行為**：在章節自適應模式（Chapter Adaptive Mode）下，學生答錯時不會直接硬跳下一題，而是透過 PPO Policy 評估當前 APR（精熟度）與挫折指數（Frustration Index），動態在「原題型鞏固 (stay)」、「退回先備斷點補救 (remediate)」、「返回主線 (return)」三種動作間切換。

#### 2. AKT (Attentive Knowledge Tracing) 與離線訓練管線｜🔵 開發中 / 研究階段
* **Evidence**:
  * 訓練代碼：[train_akt_curriculum.py](file:///c:/Projects/Mathproject_tvet_mathB/train_akt_curriculum.py), [akt_v2.py](file:///c:/Projects/Mathproject_tvet_mathB/akt_v2.py), [akt_inference.py](file:///c:/Projects/Mathproject_tvet_mathB/akt_inference.py)
  * 數據集：`synthesized_training_data.csv` (3.3 MB)
* **狀態說明**：PyTorch AKT 模型已完成課綱感知數據訓練並導出 `.pth` 權重（2.6 MB），但在即時 Web 服務（Web Runtime）中，目前主要由規則引擎與輕量級 PPO Policy (`phase2_policy.pt`) 承擔低延遲路由，AKT 深度模型尚未完全作為在線即時推論的主力微服務。

---

### F. 系統工程與部署運維 (Systems Engineering)

#### 1. 安全機制與 Session 防護｜✅ 已完成
* **Evidence**:
  * 後端：[core/session_safety.py](file:///c:/Projects/Mathproject_tvet_mathB/core/session_safety.py), [core/env_secrets.py](file:///c:/Projects/Mathproject_tvet_mathB/core/env_secrets.py)
  * 測試：[tests/test_secret_management_policy.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_secret_management_policy.py)
* **實際行為**：針對 Flask Client-side Cookie 4KB 上限實作 `trim_session_for_cookie_limit` 自動修剪機制，防止存入過大題目 JSON 導致 Cookie Overflow / 400 Bad Request；所有 API 金鑰均實作記憶體安全遮罩與日誌脫敏。

#### 2. 資料庫鎖定與 WAL 模式防護｜✅ 已完成
* **Evidence**:
  * [app.py](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L138-L141), [app.py](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L727-L735)
* **實際行為**：啟用 SQLite WAL (Write-Ahead Logging) 模式與 `timeout=30` 秒等待機制，大幅降低多使用者同時寫入作答紀錄時的 `database is locked` 衝突。

#### 3. 單元維護與資料庫安全重置 (Database Maintenance Scope)｜✅ 已完成
* **Evidence**:
  * 前端：[templates/db_maintenance.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/db_maintenance.html)
  * 後端：[core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py)
  * 測試：[tests/test_admin_db_core_clear_scope.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_admin_db_core_clear_scope.py), [tests/test_admin_db_core_outline_preserve.py](file:///c:/Projects/Mathproject_tvet_mathB/tests/test_admin_db_core_outline_preserve.py)
* **實際行為**：提供精確的資料庫維護介面，可選擇只清空作答紀錄或只重置題庫，嚴格保護使用者帳號與課綱大綱結構不被誤刪。

---

## 三、特別稽核：容易被誤認為已完成的功能 (False Completion Audit)

1. ⚠️ **學習診斷歷史資料表 (`learning_diagnosis`)**：
   * *誤區*：前端有漂亮的「學生個人診斷報告」雷達圖頁面 (`student_diagnosis.html`)。
   * *真實狀況*：該圖表是前端發送 AJAX 請求後，後端從當前記憶體與最近進度即時計算返回，**資料庫中的 `learning_diagnosis` 資料表目前為 0 筆**，並未建立歷次診斷的歷史歸檔與長期趨勢追蹤。
2. ⚠️ **傳統題目作答表 (`questions` & `quiz_attempts`)**：
   * *誤區*：Schema 內定義了標準的 `questions` 與 `quiz_attempts` 表。
   * *真實狀況*：系統已全面轉向演算法微生成器與章節自適應日誌 (`adaptive_learning_logs`)，**傳統靜態題庫表 `questions` 與 `quiz_attempts` 為 0 筆**。
3. ⚠️ **先備知識資料庫關聯表 (`skill_prerequisites`)**：
   * *誤區*：Schema 內有 `skill_prerequisites` 表。
   * *真實狀況*：DB 中該表目前為 0 筆，先備關聯已轉由 `skill_family_bridge` (67 筆) 以及靜態配置文件 `configs/adaptive/subskill_remediation.yaml` 與 `kg_outputs/` 維護。
4. ⚠️ **全自動試卷分析系統 (`exam_analysis`)**：
   * *誤區*：前端有「試卷診斷上傳」介面。
   * *真實狀況*：目前為單次體驗型 Demo，上傳後即時辨識與解析，但**資料庫 `exam_analysis` 表為 0 筆**，尚未形成完整的學期段考試卷歸檔資料夾。

---

## 四、特別挖掘：已具備強大能力但介面尚未完整產品化的功能 (Hidden Capabilities)

1. 🌟 **AST Code Self-Healing (程式碼自癒引擎)**：
   * `core/healers/` 擁有高達數十種針對 Python 代碼 AST 語法樹的自動修復規則（自動補齊 missing imports、修正 eval 安全隱患、修復正則邊界、動態取樣重試），在科研與生成管線表現極強，但一般學生/教師在日常練習介面感受不到此底層機制的運作。
2. 🌟 **技高 B4 全章節確定性微生成器群 (Deterministic Generators)**：
   * 擁有 733 個 `agent_skills_v3/` 腳本與完整 B4 機率統計生成矩陣，能保證各類題型參數不重複且絕對有解，題庫深度遠超一般靜態選擇題題庫。
3. 🌟 **PPO 強化學習與斷點補救路由演算法 (Phase 2 PPO Routing Policy)**：
   * 後端具備完整的狀態向量（APR、挫折指數、連錯次數、步驟數等 8 維特徵）推論模型，能動態決策何時進行「跨領域先備技能降維補救」。

---

## 五、現在真正可以對外（備審／發表）宣稱的產品能力

1. **具備可實際操作的完整學生端與教師端 Web 系統**（支援帳號登入、班級管理、單元導航、即時練習）。
2. **具備自主研發的「符號數學即時自動批改引擎」**（非純字串比對，支援分數、根式、多項式、區間、向量與座標數對等價判斷）。
3. **具備「章節級自適應學習閉環」**（學生作答 $\rightarrow$ 認知診斷 $\rightarrow$ PPO/Rule 策略派題 $\rightarrow$ 斷點先備知識補救 $\rightarrow$ 即時進度更新）。
4. **具備「混合式 RAG 蘇格拉底教學引導」**（結合向量嵌入與知識斷點橋接，提供循序漸進的階梯式提示而非直接給答案）。
5. **具備「多模態手寫辨識與觸控電子計算紙」**（支援觸控筆書寫與 AI 手寫數學式辨識批改）。
6. **具備高達 4,200+ 題教科書範例結構化題庫與 700+ 個動態題型生成器**（深度覆蓋技高數學 B 與國高中核心單元）。

---

## 六、邁向「可穩定服務大量學生規模化平台」的技術缺口

| 評估維度 | 目前現況 (Current State) | 正式規模化需求 (Production Scale Gap) | 嚴重等級 |
| :--- | :--- | :--- | :---: |
| **資料庫架構** | 單機 SQLite (已開 WAL 模式) | 需遷移至 PostgreSQL / MySQL，支援連線池與讀寫分離 | 🔴 高 |
| **高併發與非同步處理** | Flask 內建同步執行緒 | 需導入 Redis + Celery / RQ 處理 LLM 呼叫與 DOCX 轉檔等耗時任務 | 🔴 高 |
| **前端架構與效能** | 7,000+ 行單檔 HTML/Jinja2 內嵌 JS | 需採用 Vue 3 / React + TypeScript 模組化重構，降低渲染負載 | 🟡 中 |
| **AI 成本與 Rate Limit** | 直接對外部 API 發送請求 | 需建立後端請求佇列 (Queue)、語意快取 (Semantic Cache) 與 Token 成本配額控制 | 🔴 高 |
| **即時狀態持久化** | 依賴 Flask Session 與局部日誌 | 需建立 Redis Session Store 與分散式分散式快取 | 🟡 中 |
| **監控與日誌** | 本地檔案 log | 需導入 Prometheus + Grafana 或 Sentry 進行錯誤追蹤與系統健康監控 | 🟡 中 |
| **自動化測試覆蓋** | 448 個後端測試 (覆蓋度高) | 需補充 Playwright / Cypress 前端 E2E 自動化端對端測試 | 🟢 低 |

