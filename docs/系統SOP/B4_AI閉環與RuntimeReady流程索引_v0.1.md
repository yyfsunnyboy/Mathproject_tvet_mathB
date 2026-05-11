# B4 AI 閉環與 Runtime-Ready 流程索引 v0.1

**版本：** v0.1  
**性質：** **流程索引／導覽**（不重複定義 SOP 條文、不新增強制規則）  
**對象：** B4（技術型高中）自動出題、deterministic runtime、closure 與後續 phase 之 **prompt 與文件工作流**

---

## 1. 核心 SOP 清單與用途

以下檔案皆在 `docs/系統SOP/`，為目前 B4 閉環的 **權威流程來源**。本索引只說明**何時讀哪一份**，不取代正文。

| 檔案 | 用途（精簡） |
|------|----------------|
| **`AI閉環開發與驗收SOP_v0.1.md`** | MathProject 高中版 AI 協助開發的 **總循環**：inventory → plan → 小範圍實作 → 測試 → 報告 → 人工核准；每輪單一 phase、可驗證、可回滾。 |
| **`教材匯入與技能生成SOP_v0.1.md`** | **章節／技能層**：inventory、題型分流、generator 路線、adaptive 註冊、audit 可見度、closure、下一章 freeze 等 **章節級總流程**。 |
| **`B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`** | **Deterministic 題型批次的 runtime 驗收**：非僅 generator 測試通過；須 `/practice`、`/get_next_question`、`/check_answer`、編碼／未支援 skill／reserved 等 **smoke gate**。 |
| **`B4_phase_prompt_templates_v0.1.md`** | **Prompt 模板彙編**：Template **A/B/C/D**，用於對齊上述 SOP 的 **可複製短 prompt**，避免每輪重寫長篇 guardrails。 |

**與 SOP 搭配的 closure／phase 報告**通常位於 `reports/b4_generator_planning/`（例如 Chap2 mainline closure、各 phase summary）；**以該目錄最新報告為準**補齊「已完成／Reserved／下一 step」。

---

## 2. SOP 使用順序（建議閱讀與執行順序）

1. **`AI閉環開發與驗收SOP_v0.1.md`** — 先確認本輪是否為「單一 phase、小 scope、有測試與報告、人工核准後再下一輪」。
2. **`教材匯入與技能生成SOP_v0.1.md`** — 若涉及 **新章／新技能／題型分流／章節級 inventory**，先對齊章節流程與檢查項。
3. **`B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`** — 若本輪為 **deterministic implementation** 或驗收 runtime，**必讀**；closure 報告中的 smoke 摘要也應可对齊此檔之 checklist 語意。
4. **`B4_phase_prompt_templates_v0.1.md`** — 依本輪類型選 **Template A/B/C/D**，組出給 agent 的 **短 prompt**（見 §3）。

**實務口訣：**  
「章節從哪來」→ 教材／技能 SOP；「這批題能不能在學生端跑」→ Runtime Smoke Gate SOP；「這輪 AI 要守什麼節奏」→ AI 閉環 SOP；「貼給 agent 的欄位」→ Phase prompt templates。

---

## 3. Phase template 選用規則（A / B / C / D）

對照 **`B4_phase_prompt_templates_v0.1.md`**，選用規則如下：

| Template | 用途 | 典型產出 | 是否預設改 production code |
|----------|------|-----------|----------------------------|
| **A — Planning-only** | 盤點、taxonomy、對照表、**audit／整合規劃**、closure→adaptive 規劃等 **僅決策與文件** | 單一（或少量）`reports/.../*.md` | **否** |
| **B — Runtime-ready batch** | **Deterministic**（或專案明文允許之同等 runtime-ready）**實作批次**：generator、checker、router、allowlist、route、測試、phase report | 碼 + 測試 + report；狀態常止于 **READY_FOR_MANUAL_SMOKE** | **是**（於模板允許清單內） |
| **C — Closure** | 某批 **MANUAL_SMOKE_PASSED** 後收斂、**章節 deterministic mainline closure**、重大轉折前總結；**不新增題型** | 僅 closure／summary report（無 code 或明謂無 diff） | **否**（預設） |
| **D — Small repair** | Template B（或 smoke）**失敗**後之 **最小修補**，不擴 scope | 小 diff + 必要測試 + 簡短 fix summary | **是**（極小範圍） |

**銜接規則（與模板文件一致）：**

- Implementation（runtime-ready deterministic batch）→ **優先 Template B**。
- Template B **失敗** → **Template D** 收斂，**不**另開「大包 phase」掩蓋問題。
- Planning／audit integration 規劃 → **Template A**。
- Closure **不應每批都做**；僅主線完成、重大節點、或進入下一階段整合前 → **Template C**。

---

## 4. 何時可新增 SOP／何時只更新 changelog

**優先維護既有四章 SOP + `B4_phase_prompt_templates_v0.1.md`，避免零碎平行 SOP。**

| 情境 | 建議 |
|------|------|
| 新風險類型（例如全新驗收維度、與現有 gate 不相容） | 評估是否 **升格為 SOP 新節** 或 **獨立新 SOP**；需簡短 **版本／changelog** 說明與適用範圍。 |
| 單一批次／單一 phase 的微調（措辞、連結、範例行） | **SOP changelog / 小節追加** 為主，**避免** 全文改寫或重複另一份長 SOP。 |
| 可引用既有條文 + Template A/B/C/D 說完者 | **只新增／更新 `reports/...` phase 報告**，**不**新增 SOP。 |
| Prompt 欄位、固定 guardrails 表格式 | 擴充 **`B4_phase_prompt_templates_v0.1.md`**（仍宣告 **非** 取代 SOP 正文）。 |

---

## 5. Chap1／Chap2 已完成狀態摘要（索引用）

以下為 **截至本索引撰寫時** 與 repo 中 closure／phase 報告對齊之 **高階摘要**；細節以 `reports/b4_generator_planning/` 內對應 md 為準。

### Chap1（技術型高中 B4 機率與統計前置）

- **Deterministic / adaptive allowlist 與 registry** 已有慣例與 **regression 測試守護**（例如 closure 與後續 phase 報告中常以 Chap1 allowlist 筆數作為 regression 檢查）。
- 後續變更應維持「**不破壞 Chap1 行為**」之專案慣例（與各 phase guardrails 一致）。

### Chap2（機率與統計 · 第二章主線）

- **Deterministic mainline：** 已 **CLOSED**；**11** 個 `problem_type` 達 **MANUAL_SMOKE_PASSED**（見 `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md` 表格與 §5 reserved 說明）。
- **未納入 mainline** 之 skill／題型（如特定集合概念、手寫 listing、部分期望值應用等）維持 **reserved／未開放** UX，**不** 隨意擴 allowlist。
- **後 mainline 之「可見性／稽核」**：Phase **6I**（寫入 `b4_chap2_visibility_audit_logs`）、Phase **6J**（教師／管理端 **visibility** 頁／API）等，以各 phase **runtime-ready summary** 為準；**不**將 gated 事件計入正誤率之類 scoring（見各報告 guardrails）。

若本索引與某份 **更新較新** 的 report 衝突，**以該 report 為準** 並於下一版索引更新本節。

---

## 6. 後續預設流程（與 Template 對應）

| 階段 | 建議 Template | 說明 |
|------|----------------|------|
| **Planning**（inventory、整合方案、風險與選項，**不改 code**） | **Template A** | 產出 planning report；**不**啟動 implementation。 |
| **Runtime-ready implementation**（deterministic 批次或專案定義之同等批次） | **Template B** | 對齊 Runtime Smoke Gate，交付測試 + report；完成態常標 **READY_FOR_MANUAL_SMOKE**。 |
| **Closure**（主線完成／smoke 已核定後之收斂） | **Template C** | 文件為主；避免每小批都 closure。 |
| **Repair**（自動測試或 manual smoke 失敗後最小修） | **Template D** | 不擴題型、不大 refactor；修完仍 **READY_FOR_MANUAL_SMOKE**。 |

---

## 7. 下一建議 phase（playbook 預設）

**Phase 6J：Chap2 Teacher Audit Visibility Runtime-Ready Batch** — 建議使用 **Template B**。

- **目的（摘要）：** 讓教師／管理端 **唯讀** 檢視 Chap2 **visibility audit**（例如 `b4_chap2_visibility_audit_logs`），含最小 route／API／模板與測試；**不**改 mastery／APR／fail_streak／remediation／scoring policy。
- **若 repo 已含 6J 實作與報告：** 本條視為 **已完成路線之範例**；下一動請改依 **`b4_phase6j_*` summary** 與該報告 **Recommended next phase**（常先以 **Template A** 開下一規劃輪）— **不在本索引內啟動實作**。

---

## Final confirmation（本索引 v0.1）

| 項目 | 確認 |
|------|------|
| 是否僅新增流程索引文件 | **是** |
| 是否新增強制規則條文（凌駕既有 SOP） | **否** |
| 是否修改 production code / tests / routes / templates / generators / validators / DB / adaptive scoring | **否** |
| 是否新增題型 | **否** |
| 是否於本文件內啟動下一 phase 實作 | **否** |

---

*v0.1：將現有四份系統 SOP 與 Phase prompt templates 串成可重複工作流；細節與強制條文仍以各 SOP 正文為準。*

- 新增索引：`B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` 已補充「Visual / Handwriting / Review 題型的自動化驗收原則」，用於圖形題/表格題/手寫題的 runtime-ready 與 smoke gate 驗收基準。
