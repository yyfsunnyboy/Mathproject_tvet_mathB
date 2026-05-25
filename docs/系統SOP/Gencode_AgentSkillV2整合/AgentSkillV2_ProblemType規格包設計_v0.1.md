# Agent Skill v2 ProblemType 規格包設計 v0.1

## 1. 文件目的
本文件定義 Agent Skill v2 中，以 **ProblemType (題型)** 為最小出題單位的規格包結構與 JSON / YAML Schema。本規格確保 AI 能夠以高度確定性、安全性與符合教材的標準進行題目生成與驗證。

## 2. 核心原則
- **YAML 優先，延後 DB 化**：在 Pipeline 穩定前，所有規格以 YAML/Markdown 格式存儲於 Git，便於版本控制與審閱。
- **標竿參考**：B4 Registry 是本規格設計的 Reference Implementation，所有新欄位需與 B4 現狀保持兼容。
- **確定性優先**：不適合自動化出題或 deterministic 批改的題型（如複雜繪圖、證明題）應明確標記為 `manual_review` 或 `future_ai_judged`。

## 3. 舊版 Agent Skill 與 v2 差異

| 項目 | 舊版 Agent Skill | Agent Skill v2 |
|---|---|---|
| 最小單位 | skill | problem_type |
| 主要文件 | SKILL.md (Markdown) | subskills.yaml + problem_types.yaml + examples_map.yaml + prompt_gencode.md + evals.yaml + prerequisites.yaml |
| 產出物 | `skills/{skill_id}.py` | `generated_candidates/{problem_type_id}/` (多個版本) |
| 狀態管理 | 弱（通常直接上線） | 嚴格狀態機 (candidate / verified / runtime_ready) |
| runtime 方式 | skill.py 直接執行 | 由 Registry 驅動的動態映射 (Registry-controlled generator) |
| verifier | 基於 dynamic sampling 的基礎版 | 包含 12+ 項檢查的嚴格 runtime_ready gate |

---

## 4. 規格包檔案清單與目錄結構

每個 `skill` 規格包目錄中，**至少必須包含以下 5 個核心規格檔案**：
1. `subskills.yaml`：定義子技能層級的元數據、展示名稱與關聯例題。
2. `problem_types.yaml`：定義該技能下所有子題型的 IO 契約、批改方式、狀態與診斷標籤。
3. `examples_map.yaml`：記錄課本例題與 `problem_type` 的映射關係，做為 AI 仿寫與對照的依據。
4. `prerequisites.yaml`：定義子技能層級的先修依賴關係與診斷修復路徑。
5. `evals.yaml`：定義自動化驗證的各項閾值與測試案例。

### 目錄結構
```text
agent_skills_v2/
  _template/
    README.md
    subskills.yaml
    problem_types.yaml
    examples_map.yaml
    prerequisites.yaml
    evals.yaml
    domain_functions.yaml
    prompt_gencode.md
```

---

## 5. 各 YAML 檔案詳細 Schema 規格

### 5.1 subskills.yaml Schema
每個子技能 (SubSkill) 至少必須包含以下欄位：
- `subskill_id`: 全域唯一子技能 ID（例如 `absolute_value_numeric_evaluation`）。
- `skill_id`: 關聯的主技能 ID（例如 `vh_數學B1_AbsoluteValue`）。
- `display_name`: 學生或教師端展示名稱。
- `description`: 該子技能所涵蓋的數學概念描述。
- `observed`: 是否為可被獨立評估觀測的子技能（bool）。
- `supporting_example_ids`: 支持此子技能的課本例題 ID 清單（list）。
- `prerequisite_subskills`: 關聯的先修子技能 ID 清單（list）。
- `diagnosis_tags`: 知識診斷用標籤清單（list）。
- `runtime_notes`: 運行時注意事項或備註說明。

### 5.2 problem_types.yaml Schema
每個題型 (ProblemType) 至少必須包含以下欄位：
- `problem_type_id`: 題型唯一 ID。
- `skill_id`: 關聯的技能 ID。
- `subskill_id`: 關聯的子技能 ID。
- `display_name`: 題型顯示名稱。
- `runtime_category`: 運行時類別。**僅允許以下 6 種枚舉值**：
  - `deterministic_numeric`: 確定性數值答案（例如整數、分數、小數）。
  - `deterministic_expression`: 確定性代數式答案（例如多項式、 LaTeX 代數表達式）。
  - `deterministic_choice`: 確定性單選題答案。
  - `manual_review`: 需要教師人工閱卷的題型（如複雜繪圖、簡答題）。
  - `future_ai_judged`: 待未來 AI 視覺模型判分的題型（如推導步驟、手寫公式）。
  - `visual_or_handwriting`: 視覺繪圖或手寫輸入題型。
- `answer_type`: 預期答案數據類型（如 `integer`, `fraction`, `choice` 等）。
- `checker_type`: 批改器類型（如 `integer_checker`, `choice_checker` 等）。
- `examples_refs`: 對應的 textbook examples 參考 ID 清單。
- `prerequisite_subskills`: 該題型所需的先修子技能 ID 清單。
- `diagnosis_tags`: 診斷用細粒度標籤。
- `difficulty_policy`: 難度配置參數與出題範圍限制。
- `output_contract`: 預期輸出的 Payload 結構規範。
- `status`: 當前開發狀態。

### 5.3 examples_map.yaml Schema
為避免 AI 隨意造題，每一筆教材課本例題 (textbook_example) 必須精準對應以下欄位：
- `example_id`: 唯一的例題/隨堂練習 ID。
- `title`: 例題標題。
- `source_type`: 來源類型，如 `textbook_example` (課本例題), `textbook_practice` (隨堂練習), `self_assessment` (自我評量) 等。
- `source_section`: 課本來源章節或頁碼。
- `problem_preview`: 題目預覽文本內容（支援 LaTeX）。
- `skill_id`: 關聯的主技能 ID。
- `subskill_id`: 關聯的子技能 ID。
- `problem_type_id`: 關聯的題型 ID。
- `runtime_category`: 運行時類別。
- `classification_reason`: 分類為此題型與類別的具體原因說明。
- `manual_review_reason` 或 `future_ai_judged_reason`: 若該例題被歸類為非自動化出題，必須詳細記錄原因，防止硬塞至確定性代碼。

### 5.4 prerequisites.yaml Schema
必須支援子技能層級 (Subskill-level) 的先修與診斷依賴關係：
- `subskill_id`: 當前子技能 ID。
- `prerequisite_subskills`: 隸屬同主技能下之先修子技能 ID 清單。
- `prerequisite_skills`: 跨技能之先修外部 Skill ID 清單。
- `reason`: 先修依賴的學科邏輯說明。
- `remediation_candidates`: 診斷此子技能失敗後，推薦的補救練習題型與資源清單。

---

## 6. Verified Registry Schema (驗證註冊檔結構)

為確保運作安全性與非破壞性寫入，`verified_problem_types` 必須是 **dict list (字典列表)** 格式，絕對不可為簡單字串列表。

```yaml
verified_problem_types:
  - problem_type_id: absolute_value_numeric_evaluation
    skill_id: vh_數學B1_AbsoluteValue
    subskill_id: absolute_value_numeric_evaluation
    status: verified
    candidate_path: generated_candidates/absolute_value_numeric_evaluation/candidate_v1.py
    function_name: generate
    answer_type: integer
    checker_type: integer_checker

failed_problem_types:
  - problem_type_id: absolute_value_expression_simplification
    skill_id: vh_數學B1_AbsoluteValue
    subskill_id: absolute_value_expression_simplification
    status: failed
    latest_error_summary: "TimeoutException: Generation timed out after 5 seconds"
    preserve_previous_verified: true

manual_review_problem_types:
  - problem_type_id: absolute_value_geometric_graphing
    skill_id: vh_數學B1_AbsoluteValue
    subskill_id: absolute_value_geometric_graphing
    status: manual_review
    reason: "Requires plotting number lines and coordinate system which cannot be evaluated in a deterministic numeric format."

future_ai_judged_problem_types:
  - problem_type_id: absolute_value_proof_derivation
    skill_id: vh_數學B1_AbsoluteValue
    subskill_id: absolute_value_proof_derivation
    status: future_ai_judged
    reason: "Requires multi-step mathematical proof rendering and intermediate step analysis, which currently needs AI-vision based evaluation."
```

---

## 7. Candidate Payload Contract (Candidate 生成回傳格式契約)

Candidate 生成模組所導出的 `generate()` 函數，回傳的字典 (dict) 至少必須包含以下基本欄位：

- `problem_type_id`: 題型 ID。
- `skill_id`: 主技能 ID。
- `subskill_id`: 子技能 ID。
- `question_text`: 題目文本內容（必須為標準 LaTeX 數學表達式）。
- `answer`: 正確答案（必須與 `answer_type` 對齊）。
- `answer_type`: 答案類型類型。
- `checker_type`: 批改器類型。
- `solution_steps`: 詳細的逐步解析過程。
- `metadata`: 詮釋資料字典，**至少必須包含以下欄位**：
  - `scenario_family`: 情境家族名稱。
  - `scenario_id`: 情境 ID。
  - `parameter_signature`: 該隨機題目的參數特徵簽章（用以驗證多樣性）。
  - `question_pattern_id`: 題型樣式 ID。
  - `diagnosis_tags`: 診斷標籤清單。
  - `prerequisite_subskills`: 該隨機題目具體所需的先修子技能清單。

---

## 8. Verifier Gate 驗證閘門

在 Candidate 程式碼被註冊至 Verified Registry 前，必須順利通過以下 **12 項 Verifier Gate 必要檢查**：

1. **syntax/import/generate exists**：程式碼無 Python 語法錯誤，能被動態導入，且存在 `generate()` 導出入口函數。
2. **payload contract**：題目生成 payload 結構完整，核心欄位及 `metadata` 均無缺失。
3. **dynamic sampling >= 30**：執行連續採樣測試至少 30 次，且過程中無異常拋出。
4. **answer_type / checker_type**：答案與批改器類型相容，且在系統白名單內。
5. **correct answer self-check**：將產生的正確答案送入 Checker，批改結果必須 100% 通過。
6. **wrong answer rejection**：構建故意寫錯的答案送入 Checker，批改結果必須 100% 被拒絕判定為錯。
7. **LaTeX safety**：題目與解析中 LaTeX 語法結構正確，不得有未配對之 `$` 符號。
8. **no placeholder**：題目與解析中絕對不得有 placeholders（如 "TBD"、"TODO"、"..." 等字元）。
9. **duplicate guard**：採樣 30 次題目文本重複率必須低於上限，以防生成千篇一律題目。
10. **parameter_signature diversity**：採樣中 `parameter_signature` 隨機組合數必須高於閾值，防止假隨機多樣性。
11. **timeout**：單次題目生成耗時限制（必須在 5s 內完成）。
12. **choice validator if choice**：若為選擇題，選項必須為 4 個，正確答案必須精確包含在選項內，且選項不可重複。

---

## 9. B1 AbsoluteValue 具體範例對齊

以下為高職數學 B1 絕對值技能的實體規格對齊範例：

- **skill_id**: `vh_數學B1_AbsoluteValue`
- **subskill_id**: `absolute_value_numeric_evaluation`
- **problem_type_id**: `absolute_value_numeric_evaluation`
- **runtime_category**: `deterministic_numeric`
- **answer_type**: `integer`
- **checker_type**: `integer_checker`
- **prerequisite_subskills**: `[]`
- **example question**: `求 $|-5|$ 的值。`

---
*文件日期: 2026-05-25*
*版本: v0.1.1 (SOP 規格包更新版)*

---

## 10. Closure �n�D�]examples_map / problem_types / registry�^

### 10.1 examples_map �C�� example �������
- `example_id`
- `title`
- `source_type`
- `source_section`
- `problem_preview`
- `skill_id`
- `subskill_id`
- `problem_type_id`
- `runtime_category`
- `classification_reason`
- `generator_status`

### 10.2 problem_types.yaml �C�� problem_type �������
- `problem_type_id`
- `skill_id`
- `subskill_id`
- `runtime_category`
- `answer_type`
- `checker_type`
- `examples_refs`
- `prerequisite_subskills`
- `diagnosis_tags`
- `status`

### 10.3 registry verified_problem_types ���c�n�D
`verified_problem_types` ������ dict list�A�B�C���]�t�G
- `problem_type_id`
- `skill_id`
- `subskill_id`
- `status`
- `candidate_path`
- `function_name`
- `answer_type`
- `checker_type`

### 10.4 Final Coverage Gate �ﱵ
Skill Closure �P�w�����G
- examples_map �л\����ʻP��짹���
- observed deterministic problem_types verified �����
- registry �i�Ωʡ]wrapper �i���J verified candidate�^
- verify report�]`verify_skill_gencode.py`�^

��X�ܤ֥]�t�G
- `coverage_status`
- `full_skill_coverage`
- `final_status` (`PASS` / `PARTIAL` / `FAIL`)
- `blocking_reasons`

### 10.5 B1 AbsoluteValue ���\�ר�
- `skill_id = vh_�ƾ�B1_AbsoluteValue`
- `verified_problem_types`:
  - `absolute_value_numeric_evaluation`
  - `absolute_value_equation_basic`
  - `absolute_value_distance_from_zero`
- `coverage_status = FULL_OBSERVED_COVERAGE`
- `full_skill_coverage = true`
- `final_status = PASS`

�����G���רҽT�{��@ skill �q examples_map�Bproblem_type closed loop�Bregistry merge�Bwrapper verify �� Final Coverage Gate ������y�{�C
