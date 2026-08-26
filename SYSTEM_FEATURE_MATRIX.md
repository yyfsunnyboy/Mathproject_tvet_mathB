# AI 自適應學習系統 (Mathproject TVET Math B)｜全系統功能狀態矩陣 (Feature Matrix)

> **狀態圖例說明**：
> * **✅ 已完成**：前端可操作、後端接通、資料庫有實際資料流、主流程可完整走完、有測試或實際運作數據。
> * **🟡 半完成**：功能可用但僅限特定情境、有 UI 但底層未持久化、或為單次 Demo 尚未產品化。
> * **🔵 開發中**：有明確核心程式碼/離線訓練腳本/近期實作痕跡，但尚未形成前端完整產品閉環。
> * **⚪ 規劃中／骨架**：僅有資料表預留、UI 按鈕或 TODO/概念，未有完整實作。

---

## 1. 學生端功能矩陣 (Student Features)

| 功能名稱 | 目標使用者 | 狀態 | 前端實作 | 後端實作 | 資料庫支援 | 測試檔案 | 限制與未竟之處 | 驗證證據 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **帳號登入與註冊** | 學生/教師 | ✅ | [templates/login.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/login.html)<br>[templates/register.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/register.html) | [app.py:L98](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L98)<br>[core/routes/auth.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/auth.py) | `users` (408 筆) | `tests/test_core_backup_users_classes.py` | 無忘記密碼/Email 重設機制 | `app.py:L101-L104` (`load_user`) |
| **課綱階層導航** | 學生 | ✅ | [templates/dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/dashboard.html) | [app.py:L467](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L467)<br>[core/utils.py](file:///c:/Projects/Mathproject_tvet_mathB/core/utils.py) | `skill_curriculum` (507 筆)<br>`progress` (102 筆) | `tests/test_admin_skill_display_order.py` | 全域分類視圖之進度彙整尚未支援多對多細緻拆分 | `dashboard.html:L1-L200` |
| **動態互動題目練習** | 學生 | ✅ | [templates/index.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/index.html)<br>[static/js/choice_math.js](file:///c:/Projects/Mathproject_tvet_mathB/static/js/choice_math.js) | [core/routes/practice.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/practice.py) | `skills_info` (496 筆)<br>`textbook_examples` (4,228 筆) | `tests/test_practice_question_session.py` | JS 邏輯過度集中於 `index.html` 內嵌腳本 | `core/routes/practice.py:L50-L150` |
| **符號數學自動批改** | 學生 | ✅ | `index.html` (AJAX 提交) | [core/domain_functions.py](file:///c:/Projects/Mathproject_tvet_mathB/core/domain_functions.py)<br>[core/math_formula_normalizer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/math_formula_normalizer.py) | `progress` (記錄過關次數) | `tests/test_gencode_expression_equivalence_checker.py` | 高階幾何證明題尚未支援自動證明 | `core/routes/practice.py:check_answer` |
| **電子計算紙 (Scratchpad)** | 學生 | ✅ | [templates/index.html:L56](file:///c:/Projects/Mathproject_tvet_mathB/templates/index.html#L56) (Canvas) | 前端 Base64 處理 | 前端記憶體 / Session | `tests/test_adaptive_practice_drawing_frontend.py` | 筆跡未以向量資料庫持久化保存 | `templates/index.html:L56-L69` |
| **AI 手寫拍照/畫布辨識** | 學生 | ✅ | `index.html` (Canvas 辨識鈕) | [core/handwriting_ai_check.py](file:///c:/Projects/Mathproject_tvet_mathB/core/handwriting_ai_check.py)<br>[core/routes/analysis.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/analysis.py) | 無需表格 (即時轉譯) | `tests/test_ai_check_handwriting.py` | 需連線外部 Gemini API 或本地 Vision 模型 | `POST /api/practice/ai-check-handwriting` |
| **蘇格拉底式 AI 助教對話** | 學生 | ✅ | `index.html` (AI 助教抽屜) | [core/ai_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/ai_analyzer.py)<br>[core/rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/rag_engine.py) | `prompt_templates` (8 筆) | `tests/test_chat_follow_up_prompts.py` | 本地小模型模式下對長對話意圖控制偶有漂移 | `POST /chat_ai`, `POST /api/rag_chat` |
| **非選題樹狀圖繪製** | 學生 | ✅ | [templates/free_response_practice.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/free_response_practice.html) | [core/routes/free_response_practice.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/free_response_practice.py) | 前端 Session | `tests/test_phase5f_d_free_response_practice_route.py` | 目前專用於 B4 排列組合與機率樹狀圖 | `GET /free_response_practice` |
| **錯題本複習與收藏** | 學生 | 🟡 | [templates/mistake_notebook.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/mistake_notebook.html) | [core/routes/analysis.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/analysis.py) | `mistake_notebook_entries` (3 筆)<br>`mistake_logs` (0 筆) | `tests/test_b4_3_2_review_payload_repair.py` | 需手動收藏或特定模式觸發，日常練習未自動全量記錄 | `GET /mistake-notebook` |
| **個人診斷雷達圖** | 學生 | 🟡 | [templates/student_diagnosis.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/student_diagnosis.html) | [core/diagnosis_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/diagnosis_analyzer.py) | `learning_diagnosis` (0 筆，由記憶體即時計算) | `tests/test_rag_diagnosis_mapping.py` | 診斷報告未持久化至 DB 作歷史版本對比 | `GET /student/diagnosis` |
| **試卷拍照上傳 OCR** | 學生 | 🟡 | [templates/exam_upload.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/exam_upload.html) | [core/routes/exam.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/exam.py)<br>[core/exam_analyzer.py](file:///c:/Projects/Mathproject_tvet_mathB/core/exam_analyzer.py) | `exam_analysis` (0 筆，單次轉發) | `tests/test_classify_image_text_consistency.py` | 缺少多頁試卷拼合與歷史段考歸檔管理 | `POST /upload_exam` |
| **知識圖譜可視化導航** | 學生/教師 | 🟡 | [templates/knowledge_graph.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/knowledge_graph.html) | [core/routes/knowledge_graph.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/knowledge_graph.py) | `kg_outputs/*.json` (26 檔案) | `test_kg_loader.py` | 國中單元完整，高中/技高部分節點仍為靜態 YAML/CSV | `GET /knowledge-graph` |
| **相似題生成推薦** | 學生 | 🔵 | [templates/similar_questions.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/similar_questions.html) | [core/routes/practice.py:L800](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/practice.py) | 依賴 Prompt 即時生成 | `tests/test_phase4f_main_a_adaptive_generator_first.py` | 依賴即時 LLM 呼叫，延遲較高且缺少變形難度控制 | `POST /generate-similar-questions` |
| **同儕競賽與即時對戰** | 學生 | ⚪ | 無 | 無 | 無 | 無 | 僅在架構概念討論中，無程式碼 | 無 |

---

## 2. 教師端與班級管理矩陣 (Teacher Features)

| 功能名稱 | 目標使用者 | 狀態 | 前端實作 | 後端實作 | 資料庫支援 | 測試檔案 | 限制與未竟之處 | 驗證證據 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **班級建立與邀請碼** | 教師 | ✅ | [templates/teacher_dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_dashboard.html) | [core/routes/classroom.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/classroom.py) | `classes` (1 筆)<br>`class_students` (33 筆) | `tests/test_core_backup_users_classes.py` | 無班級學期歸檔與多位協同教師權限 | `POST /classes/create` |
| **學生 Excel 批次匯入** | 教師 | ✅ | `teacher_dashboard.html` (匯入彈窗) | [core/routes/classroom.py:L120](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/classroom.py#L120) | `users`, `class_students` | `tests/test_core_roundtrip_21sheet_import.py` | 格式錯誤時之提示訊息可再更具體 | `POST /api/classes/<id>/students/upload` |
| **課綱與技能編修後台** | 教師/管理員 | ✅ | [templates/admin_skills.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_skills.html)<br>[templates/admin_curriculum.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_curriculum.html) | [core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py) | `skills_info`, `skill_curriculum` | `tests/test_admin_skill_display_order.py` | 調整順序時需手動填寫 index | `GET /skills`, `GET /curriculum` |
| **教科書範例題目管理** | 教師/管理員 | ✅ | [templates/admin_examples.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/admin_examples.html) | [core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py) | `textbook_examples` (4,228 筆) | `tests/test_admin_v3_example_lifecycle.py` | 題目數量龐大時分頁載入速度需加強 | `GET /examples` |
| **AI Prompt 與金鑰設定** | 管理員 | ✅ | [templates/ai_prompt_settings.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/ai_prompt_settings.html) | [core/routes/admin.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/admin.py)<br>[core/ai_wrapper.py](file:///c:/Projects/Mathproject_tvet_mathB/core/ai_wrapper.py) | `prompt_templates` (8 筆) | `tests/test_ai_config_gemini_models.py` | 目前支援 Gemini 與 Local AI，尚未開放多租戶自訂金鑰 | `POST /test_api_key` |
| **B4 第二章可見度稽核** | 教師 | ✅ | [templates/teacher_b4_chap2_audit.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_b4_chap2_audit.html) | [core/routes/b4_chap2_teacher_audit.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/b4_chap2_teacher_audit.py) | `b4_chap2_visibility_audit_logs` (220 筆) | `tests/test_b4_chap2_phase6j_teacher_audit_visibility.py` | 專為 B4 第 2 章設計，其他章節無獨立 audit log 表 | `GET /teacher/b4-chap2-audit` |
| **教師班級學習分析面板** | 教師 | 🟡 | [templates/teacher_dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_dashboard.html)<br>[templates/teacher_analysis.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_analysis.html) | [app.py:teacher_dashboard](file:///c:/Projects/Mathproject_tvet_mathB/app.py) | `class_students`, `progress` | `tests/test_b4_chap2_phase6n_r_dashboard_link.py` | 數據依賴即時 Join，缺少預聚合統計快取表 | `GET /teacher_dashboard` |
| **Word/MathType 教材匯入器** | 管理員 | 🟡 | [templates/textbook_importer_v2.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/textbook_importer_v2.html) | [core/textbook_processor_v2.py](file:///c:/Projects/Mathproject_tvet_mathB/core/textbook_processor_v2.py) | `textbook_examples` | `tests/test_docx_importer.py` | 轉檔超過 30 秒易受 HTTP 超時限制，需導入非同步佇列 | `GET /textbook_importer_v2` |
| **自訂作業指派與排程** | 教師 | ⚪ | [templates/teacher_dashboard.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/teacher_dashboard.html) (靜態介面預留) | 無獨立作業指派 Table 與排程 Route | 無作業指派表 | 無 | 僅在 UI 預留按鈕，無實體作業發派功能 | `teacher_dashboard.html:作業按鈕` |

---

## 3. 自適應學習與題庫生成矩陣 (Adaptive & Question Bank)

| 功能名稱 | 目標使用者 | 狀態 | 前端實作 | 後端實作 | 資料庫支援 | 測試檔案 | 限制與未竟之處 | 驗證證據 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **章節自適應練習閉環** | 學生 | ✅ | [templates/adaptive_practice_v2.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/adaptive_practice_v2.html) | [core/adaptive/session_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/adaptive/session_engine.py)<br>[core/adaptive/routing.py](file:///c:/Projects/Mathproject_tvet_mathB/core/adaptive/routing.py) | `adaptive_learning_logs` (344 筆)<br>`skill_family_bridge` (67 筆) | `tests/test_adaptive_m2_api.py` | 跨冊別超大範圍補救路徑目前主要覆蓋 B4 與國中核心 | `POST /api/adaptive/submit_and_get_next` |
| **微生成器題型庫 (v3)** | 學生 | ✅ | `index.html` (動態載入) | `agent_skills_v3/` (733 個腳本)<br>[core/generator_route_resolver.py](file:///c:/Projects/Mathproject_tvet_mathB/core/generator_route_resolver.py) | `gencode_component_tracker` (243 筆) | `tests/test_b4_chap2_phase6c1_probability_basic.py` | 少數邊緣幾何題目之 LaTeX 格式偶有微小排版間距差異 | `agent_skills_v3/` (733 檔案) |
| **PPO 認知路由策略推論** | 系統內部 | ✅ | 無 (後端自動運算) | [core/adaptive/ppo_adapter.py](file:///c:/Projects/Mathproject_tvet_mathB/core/adaptive/ppo_adapter.py) | [models/adaptive/phase2_policy.pt](file:///c:/Projects/Mathproject_tvet_mathB/models/adaptive/phase2_policy.pt) | `tests/test_adaptive_phase2_policy.py` | 狀態特徵向量維度固定為 8 維 | `core/adaptive/ppo_adapter.py:L55` |
| **AKT 深度知識追蹤模型** | 系統內部 | 🔵 | 無 | [train_akt_curriculum.py](file:///c:/Projects/Mathproject_tvet_mathB/train_akt_curriculum.py)<br>[akt_inference.py](file:///c:/Projects/Mathproject_tvet_mathB/akt_inference.py) | [models/akt_curriculum.pth](file:///c:/Projects/Mathproject_tvet_mathB/models/akt_curriculum.pth) (2.6 MB) | `tests/test_skill_policy_trainer_env.py` | 深度神經網路尚未作為在線即時推論微服務部署 | `models/akt_curriculum.pth` |

---

## 4. AI 與輔助工程矩陣 (AI & Engineering)

| 功能名稱 | 目標使用者 | 狀態 | 前端實作 | 後端實作 | 資料庫支援 | 測試檔案 | 限制與未竟之處 | 驗證證據 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **混合式 RAG 檢索** | 學生/助教 | ✅ | `index.html` (觸發提示) | [core/rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/rag_engine.py)<br>[core/advanced_rag_engine.py](file:///c:/Projects/Mathproject_tvet_mathB/core/advanced_rag_engine.py) | ChromaDB + `rag_embeddings_cache.pkl` | `tests/test_adaptive_rag_hint.py` | 向量索引目前於伺服器啟動時全量載入記憶體 | `core/rag_engine.py:init_rag` |
| **題目代碼閉環生成與 AST 自癒** | 開發者/系統 | ✅ | 無 (後台管線) | [core/code_generator.py](file:///c:/Projects/Mathproject_tvet_mathB/core/code_generator.py)<br>[core/healers/](file:///c:/Projects/Mathproject_tvet_mathB/core/healers/) | `skill_gencode_prompt` | `tests/test_ast_healer.py`<br>`tests/test_gencode_pipeline_policy_gate.py` | 自動生成後仍需人工驗證 gate 確保 100% 數學嚴謹 | `core/healers/` |
| **實時 AI 題型生成演示 (Live Show)** | 科研/展示 | ✅ | [templates/live_show.html](file:///c:/Projects/Mathproject_tvet_mathB/templates/live_show.html) | [core/routes/live_show.py](file:///c:/Projects/Mathproject_tvet_mathB/core/routes/live_show.py) | 無需表格 (即時執行) | `tests/test_run_generated_code_regression.py` | 需要可連線之 LLM API Key | `GET /live_show` |
| **Session 防護與 Cookie 自動修剪** | 系統底層 | ✅ | 無 | [core/session_safety.py](file:///c:/Projects/Mathproject_tvet_mathB/core/session_safety.py) | Client-side Session | `app.py:keep_session_cookie_small` | 本地 Session 仍有單一客戶端限制，規模化需 Redis | `app.py:L164-L176` |
| **SQLite WAL 與並行防鎖定** | 系統底層 | ✅ | 無 | [app.py:L727-L735](file:///c:/Projects/Mathproject_tvet_mathB/app.py#L727-L735) | SQLite WAL Mode | 系統正常運行 | 單機檔案資料庫，跨節點叢集時無法橫向擴展 | `PRAGMA journal_mode=WAL` |
| **非同步任務佇列 (Async Queue)** | 系統底層 | ⚪ | 無 | 僅局部 threading | 無 (無 Redis / Celery) | 無 | 耗時 LLM/轉檔任務可能阻塞 Web 工作執行緒 | 缺少 Celery 設定 |

