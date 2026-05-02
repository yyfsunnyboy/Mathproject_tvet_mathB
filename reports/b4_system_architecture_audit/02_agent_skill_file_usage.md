# Agent Skill 檔案用途與架構調查報告 (02_agent_skill_file_usage.md)

> ## 人工校正版註記
> 本報告為系統架構盤點文件，主要用途是記錄目前程式碼與目錄結構中「實際觀察到」的事實。涉及高職數學 B4 導入方向的內容，已依據目前 B4 原始教材資料校正：B4 主軸為排列組合、二項式、機率、統計與資料分析，不包含微積分、向量與圓錐曲線。因此本報告中的建議不得被視為最終 SOP，後續應以 B4 自動出題 SOP 為準。

## 1. `agent_skills` 目錄結構摘要

在 `agent_skills` 中，每個技能（如 `jh_數學1上_FourArithmeticOperationsOfIntegers`）皆遵循標準化的檔案結構：
- `skill.json`：技能的元資料（Metadata）設定檔。
- `evals.json`：評測與測試案例的設定檔。
- `SKILL.md`：核心 System Prompt 與技能規格文件。
- `prompt_benchmark.md`：Benchmark 模式專用的 Prompt。
- `prompt_liveshow.md`：LiveShow 模式專用的 Prompt。
- `experiments/`：存放實驗性腳本或暫存檔案的目錄。

## 2. 檔案用途表

| 檔案名稱 | 用途說明 |
| :--- | :--- |
| **`SKILL.md`** | 定義 K12 數學演算法工程師的角色與行為邊界。內容包含 Skill Identity、Output Contract、工程限制（Injected APIs）、Family Catalogue (例如 I1~I8 的拓撲定義) 以及子技能節點等。這是一份兼具「系統級提示詞」與「規格文件」的文件。 |
| **`skill.json`** | 定義技能的屬性，例如 `skill_id`、`display_name`、`family`、`level_range`、`injected_apis`、支援的 `modes` (BENCHMARK, LIVESHOW) 以及別名。 |
| **`evals.json`** | 定義該技能的測試用例集合。包含不同難度 (level) 或 Ablation Target 的評估 ID、超時設定及生成參數。 |
| **`prompt_benchmark.md`** | 針對 `BENCHMARK` 模式的任務提示詞。要求模型依照指定的 `level` 難度，無中生有生成題目，並附帶強烈的格式化與結構化要求。 |
| **`prompt_liveshow.md`** | 針對 `LIVESHOW` 模式的任務提示詞。這是一個「結構同構出題引擎」，接收 `{{OCR_RESULT}}` 後，判定其 Family 拓撲，並生成一題結構、符號順序完全相同，但數值重新配置的新題。 |

## 3. 被哪些程式讀取 (`agent_tools` 目錄調查)

根據搜尋 `agent_tools/` 的結果，各檔案的讀取情況如下：

- **`SKILL.md`**：
  - `validate_skill_md.py`：驗證所有技能的 `SKILL.md` 格式一致性。
  - `test_ab_verification.py`：在測試特定 Ablation mode（如 Ab2, Ab3）時讀取此檔作為 Prompt。
  - `check_fake_api.py`：檢查是否移除不存在的假 API。
  - `benchmark.py`：作為 Benchmark 模式的 Fallback Prompt，當 `prompt_benchmark.md` 不存在或特定模式下會讀取。
- **`evals.json`**：
  - `validate_evals.py`, `validate_all_evals.py`：驗證 JSON 格式與分布。
  - `validate_code.py`, `test_ab_verification.py`：確保檔案存在。
  - `benchmark.py`：讀取測試用例以執行批次評測生成。
- **`prompt_benchmark.md`**：
  - `benchmark.py`：在執行評估時優先讀取此檔作為任務 Prompt。
- **`prompt_liveshow.md`** 與 **`skill.json`**：
  - 在本次 agent_tools 搜尋範圍內，目前未找到明確的直接讀取紀錄；是否由 Backend runtime 或 live_show 相關模組讀取，需另行查證。

## 4. `prompt_benchmark.md` 與 `prompt_liveshow.md` 的差異

- **`prompt_benchmark.md` (難度分級生成)**：目的是「從零生成」。輸入參數為難度等級（如 `level=1`、`level=2`），Prompt 會規範該難度對應的數值範圍與子結構，產出符合難度設計的新題目。
- **`prompt_liveshow.md` (結構同構克隆)**：目的是「複製變形」。輸入為學生的原題 OCR 文字，Prompt 要求模型先分析原題隸屬於哪一個 Family，然後在「絕對保持運算子數量、順序與括號拓撲」的嚴格限制下，重新隨機生成數字，產生出一道同構的新題。

## 5. `SKILL.md` 的定位 (Runtime / Benchmark / 文件)

`SKILL.md` 目前屬於 **混合用途 (Hybrid)**：
1. **規格文件**：它定義了人類工程師與系統理解此技能的分類（Family Catalogue）與規範。
2. **Fallback / Baseline Prompt**：在 `benchmark.py` 與 `test_ab_verification.py` 中，它被實際讀取並作為系統級提示詞 (System Prompt) 餵給模型，特別是在某些實驗基準線（Ablation）下。
（結論：它是一份寫成 Prompt 格式的規格書，在系統架構中確實有被當作 Runtime/Benchmark 的 Baseline 提示詞使用。）

## 6. 可沿用到高職 B4 的建議與初步缺口/風險

### 可沿用到高職 B4 的部分
- agent skill 的檔案結構可作為 B4 技能包參考。
- SKILL.md 可作為教學技能規格與 prompt 規範。
- skill.json 可擴充 subskills、problem_types、generator_keys、domain_functions 等 metadata。
- evals.json 可擴充為 problem_type 層級的測試案例。
- prompt_benchmark.md 可用於離線 benchmark 與 generator 評測。
- prompt_liveshow.md 可保留為 live demo / 題型同構改寫用途，但 B4 長文字題與統計表格題需加強限制。

### 需要修正的觀念
- B4 不應採用「一個 skill 一支 generator」。
- B4 應採用：skill → subskill → problem_type → generator → domain function
- problem_type 才是自動出題程式的最小單位。
- subskill 才是自適應學習追蹤與補救的較合理單位。

### B4 風險
- 統計與機率文字題容易出現題幹、答案、選項不一致。
- 表格型與圖表型題目需要 table/chart domain functions 與 verifier。
- prompt_liveshow 的同構生成不應直接用於正式學生端，需經 eval 與人工審查。
- SKILL.md 若同時作為文件與 fallback prompt，後續需要明確標註 runtime / benchmark / liveshow 用途。
