# Phase 6I — Adaptive Audit Logging Minimal Implementation Summary

**狀態：READY_FOR_MANUAL_SMOKE**

---

## 1. Scope and guardrails

### 1.1 目標

依 `reports/b4_generator_planning/b4_phase6h_chap2_adaptive_audit_integration_plan.md`，**最小實作** Chap2 deterministic **答題事件**與 **gated 事件**（未開放 skill、reserved listing）之 **visibility-only** audit，寫入專用資料表。  
**不**新增題型、**不**改 generators／validators／allowlist／coverage matrix、**不**觸發 remediation、**不**改 adaptive scoring **政策**。

### 1.2 與既有 mastery 路徑之關係（重要）

`core/routes/practice.py` 內 Chap2 `check_answer` **仍呼叫既有** `update_progress(...)`（Phase 6C 以來行為）。  
Phase 6I **僅追加** `persist_b4_chap2_deterministic_answer_event(...)`，**未**新增第二條 mastery／APR 更新鏈；**gated** 路徑 **不**呼叫 `update_progress`。

### 1.3 硬性限制對照

| 項目 | 確認 |
|------|------|
| 只做 visibility audit logging | ✅ |
| 新增 mastery／APR／fail_streak／remediation 邏輯 | ❌ 未新增 |
| 改 adaptive scoring policy | ❌ |
| 新題型／generators／validators／allowlist | ❌ |
| Phase 6J | ❌ 未啟動 |

---

## 2. Files changed

| 路徑 | 說明 |
|------|------|
| `models.py` | 新增 ORM `B4Chap2VisibilityAuditLog`；`init_db` 內 `CREATE TABLE IF NOT EXISTS b4_chap2_visibility_audit_logs` + 索引 |
| `core/vocational_math_b4/services/b4_chap2_visibility_audit.py` | **新增**：`persist_b4_chap2_gated_event`、`persist_b4_chap2_deterministic_answer_event`、session trace `b4_ch2_audit_sid` |
| `core/routes/practice.py` | `get_next_question`／`get_adaptive_question` not-enabled gate；Chap2 reserved listing gate；Chap2 `check_answer` 成功計分後寫入 answer audit（在既有 `update_progress` 之前） |
| `tests/test_b4_chap2_phase6i_visibility_audit_logging.py` | **新增**：answer correct／incorrect、gated 兩類、Progress／AdaptiveLearningLog 在 gated 下不增、Chap1 allowlist 13 |
| `reports/b4_generator_planning/b4_phase6i_adaptive_audit_logging_minimal_implementation_summary.md` | 本報告 |

---

## 3. Logging implementation summary

- **寫入層**：`B4Chap2VisibilityAuditLog`（SQLite；`db.session.commit()`；失敗 `rollback` + `logger.warning`，**不**中斷 HTTP）。
- **`source_phase`**：常數 `b4_chap2_phase6i`（欄位 `B4_CHAP2_VISIBILITY_SOURCE_PHASE`）。
- **`session_id`**：首次寫入時於 Flask `session` 建立 `b4_ch2_audit_sid`（UUID hex），便於同瀏覽連線多筆對齊。
- **`student_id`**：`current_user.is_authenticated` 時寫入，否則 `NULL`。

---

## 4. Deterministic answer event schema（`record_kind=deterministic_answer`）

| 欄位 | 說明 |
|------|------|
| `student_id` | 登入使用者 id，可 null |
| `session_id` | `b4_ch2_audit_sid` |
| `skill_id` | Chap2 deterministic allowlist skill |
| `problem_type_id` | `current` payload `problem_type_id`／`problem_type` |
| `generator_key` | payload（截斷 256） |
| `answer_type` | 如 `rational_fraction`／`integer`／`expected_value` |
| `expected_answer` | `correct_answer`／`answer` |
| `user_answer` | POST body |
| `is_correct` | bool |
| `checker_name` | `check_integer_answer`／`check_expected_value_answer`／`check_rational_answer`／`checker_exception` |
| `difficulty` | `difficulty` 或 `difficulty_level` 轉 int |
| `diagnosis_tags` | JSON 字串化 |
| `timestamp` | `created_at`（ORM `datetime.utcnow`） |
| `source_phase` | `b4_chap2_phase6i` |
| `gated_event_type` | **null** |
| `public_message` | **null** |

---

## 5. Gated event schema（`record_kind=gated`）

| 欄位 | 說明 |
|------|------|
| `gated_event_type` | `not_enabled_skill`（`B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`）或 `reserved_problem_type`（listing） |
| `skill_id` | 請求 skill |
| `problem_type_id` | 有則寫（not-enabled 在 `next_question` 可由 query 帶入；reserved 必填） |
| `public_message` | 對外常數：`B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR` 或 `B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR` |
| `is_correct` | **null**（不計入正誤統計語意） |
| `checker_name` | **null** |
| 其餘答題欄位 | 多為 **null** |

**掛載點：**

- `next_question`：`is_b4_chapter2_skill_not_enabled_in_phase6c1` 回 422 前；reserved listing 回 422 前。
- `get_adaptive_question`（preflight）：Chap2 not-enabled skill 回 422 前。

---

## 6. Visibility-only confirmation

- 本輪 **僅新增** DB 寫入與 **不改** `AdaptiveLearningLog`、不呼叫 RAG／remediation。
- Gated 流程：**不**更新 `Progress`、**不**新增 `AdaptiveLearningLog`（測試已對照 `AdaptiveLearningLog` 筆數）。
- Answer 流程：**既有** `update_progress` 保留；audit 為旁路記錄。

---

## 7. Tests run

```powershell
python -m pytest `
  tests/test_b4_chap2_phase6i_visibility_audit_logging.py `
  tests/test_b4_chap2_phase6g0_skill_availability_ux.py `
  tests/test_b4_chapter1_adaptive_allowlist.py `
  -q --tb=short
```

**結果：`25 passed`**（環境 FutureWarning／BERT Deprecation 不計入本輪）。

---

## 8. Known limitations

- **Teacher dashboard／匯出 API**：未實作；僅 DB 可查。
- **未登入** `check_answer`：若外層無 `login_required`，既有 `update_progress` 可能與匿名使用者互動；audit 仍可能寫入 `student_id=NULL`（與 Phase 6H 規劃一致）。
- **Schema rollback**：刪表 `DROP TABLE IF EXISTS b4_chap2_visibility_audit_logs;` 可還原（自行備份資料）。
- **Partial Chap2 失敗**（例如 payload validation 422）：本輪 **未**全面記錄；可留 Phase 6J+。

---

## 9. Recommended next phase

- **Phase 6J（建議）**：教師唯讀 API 或簡易列表頁（篩選 `skill_id`／`record_kind`／日期）；CSV 匯出；仍 **visibility-only**。
- 或與現有 admin 報表整合（另開規劃）。

**本輪未啟動 Phase 6J。**

---

## 10. Final confirmation

| 項目 | 確認 |
|------|------|
| 是否只做 visibility audit logging（語意：本輪新增之 audit 管線僅記錄／gated，不新增 APR／remediation） | **是** |
| 是否修改 mastery（**未**改 `update_progress` 簽名或政策；**保留**既有 Chap2 行為） | **否**（無新政策；既有仍寫 Progress） |
| 是否修改 APR | **否** |
| 是否修改 fail_streak | **否**（未改 session stats 路徑） |
| 是否觸發 remediation | **否** |
| 是否新增題型 | **否** |
| 是否修改 generators／validators | **否** |
| 是否修改 DB schema | **是**（新增表 `b4_chap2_visibility_audit_logs` + 索引；`init_db` + `db.create_all` 可建） |
| 是否啟動下一 phase | **否** |

---

*Phase 6I implementation complete. 狀態：**READY_FOR_MANUAL_SMOKE**。*
