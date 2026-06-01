# Gencode與AgentSkillV2整合總體設計 v0.2

## 0. 文件目的與最高原則
本文件為 Gencode 與 AgentSkillV2 整合的最高 SOP 及總流程法規。後續所有 Codex / Antigravity 任務凡涉及 Gencode、Phase 0/1/2/3 流程、ProblemTypeSpec、runtime wrapper 與 source classification 等，均須以此文件為最高規範，並在修改回報中明確列出遵守之條款。

### 12 大最高原則
1. **ProblemTypeSpec** 是 Phase 2 / Phase 3 / Runtime Generation 的唯一權威來源，一切 runtime 生成必須以此為準。
2. **Source examples** 只能作為分類與結構推導之 evidence，絕不可直接主導或強行限制 runtime generator 的生成內容。
3. **Phase 1** 只負責來源盤點、來源分層與題型歸納，**絕對不可**過早阻擋（block）整個 skill。
4. **Gate 必須分層**：區分為 source-level reject、problem-type-level pending/blocked、及 skill-level blocked，避免單題問題上升至 Skill 阻擋。
5. **單一壞題**、少量 missing_answer、broken_latex 或 OCR noise，**絕對不可**直接升級為整個 skill blocked。
6. 只要 **usable core examples** 足以形成至少一個合法 ProblemTypeSpec，即允許後續流程繼續，但需於報告中提示 warning。
7. **分類依據**：AI classification、rule classification、registry classification 均為 classification_source evidence；後續流程只能讀取並信任 `final_classification`。
8. **Phase 3 嚴格邊界**：不得重新猜測題型、不得從 source examples 反推 checker，更不得自行覆寫 Phase 2 定義的 `answer_contract`。
9. **反特例化**：不得為單一 skill_id、problem_type、章節或特定題型寫死通過條件或強行寫入特例邏輯。
10. **Coverage $\neq$ Quality**：coverage gate 通過僅代表具備 runtime/review 路徑，不等於 quality gate（學生端可用性）通過。
11. **Runtime-Ready 定義**：不只代表會出題與批改，還必須通過 textbook coverage、runtime quality、web runtime 與 source alignment 的四重檢查。
12. **Codex 任務規範**：後續每一輪 Codex / Antigravity 任務都必須先閱讀本設計，並於回報中列出遵守了哪些條款。

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

## 2. 五層流程定義與邊界

### Layer 1：Import / Source Normalization (匯入與標準化)
- **職責**：切題、題幹清理、答案/選項擷取、LaTeX 語意保留、關聯 chapter/section/skill_id、標記 source_type（可引用 MathType DOCX 轉 LaTeX 工具）。
- **禁止**：不得判斷 problem_type、不得判斷 runtime readiness、不得建立 generator，更不得因題目不好直接刪除原始資料。

### Layer 2：Source Audit (來源品質審核)
- **職責**：審查每題來源品質，標記 source_item_status（如 usable / rejected / enrichment / future_ai_judged / source_bank_only），並記錄 missing_answer、broken_latex、graph_required 等標記。
- **禁止**：不得因少量 rejected 題目而阻擋整個 skill 的推進，也不得在此階段建立 ProblemTypeSpec 或決定 Phase 3 generator。

### Layer 3：Problem Type Induction (題型歸納)
- **職責**：僅使用 **usable core examples** 歸納 candidate problem types，產出 target_task、task_family、answer_type，以及草擬的 answer_contract / semantic_contract，以 `final_classification` 作為唯一分類結果。
- **禁止**：不得讓 source_quality_reject 題目參與 core induction，不得讓 registry_rule 自動等於 needs_review，也不得把素養題預設放入 core induction。

### Layer 4：Spec Gate (規格審查門檻)
- **職責**：以 **problem_type 為單位** 判斷 readiness（runtime_ready / pending_template / blocked），驗證 AnswerContract、SemanticContract 等契約完整性，判斷是否可進入 Phase 3。
- **禁止**：不得以整個 skill 為唯一 gate 單位，不得把 source-level reject升級為 skill-level blocked，亦不得對特定 skill 寫死放行。

### Layer 5：Runtime Generation (代碼生成與綁定)
- **職責**：僅根據通過 Spec Gate 的 ProblemTypeSpec 生成 runtime code，使用 answer_contract 產生 checker，使用 semantic_contract 控制生成語意與 randomization，產生 verified generator 後由 registry 接入 thin wrapper。
- **禁止**：不得重新猜測 problem_type，不得從 source examples 反推 checker，亦不得覆寫 Phase 2 的 AnswerContract 或 fallback 到 legacy skills 以掩蓋錯誤。

---

## 3. Phase 0 / 1 / 2 / 2.5 / 3 階段定義

### Phase 0：Scope Freeze (範圍凍結)
- **輸出**：明確的 skill_id、source count、source_type distribution、allowed files、forbidden files 及 target phase，確認本輪邊界。

### Phase 1：Source Audit + Problem Type Induction (來源審查與題型歸納)
- **輸出**：usable_core_examples、rejected_examples、enrichment_examples、source_bank_only_examples、candidate_problem_types 與 classification_report，不輸出正式 generator/checker。
- **條款 3.4：Non-Destructive Salvage（非破壞性智能拯救原則）**：明確定義管線在物理掃描端遇到屬於 `core_example`（核心課本原題）但發生 `missing_answer` 或 `broken_latex` 的殘缺資料時，禁止粗暴判定為 `source_quality_reject` 並直接拋棄。引擎必須執行全自動「智能降級補齊」，在記憶體中動態灌入標準佔位符（如預設答案 `"0"` 或 `"A"`），強制標記為 `FORCE_ALLOWED_FOR_INDUCTION` 安全送入 Phase 2，由 AI 在生成端重新透過 SymPy 補齊解算邏輯。

### Phase 2：ProblemTypeSpec / Contract 建立 (規格包與契約產出)
- **輸出**：最終的 ProblemTypeSpec、AnswerContract、SemanticContract、StemContract、GeneratorContract、ValidatorContract、examples_map 與 source_bank map。不得接受 legacy 未 canonical 的 equivalence 值。

### Phase 2.5：Spec Gate (規格稽核)
- **輸出**： readiness 判定結果（runtime_ready / pending_template / pending_renderer / blocked）與 blockers / warnings 清單。

### Phase 3：Runtime Generation / Registry / Thin Wrapper (運行生成與註冊)
- **輸入**：僅接受 Phase 2.5 通過之 ProblemTypeSpec。
- **輸出**：經 verified 的 generator、non-destructive merged registry、以及通過 runtime smoke 測試的 thin wrapper。絕對禁止將 manual_review/future_ai_judged 題型塞入 deterministic checker。

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
1. **本次修改對應 SOP 哪一層？** (Layer 1 ~ Layer 5)
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

*本文件職責：定義整合總體流程、最高法規與閉環安全機制。*
*不負責事項：不定義 YAML schema 細部欄位與 equivalence 白名單細則。*
*應參考的其他 SOP：[AgentSkillV2_ProblemType規格包設計_v0.2.md](file:///e:/Python/Mathproject_tvet_mathB/docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.2.md)、[AnswerContract_EquivalenceType_Gate_v0.2.md](file:///e:/Python/Mathproject_tvet_mathB/docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.2.md)。*