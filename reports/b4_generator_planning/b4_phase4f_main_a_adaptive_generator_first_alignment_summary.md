# Phase 4F-Main-A：B4 Chapter 1 Adaptive Generator-First Source Alignment — 總結

**日期：** 2026-05-05  
**範圍：** `GET /get_adaptive_question`（`core/routes/practice.py`）、Preflight allowlist／validator、焦點測試。

---

## 曾檢視的檔案（audit）

| 檔案 | 目的 |
|------|------|
| `core/routes/practice.py` | `get_adaptive_question`：review／single／multiple、DB `recommend_question`、generator、`adaptive_audit`、`source_type`。 |
| `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` | Allowlist、`filter_skill_pool_*`、`validate_b4_deterministic_adaptive_generator_payload`、`format_adaptive_question_audit_dict`、`is_pure_b4_allowlisted_adaptive_pool`、`allowlisted_b4_candidates`。 |
| `core/adaptive_engine.py`（概念） | `recommend_question` 為 DB TextbookExample 推薦入口（未改動）。 |
| `core/adaptive/session_engine.py`、`core/routes/adaptive_api.py` | Adaptive v2／PPO-RAG 路徑：與本 Phase 之「practice 頁 deterministic adaptive API」分流（見下文 Task H）。 |
| `tests/test_b4_chapter1_adaptive_allowlist.py` | Preflight allowlist 迴歸。 |
| `tests/test_vocational_math_b4_question_router_registry_canonical.py` | Router canonical 迴歸。 |

---

## 變更的檔案

| 檔案 | 變更要旨 |
|------|-----------|
| `core/routes/practice.py` | B4 sourcing：`pure_b4` → `generator_first`；混合池 DB 空且複習池含 allowlisted B4 → `generator_fallback`（review 模式改以「完整篩選後複習池」計算 B4 候選，避免 weakness routing 縮成單一非 B4 skill 後失去 fallback）；DB 命中 → `db_textbook_example`；payload 未過 validator → `rejected_excluded_problem_type`。 |
| `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py` | （Preflight／Main-A 延續）`format_adaptive_question_audit_dict` 支援 `source_type`；`is_pure_b4_allowlisted_adaptive_pool`、`allowlisted_b4_candidates`。 |
| `tests/test_phase4f_main_a_adaptive_generator_first.py` | **新增**：空 DB／mock、`source_type`、excluded problem type、非 B4-only 404、DB path audit；review 混合／DB path 案例對 `core.adaptive_engine.select_review_skill` 做 monkeypatch 以固定 weakness 選到的 skill（避免非決定性）。 |

**未修改（符合硬約束）：** Phase 4E coverage matrix、`question_router` 核心、`skills/*` generators（除測試用 monkeypatch）、frontend、`app.py`。

---

## 最終題源政策（final sourcing policy）

採 **混合策略**：

1. **純 allowlisted B4 池**（`is_pure_b4_allowlisted_adaptive_pool(target_skill_ids)` 為真）：**不呼叫** `recommend_question`，直接 **generator-first**（`source_type = generator_first`）。仍通過 `skills.<id>.generate()` 與 `validate_b4_deterministic_adaptive_generator_payload`。
2. **混合池**（含非 B4 或與 allowlist 組合）：**先** `recommend_question`（DB TextbookExample）；  
   - 有 template → **DB-first**，`source_type = db_textbook_example`；  
   - 無 template 且「fallback 候選池」內仍有 allowlisted B4 → **generator_fallback**，`source_type = generator_fallback`；  
   - 無 template 且無 allowlisted B4 可抽 → **404**「題庫中已無合適的題目…」（非 B4-only 空庫行為維持）。

**Review 模式重點：** weakness routing 會把 `target_skill_ids` 縮成單一技能；**B4 fallback 候選改由「Preflight 篩選後的整段 `review_skill_pool`」** 計算（`filtered_review_pool_for_generator_fallback`），否則會出現「路由選了 JH，但複習池其實還有 B4」卻仍 404 的矛盾。

---

## Allowlist 整合點

- **入池篩選：** `filter_skill_pool_for_b4_chapter1_deterministic_adaptive`（B4 必須在 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`，並排除 manual_review 技能）。
- **純 B4 判定：** `is_pure_b4_allowlisted_adaptive_pool(target_skill_ids)`。
- **Fallback 候選：** `allowlisted_b4_candidates(candidate_pool_for_b4_fallback)`；review 模式下 `candidate_pool_for_b4_fallback` 為完整篩選後複習池，其餘模式為當次 `target_skill_ids`。
- **產出後防呆：** `validate_b4_deterministic_adaptive_generator_payload`（僅對 `vh_數學B4_*` 強制）。

---

## 排除題型（excluded problem type）防線

- **設定層：** `B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES`（`binomial_expansion_basic`、`tree_diagram_listing`、`pascal_triangle_derivation`）。
- **執行層：** 凡 B4 vocational skill 經 generator 回傳後必跑 validator；不符則 **HTTP 422**，`source_type=rejected_excluded_problem_type`，`adaptive_audit` 可含 `reject_detail`（當 `adaptive_audit=1`）。

---

## `adaptive_audit=1` 與 `source_type` 列舉

| `source_type` | 情境 |
|---------------|------|
| `generator_first` | 純 allowlisted B4 池，略過 DB。 |
| `generator_fallback` | 混合池且 `recommend_question` 為 `None`，但複習池／當次 skill 列表中仍有 allowlisted B4。 |
| `db_textbook_example` | DB 取得 `TextbookExample` template。 |
| `rejected_excluded_problem_type` | B4 payload 遭 validator 拒絕。 |

---

## Task H：Adaptive v2／`session_engine`

- **`/get_adaptive_question`** 為舊版 practice 自適應 API；**`core.adaptive.session_engine` + `adaptive_api`** 為另一條（PPO／RAG／micro-generator）管線。
- 本 Phase **未**將 B4 Chapter 1 deterministic allowlist 掛入 `session_engine`；若未來要統一行為，需在 `submit_and_get_next` 或出題分支顯式套用同一 `filter`／`validate`／`source_type` 契約，並避免破壞三層架構（progression／routing／remediation）。

---

## QA 指令（含迴歸）

於專案根目錄（Windows PowerShell 範例）：

```powershell
Set-Location "d:\Python\Mathproject_tvet_mathB"
python -m pytest tests/test_phase4f_main_a_adaptive_generator_first.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -v --tb=short
```

**本次執行結果：** 37 passed（含 5 支 Main-A 新測、8 allowlist、24 router canonical）。

---

## 空 DB 行為（before / after）

| 情境 | Before（概念） | After |
|------|----------------|-------|
| 純 B4 allowlist 複習池、DB 無題 | 仍可能走 DB／推薦為空 → **404** | **generator_first**，200 |
| Review 混合池（JH+B4）、weakness 選 JH、DB 無題 | `allowlisted_b4_candidates` 只看單一 JH → 無 B4 fallback → **404** | 由整池挑 B4 → **generator_fallback**，200 |
| 僅非 B4、DB 無題 | **404** | **404**（維持） |

---

## 已知限制（known limitations）

- **DB 推薦範圍：** `recommend_question` 仍以當次傳入的 `target_skill_ids` 為準（review 下多為 weakness 選出的**單一** skill）；fallback 僅補「B4 generator」，**不**自動擴張 RS 對其他技能的 DB 檢索。
- **`question_id`：** 無 DB template 時為 `0`（與「真實題庫列」無對應）。
- **隨機性：** `gen_seed` 存在時同時影響「抽中的 allowlisted skill」（fallback／pure pool）與傳入 `generate(seed=...)`（若 skill 支援）。
- **Adaptive v2：** 題源／閘門與本 API 不一致時，產品上可能出現兩套 adaptive 體驗差異。

---

## Phase 4F-Main-B 建議方向

1. **Single／multiple 模式：** 確認章節展開後的 `target_skill_ids` 與 DB 空庫組合是否需在 E2E 再補一兩個 integration case（目前 Main-A 測試以 **review** 與 monkeypatch 為主）。
2. **前端／Session：** 若 UI 依賴 `question_id` 追蹤錯題或紀錄，需定義 `question_id=0` 時的 logging／analytics 契約。
3. **Observability：**  production log 已寫 `question_audit`；可評估是否對 `session_engine` 路徑加上對等的 `source_type` 以利對齊報表。
4. **Adaptive v2 對齊：** 若產品希望「只有一套」deterministic B4 閘門，於 `session_engine` 出題前套用同一 validator／allowlist（仍須遵守 AGENTS.md 不分層坍縮）。

---

**結論：** Main-A 達成「B4 deterministic adaptive 在 DB 無題時仍可 generator 供題」，並以 `source_type` 區分題源與拒題；review 混合池關鍵修正為 **fallback 候選取自完整 Preflight 複習池**，與 weakness 單點路由解耦。
