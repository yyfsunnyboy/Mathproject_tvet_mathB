# Route / API Evidence Report

## 1. 已閱讀檔案
- `app.py`
- `adaptive_review_api.py`
- `adaptive_review_integration.py`
- `adaptive_review_mode.py`
- `check_routes.py`
- `templates/adaptive_review_simple.html`
- `templates/adaptive_review.html`
- `templates/adaptive_practice_v2.html`
- `templates/adaptive_learning_entry.html`

## 2. Route Evidence Table

| route_path | http_method | function_name | file_path | line_or_nearby_keyword | directly_observed_purpose | observed_input_keys | observed_output_keys | related_template_or_frontend_call | evidence_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/` | GET | `home` | `app.py` | `@app.route('/')` | 根目錄導向 | N/A | N/A | N/A | 判斷是否登入並導向 |
| `/uploads/question_assets/<path:filename>` | GET | `question_asset_file` | `app.py` | `@app.route('/uploads/question_assets/<path:filename>')` | 下載圖片等靜態檔 | N/A | N/A | N/A | |
| `/login` | GET, POST | `login` | `app.py` | `@app.route('/login', methods=['GET', 'POST'])` | 登入 | `username`, `password`, `role` | N/A | `login.html` | |
| `/register` | GET, POST | `register` | `app.py` | `@app.route('/register', methods=['GET', 'POST'])` | 註冊 | `username`, `password`, `role` | N/A | `register.html` | |
| `/logout` | GET | `logout` | `app.py` | `@app.route('/logout')` | 登出 | N/A | N/A | `login.html` | |
| `/adaptive-review` | GET | `adaptive_review` | `app.py` | `@app.route('/adaptive-review')` | 自適應入口 | N/A | N/A | `adaptive_review_simple.html` | |
| `/teacher_dashboard` | GET | `teacher_dashboard` | `app.py` | `@app.route('/teacher_dashboard')` | 教師首頁 | N/A | N/A | `teacher_dashboard.html` | |
| `/teacher/analysis` | GET | `teacher_analysis` | `app.py` | `@app.route('/teacher/analysis')` | 錯題分析 | N/A | N/A | `teacher_analysis.html` | |
| `/test_api_key` | POST | `test_api_key` | `app.py` | `@app.route('/test_api_key', methods=["POST"])` | 測試 Gemini API Key | `api_key`, `cloud_model`... | `success`, `message`... | N/A | |
| `/debug/session_key_status` | GET | `debug_session_key_status` | `app.py` | `@app.route('/debug/session_key_status')` | 除錯 key 狀態 | N/A | `has_key`, `key_len`... | N/A | |
| `/dashboard` | GET | `dashboard` | `app.py` | `@app.route('/dashboard')` | 學生儀表板 | query: `view`, `curriculum`, `volume`... | N/A | `dashboard.html` | |
| `/api/adaptive-review/start` | POST | `start_review_session` | `adaptive_review_api.py` | `@adaptive_review_bp.route('/start', methods=['POST'])` | 啟動自適應複習會話 (有取得題目、自適應功能) | `student_id`, `history`, `n_recommendations`, `use_rl` | `status`, `data` (包含 `student_id`, `current_apr`, `recommendations`, `session_id`) | `adaptive_review.html`, `adaptive_review_simple.html` |
| `/api/adaptive-review/analyze/<student_id>` | GET | `analyze_student` | `adaptive_review_api.py` | `@adaptive_review_bp.route('/analyze/<student_id>', methods=['GET'])` | 分析學生弱項 (有自適應功能) | query: `history_json` | 未能完整確認 (程式碼截斷) | N/A | |
| `/api/adaptive-review/feedback` | POST | 未知 (僅 docstring 顯示) | `adaptive_review_api.py` | `POST /api/adaptive-review/feedback` | 提交答題反饋 (有送出答案、自適應、補救、返回主線功能) | 推測：`student_id`, `history`, `item_id`, `correct` (從 template 觀察) | 推測：回傳狀態資料 (從 template 觀察) | `adaptive_review.html` | Python 實作細節被截斷 |
| `/api/adaptive-review/question/<item_id>` | GET | 未知 (僅 docstring 顯示) | `adaptive_review_api.py` | `GET  /api/adaptive-review/question/<item_id>` | 獲取題目 (有取得題目功能) | 未能完整確認 | 未能完整確認 | N/A | Python 實作細節被截斷 |
| `/api/adaptive-review/chat` | POST | 未知 (僅 docstring 顯示) | `adaptive_review_api.py` | `POST /api/adaptive-review/chat` | AI 引導式提示 (有 AI 助教功能) | 未能完整確認 | 未能完整確認 | N/A | Python 實作細節被截斷 |
| `/api/adaptive-review/health` | GET | 未知 (僅 docstring 顯示) | `adaptive_review_api.py` | `GET  /api/adaptive-review/health` | 健康檢查 | 未能完整確認 | 未能完整確認 | N/A | Python 實作細節被截斷 |
| `/api/adaptive-review/check-handwriting` | POST | 未知 | `adaptive_review_api.py` (推測) | 僅在 `adaptive_review_simple.html` 的 fetch 呼叫中找到 | 檢查手寫 (有 AI 助教功能) | `image_base64`, `question_text`, `correct_answer` | `is_process_correct`, `reply` | `adaptive_review_simple.html` | 在 HTML 中發現此 endpoint，後端查無此 function 定義 |

## 3. Template API Call Evidence Table

| template_file | api_or_route_called | method | payload_keys_seen | response_keys_used | nearby_keyword | evidence_note |
| --- | --- | --- | --- | --- | --- | --- |
| `adaptive_review_simple.html` | `/api/adaptive-review/check-handwriting` | POST | `image_base64`, `question_text`, `correct_answer` | `is_process_correct`, `reply` | `function checkHandwriting()` | 確認有手寫辨識 API 的 fetch 呼叫 |
| `adaptive_review.html` | `/api/adaptive-review/start` | POST | `student_id`, `history`, `n_recommendations`, `use_rl` | `status`, `data.recommendations`, `data.current_apr` | `async function startReview()` | 啟動會話 |
| `adaptive_review.html` | `/api/adaptive-review/feedback` | POST | `student_id`, `history`, `item_id`, `correct` | `data.data` | `async function submitFeedback(isCorrect)` | 提交答案反饋 |
| `adaptive_learning_entry.html` | `practice.adaptive_summative_page` | GET | `skill_id`, `unit_name`, `mode` (via URL search params) | N/A | `function goAdaptive(mode)` | 點擊教學或評量時透過 `window.location.href` 跳轉 |

## 4. Adaptive / Remediation Field Evidence

| field_name | file_path | function_or_template | context | evidence_note |
| --- | --- | --- | --- | --- |
| `currentMode` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... currentMode: "", ... }` | 確認前端狀態有此欄位 |
| `postMode` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... postMode: "", ... }` | 確認前端狀態有此欄位 |
| `inRemediation` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... inRemediation: false, ... }` | 確認前端狀態有此欄位 |
| `isRemediationActive` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... isRemediationActive: false, ... }` | 確認前端狀態有此欄位 |
| `localRemediationCompleted` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... localRemediationCompleted: false, ... }` | 確認前端狀態有此欄位 |
| `returnReady` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... returnReady: false, ... }` | 確認前端狀態有此欄位 |
| `hasReturnedToMain` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... hasReturnedToMain: false, ... }` | 確認前端狀態有此欄位 |
| `ppoRouteAction` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... ppoRouteAction: "", ... }` | 確認前端狀態有此欄位 |
| `frustrationIndex` | `adaptive_practice_v2.html` | Javascript state object | `const state = { ... frustrationIndex: 0, ... }` | 確認前端狀態有此欄位 |
| `predicted_difficulty` | `adaptive_review_api.py` | `_fetch_seed_question_by_item_id` | `predicted_difficulty = engine.item_properties.get(item_id, {}).get('difficulty', 0.5)` | 來自 AKT 難度推測 |
| `BETA_THRESHOLD` | `adaptive_review_mode.py` | global constant | `BETA_THRESHOLD = 0.65` | 目標掌握度閥值 |
| `max_consecutive_failures` | `adaptive_review_mode.py` | `REVIEW_CONFIG` dictionary | `'max_consecutive_failures': 3` | 連錯次數上限設定 |
| `last_apr` | `adaptive_review_api.py` | `_save_review_state` | SQL query: `last_apr = excluded.last_apr` | 儲存於 `adaptive_review_state` table |
| `mastery` | `adaptive_review_mode.py` | `analyze_weak_skills` | `skill_stats.append({ ... 'mastery': float(np.mean(mastery_scores)) ... })` | 掌握度指標 |

## 5. Unknowns
- 未在提供的 `adaptive_review_api.py` 程式碼中完整看到 `POST /api/adaptive-review/feedback` 的 Python 實作細節，僅在 docstring 中看到描述，以及在 `adaptive_review.html` 中看到前端 fetch 呼叫。
- 未在提供的 `adaptive_review_api.py` 中完整看到 `POST /api/adaptive-review/chat`、`GET /api/adaptive-review/question/<item_id>` 與 `GET /api/adaptive-review/health` 的 Python 實作細節，僅在 docstring 看到定義。
- 未在提供的任何 Python 檔案中看到 `POST /api/adaptive-review/check-handwriting` 的後端實作（僅在 `adaptive_review_simple.html` 看到前端呼叫）。
- 未能完整閱讀 `adaptive_practice_v2.html` 的 JavaScript `<script>` 區塊，因此無法確認該檔案內所有呼叫的 API endpoint 與 payload（程式碼有截斷）。
- 未閱讀 `practice_bp` 所在的檔案，因此無法確認 `adaptive_learning_entry.html` 所呼叫的 `practice.adaptive_summative_page` 路由後端邏輯。
