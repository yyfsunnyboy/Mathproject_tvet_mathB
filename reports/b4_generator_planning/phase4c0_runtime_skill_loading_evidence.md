# Phase 4C-0 skills runtime loading evidence report

## 1. 調查目的
確認目前系統如何由前端傳入 `skill_id`，並在後端載入 `skills/{skill_id}.py` 後呼叫 `generate()` / `check()`；本報告僅提供 runtime 證據，不修改程式。

## 2. 已閱讀檔案
- `app.py`
- `core/routes/__init__.py`
- `core/routes/practice.py`
- `core/session.py`
- `skills/jh_數學1上_FourArithmeticOperationsOfIntegers.py`（代表性 skills module，檢視 `generate/check` 實作與回傳）
- `templates/adaptive_practice_v2.html`
- `templates/index.html`
- `templates/practice.html`（不存在，依指示忽略）

## 3. skill_id 載入 skills/*.py 的位置
| file_path | function_or_route | loading_method | observed_code_keyword | evidence_summary |
|---|---|---|---|---|
| `core/routes/practice.py` | `get_skill(skill_id)` | `importlib.import_module`（module path 拼接） | `importlib.import_module(f"skills.{skill_id}")` | 直接用 `skill_id` 組成 `skills.{skill_id}` 載入模組；失敗回傳 `None`。 |
| `core/routes/practice.py` | `/get_next_question` | `importlib.reload` 或 `importlib.import_module` | `module_path = f"skills.{skill_id}"` | 若模組已載入則 `reload`，否則 `import_module`；之後呼叫 `mod.generate(level=...)`。 |
| `core/routes/practice.py` | `/get_adaptive_question` | 透過 `get_skill`（同上 importlib） | `mod = get_skill(question_template.skill_id)` | 用推薦出的 `question_template.skill_id` 載入對應 skill 模組並呼叫 `generate()`。 |
| `core/routes/practice.py` | `/check_answer` | 透過 `get_skill`（同上 importlib） | `result = mod.check(user_ans, current['answer'])` | 由 session 取當前 skill 後載入模組並呼叫 `check()`。 |
| `core/routes/practice.py` | `/generate-similar-questions` | `importlib.import_module`（module path 拼接） | `importlib.import_module(f"skills.{skill_id}")` | 逐個 skill 載入後，若有 `generate` 就呼叫。 |

## 4. generate() 契約
| required_function | expected_input | expected_output_fields | evidence_file | notes |
|---|---|---|---|---|
| `generate` | 後端主要以 `generate(level=...)` 呼叫（另有 `**kwargs` 可能） | **強需求（由 route 明確檢查/使用）**：`question_text`、`correct_answer`（或可被正規化） | `core/routes/practice.py` | `/get_next_question` 內會把 `question -> question_text`、`answer -> correct_answer` 做補值；若最終缺 `question_text/correct_answer`，會重試並可能失敗。 |
| `generate` | 同上 | **常見附帶欄位（前端可能使用）**：`answer`、`image_base64`、`visual_aids`、`context_string`、`inequality_string` | `core/routes/practice.py`, `templates/index.html`, `templates/adaptive_practice_v2.html` | `check_answer` 用 `current['answer']` 作為 `check()` 第二參數，因此 skill 回傳 `answer` 在現行流程中是實務必要（至少對此 route）。 |
| `generate` | `level=1`（similar questions） | 任意題目 dict，再由 route 補 `skill_id/skill_ch_name` | `core/routes/practice.py` | `/generate-similar-questions` 只檢查 `hasattr(mod,'generate')` 後直接呼叫。 |

## 5. check() 契約
| required_function | expected_input | expected_return_type | evidence_file | notes |
|---|---|---|---|---|
| `check` | `check(user_answer, correct_answer)` | **建議/主流**：`dict`，含 `correct`(bool)、`result`(str) | `core/routes/practice.py` | `/check_answer` 直接讀 `result.get('correct', False)`。 |
| `check` | 同上 | `bool` 也可（後端會包裝成 dict） | `core/routes/practice.py` | 有 `if isinstance(result, bool): result = {'correct': ..., 'result': ...}` 的相容邏輯。 |

## 6. 前端呼叫與資料欄位
| template_file | frontend_function | api_or_route_called | payload_keys | response_keys_used | notes |
|---|---|---|---|---|---|
| `templates/index.html` | `getSkillId()` + `loadQuestion()` | `GET /get_next_question?skill=...&level=...` | query: `skill`, `level`（`skill` 由 URL `/practice/<skill_id>` 解析） | `new_question_text`, `context_string/inequality_string`, `image_base64`, `visual_aids`, `consecutive_correct`, `current_level`, `answer_type` | 傳統練習主流程。 |
| `templates/index.html` | submit handler | `POST /check_answer` | body: `{ answer }` | `correct`, `result`, `suggested_prerequisite` | `check()` 結果最終反映在 `correct/result`。 |
| `templates/adaptive_practice_v2.html` | init (`skillId` from template var) + `postAdaptive` | `POST /api/adaptive/submit_and_get_next` | `basePayload.skill_id`、`mode`、後續 `session_id`, `step_number`, `user_answer` | `question_text/question`, `correct_answer/answer/expected_answer`, `target_subskills`... | adaptive flow 主要走 `/api/adaptive/*`，不是直接呼叫 `skills/*.py`；但前端仍會傳 `skill_id`。 |

## 7. fallback 行為
- `get_skill(skill_id)` 載入失敗：回傳 `None`（`core/routes/practice.py`）。
- `/get_adaptive_question`：`mod` 為 `None` 時回 `500`（`無法載入技能模組 ...`）。
- `/check_answer`：`mod` 為 `None` 時回 `{correct:false, result:"模組載入錯誤"}`。
- `/generate-similar-questions`：單一 skill 載入/生成失敗會 `except: pass`（略過該 skill）。
- `/get_next_question`：import/generate 失敗會進入外層 `except` 回 `500`（`生成題目失敗`）。

## 8. 對 B4 wrapper 的影響
根據現有 evidence：
- `skills/{skill_id}.py` wrapper **最少需要**：
  - `generate(level=..., **kwargs 可選)`
  - `check(user_answer, correct_answer)`
- `generate()` **最少要回傳**（現行練習路由安全值）：
  - `question_text`（或 `question` 可被正規化）
  - `correct_answer`（或 `answer` 可被正規化）
  - `answer`（建議同時提供，因 `/check_answer` 取 session 的 `current['answer']`）
- `check()` **最少要支援**：
  - 回 `dict`：`{"correct": bool, "result": str}`（最穩）
  - 或回 `bool`（後端有兼容包裝，但訊息會是預設字串）
- wrapper 是否可呼叫 `core/vocational_math_b4/generators`：
  - **可以**（從 runtime 載入機制看，後端只要求 `skills.{skill_id}` 模組可 import 並提供 `generate/check`；模組內部可自行 import core 服務）。
- 是否需維持舊欄位名稱：
  - **建議維持** `question_text`, `correct_answer`, `answer`。雖有 `question->question_text`、`answer->correct_answer` 補值，但 `answer` 對 `/check_answer` 路徑仍具實務相容價值。

## 9. Unknowns
- `adaptive_practice_v2.html` 對應的 `/api/adaptive/*` 後端內部是否也直接走 `skills/{skill_id}.py`，本次未展開到該 API 實作細節（僅確認前端傳入 `skill_id` 與回應欄位使用）。
- 舊 skill 模組是否全部保證同時回傳 `answer` 與 `correct_answer`，本次僅抽樣代表檔案，未逐檔清點。
