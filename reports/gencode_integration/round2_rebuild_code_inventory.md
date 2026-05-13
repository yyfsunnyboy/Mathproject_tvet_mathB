# Gencode × B4 整合前盤點 Round 2：舊版 Rebuild Code / Generate Code 流程盤點

本報告旨在盤點舊版專案中的「代碼生成 (Generate Code)」與「重建代碼 (Rebuild Code)」流程，評估其整合至 B4 SOP 架構的技術細節、風險與必要修改。

---

## 1. 入口與觸發機制 (Entry Points)

### 1.1 教師/管理員手動觸發
*   **頁面**: `admin_skills.html` (路由: `/skills`)
*   **按鈕**: 「重建 Code」(`<button class="btn btn-secondary" onclick="regenerateSkillCode(...)">`)
*   **後端 API**: `admin_regenerate_skill_code` (位於 [admin.py](file:///d:/Python/Mathproject_tvet_mathB/core/routes/admin.py))
    *   **邏輯**: 呼叫 `auto_generate_skill_code(skill_id, force_architect_refresh=True)`。
    *   **特性**: 強制刷新 Prompt Architect，確保使用最新的課本例題 (TextbookExample) 進行規格分析。

### 1.2 自動觸發 (題目晉升)
*   **功能**: 當學生上傳的題目經審核「晉升」為正式例題時。
*   **後端 API**: `admin_promote_question` (位於 [admin.py](file:///d:/Python/Mathproject_tvet_mathB/core/routes/admin.py))
    *   **邏輯**: 
        1.  將 `StudentUploadedQuestion` 轉存至 `TextbookExample`。
        2.  呼叫 `PromptArchitect` 生成最新規格 (MASTER_SPEC)。
        3.  呼叫 `auto_generate_skill_code(skill_id)`。

---

## 2. 生成引擎核心：`core/code_generator.py`

生成流程採用的 `auto_generate_skill_code` 是目前系統中最複雜的邏輯，分為以下五個階段：

### Phase 0: AI 生成與 Prompt 構建
*   **工具**: `PromptBuilder`
*   **邏輯**: 
    *   優先讀取 `SkillGenCodePrompt` 表中的 `MASTER_SPEC`。
    *   若有開啟 `use_golden_prompt`，則使用實驗過濾後的黃金 Prompt。
    *   調用 `_call_ai` (封裝 `ai_wrapper`) 獲取原始 Python 代碼。

### Phase 1: 基礎清理 (Basic Cleanup)
*   **功能**: 處理 Markdown 標記 (```python)、多餘的解釋文字與結尾說明。
*   **關鍵函數**: `_basic_cleanup`
*   **模式**: 對於 Local 模型 (Qwen) 採用 `strict_mode`，對於 Cloud 模型 (Gemini) 則較為寬鬆以保留 docstring。

### Phase 2 & 3: 進階修復 (Healers)
*   **控制項**: 根據 `AblationSetting` (Ab1/Ab2/Ab3) 決定啟用的修復程度。
*   **RegexHealer**: 
    *   修正 LaTeX 轉義字符 (`\v` -> `\\v`)。
    *   修正 `safe_eval` 格式。
    *   自動注入遺漏的 `check()` 函數。
*   **ASTHealer**: 
    *   **結構分析**: 使用 `ast.parse` 檢查語法，修復幻覺函數調用。
    *   **Semantic Rescue (LLM 自癒)**: 若 AST 解析失敗，會將錯誤訊息丟回 AI 進行「語義級別」的代碼重寫。

### Phase 4: 注入與驗證 (Injection & Validation)
*   **Domain 注入**: `_inject_domain_libs` 會讀取 `agent_skills/{skill_id}/skill.json`，將 `RadicalOps`、`FractionOps` 等 Domain Library 的完整實作注入代碼，使其成為 **Self-Contained (自包含)** 檔案。
*   **語法驗證**: `_validate_code` 調用靜態編譯檢查。

### Phase 5: 動態採樣 (Dynamic Sampling)
*   **沙盒環境**: 透過 `subprocess` 在獨立環境執行生成的代碼。
*   **驗證指標**: 
    *   執行 `generate()` 3 次。
    *   檢查是否發生無窮迴圈 (Timeout 5s)。
    *   檢查產出的字典結構是否包含 `question_text` 與 `correct_answer`。

---

## 3. 實驗與狀態追蹤

### 3.1 實驗日誌 (`experiment_log`)
每次生成皆會記錄：
*   `repaired`: 是否經過 Healer 修復。
*   `regex_fixes` / `ast_fixes`: 具體修復次數。
*   `is_valid`: 最終是否通過動態驗證。
*   `raw_response` 與 `final_code`: 保存生成的前後對比。

### 3.2 Ablation Study (對照組管理)
*   **Ab1 (Bare)**: 無工具庫注入，無 Healer。
*   **Ab2 (Infra)**: 注入工具庫，但無進階 Healer。
*   **Ab3 (Full)**: 工具庫 + Regex Healer + AST Healer (生產環境標準)。

---

## 4. 整合至 B4 SOP 的技術缺口分析

經過盤點，將此流程整合至 B4 SOP (技高數 B 第四冊) 存在以下挑戰：

| 挑戰項目 | 現況描述 | 整合建議 |
| :--- | :--- | :--- |
| **狀態流轉 (Gating)** | 目前生成後直接覆蓋檔案，缺乏 `Verified` 狀態位。 | 在 `SkillInfo` 增加 `gencode_status` 欄位 (Draft -> Verified -> Production)。 |
| **路由硬編碼** | B4 路由寫死在 `question_router.py`，無法動態註冊新生成的 Generator。 | 建立 `B4GeneratorRegistry` 資料表，將 Python 映射關係遷移至資料庫。 |
| **版本控制** | 同一個 `skill_id` 只能有一個 `.py` 檔案。 | 引入 `generator_version` 概念，允許存儲多個生成版本進行 A/B Testing。 |
| **錯誤回傳 UI** | 目前生成失敗僅在 Console 報錯，教師端 SweetAlert 訊息不夠細緻。 | 應將 `ASTHealer` 的修復日誌 (`ast_stats.logs`) 傳回前端展示。 |

## 5. 結論

舊版的 `code_generator.py` 已經具備非常成熟的「自癒 (Self-healing)」與「驗證 (Subprocess Sampling)」能力，這在業界屬於先進做法。整合到 B4 的核心工作不在於改寫生成邏輯，而在於 **「建立路由對應表」** 與 **「增加狀態審核機制」**，確保自動生成的題目在進入 Production 前經過教師的動態採樣驗證。

---
*報告完成日期: 2026-05-13*
*盤點人員: Antigravity AI*
