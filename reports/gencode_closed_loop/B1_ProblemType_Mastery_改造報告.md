# B1 學生晉級制度改造報告：Generator 題型掌握制

**日期**：2026-11-22  
**範圍**：僅 `vh_數學B1_*`（不含 Outline／SubSection；不含 B2～B4）  
**狀態**：實作完成，等待人工驗收（不自動進入 B2）

---

## 1. 原本的連續答對制度實際如何運作？

| 層級 | 行為 |
|---|---|
| 資料來源 | `Progress.consecutive_correct`（`update_progress` 答對 +1、答錯歸零） |
| 門檻 | 練習頁 UI 使用 `get_pass_target(skill_id)`＝綁定教材例題數；管理中心另有 `skills_info.consecutive_correct_required` 欄位（Skill 卡正式判定已改以教材參考數／熟練度為主） |
| 學生端顯示 | `#streak-counter`：「連續答對 X / Y 題」 |
| 過關語意 | 學生端以連對進度作為練習目標顯示；答錯會把連對歸零，造成挫折 |
| 選題 | `practice_type_rotation` 依 session 狀態輪替 `problem_type_id` |

---

## 2. 修改後如何計算「已掌握題型 X/Y」？

- **X**＝該學生在該 Skill 下，`student_problem_type_mastery.status = MASTERED` 且屬於目前 Runtime 可用題型集合的 distinct `problem_type_id` 數。
- **Y**＝`generator_problem_type_inventory.inventory_skill_generator_problem_types(skill_id).usable_problem_type_ids` 去重後長度。
- 同一題型重複答對不增加 X。
- 答錯不歸零已掌握題型。
- `Y = 0` 時顯示「暫無可練習題型」，且 `complete = false`（不自動晉級）。

相容欄位（沿用既有 UI 契約）：

- `consecutive_correct` ← X  
- `pass_target` ← Y  
- `progress_mode = "problem_type_mastery"`

---

## 3. 各 Skill 的 Y 如何從 Runtime Generator 取得？

權威服務：`core/gencode/services/generator_problem_type_inventory.py`

- 以 Runtime 可用 `problem_type_id` 為準（非教材例題數、非 Python 檔案數、非 V3 eligible 來源數、非舊連對門檻）。
- 相同 `problem_type` 多個 Generator component 只算一種。
- 不可被學生端實際選用的題型不進分母。

代表性現況（測試 DB 盤點）：

| Skill | Y |
|---|---|
| AbsoluteValueInequality | 4 |
| PointSlopeForm | 2 |
| DistanceBetweenPointAndLine | 5 |
| GeneralFormOfLinearEquation | 11 |
| SubSection332 | 0（不套用正式過關） |

---

## 4. MASTERED 如何判定？

實作：`core/practice_type_mastery.py` → `record_type_attempt`

1. 正常練習流程中，**獨立答對**該題型新題 → `MASTERED`（寫入 `mastered_at`／可選 `mastery_attempt_id`）。
2. 已是 `MASTERED` 再答對 → 不變、不重複累加。
3. 已是 `MASTERED` 再答錯 → **保留 MASTERED**（不因本型或其他型答錯撤銷）。

狀態機：`NOT_STARTED` → `PRACTICING` →（連續錯 ≥2）`REMEDIATION` →（獨立答對）`MASTERED`。

---

## 5. 學生答錯或 AI 補救後如何處理？

| 情境 | 處理 |
|---|---|
| 答錯 | 記錄錯誤；該題型維持 PRACTICING／REMEDIATION；其他已掌握進度保留 |
| AI 提示／分步／看解答 | `analysis.chat_ai` 呼叫 `mark_question_assisted(question_uid)` |
| 提示後答對同一題 | `assisted=True` → 不給 MASTERED，設 `needs_independent_verify` |
| 之後同型變化題獨立答對 | `assisted=False` → 可升 MASTERED |
| 連續錯兩次 | 標記 REMEDIATION（沿用既有 AI 補救入口，不另建平行補救） |

選題：B1 將 DB mastery 同步進 `practice_type_rotation`（MASTERED→passed、PRACTICING/REMEDIATION→weak、其餘 unseen），優先未掌握題型。

---

## 6. 進度如何保存到資料庫？

### 新表 `student_problem_type_mastery`

欄位：`user_id`, `skill_id`, `problem_type_id`, `status`, `consecutive_wrong`, `needs_independent_verify`, `attempt_count`, `last_attempt_*`, `mastered_at`, `mastery_attempt_id`, timestamps。  
唯一鍵：`(user_id, skill_id, problem_type_id)`。

### Migration

- 腳本：`scripts/migrate_b1_problem_type_mastery.py`（idempotent `CREATE TABLE IF NOT EXISTS`）
- 模型：`models.StudentProblemTypeMastery` + bootstrap DDL
- 備份：`backups/b1_type_mastery_pre_migrate/`
- **未**把舊 `Progress.consecutive_correct` 換算成 MASTERED

### 寫入點

`practice.check_answer` 在可計分作答後呼叫 `record_type_attempt`（與既有 PracticeAttempt／錯題本同一交易流程）。

---

## 7. 題型新增、停用、更名後如何處理？

| 事件 | 行為 |
|---|---|
| 新增題型 | 舊掌握保留；新題型進 Y 且預設未掌握 |
| 題型下線／不可選用 | 歷史列保留；不再計入目前 Y |
| 更名／合併 | 需明確映射 Migration（本輪未做自動 remap；不可無聲遺失） |
| Outline／SubSection／非 B1 | 不套用本題型掌握制 |

---

## 8. 管理中心、學生端、分析頁是否一致？

| 表面 | 狀態 |
|---|---|
| 學生練習頁 | ✅「已掌握題型 X/Y」（後端真實進度） |
| Skill 卡／Dashboard 刷新 | ✅ B1 overlay 為「已掌握題型 X/Y」；非 B1 仍「連續答對」 |
| `/check_answer`／`/get_next_question` | ✅ 回傳 `progress_mode`／X／Y（student payload 白名單已補齊） |
| 管理中心「晉級門檻」欄位 | ⚠️ 仍顯示「連續答對題數」編輯欄；B1 Runtime 實際不再用它當過關分母（建議人工驗收後再改文案／說明，避免大改 Admin） |
| 分析／錯題本／AI 助教 | ✅ 既有流程保留；助教標記 assisted 阻擋冒充掌握 |

---

## 9. 測試通過數量及尚未測試項目

### 已通過

| 套件 | 結果 |
|---|---|
| `scripts/test_b1_type_mastery.py` | **15/15 PASS**（含 4 題型掌握、同型四次=1、答錯保留、assisted 不掌握、獨立驗證、0 題型不完成、B2 skip、DB 持久） |
| `scripts/test_b1_type_mastery_route.py` | **4/4 PASS**（練習頁標籤、`get_next_question` progress_mode=problem_type_mastery） |
| `tests/test_unified_correct_answer_flow.py` + `tests/test_practice_streak_progress.py` | **21 PASS** |

證據：

- `reports/gencode_closed_loop/b1_type_mastery_test_latest.json`
- `reports/gencode_closed_loop/b1_type_mastery_route_latest.json`

### 尚未／建議人工驗收

- 真實瀏覽器＋iPad 橫向手寫區（未在本輪自動化完成）
- 完整登入→答題→重新整理→重登的端到端視覺確認
- QIS／PointSlopeForm 真人作答一遍
- 管理中心門檻欄位文案是否要改
- 適性練習（adaptive）頁面是否需同步文案（本輪判定：B1 standard practice 為主；adaptive 未改晉級規則）

---

## 10. 是否影響 B2～B4？

**否。**  
閘門：`is_b1_type_mastery_skill()` 僅 `vh_數學B1_*` 且排除 Outline／SubSection。  
B2 呼叫 `record_type_attempt` 會 `skipped`，不寫列。  
Skill 卡非 B1 仍顯示連續答對。

---

## 11. 哪些項目仍需人工驗收？

1. Flask **5001** 受控重啟後，學生端實際看到「已掌握題型 X/Y」。
2. AbsoluteValueInequality：四種題型各獨立答對 → 4/4。
3. 提示後答對不得直接變掌握；換新同型題再獨立答對才進位。
4. 答錯後進度不歸零。
5. 重新整理／重登進度一致。
6. iPad 橫向不壓縮手寫區。
7. B2～B4 任一 Skill 仍顯示連續答對語意。
8. 管理中心欄位文案是否後續調整。

---

## 修改檔案清單

- `core/practice_type_mastery.py`（新）
- `core/routes/practice.py`（寫入／讀取／輪替同步）
- `core/routes/analysis.py`（assisted 標記）
- `core/skill_card_mastery.py`（B1 Skill 卡 overlay）
- `core/practice_student_payload.py`（允許 progress 欄位）
- `models.py`（表與 bootstrap）
- `scripts/migrate_b1_problem_type_mastery.py`
- `scripts/test_b1_type_mastery.py` / `scripts/test_b1_type_mastery_route.py`
- `templates/index.html`、`templates/partials/skill_card.html`、`templates/dashboard.html`
- `tests/test_unified_correct_answer_flow.py`（字串斷言對齊）

## Runtime 影響

- 需受控重啟 **Flask 5001** 載入新程式。
- **不**動 Flask 5000／Cloudflare。
- **不** commit／push。
- **不**重建 Generator、不重匯教材。

## 結案

B1 Generator 題型掌握制已落地：判定、持久化、選題同步、學生端／Skill 卡顯示一致；自動化測試通過。  
**停止於此，等待人工驗收；不進入 B2。**
