# Agent Skill v2 與 ProblemType 規格包設計 v0.1

## 1. 文件目的
本文件定義了 Agent Skill v2 的標準規格包格式。該規格包將作為高職數學 B1-B3 教材流水線的核心數據結構，用於驅動教材匯入、problem_type 拆解、gencode candidate 生成、自動化驗證 (Verifier) 以及最終的 runtime_ready registry 註冊流程。

## 2. 設計原則
- **ProblemType 是最小單元**：Generator 的開發與驗證以 `problem_type` 為最小單位，而非整個 Skill，以降低 AI 生成難度並提高批改精確度。
- **Skill 作為邏輯聚合**：Skill 不再直接對應單一 Generator，而是多個 `problem_type` 的邏輯集合與 progression 控制點。
- **規格包非執行代碼**：Agent Skill v2 是靜態規格包 (Specification Package)，定義了「應該生成什麼」與「如何驗證」，而非直接運行的生產代碼。
- **Gencode 僅產出 Candidate**：AI 生成的代碼初始狀態均為 `candidate`，嚴禁未經驗證直接上線。
- **Runtime_Ready 准入機制**：必須通過 13 項自動化驗證閘門 (Verifier Gate) 並經人工 Promotion 後，方可進入 `runtime_ready` 狀態。
- **YAML 優先，延後 DB 化**：在 Pipeline 穩定前，所有規格以 YAML/Markdown 格式存儲於 Git，便於版本控制與審閱。
- **標竿參考**：B4 Registry 是本規格設計的 Reference Implementation，所有新欄位需與 B4 現狀保持兼容。
- **確定性優先**：不適合自動化出題或 deterministic 批改的題型（如複雜繪圖、證明題）應明確標記為 `manual_review` 或 `future_ai_judged`。

## 3. 舊版 Agent Skill 與 v2 差異

| 項目 | 舊版 Agent Skill | Agent Skill v2 |
|---|---|---|
| 最小單位 | skill | problem_type |
| 主要文件 | SKILL.md (Markdown) | skill.yaml + problem_types.yaml + prompt_gencode.md + evals.yaml |
| 產出物 | `skills/{skill_id}.py` | `generated_candidates/{problem_type_id}/` (多個版本) |
| 狀態管理 | 弱（通常直接上線） | 嚴格狀態機 (candidate / verified / runtime_ready) |
| runtime 方式 | skill.py 直接執行 | 由 Registry 驅動的動態映射 (Registry-controlled generator) |
| verifier | 基於 dynamic sampling 的基礎版 | 包含 13 項檢查的嚴格 runtime_ready gate |

## 4. 目錄結構

### 範本目錄
```text
agent_skills_v2/
  _template/
    README.md
    skill.yaml
    problem_types.yaml
    examples_map.yaml
    domain_functions.yaml
    prompt_gencode.md
    evals.yaml
```

### 未來實例 (以 B1 第一章為例)
```text
agent_skills_v2/
  vocational_math_b1/
    chapter_1/
      coordinate_and_distance/  # skill_slug
        skill.yaml
        problem_types.yaml
        examples_map.yaml
        domain_functions.yaml
        prompt_gencode.md
        evals.yaml
```

## 5. 各檔案用途
- **skill.yaml**：定義技能層級的元數據、課程位置、先修關係與家族分類。
- **problem_types.yaml**：定義該技能下所有子題型的 IO 契約、批改方式、狀態與診斷標籤。
- **examples_map.yaml**：記錄課本例題與 `problem_type` 的映射關係，作為 AI 生成的參考源。
- **domain_functions.yaml**：定義該家族允許使用的數學函數白名單，防止 AI 幻覺或重複造輪子。
- **prompt_gencode.md**：針對該特定技能優化的 AI 生成提示詞模板。
- **evals.yaml**：定義自動化驗證的各項閾值與測試案例。
- **README.md**：該規格包的維護說明與變更記錄。

## 6. skill.yaml 欄位規格
- `skill_id`: 全域唯一 ID (例如 `vh_數學B1_CoordinateSystem`)。
- `skill_name`: 易讀名稱。
- `curriculum`: 課程體系 (預設 `vocational`)。
- `volume`: 冊別 (例如 `數學B1`)。
- `chapter`: 章。
- `section`: 節。
- `family_id`: 所屬數學家族 (如 `counting`, `algebra`)。
- `curriculum_profile`: 難度配置檔案引用。
- `prerequisite_skills`: 先修技能清單。
- `downstream_skills`: 後續技能清單。
- `source_textbook`: 來源教材版本。
- `status`: 技能總體狀態。
- `notes`: 備註說明。

## 7. problem_types.yaml 欄位規格
- `problem_type_id`: 子題型 ID。
- `subskill_id`: 關聯的子技能 ID。
- `display_name`: 學生端顯示名稱。
- `generator_key`: 唯一註冊 key。
- `answer_type`: 答案類型 (`choice`, `numeric`, `latex`, `handwriting`)。
- `checker_type`: 批改器類型 (如 `check_integer_answer`, `check_latex_expression`)。
- `allowed_domain_functions`: 允許調用的核心函數。
- `forbidden_patterns`: 禁止出現的代碼模式。
- `difficulty_policy`: 難度控制參數。
- `output_contract`: 預期輸出的 Payload 結構。
- `status`: 當前開發狀態 (見下文)。
- `manual_review`: 是否需人工介入 (bool)。
- `future_ai_judged`: 是否為 AI 視覺批改預留 (bool)。
- `runtime_policy`: 運行時策略 (`deterministic`, `adaptive`)。
- `diagnosis_tags`: 診斷用標籤。
- `remediation_candidates`: 補救建議題型清單。

### Status 狀態機
- `draft`: 規格草稿。
- `candidate`: AI 已初步生成代碼。
- `generated`: 已通過基礎修復。
- `verified`: 通過所有自動化驗證閘門。
- `runtime_ready`: 已完成人工審閱，正式上線。
- `failed`: 驗證失敗需重新生成。
- `manual_review`: 轉為人工審閱模式。
- `future_ai_judged`: 待 AI 視覺功能。
- `deprecated`: 已棄用。

## 8. examples_map.yaml 欄位規格
- `example_id`: 例題唯一 ID。
- `source_type`: `textbook_example`, `textbook_practice`, `self_assessment`, `teacher_added`, `student_promoted`。
- `source_location`: 課本頁碼或章節。
- `skill_id`: 關聯技能。
- `problem_type_id`: 關聯題型。
- `role`: 在 gencode 中的角色 (`few_shot_seed`, `validation_target`)。
- `style_ref`: 風景偏好引用。
- `eval_ref`: 關聯的評測點。
- `needs_review`: 是否需人工校對教材。
- `notes`: 備註。

## 9. domain_functions.yaml 欄位規格
- `family_id`: 數學家族。
- `allowed_imports`: 允許 import 的模組。
- `allowed_domain_functions`: 建議調用的工具函數 (如 `gcd`, `lcm`, `RadicalOps`)。
- `forbidden_functions`: 禁止使用的函數 (如 `eval`, `exec`, `input`)。
- `rendering_helpers`: 畫圖或渲染輔助函數。
- `checker_functions`: 特殊批改邏輯引用。
- `validator_functions`: Payload 結構驗證函數。

**核心禁止事項**：
- **禁止自行實作基礎數學函數**：AI 不可自行實作 GCD / Combination / Statistics 等已有標準庫或領域函數的邏輯。
- **禁止無限循環**：while True 必須具備熔斷機制。

## 10. prompt_gencode.md 規格
Prompt 必須強制 AI 遵守以下規則：
- **角色設定**：資深 Python 數學 Generator 工程師。
- **輸入參考**：嚴格對照 `problem_type spec` 與 `textbook examples`。
- **輸出契約**：必須符合 `generator_payload` 結構。
- **代碼純度**：只輸出可執行的 Python 代碼塊，禁止 markdown 冗餘文字。
- **禁止幻覺**：只能使用 `allowed_domain_functions` 中定義的函數。
- **生成位置**：代碼僅作為 `candidate` 提交，不可直接修改 Production 路由。

## 11. evals.yaml 規格
- `contract_tests`: 基本 Payload 結構檢查。
- `sampling_tests`: 隨機採樣穩定性檢查。
- `checker_tests`: 正確答案自我測試。
- `wrong_answer_tests`: 錯誤答案排除測試。
- `latex_safety_tests`: LaTeX 語法檢查。
- `duplicate_guard_tests`: 題目重複性與假多樣性檢查。
- `timeout_seconds`: 生成限時 (預設 5s)。
- `min_sampling_count`: 最少採樣次數 (預設 30次)。
- `promotion_threshold`: 自動 Verified 的閾值。

## 12. 與 B4 Registry 的對應關係

| Agent Skill v2 欄位 | B4 registry 欄位 |
|---|---|
| skill_id | skill_id |
| problem_type_id | problem_type_id |
| generator_key | generator_key |
| answer_type | answer_type |
| checker_type | checker_type |
| status | status |
| manual_review | manual_review |
| future_ai_judged | future_ai_judged |
| remediation_candidates | remediation_candidates |

## 13. B1 Prototype 使用流程
1. **教材匯入**：將課本內容結構化。
2. **建立規格包**：生成 `skill.yaml` 與 `problem_types.yaml`。
3. **映射例題**：完成 `examples_map.yaml`。
4. **生成 Candidate**：執行 `prompt_gencode.md` 調用 AI 產生代碼。
5. **運行 Verifier**：根據 `evals.yaml` 執行 13 項驗證。
6. **人工 Promotion**：審閱 Verified 代碼，標記為 `runtime_ready`。
7. **動態註冊**：將通過的規格自動同步至生產 Registry。

## 14. 不做事項
- **不匯入 B1 實體教材**：本階段僅設計範本。
- **不生成實際 Generator**：僅定義生成規格。
- **不修改 Production Runtime**：不變動路由代碼。
- **不修改資料庫**：保持 YAML 存儲。
- **不導入 Edge AI**：首階段使用 Cloud API 確保穩定性。

## 15. 下一步
下一步為 **Phase 3A：B1 單一小節教材匯入與 Agent Skill v2 prototype 準備**。
在執行 Phase 3A 前，應由開發團隊人工審核本範本是否足以涵蓋 B1 首個小節（坐標系與距離公式）的所有題型需求。
