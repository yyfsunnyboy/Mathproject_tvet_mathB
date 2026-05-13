# Gencode 與 Agent Skill v2 整合總體設計 v0.1

## 1. 文件目的
本文件旨在規劃高職數學 B1-B4 教材流水線的總體實作架構與時程。透過將研究線的 Agent Skill 原型轉化為部署線的生產級架構，實現以下目標：
- **規格化 B4 既有成果**：將硬編碼的路由與狀態轉化為可管理的 Registry。
- **建立 B1-B3 流水線**：定義從教材匯入到 `runtime_ready` 的標準自動化流程。
- **Agent Skill v2 升級**：將 Skill 定義從單一檔案提升為包含數學家族、題型規格與驗證邏輯的規格包。
- **最大化 AI 自動化**：利用 LLM 執行盤點、生成與驗證，同時保留必要的人工審閱門檻。

## 2. 核心決策

### 2.1 B4 不重新生成
B4 章節已具備完整的手動開發 Generator 與路由，本計畫不對 B4 執行重新生成。B4 的任務是：
- **補齊 Registry**：將現有 `question_router.py` 中的映射關係匯出為規格檔。
- **統一狀態標記**：明確區分 `runtime_ready`、`manual_review` 與 `future_ai_judged`。
- **標竿參考**：作為 B1-B3 自動化生成的參考實現 (Reference Implementation)。

### 2.2 B1 作為新版流水線 prototype
B1 將作為首個驗證「自動化流水線」的章節，完整跑通以下流程：
> 教材匯入 → 主技能確認 → subskill/problem_type 拆解 → examples_map → gencode candidate → verifier → registry → runtime_ready → practice smoke。

### 2.3 不急著 DB 化
考量到整合初期規格仍有變動可能，目前不修改 `models.py` 或新增資料表。採用 **YAML / JSON Registry** 作為過渡方案，待 B1 至少一章節穩定後，再評估正式 DB Schema。

### 2.4 Agent Skill 升級為 v2
Agent Skill v2 不再是單一的 `skills/{skill_id}.py`，而是由以下組成的規格包：
- **Math Family Core**：定義數學家族通用的領域函數 (Domain Functions) 與 Checker。
- **Curriculum Profile**：定義不同學程 (技高/普高) 的難度與題量偏好。
- **ProblemType Spec**：定義最小生成單位的輸入/輸出契約與 LaTeX 規範。

### 2.5 Edge AI 暫不進第一版正式流程
Edge AI (如 Qwen Coder) 暫列為實驗性質的 Provider。第一階段流水線優先使用穩定度較高的 Cloud 模型 (Gemini/GPT)，確保 B1 Pipeline 邏輯正確。

## 3. 研究成果與部署版的對應

部署版並非放棄研究成果，而是將原型 (Prototype) 轉化為可部署的生產架構 (Production Architecture)。

| 舊版研究成果 | 高職部署版轉化 | 說明 |
|---|---|---|
| Agent Skill / SKILL.md | Agent Skill v2 / problem_type spec | 從單一 Markdown 升級為結構化規格包。 |
| 鷹架 prompt | prompt_gencode + domain allowlist | 將提示詞與領域函數白名單分離，增加生成穩定性。 |
| AST Healer | candidate generator 修復流程 | 保留自動修復語法錯誤的能力。 |
| MCRI | verifier report / runtime_ready gate | 將多樣性檢查轉化為正式的准入閘門。 |
| Code-as-Content | deterministic generator | 維持「代碼即題目」的確定性生成。 |
| AKT / PPO | adaptive practice / routing trace | 將 IRT 路由軌跡化，便於診斷與優化。 |
| Hybrid RAG | 學生補救提示與問答輔助 | 轉化為 RAG 補救引導內容。 |

## 4. 新版資料與規格架構

系統採用以下層級結構，確保題目生成的精確度：
**Skill → SubSkill → ProblemType → GeneratorKey → Generator Function → Checker / Validator**

### 為什麼 ProblemType 是最小單位？
- **Skill 範圍過廣**：一個 Skill (如 `vh_數學B4_Combination`) 包含多種截然不同的題型（基本運算、選取問題、組合等式）。
- **單一職責原則**：每個 Generator 函數僅負責一個 `problem_type`，能顯著降低 AI 生成時的邏輯複雜度，並提高驗證 (Verifier) 的準確性。

## 5. Agent Skill v2 建議結構

```text
agent_skills_v2/
  family_core/
    <math_family>/           # 例如 counting, probability
      family.yaml            # 家族基本屬性
      domain_functions.yaml  # 允許使用的數學函數白名單
      common_checkers.yaml   # 家族通用的批改邏輯
      profiles/
        vocational_math.yaml # 高職專屬規格

  vocational_math_b1/        # 按冊分類
    chapter_x/               # 按章分類
      skill.yaml             # 技能主表與 SubSkill 關聯
      problem_types.yaml     # 核心規格：定義每個題型的 IO 契約
      examples_map.yaml      # 課本例題與 problem_type 的映射關係
      prompt_gencode.md      # 針對該章節優化的生成提示詞
      evals.yaml             # 驗證樣本與預期結果
```

## 6. Registry 過渡策略

在正式 DB 化前，使用 `configs/` 目錄下的 YAML 檔案作為動態路由來源。

### 建議欄位
- `skill_id`, `subskill_id`, `problem_type_id`, `generator_key`
- `module_path`, `function_name`
- `answer_type`, `checker_type`
- `chapter`, `status`, `source`, `version`
- `manual_review` (bool), `future_ai_judged` (bool)
- `verified_at`, `notes`

### Status 狀態機
- `candidate`: AI 剛生成，待驗證。
- `generated`: 已生成但尚未通過完整門檻。
- `verified`: 已通過自動化驗證。
- `runtime_ready`: 已通過人工確認，可進入生產路由。
- `failed`: 驗證失敗。
- `manual_review`: 需轉為手寫/人工閱卷。
- `future_ai_judged`: 待未來 AI 視覺模型判分。
- `deprecated`: 已廢棄。

## 7. 分期實作計畫

### Phase 0：總體 SOP 固化 (當前)
- **目標**：完成本總體實作計畫書。
- **產出**：`docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.1.md`。
- **不做事項**：不修改任何代碼。
- **驗收標準**：文件獲得核准。

### Phase 1：B4 既有成果規格化
- **目標**：不重生 B4，但將現有狀態轉化為可動態讀取的 Registry。
- **產出**：`configs/b4_generator_registry.v0.1.yaml`、盤點報告。
- **不做事項**：不改動 `question_router.py` 邏輯，僅做資訊匯出。

### Phase 2：Agent Skill v2 規格設計
- **目標**：定義 `ProblemType` 的 JSON Schema 與規格包範本。
- **產出**：規格設計文件、`agent_skills_v2/_template/`。

### Phase 3：B1 單一小節 Prototype
- **目標**：完成 B1 首個小節的完整自動化生成閉環。
- **流程**：教材匯入 → 拆解 → 生成 Candidate → Verifier → Registry。

### Phase 4：Verifier / Runtime Ready Gate 最小版
建立 13 項必要閘門：
1. Syntax check
2. Import check
3. generate() exists
4. Output contract check
5. Dynamic sampling (30+ 次)
6. Answer_type check
7. Checker_type check
8. Correct answer self-check
9. Wrong answer rejection
10. LaTeX safety
11. No placeholder
12. Duplicate / fake diversity guard
13. Timeout guard

### Phase 5：教師端 UI 最小版
- **目標**：提供教師管理教材流水線的最小操作界面。
- **功能**：例題對應、產生 Candidate、執行驗證、手動 Promotion `runtime_ready`。
- **不做**：不做一鍵自動生成、不開放自動 Promotion。

### Phase 6：B1 擴章，B2-B3 複製
按照 B1 單元 → B1 全冊 → B2 → B3 順序遞進，每章產出對應 Registry 與報告。

### Phase 7：Edge AI Provider 導入
在 Spec 穩定後，引入 Edge AI 輔助產生 Candidate 與低風險題型變體。

### Phase 8：穩定後 DB 化
待 Pipeline 穩定運行一學期後，將 Registry 正式遷移至資料庫（`MathFamily`, `ProblemType` 等資料表）。

## 8. 最小人工介入策略

| 類型 | AI 可以做 | 人工只做 (Gatekeeper) | 禁止 AI 自動做 |
|---|---|---|---|
| **教材處理** | 盤點檔案、拆解 ProblemType 草稿 | **確認 ProblemType 是否合理** | 直接覆蓋 Production Generator |
| **生成驗證** | 產生 Candidate、執行 Verifier | **抽查代表性題目** | 直接修改 `question_router.py` |
| **路由狀態** | 匯出 Registry、產出 Audit Report | **決定 Runtime_ready Promotion** | 直接新增 DB Table |
| **品質控制** | 執行 13 項 Gate 檢查 | **決定 Manual_review 題型** | 直接開放學生端 |

## 9. 不適合第一階段自動化的題型
以下題型列為 `manual_review` 或 `future_ai_judged`：
- **圖形/表格題**：涉及複雜繪圖與布局。
- **樹狀圖/列舉題**：涉及多路徑邏輯與手寫。
- **證明/過程題**：需要 AI 視覺判斷推導過程。

## 10. 下一步
下一個實作任務是 **Phase 1**：
**B4-Registry-A：匯出既有 B4 Generator Registry v0.1**

- **目標**：將 B4 現有路由、Allowlist 與驗證狀態整理為結構化 YAML。
- **產出**：`reports/gencode_integration/b4_existing_generator_registry_audit.md`。

---
*文件日期: 2026-05-13*
*版本: v0.1*
