# Phase 4F-Main-B：B4 Chapter 1 Adaptive Single／Multiple E2E Smoke — 總結

**日期：** 2026-05-05  
**範圍：** `GET /get_adaptive_question`、`POST /check_answer`（練習路線）、焦點 pytest；不改 Phase 4E matrix、不改 B4 generators／`question_router`。

---

## 曾檢視的檔案

| 檔案 | 目的 |
|------|------|
| `core/routes/practice.py` | `get_adaptive_question`（single／multiple／review）、`check_answer`、session `set_current`／`get_current`。 |
| `core/session.py` | `set_current` 與 `question_text`／`answer` 相容鍵。 |
| `skills/vh_數學B4_CombinationDefinition.py` | `generate`／`check` 證明 E2E 批改可行。 |
| `core/routes/adaptive_api.py` | Adaptive v2 API：`submit_and_get_next` 進入點。 |
| `core/adaptive/session_engine.py` | `submit_and_get_next`、` _load_question_from_skill_module`（與 practice adaptive 分流）。 |
| `tests/test_phase4f_main_a_adaptive_generator_first.py` | Main-A 契約（review DB／generator、`source_type`）。 |
| `models.py`（`SkillCurriculum`） | single／multiple 使用 `db.session.query(SkillCurriculum.skill_id).filter(...)`。 |

---

## 變更的檔案

| 檔案 | 變更要旨 |
|------|-----------|
| `tests/test_phase4f_main_b_adaptive_e2e_smoke.py` | **新增**：Main-B E2E／smoke（9 個測試）：single／multiple 透過 stub `SkillCurriculum.skill_id` 查詢鏈；review 複習池；`/check_answer` 正答；三種 excluded `problem_type_id`；`adaptive_audit` 欄位；single 混合池 `generator_fallback`。 |

**未修改：** production 程式碼（`practice.py`、generators、coverage matrix、router）。

---

## E2E 情境涵蓋（對照需求）

| # | 情境 | .assert |
|---|------|---------|
| 1 | **Single allowlisted B4**：`mode=single`，stub 章節→技能，`recommend_question` 空，`adaptive_audit=1`，再 `POST /check_answer` 正答 | 200、`new_question_text`、`correct_answer`、`source_type=generator_first`、audit 含 `skill_id`／`problem_type_id`／`generator_key`／`router_trace`；批改 `correct=True` |
| 2 | **Multiple、僅 B4、DB 空** | 200、`generator_first`，skill 為 stub 池中之一 |
| 3 | **Review、複習池多個 B4、`recommend` 未呼叫** | 200、`generator_first` |
| 4 | **Review、JH+B4、weakness 固定選 JH、DB 空** | 200、`generator_fallback`、skill 為池中 allowlisted B4 |
| 5 | **僅非 B4、DB 空** | **404**（行為與 Main-A 一致） |
| 6 | **Excluded problem types**（parametrize：`binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation`） | **422**、`source_type=rejected_excluded_problem_type`；JSON **無** `new_question_text`／`correct_answer` |
| 7 | **Single、JH+B4 混合池、DB 空** | 200、`generator_fallback`（補強「非 review」混合池） |

---

## `adaptive_audit` 欄位範例（摘要）

成功路徑由 `format_adaptive_question_audit_dict` 產生，典型鍵包含：

- `source_type`：`generator_first` | `generator_fallback` | `db_textbook_example`
- `skill_id`、`problem_type_id`、`generator_key`、`subskill_id`
- `selection_reason`（來自 `router_trace`）
- `router_trace`：至少含 `input_skill_id`、`selected_problem_type_id`、`selected_generator_key` 等（依路由器輸出）

422 拒題時：`source_type=rejected_excluded_problem_type`，並可含 `reject_detail`（例如 `excluded_problem_type:<id>`）。

---

## QA 指令與結果

```powershell
Set-Location "d:\Python\Mathproject_tvet_mathB"
python -m pytest tests/test_phase4f_main_b_adaptive_e2e_smoke.py tests/test_phase4f_main_a_adaptive_generator_first.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -v --tb=short
```

**結果（本機執行）：** **46 passed**（Main-B：9；Main-A：5；allowlist：8；router canonical：24）。

---

## Adaptive v2／`session_engine` 對齊稽核（輕量）

| 項目 | 說明 |
|------|------|
| **進入點** | `core/routes/adaptive_api.py` → `submit_and_get_next`（`core/adaptive/session_engine.py`）。 |
| **技能／題目來源** | Payload 內 `skill_id`、catalog `entries`、PPO／heuristic routing、`_load_question_from_skill_module` 等；**未**套用 `b4_chapter1_deterministic_allowlist` 或 `validate_b4_deterministic_adaptive_generator_payload`。 |
| **與 Main-A／B 關係** | practice 線的 `get_adaptive_question` 為 **獨立** deterministic adaptive API；**本 Phase 未**深改 `session_engine`。若要行為一致，需另起工作項在 v2 出題前掛同款 allowlist／validator／`source_type` 契約（仍須遵守 AGENTS.md 三層不分層坍縮）。 |

---

## 已知限制

1. **Single／multiple E2E** 依測試層 stub `db.session.query(SkillCurriculum.skill_id)` 鏈（實際 ORM 第一參數為 **欄位** `SkillCurriculum.skill_id`，非 model 類別）；真實 DB 需有對應 `skill_curriculum` 列方能不經 stub 通過。
2. **`/check_answer`** 在 `question_id=0` 時不呼叫 `update_student_ability`（條件為 `if question_id:`）；E2E 僅驗證批改成功，不涉及 IRT／能力寫回。
3. **Review weakness** 具隨機／統計成分；需驗證 `generator_fallback` 的 case 仍以 `select_review_skill` monkeypatch 固定為 JH（與 Main-A 一致）。
4. **Adaptive v2** 與 practice adaptive **題源政策不同**，產品上可能出現兩套體驗差異。

---

## Phase 4F-Main-C 建議

1. **可選「真 DB」smoke**：在測試或 staging 種入最小 `SkillCurriculum`（vocational B4 章節）列，移除 query stub，驗證與前端 `skill_ids` 真實對應。
2. **`question_id=0` 行為**：若需完整自適應能力追蹤，定義 generator 題是否寫入合成 `question_id` 或略過 RS 更新（需產品／資料團隊共識）。
3. **Adaptive v2 與 B4**：若要高劃一，於 `submit_and_get_next` 或 skill module 載入後，對 `vh_數學B4_*` 套用同一 validator（與 closure matrix 仍分離）；並在 API 回傳中增加可比較的 `source_type` 或 `adaptive_lane=practice_v1|session_v2` 供觀測。
4. **前端迴歸**：Main-B 僅後端 HTTP；Main-C 可補最小 Playwright／手搓腳本走「取題→填答→下一題」若產品有專用頁。

---

**結論：** Main-B 以 **9 支**聚焦測試覆蓋 single／multiple／review、空 DB、`/check_answer`、三種 excluded 題型與 `adaptive_audit` 可見欄位；與 Main-A／allowlist／router **46 支**併跑全綠。**session_engine** 路線仍 **未**掛 B4 Chapter 1 deterministic allowlist，於上表列為範圍外並建議 Main-C 決策是否對齊。
