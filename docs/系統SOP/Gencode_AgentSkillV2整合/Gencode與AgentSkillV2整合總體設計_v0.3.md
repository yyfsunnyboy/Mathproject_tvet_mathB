# Gencode與AgentSkillV2整合總體設計 v0.3

## 0. 文件目的與最高原則
本文件為 Gencode 與 AgentSkillV2 整合的最高 SOP 及總流程法規。後續所有 Codex / Antigravity 任務凡涉及 Gencode、Phase 0/1/2/3 流程、ProblemTypeSpec、runtime wrapper 與 source classification 等，均須以此文件為最高規範，並在修改回報中明確列出遵守之條款。

### 16 大最高原則

**v0.2 原則（1–12，完整保留）**

1. **ProblemTypeSpec** 是 Phase 2 / Phase 3 / Runtime Generation 的唯一權威來源，一切 runtime 生成必須以此為準。
2. **Source examples** 只能作為分類與結構推導之 evidence，絕不可直接主導或強行限制 runtime generator 的生成內容。
3. **Phase 1** 只負責來源盤點、來源分層與題型歸納，**絕對不可**過早阻擋（block）整個 skill。
4. **Gate 必須分層**：區分為 source-level reject、problem-type-level pending/blocked、及 skill-level blocked，避免單題問題上升至 Skill 阻擋。
5. **單一壞題**、少量 missing_answer、broken_latex 或 OCR noise，**絕對不可**直接升級為整個 skill blocked。
6. 只要 **usable core examples** 足以形成至少一個合法 ProblemTypeSpec，即允許後續流程繼續，但需於報告中提示 warning。
7. **分類依據**：AI classification、rule classification、registry classification 均為 classification_source evidence；後續流程只能讀取並信任 `final_classification`。
8. **Phase 3 嚴格邊界**：不得重新猜測題型、不得從 source examples 反推 checker，更不得自行覆寫 Phase 2 定義的 `answer_contract`（展現型態強制校正除外，見 AnswerContract SOP §4.3）。
9. **反特例化**：不得為單一 skill_id、problem_type、章節或特定題型寫死通過條件或強行寫入特例邏輯。
10. **Coverage $\neq$ Quality**：coverage gate 通過僅代表具備 runtime/review 路徑，不等於 quality gate（學生端可用性）通過。
11. **Runtime-Ready 定義**：不只代表會出題與批改，還必須通過 textbook coverage、runtime quality、web runtime 與 source alignment 的四重檢查。
12. **Codex 任務規範**：後續每一輪 Codex / Antigravity 任務都必須先閱讀本設計，並於回報中列出遵守了哪些條款。

**v0.3 增補原則（13–16）**

13. **【薄入口外殼原則】**：`skills/{skill_id}.py` 僅作前台請求之 Thin Facade；所有實體計算、多模板分流、選項 shuffle 與 SymPy 驗證，必須穿透外殼，在全域 `generate_for_skill()` → `SLOT_REGISTRY` 動態插槽庫中執行。詳見 [AgentSkillV2_ProblemType規格包設計_v0.3.md §1.5](AgentSkillV2_ProblemType規格包設計_v0.3.md)。
14. **【插槽去耦合解鎖原則】**：任一 ProblemTypeSpec 若僅完成編譯而未在 `template_slot_resolver.TASK_FAMILY_TO_SLOT` 與 `slot_generators.SLOT_REGISTRY` 雙向註冊實體處理函數，執行期必發生**退化坍塌**（fallback 至通用 stub 或重複題幹）。規格編譯與插槽實作為**強制共生運作**，缺一不可。
15. **【數據驅動靈魂 Token 原則】**：題幹完整性約束所要求的核心關鍵字（靈魂 Token），必須 100% 由 `semantic_contract.required_concepts` 與 Phase 1 來源樣本動態提取驅動；Codegen 提示詞（`build_generator_code_prompt` §5）與插槽生成器均須引用該 Token 集合，**嚴禁**針對單一 skill_id 寫死特例字串。

16. **【Phase 錯誤對照權威地圖（Self-Healing 自我修復）】**：當自動化流水線在不同 Phase 出現 Warning 或 Error 時，管線與 AI 修復任務**必須**依下列權威地圖進行規則對照與自我修復（Self-Healing），**不得**跨文件混用或自行臆測修復策略：
    - **Phase 1（來源審查）與 Phase 2（規格建構）**：凡涉及「單元分類、樣本拯救、阻擋層級判定、抽題 pool 分流」之異常，**唯一對照權威**為本文件《Gencode與AgentSkillV2整合總體設計_v0.3.md》。
    - **Phase 2.5（規格稽核）與 Phase 3（編譯期）**：凡涉及「選擇題、填充題、多小題、圖表題之展現型態（`presentation_mode`）、Contract 欄位剛性覆寫、幽靈快取洗淨」之異常，**唯一對照權威**為《AnswerContract_EquivalenceType_Gate_v0.3.md》。
    - **Phase 3 生成產物與 Runtime 執行期**：凡涉及「技能檔外殼極簡化（Thin Facade）、註冊表非破壞性合併（Non-Destructive Merge）、以及插槽動態註冊分流」之異常，**唯一對照權威**為《AgentSkillV2_ProblemType規格包設計_v0.3.md》。
    - **執行規則**：Gen Code 批次管線報錯時，必須先抓取報錯 Phase 標籤（如 `Phase 2.5`），自動載入對應 SOP 全文作為修復 Context，再觸發 Self-Healing 修正；實現無人值守 24 小時自我閉環出題。

---

## 1. Controlled AI Closed Loop (AI 閉環流程)
所有自動生成任務必須嚴格遵循以下閉環流程，確保小步快跑、安全可控：
`inventory (盤點) → plan (計畫) → implement (實作) | test (測試) → report (報告) → human approve (人工審核)`

### 閉環執行規則
- **小步閉環**：每輪只處理一個 phase，且一次只處理少量（建議 1-3 個）problem_type。
- **盤點先行**：每輪開始前先盤點 existing files，提出 implementation plan，明訂 allowed files 與 forbidden files，經人工核准後方可改 code。
- **嚴防擴大**：不允許 AI 自行擴大開發 scope，或為了通過測試而新增臨時、錯誤或破壞架構的 hardcode。
- **測試與報告**：每輪必須有完整的測試與品質 summary report。完成後狀態停在 READY_FOR_REVIEW、BLOCKED 或 CLOSED，等待人工 approve，不得自行連續開啟下一階段。

---

## 2. 六層流程定義與邊界

> v0.3 說明：v0.2 之 Layer 1–5 **完整保留**；本版增量新增 **Layer 6（執行期插槽動態註冊與分流實作層）**，與 Phase 3 尾端及 Runtime 抽題路徑銜接。

### Layer 1：Import / Source Normalization (匯入與標準化)
- **職責**：切題、題幹清理、答案/選項擷取、LaTeX 語意保留、關聯 chapter/section/skill_id、標記 source_type（可引用 MathType DOCX 轉 LaTeX 工具）。
- **禁止**：不得判斷 problem_type、不得判斷 runtime readiness、不得建立 generator，更不得因題目不好直接刪除原始資料。
- **【行政歸屬唯讀校驗（vh_數學 標準格式矩陣）】**：
  1. 管線掃描端**必須**強制校驗 `skill_id` 是否完美吻合資料庫既有之 `vh_數學...` 標準格式矩陣；**嚴禁**自行發明、猜測或補寫不存在的 ID 前綴（含已廢棄之草稿前綴）。
  2. 不符標準之 malformed 損毀字串須在 Layer 1 **入口剛性攔截**，標記 `skill_id_format_violation`，**沒收 DB 寫入權**，禁止進入後續 Phase。
  3. 校驗器由 `pipeline_orchestrator.py` 在教材匯入（Scenario 1️⃣）啟動、`_load_examples` 之後強制執行；AI **不得**自行更名、補前綴或繞過校驗。

### Layer 2：Source Audit (來源品質審核)
- **職責**：審查每題來源品質，標記 source_item_status（如 usable / rejected / enrichment / future_ai_judged / source_bank_only），並記錄 missing_answer、broken_latex、graph_required 等標記。
- **禁止**：不得因少量 rejected 題目而阻擋整個 skill 的推進，也不得在此階段建立 ProblemTypeSpec 或決定 Phase 3 generator。
- **【Anchor Shield（單元錨定防線）】**：
  1. 管線從 Word 讀入並寫入資料庫的 **`skill_id` 為最高行政命令且唯讀**；Layer 2 僅可審查來源品質，**嚴禁** AI 以分類錯誤、超綱或低置信度為由，將題目剔除出本單元或改派至其他 `skill_id`。
  2. 若 AI 觸發 `unclassified_low_confidence` 或企圖拒絕收錄，管線**必須沒收 AI 的拒絕權**，強制標記 `FORCE_ALLOWED_FOR_INDUCTION` 並全自動分發臨時代理題型 ID，硬推推進後續 Phase，死守 **Fidelity over Coverage（課本忠實度高於題型覆蓋率）** 紅線。
  3. `should_remap` 僅可作為**人工覆寫**標記，**不得**由 AI 在 Layer 2 自動觸發以繞過 Anchor Shield。
- **【行政歸屬唯讀校驗（複核關卡）】**：
  1. Layer 2 審查時須**二次複核** Layer 1 已鎖定之 `skill_id` 仍符合 `vh_數學...` 標準格式矩陣；若發現漏網、AI 改寫或 OCR 損毀，立即升級為 `skill_id_format_violation` 並阻擋該批次。
  2. 審查報告須記錄 `skill_id_prefix_validated: true/false` 與 `skill_id_prefix_validation_reason`（如 `vocational_high_school_math_core_scope`），作為 Phase 1 Gate 必要欄位。

### Layer 3：Problem Type Induction (題型歸納)
- **職責**：僅使用 **usable core examples** 歸納 candidate problem types，產出 target_task、task_family、answer_type，以及草擬的 answer_contract / semantic_contract，以 `final_classification` 作為唯一分類結果。
- **禁止**：不得讓 source_quality_reject 題目參與 core induction，不得讓 registry_rule 自動等於 needs_review，也不得把素養題預設放入 core induction。
- **【Anchor Shield（單元錨定防線）】**：
  1. 題型歸納必須在**當前唯讀 `skill_id` 錨定範圍內**進行；AI **嚴禁**以「此題不屬於本單元」為由，將 core example 移出 induction 或改寫 `skill_id`。
  2. 對 `unclassified_low_confidence` 之靈魂課本原題，管線**不得**移入 `skipped` 列表；必須在現場分發臨時代理題型 ID（如 `proxy_<skill_id>_<hash>`），強制送入 Phase 2 觸發多模板生成（Multi-Template Generator）。
  3. 歸納結果之 `final_target_task` / `final_task_family` 僅描述題型語意，**不得**覆寫或質疑 Word 匯入時鎖定之 `skill_id` 行政歸屬。

### Layer 4：Spec Gate (規格審查門檻)
- **職責**：以 **problem_type 為單位** 判斷 readiness（runtime_ready / pending_template / blocked），驗證 AnswerContract、SemanticContract 等契約完整性，判斷是否可進入 Phase 3。
- **禁止**：不得以整個 skill 為唯一 gate 單位，不得把 source-level reject升級為 skill-level blocked，亦不得對特定 skill 寫死放行。

### Layer 5：Runtime Generation (代碼生成與綁定)
- **職責**：僅根據通過 Spec Gate 的 ProblemTypeSpec 生成 runtime code，使用 answer_contract 產生 checker，使用 semantic_contract 控制生成語意與 randomization，產生 verified generator 後由 registry 接入 thin wrapper。
- **禁止**：不得重新猜測 problem_type，不得從 source examples 反推 checker，亦不得覆寫 Phase 2 的 AnswerContract 或 fallback 到 legacy skills 以掩蓋錯誤。

### Layer 6：執行期插槽動態註冊與分流實作層（Runtime Dynamic Slot Overloading Layer）

- **職責**（v0.3 新增實體流程層）：
  1. 當題型規格通過 Spec Gate（Phase 2.5 `runtime_ready` 或帶 warning 之 `runtime_ready_with_warning`）後，必須在 `core/gencode/template_slot_resolver.py` 的 **`TASK_FAMILY_TO_SLOT`** 靜態對照表中，將 `target_task` / `template_families` Contract Token 綁定至具名 slot 字串（資料驅動，禁止 skill 硬編碼）。
  2. 同時在 `core/gencode/slot_generators.py` 的 **`SLOT_REGISTRY`** 映射表中，實體掛載對應處理函數（例如：兩點聯立求線性函數之單選分支、多模板生活情境字題池、純數值代入求值分支等）。
  3. `generate_from_problem_type_spec()` 執行時依 `resolve_template_slot()` 分流，產出經 `validate_generator_payload()` 驗證之 payload，再交由 Thin Facade 對外服務。
  4. Phase 2 **低樣本多樣性特赦**（`low_sample_diversity_tolerance_applied`）僅可移除重複類 diversity blocker，**不得**繞過本層未註冊插槽之硬性缺失（`slot_generator_not_registered` 仍為 blocked）。

- **禁止**：
  1. 任何插槽處理函數在隨機路徑、`seed=0` 或 fallback 分支下，將 `question_text` 退化為 minimalist 佔位符（如「請計算」「待補」）。
  2. 最終執行期 `question_text` 長度必須自然且穩健地 **超過 30 字**；並須嵌入由 `semantic_contract.required_concepts` 與教材源例對齊之**靈魂 Token**（原則 15）。
  3. 僅在 `SLOT_REGISTRY` 註冊名稱、卻無實體數學分支實作 — 視同 **Slot Hollow Registration（空心註冊）**，Quality Gate 不得標記為 Runtime-Ready。
  4. 在 `skills/{skill_id}.py` 內實作本層邏輯（違反原則 13）。

- **與 Phase 3 的銜接順序**：
  `Spec Gate 通過` → `TASK_FAMILY_TO_SLOT 綁定` → `SLOT_REGISTRY 掛載` → `Phase 3 序列化 Thin Facade` → `runtime_smoke` → `publish`。

---

## 3. Phase 0 / 1 / 2 / 2.5 / 3 階段定義

### Phase 0：Scope Freeze (範圍凍結)
- **輸出**：明確的 skill_id、source count、source_type distribution、allowed files、forbidden files 及 target phase，確認本輪邊界。

### Phase 1：Source Audit + Problem Type Induction (來源審查與題型歸納)
- **輸出**：usable_core_examples、rejected_examples、enrichment_examples、source_bank_only_examples、candidate_problem_types 與 classification_report，不輸出正式 generator/checker。
- **條款 3.4：Non-Destructive Salvage（非破壞性智能拯救原則）**：明確定義管線在物理掃描端遇到屬於 `core_example`（核心課本原題）但發生 `missing_answer` 或 `broken_latex` 的殘缺資料時，禁止粗暴判定為 `source_quality_reject` 並直接拋棄。引擎必須執行全自動「智能降級補齊」，在記憶體中動態灌入標準佔位符（如預設答案 `"0"` 或 `"A"`），強制標記為 `FORCE_ALLOWED_FOR_INDUCTION` 安全送入 Phase 2，由 AI 在生成端重新透過 SymPy 補齊解算邏輯。

### Phase 2：ProblemTypeSpec / Contract 建立 (規格包與契約產出)
- **輸出**：最終的 ProblemTypeSpec、AnswerContract、SemanticContract、StemContract、GeneratorContract、ValidatorContract、examples_map 與 source_bank map。不得接受 legacy 未 canonical 的 equivalence 值。
- **條款 3.6：錯誤診斷與補救節點映射合約（Diagnosis Remediation Mapping）**：
  1. **語意關鍵字動態驅動**：當管線讀入之唯讀 `skill_id` 名稱內包含「**排列**」、「**組合**」或「**機率**」關鍵字時，`problem_type_induction.py` 在歸納題型時**必須自動且剛性注入**下列四大經典診斷標籤：
     - `p_c_confusion`：排列（$P$）與組合（$C$）混淆
     - `sample_space_error`：樣本空間定義錯誤
     - `double_counting`：重複計數
     - `denominator_error`：分母／機率分數計算錯誤
  2. 注入須覆蓋三層輸出：`subskills_detail`、`diagnosis_tags` 頂層清單、以及 `per_example_classification[].diagnosis_tag_candidates`。
  3. 上述 tag 為後台 RAG 檢索補救路徑之**唯一特徵鍵**；`diagnosis_engine`（或等價判定擴充模組）比對學生錯答特徵後，**必須**拋出已登記 tag，不得自創臨時標籤。
  4. 補救橋接候選之 Chroma / bridge 身份仍須遵守 `skill_id:family_id` 規則（見 AGENTS.md §9），`diagnosis_tags` 僅作檢索特徵，不得取代 family 身份鍵。

### Phase 2.5：Spec Gate (規格稽核)
- **輸出**： readiness 判定結果（runtime_ready / pending_template / pending_renderer / blocked）與 blockers / warnings 清單。

### Phase 3：Runtime Generation / Registry / Thin Wrapper (運行生成與註冊)
- **輸入**：僅接受 Phase 2.5 通過之 ProblemTypeSpec；且對應 `target_task` 已完成 **Layer 6** 雙表註冊（`TASK_FAMILY_TO_SLOT` + `SLOT_REGISTRY`），或明確標記 `pending_template` 不得發布。
- **輸出**：經 verified 的 generator、non-destructive merged registry、以及通過 runtime smoke 測試的 **Thin Facade**（`skills/{skill_id}.py`，僅含白名單委託）。絕對禁止將 manual_review/future_ai_judged 題型塞入 deterministic checker。
- **v0.3 增量**：序列化前須執行 AnswerContract §4.3 展現型態強制作戰；同步前須執行 induced spec 幽靈快取清除（canonical whitelist purge）。

### 條款 3.5：Phase 錯誤對照權威地圖（Self-Healing 自我修復閉環）

當自動化流水線在不同 Phase 出現 Warning 或 Error 時，管線與 AI 修復任務**必須**依下列權威地圖進行規則對照與自我修復，**不得**跨文件混用或自行臆測修復策略：

| Phase 範圍 | 異常類型 | 唯一對照權威 SOP |
|----------|---------|-----------------|
| Phase 1（來源審查）、Phase 2（規格建構） | 單元分類、樣本拯救、阻擋層級判定、抽題 pool 分流 | 本文件《Gencode與AgentSkillV2整合總體設計_v0.3.md》 |
| Phase 2.5（規格稽核）、Phase 3（編譯期） | 選擇題、填充題、多小題、圖表題之 `presentation_mode`、Contract 欄位剛性覆寫、幽靈快取洗淨 | 《AnswerContract_EquivalenceType_Gate_v0.3.md》 |
| Phase 3 生成產物、Runtime 執行期 | Thin Facade 極簡化、Non-Destructive Merge、插槽動態註冊分流 | 《AgentSkillV2_ProblemType規格包設計_v0.3.md》 |

**Self-Healing 執行流程**：
1. 管線報錯時，先抓取報錯 Phase 標籤（例如 `Phase 2.5`）。
2. 依上表自動載入對應 SOP 全文，作為 AI 修復 Context。SOP 實體目錄**剛性錨定**為：`docs/系統SOP/Gencode_AgentSkillV2整合/`（**禁止**引用草稿路徑 `docs/SOP/`）。
3. 將 SOP 條款與報錯堆疊餵入修復 Prompt，觸發確定性自我校正。
4. 修復完成後重新執行該 Phase Gate，形成無人值守 24 小時自我閉環。

---

## 4. Gate 分層阻擋規則
為防止單一題目缺陷導致整個單元無法發布，阻擋邏輯嚴格分層：

### A. Source-level reject (單題排除)
- **適用**：missing_answer、broken_latex、answer_choice_mismatch、severe_ocr_noise、incomplete_stem。
- **效果**：僅排除該題，**不阻擋**該 problem_type，更不阻擋該 skill。

### B. Problem-type-level pending / blocked (題型阻擋)
- **適用**：answer_contract 無法建立、必要 renderer 尚未支援、generator_contract 不完整、需 AI-judged 才能評分、source examples 數量過少無法歸納。
- **效果**：該 problem_type 暫不進入 Phase 3，但**不影響**其他合法 problem_type 的推進。

### C. Skill-level blocked (單元阻擋)
- **僅適用**於：
  1. usable core examples = 0。
  2. 無法形成任何 ProblemTypeSpec。
  3. 大多數 core examples 明顯不屬於該 skill_anchor.families。
  4. skill_id / section / curriculum 對應嚴重錯誤。
  5. answer_contract 系統性毀損。
  6. runtime generation 存在安全性風險。
- **效果**：整個 skill 停止發布，列入 blocked.

### D. 不得升級為 skill-level blocked 的情境
不得因以下原因阻擋整個 skill：
- 少量 source_quality_reject
- 少量 missing_answer
- 單一 broken_latex
- registry_rule 產生 needs_review
- 某一個 problem_type pending
- enrichment examples 被排除
- future_ai_judged candidates 存在
- source_bank_only 題存在
- 素養題存在
- runtime_ready_candidate 尚未完成
- **條款 4.5：Unclassified Exception Escalation（未分類低置信度強制作戰原則）**：針對情境縱深極深、帶有圖表或複雜生活特徵（如汽車油量、手機費率）而導致 Token Overlap 分數偏低，被演算法判定為 `unclassified_low_confidence` 的靈魂課本原題，嚴禁移入 `skipped` 列表。管線必須在現場全自動分發臨時代理題型 ID，硬推其推進 Phase 2 觸發多模板生成（Multi-Template Generator），死守 Fidelity over Coverage（課本忠實度高於題型覆蓋率） 的最高品質紅線。

---

## 5. final_classification 詳細規則
每一題 source example 必須有：
- example_id
- source_quality_status
- final_target_task
- final_task_family
- classification_source
- classification_confidence
- included_in_core_induction
- included_in_source_bank
- exclude_reason
- review_required
- review_reason

規則：
- 後續流程只能使用 final_classification。
- AI / registry / parser 原始結果只作 evidence。
- 如果 final_target_task 屬於 expected_subskill_candidates，且 final_task_family 屬於 skill_anchor.families，且 source_quality_status != rejected，則不可給 alignment_score=0。
- registry_rule 合法命中時，應為 accepted_by_rule 或 soft_accept，不可一律標 needs_review。
- AI 沒有輸出，不代表分類失敗；若 registry_rule 可合法分類，仍可進入 induction。
- classification_missing 且無 rule / AI / parser 可判時，才列入 manual review。

### 5.1 LinearFunction 反例：分類成功但 gate 誤擋
- **現象**：
  - 多數 final classification 已落在 expected_subskill_candidates 內，卻 alignment_score=0。
  - registry_rule 可分類，卻被一律算成 needs_review。
  - 少量 source_quality_reject 導致整個 skill 被 blocked。
  - problem_type 已形成，卻因 majority_needs_review 阻擋整個 Phase 1。
- **正確行為**：source_quality_reject 只排除單題；合法 problem_type 可繼續；compute_numeric 若不屬於主技能可 warning 或 candidate-only；絕對不可為 LinearFunction 寫死放行特例。

### 5.2：Dynamic Shape Relaxation（動態數學形態容忍機制）
放寬早期只認純整數/有理數的死板正則。稽核點必須根據原始核心範例特徵全自動進行動態調節。若題型目標是求出函數關係式或選擇題，必須放行包含合法未知數（如 $x, y, t$）、LaTeX 數學減號（$−$）與選項單一字元，拒絕誤判封殺，確保多元課本題型能順利斬獲 `BUILD_PASS`。

---

## 6. 素養題與題庫抽題機制

### A. Gencode 自動生成路徑
- 素養題/情境長文題預設**不進入** core induction。
- 只有當其「可抽出明確 target_task、可建立穩定 answer_contract、不需保留完整長文語境、不需圖形/表格/手寫等人工判讀」時，方可標記為 `runtime_ready_candidate`，否則應標記為 `enrichment_source` / `source_bank_only` / `manual_review`。不得為湊 runtime 而強行改寫失真。

### B. 題庫原題抽題路徑 (source_bank_pool)
- 雖然素養題不進自動生成，但仍可作為題庫原題（source_bank_item）被學生抽到。
- **可抽**：一般例題、隨堂練習、自我評量、素養題、以及標為 `enrichment_source`、`manual_review` 或 `future_ai_judged` 的教材原題。
- **不可抽**：source_quality_reject、題幹不可讀的 broken_latex、需自動批改但 missing_answer、或 should_remap 尚未修正的題目。
- **前台限制**：若抽到 manual_review / future_ai_judged 原題，前台必須標示為「待人工批改/暫不自動批改/練習展示題」，絕不可偽裝成自動批改題。

---

## 7. 運行抽題政策 (Practice Pool Policy)
運行練習（runtime practice）抽題區分為兩層：
1. **generated_runtime_pool**：
   - 來源：verified problem types 及 registry-bound generators。
   - 規則：預設採 problem_type 均衡輪詢（round-robin）或 weighted random。不得因每次 API 重新載入而重置 state 導致重複抽同題型。
   - **驗收要求**：若某 problem_type 已 verified / runtime_ready，但前台或 Web Runtime Audit 連續 50 題都抽不到，必須 FAIL。不得因 importlib.reload 或 wrapper state reset 導致永遠抽同一個 problem_type。
   - **Gencode runtime audit**：必須使用 generated_only 模式進行，避免用 source_bank_pool 的存在來掩蓋 generator 本身分布或抽題不均的問題。
2. **source_bank_pool**：
   - 來源：教材原題、examples_map 中的 `source_bank_only` / `enrichment_source`。
   - 規則：無 answer_contract 或 checker_key 學生端不支援自動批改，手寫/開放題須走人工或 AI 判讀流程。

### practice_pool_policy 設定
- `generated_only`：僅抽自動生成題（Gencode 稽核時使用）。
- `source_bank_only`：僅抽教材原題（教師展示使用）。
- `mixed_generated_and_source_bank`（預設）：一般學生自動練習使用，兩 pool 混合抽題。
- `assessment_verified_only`：自動評量使用，僅抽通過評量驗證的生成題。

---

## 8. Bootstrap 與橋接規則
舊 skill.py 轉換之 bootstrap 只能作為臨時橋接：
1. 僅能在 DB examples 不足、source misaligned 或舊有代碼高度可信時使用。
2. 產出之 payload 必須更新為目標 skill_id、problem_type_id 與標準 answer_contract。
3. wrapper / adapter 必須通過 `py_compile` 與 sample verification。
4. `final_status` 只能標記為 `PASS_BOOTSTRAP_ONLY`，絕不可標記為 `FULL_OBSERVED_COVERAGE`。
5. 不得用 bootstrap 逃避 source classification，也不得反向污染正式 registry。

---

## 9. Quality Gate 與 Runtime Gate 稽核

### Quality Gate (品質門檻)
- **Textbook Fidelity**：不可為衝 coverage 硬做課本沒有的題型。作圖/補表/推導題應分流至 `visibility_only` 或 `future_ai_judged`。
- **Choice Contract**：選擇題 choices 不可重複，answer 必須是 A/B/C/D 且存在於 choices 中。
- **Visual/Table Payload**：題幹提及圖表者，payload 必須有 `visual_aids` 或 `chart_spec`。
- **Diversity & Fake Diversity**：參數不可固定輪播，題幹應有 scenario_family。只換人名（如 A/B 換甲/乙）而數學骨架相同者，仍屬同一 scenario，不得充當多樣性。
- **Localization**：前台題目、選項、解析與圖表標題必須 100% 中文化，不得殘留英文模板。

### Runtime & Web Runtime Gate (運行稽核)
- 實測進入 `/practice`，確保 `/get_next_question` 與 `/check_answer` 運作正常，且 encoded/decoded skill_id 均相容。
- 嚴禁顯示 `No module named skills.<skill_id>`，或 fallback 到 legacy 引入以掩蓋錯誤。
- `/get_next_question` 回傳 payload 必須保留 `problem_type_id`、`answer_contract` 與 `route_source`（須為 `gencode_wrapper`）。

---

## 10. 四層完成狀態與 Runtime-ready / Closure 定義
一個 skill 或 problem_type 要達到真正的 runtime-ready，必須通過以下四層完成狀態：
1. **Technical Closed Loop PASS**：
   - 條件：Phase 1 審查通過、Phase 2 規格建構通過、Phase 3 生成且 verified。
   - registry / wrapper 綁定均已完成，執行 `py_compile` 與運行 smoke 測試通過。
2. **Runtime Quality PASS**：
   - 條件：通過 choice quality audit (選項分布不固定、正解 label 格式正確) 且無 active blocking。
   - 必須符合 textbook fidelity、visual payload、scenario diversity 等品質 Gate。
3. **Web Runtime PASS**：
   - 條件：前台 API 實際 `/practice`、`/get_next_question` 與 `/check_answer` 均正常，且 `route_source = gencode_wrapper`。
   - 所有已 verified 的 problem_type 均能實測被抽到，無 fallback 漏題。
4. **Source Alignment PASS / PARTIAL**：
   - 條件：檢查 DB textbook examples 的真實 source form 是否被 runtime generator 語意覆蓋。
   - 若有 underrepresented 情況，標記為 `Source Alignment PARTIAL`，可進技術發布審核，但必須列入 enhancement backlog，不得宣稱完整貼近課本題型。

- **核心規則**：Phase 3 PASS 只代表技術發布門檻，唯有通過上述四層狀態，才算真正達到 runtime-ready closure。

---

## 11. 後續任務引用與變更回報規範
所有後續 Codex 任務，在提交 PR 或回報時，必須在報告中明確回答以下檢驗項目：
1. **本次修改對應 SOP 哪一層？** (Layer 1 ~ Layer 6)
2. **是否修改 production code / Python 邏輯？** (本輪是否為純配置/規格修改)
3. **是否新增 hardcode / 特例？** (是否有針對特定單元的 hardcode 邏輯)
4. **對 Gate 的影響是什麼？** (是否有影響 source-level / problem-type-level / skill-level 判定)
5. **是否影響 generated_runtime_pool 或 source_bank_pool？**
6. **是否影響 AnswerContract / checker？**
7. **是否通過 UTF-8 無 BOM 編碼安全與 mojibake 檢查？**
8. **是否通過 py_compile 與 smoke test？**
9. **是否迴歸測試過往反例？** (如 Cartesian wrapper 污染或 numeric generator_not_ready 誤判)

---

## 12. 版本紀錄
| 日期 | 版本 | 職責與變更內容 | 紀錄人 |
|---|---|---|---|
| 2026-05-25 | v0.1 | 首版總體設計，後續因編碼問題導致亂碼污染 | Codex |
| 2026-05-31 | v0.2 | 重整 v0.2，將資料規格與答案判定細則完全解耦，吸收閉環稽核與雙 pool 抽題規則，100% 乾淨 UTF-8 | Antigravity |
| 2026-06-01 | v0.2.1 | 增補條款 3.4 非破壞性智能拯救原則、條款 4.5 未分類低置信度強制作戰原則、以及條款 5.2 動態數學形態容忍機制 | Antigravity |
| 2026-06-01 | v0.3 | 15 大原則（增補 13–15）；六層架構新增 Layer 6 執行期插槽層；焊入 Thin Facade 與 Runtime Multi-Slot Engine；完整保留 v0.2 流程與 Gate | 首席系統架構師 |
| 2026-06-13 | v0.3.1 | 增補原則 16 Phase 錯誤對照權威地圖；Layer 2/3 焊入 Anchor Shield 單元錨定防線；新增條款 3.5 Self-Healing 自我修復閉環 | 首席系統架構師 |
| 2026-06-13 | v0.3.2 | 洗淨版：Layer 1/2 改為 `vh_數學` 行政歸屬唯讀校驗；條款 3.6 改為語意關鍵字驅動診斷標籤；條款 3.5 錨定真實 SOP 目錄；新增 §13 Gen Code 職責對照 | 首席系統架構師 |
| 2026-06-26 | v0.3.3 | 新增 §14 最終產品教師端流程與 Automated Domain Bootstrap & Healer；增補原則 17；廢止「工程師人工建 domain／老師用 Codex」舊假設 | 首席系統架構師 |

---

## 13. Gen Code 核心程式職責對照（GEM 五大場景落地）

> v0.3.2 增量：落實 GEM 使用說明之五大場景，下列 **6 支 Gen Code 核心程式** 為唯一允許修改之調度與生成後台；**嚴禁**在任一 `skills/{skill_id}.py` 薄外殼內堆疊實體邏輯。

| 程式名稱（路徑） | 對應場景 | 修改職責 |
|----------------|---------|---------|
| `core/gencode/pipeline_orchestrator.py` | 1️⃣ 教材匯入、編譯期 Self-Healing／Domain Bootstrap | 校驗 `vh_數學` 行政歸屬矩陣；capability-first resolution；Automated Domain Bootstrap & Healer 編排（§14） |
| `core/gencode/problem_type_induction.py` | 1️⃣ 教材匯入、Phase 1 盤點切題 | 語意關鍵字驅動診斷標籤；`required_capabilities` 與 induced spec；自動分流 core examples |
| `core/gencode/runtime_skill_wrapper.py` | 2️⃣ 出題生成、3️⃣ 提示生成 | 全域調度器；僅消費 **verified** domain provider；委託 Domain 模組 |
| `core/gencode/slot_generators.py` | 2️⃣ 出題生成 | 全域插槽庫；委託 verified domain operations |
| `core/gencode/scenario_pool_manager.py`（Template Domain，待建或擴充） | 2️⃣ 出題生成 | 情境文本池；題幹組裝 |
| `core/diagnosis_analyzer.py` 或等價 `diagnosis_engine` 擴充 | 4️⃣ 錯誤診斷、5️⃣ 補救建議 | 答錯診斷標籤 |

**剛性約束**：
1. 系統負責決策與數學嚴格防守；AI Bootstrap 僅在確認缺 domain 後啟動（§14.7）。
2. 上述程式之修改須遵守規格包 SOP §1.5.6 防胖防禦線。
3. 新增 Gen Code 邏輯時，須在變更回報（§11）明列對照之 SOP 條款與場景編號。

## 14. 最終產品：教師端自動出題與 Automated Domain Bootstrap & Healer（v0.3.3 · **必要能力**）

> **產品定位（不可降級）**：下列流程為 **最終產品必要能力**，不是未來選配功能。正式產品的使用者是一般數學老師；**不得**假設老師會使用 Codex、Python、Git、registry、domain、capability、scaffold、validator 等工程術語或工具。

### 14.1 教師端標準流程（唯一對外敘事）

```text
匯入教材
→ 按「V3 重新生成」
→ 系統自動辨識 problem_type 與 required_capabilities
→ 優先重用既有 domain
→ 產生 component
→ 自動 compile / smoke / integrity validation
→ 顯示生成例題
→ 教師確認並發布
```

技術細節（Phase 1 induced spec、Shadow Bridge、Publish Gate）見 [SOP_Gencode_AgentSkillV3_Specification.md](../Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md) §1.10 與 [SOP_Gencode_AgentSkillV3_PipelineFlow.md](../Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md) §1.7。

### 14.2 缺少 capability 時的自動補全（不得轉嫁給老師寫程式）

若 `required_capabilities` 尚無 provider，系統 **不得** 要求老師撰寫 Python 或修改 registry，而 **必須** 自動進入：

```text
DOMAIN_CAPABILITY_UNRESOLVED / PARTIAL
→ 建立 Domain Gap Report
→ 聚合同類教材例題
→ Automated Domain Bootstrap
→ 建立 candidate domain
→ 產生 core / operations / registry draft / adapter / validator / tests
→ 自動測試
→ Domain Healer 局部修補
→ 產生題目預覽
→ 教師確認教學語意與題目品質
→ 升格 verified
→ 自動重跑原失敗 components
```

### 14.3 與 V3 架構的通用原則（已確立 · 本文件背書）

1. 每個教材例題為獨立 `src_{example_id}` component（見 V3 Specification §1.2）。
2. Phase 1 先建立 induced spec，再進 domain resolution（capability-first）。
3. Resolver 採 **capability-first matching**；`SKILL_TO_DOMAIN` 只是 **confirmed binding**，不是 V3 使用資格門檻。
4. 未註冊 skill 可用 **derived binding** 正常生成與發布（Bootstrap Gate ≠ Publish Gate）。
5. 無完整 provider 時 **必須安全停止**，不得錯配相近 domain 通過驗證。
6. 新 domain **建立一次**後，所有具相同 capability 的 skills **共用**；不得為每個 skill 建立專用 generator 或 domain。

### 14.4 教師只處理教學語意

教師可回答的問題範例（系統以結構化問答呈現，**不**暴露 stack trace）：

- 角度採度數或弧度？
- 變異數採母體或樣本公式？
- 答案要求精確值或近似值？近似到小數第幾位？
- 多解是否全部列出？
- 題目難度與教材是否一致？

**禁止**要求教師：查看 stack trace、修改 Python、選擇 registry key、使用 Codex 修復。

### 14.5 教師端狀態文字（建議對照）

| 教師可見狀態 | 內部語意（管理員診斷頁） |
|-------------|-------------------------|
| 已找到既有出題能力 | existing domain / operation matched |
| 正在生成題目 | Shadow Bridge / component codegen |
| 偵測到新的數學能力 | `DOMAIN_CAPABILITY_UNRESOLVED` |
| 正在建立可重用出題能力 | Automated Domain Bootstrap → `candidate` |
| 自動測試與修補中 | validator + Domain Healer |
| 等待教師確認 | `candidate` 預覽就緒 |
| 已核准並重新生成 | `verified` + 原失敗 components 重跑 |
| 需要管理員審查 | healer 超限或 bootstrap 失敗 |

技術錯誤詳情僅保留於管理員診斷頁，**不**直接暴露給一般教師。

### 14.6 成功與失敗標準（產品級）

| 情境 | 預期結果 |
|------|----------|
| **已有 domain** | 按 V3 重新生成 → 自動生成 → `verified` |
| **缺少 domain** | 不 500、不產錯題、不阻斷其他 components、不要求老師寫程式、自動建立 `candidate` |
| **Candidate 通過** | 教師確認 → `verified` → 原失敗 components 自動重跑 |
| **Candidate 無法修復** | 保留 evidence → 待管理員審查 → **不**影響其他 skill |

### 14.7 成本控制（產品政策）

```text
先重用 existing artifact
→ no-LLM deterministic classification
→ existing-domain capability matching
→ 相近 domain extension analysis
→ 確認真的缺 domain
→ 才呼叫 AI Bootstrap
```

AI 啟動前須向教師／管理員顯示：預估呼叫次數、預估 token、預計建立或擴充的 domain、預計 operations、受影響 components。`source_hash` 未變時 **必須** 重用既有 classification、gap report 與 `candidate`，**不得** 重複呼叫 AI。

### 14.8 本節取代的舊規則（變更說明）

| 舊敘述（已廢止） | 新正式架構 |
|------------------|------------|
| 新 domain 必須由工程師人工建立 | Automated Domain Bootstrap 自動建立 `candidate` |
| 未知 skill 必須先加入 `SKILL_TO_DOMAIN` | derived binding + Bootstrap Gate；confirmed binding 僅為加速 |
| Auto-Bootstrap 只產生 gap report | Gap Report + Bootstrap 產物 + Healer + 預覽 + 升格 |
| 老師需使用 Codex 修復 | Domain Healer 自動修 `candidate` 隔離區；老師只確認教學語意 |

權威實作細節（domain 狀態 `draft`／`candidate`／`verified`、驗證 Gate、Healer 禁止項）見 V3 Specification **§1.10**。

### 14.9 原則 17（v0.3.3 增補）

**17. 【教師優先、工程內隱原則】**：Gencode 最終產品對外只呈現教材匯入、重新生成、預覽確認與發布；所有 domain bootstrap、healer、registry draft 與 validator 均為 **系統內部閉環**。Self-Healing（原則 16）在產品語境下 **包含** Automated Domain Bootstrap 與 Domain Healer，且僅作用於隔離區 `candidate`，**不得**要求教師操作 Codex 或修改 production core。

---

*本文件職責：定義整合總體流程、最高法規、六層架構邊界與閉環安全機制。*
*不負責事項：不定義 YAML schema 細部欄位與 equivalence 白名單細則。*
*應參考的其他 SOP：[AgentSkillV2_ProblemType規格包設計_v0.3.md](AgentSkillV2_ProblemType規格包設計_v0.3.md)、[AnswerContract_EquivalenceType_Gate_v0.3.md](AnswerContract_EquivalenceType_Gate_v0.3.md)、[SOP_Gencode_AgentSkillV3_Specification.md](../Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_Specification.md) §1.10（Automated Domain Bootstrap & Healer）。*
