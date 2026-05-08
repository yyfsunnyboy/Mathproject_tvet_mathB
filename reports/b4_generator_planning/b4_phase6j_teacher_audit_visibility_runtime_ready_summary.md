# B4 Phase 6J — Chap2 Teacher Audit Visibility（Runtime-Ready Summary）

**狀態：READY_FOR_MANUAL_SMOKE**

## 1. Scope and guardrails

- **範圍**：在教師或管理身分下，唯讀檢視 `b4_chap2_visibility_audit_logs`（Phase 6I 寫入之可見性稽核列）；提供最小 HTML 列表與 JSON API，支援基本查詢參數。
- **未觸及**：mastery、APR、fail_streak、remediation、自適應 scoring policy、題型／generators／validators、allowlist 成員、coverage matrix、Chap1 行為、DB schema（無 migration／欄位變更）。

## 2. Files changed

| 檔案 | 說明 |
|------|------|
| `core/routes/b4_chap2_teacher_audit.py` | **新增**：HTML／JSON 路由、查詢與權限檢查（teacher 或 admin） |
| `core/routes/__init__.py` | 匯入新模組以註冊路由 |
| `templates/teacher_b4_chap2_audit.html` | **新增**：表格呈現稽核欄位、GET 篩選表單、無資料文案 |
| `tests/test_b4_chap2_phase6j_teacher_audit_visibility.py` | **新增**：隔離暫存 SQLite 之測試（避免與開發中主 DB 鎖互卡） |
| `reports/b4_generator_planning/b4_phase6j_teacher_audit_visibility_runtime_ready_summary.md` | 本報告 |

## 3. Route / API summary

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/teacher/b4-chap2-audit` | HTML 頁；需登入且 `role == teacher` 或 `is_admin` |
| GET | `/api/teacher/b4-chap2-audit` | JSON：`{ ok, items[], count }`；無權限回 `403` |

查詢參數（兩者相同）：

- `limit`：預設 50，上限 200，非法值則回退預設。
- `record_kind`：可選 `deterministic_answer`、`gated`；非法值忽略（不篩）。
- `skill_id`、`problem_type_id`：可選，完全比對；空白視為不篩。

排序：依 `created_at` 降冪，同時間再依 `id` 降冪。

## 4. Displayed fields

HTML 表格與 JSON `items[]` 皆涵蓋（nullable 以空字串或 `null` 呈現，頁面不 crash）：

`timestamp`（`created_at`）、`record_kind`、`gated_event_type`、`student_id`、`session_id`、`skill_id`、`problem_type_id`、`generator_key`、`answer_type`、`user_answer`、`expected_answer`、`is_correct`（HTML 以 是／否／空白）、`checker_name`、`difficulty`、`diagnosis_tags`、`public_message`、`source_phase`。

## 5. Filter support

- `limit`、`record_kind`、`skill_id`、`problem_type_id` 如上；無分頁、無 CSV、無圖表。
- 若 HTML 查詢結果為 0 列：顯示「目前尚無 Chap2 audit logs。」（含「僅篩選條件下無列」之情境）。

## 6. Visibility-only confirmation

- 路由僅執行 **SELECT** 類 ORM 查詢，不呼叫 `persist_b4_chap2_*`、不寫 `AdaptiveLearningLog`、不改 `Progress`／mastery 相關流程。
- 不觸發 remediation、不影響學生出題或下一題選擇；gated 列之展示不影響任何正誤率統計邏輯（本頁無統計）。

## 7. Tests run

```text
python -m pytest tests/test_b4_chap2_phase6j_teacher_audit_visibility.py -q
# 13 passed（2026-05-08，約 153s；含 transformers 等既有警告）

python -m pytest tests/test_b4_chap2_phase6i_visibility_audit_logging.py tests/test_b4_chap2_phase6g0_skill_availability_ux.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q
# 49 passed（2026-05-08，約 166s）
```

## 8. Manual smoke checklist

1. 以 **teacher** 或 **admin** 帳號登入。
2. 開啟 `GET /teacher/b4-chap2-audit`：應見表格或「目前尚無 Chap2 audit logs。」，無 traceback。
3. 於練習流程製造 Phase 6I 類列後重新整理，確認 deterministic / gated 列皆出現。
4. 變更 `limit`、`record_kind`、`skill_id`、`problem_type_id` 後結果合理。
5. 以 **student** 開啟同一路徑：應導向 dashboard（無稽核內容）；`GET /api/teacher/b4-chap2-audit` 應 `403`。
6. `GET /api/teacher/b4-chap2-audit?limit=5` 應回 JSON 且 `count` 與 `items` 長度一致。
7. 確認練習、check_answer、Chap1 流程與本輪改動前行為一致。

## 9. Known limitations

- 未與主選單深度整合；可自教師儀表板頁尾連結「← 教師儀表板」返回 `/teacher_dashboard`。
- 大量列時僅依 `limit` 截斷，無伺服端游標分頁。
- 每次 `create_app()` 仍會執行專案既有啟動邏輯，單檔 pytest 耗時較長（與專案現況一致）；測試已改為 **tmp_path 隔離 DB** 以降低與執行中 `app.py` 的 SQLite 鎖衝突。
- JSON 之 `timestamp` 為 ISO 字串附加 `Z`（naive UTC 慣例）；若前端需嚴格時區，請自行解析。

## 10. Recommended next phase

- **非本輪**：Phase 6K 或後續可選議題——主選單入口、審計匯出、與班級／學期維度篩選（需另開規格與權限模型）。
- 本輪依使用者指示 **不啟動 Phase 6K**。

## 11. Final confirmation

- 是否只做 teacher audit visibility：**是**
- 是否修改 mastery：**否**
- 是否修改 APR：**否**
- 是否修改 fail_streak：**否**
- 是否觸發 remediation：**否**
- 是否新增題型：**否**
- 是否修改 generators / validators：**否**
- 是否修改 allowlist 成員：**否**
- 是否修改 DB schema：**否**（未變更 `models.py` 或 migration）
- 是否啟動下一 phase：**否**
