# B4 Phase Prompt Templates v0.1

**版本：** v0.1  
**性質：** Prompt 模板彙編（**非**新增 SOP 規則條文）  
**對照必讀（本版撰寫時均已存在於 repo）：**

| 文件 | 路徑 | 狀態 |
|------|------|------|
| AI 閉環開發與驗收 SOP | `docs/系統SOP/AI閉環開發與驗收SOP_v0.1.md` | ✅ |
| 教材匯入與技能生成 SOP | `docs/系統SOP/教材匯入與技能生成SOP_v0.1.md` | ✅ |
| B4 Deterministic Runtime Smoke Gate SOP | `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` | ✅ |
| Chap2 deterministic mainline closure | `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md` | ✅ |
| Phase 6G-0 skill availability UX | `reports/b4_generator_planning/b4_phase6g0_chap2_skill_availability_ux_cleanup_summary.md` | ✅ |

> 若未來某路徑 **missing**，於本表該列標註 `missing`，**不**因此擴大搜尋或改 code。

---

## 文件目的

本文件**不是**新的 SOP 強制規則，而是把 Chap1 / Chap2 已走過的流程，整理成**可重複套用的短 prompt 模板**，供技術型高中（B4）自動出題與 AI 閉環後續 phase 使用。

**目標：**

- 減少每一輪從零撰寫長篇 prompt
- 減少一問一答式的 guardrails 重複貼上
- 對齊既有 SOP（含 Runtime Smoke Gate v0.1.2、§8.1 UX）但不複製全文
- 讓 implementation / planning / repair / closure 有固定「欄位」，可直接貼給 agent
- **保留** runtime-ready deterministic batch 的必要驗收標準（見 Template B）

---

## Template A：Planning-only Phase

**用途：** inventory、taxonomy、checker mapping、adaptive audit planning、closure-to-adaptive planning 等——**僅規劃、不寫 production code**。

**複製用模板：**

```markdown
## B4 Planning-only Phase（套 Template A）

### project context
- 專案：MathProject 技術型高中／B4 自動出題與 AI 閉環
- 參照 SOP：`AI閉環開發與驗收SOP_v0.1.md`、`教材匯入與技能生成SOP_v0.1.md`、`B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`（不重寫 SOP，必要時只提「需對齊哪一節」）

### phase name
- （例如：Phase 6H Chap2 Adaptive Audit Integration **Planning**）

### goal
- （1–3 句：本輪要達成的「決策／_inventory／可執行計畫」）

### input reports
- （列出報告路徑；若 missing 註記 missing，不擴大搜尋）

### output report path
- （唯一允許新增／更新：`reports/.../xxx.md`）

### allowed action
- 只新增／更新上述 **report**
- 可在報告內附：表格、選項、風險、建議 implementation 邊界（文字層）

### forbidden changes
- 不修改 production code / tests / routes / templates
- 不修改 generators / validators / question_router / allowlist
- 不修改 database / coverage matrix
- 不修改 adaptive scoring / mastery / APR / remediation
- 不新增題型、不啟動 implementation phase

### required sections（輸出報告建議目錄）
- Scope and guardrails
- Evidence / inputs
- Options or recommendations（若適用）
- Risks and dependencies
- Recommended next phase（**不**執行）
- Final confirmation（逐條：僅文件／無 code 等）

### final confirmation（agent 填）
| 項目 | 是/否 |
|------|------|
| 僅新增／更新 report | 是 |
| 未改 production code | 是 |
| 未改 tests | 是 |
| 未啟動 implementation | 是 |
```

---

## Template B：Runtime-ready Deterministic Batch

**用途：** 每批 deterministic `problem_type` 實作；預期一次涵蓋 generator、checker、router、allowlist、route 接線、測試、phase report；適用 Chap2 後續與未來 B1–B4 同架構。

**複製用模板：**

```markdown
## B4 Runtime-ready Deterministic Batch（套 Template B）

### phase name
- （例如：Phase 6X — …）

### completed prior phases
- （已 closure 或已 MANUAL_SMOKE_PASSED 之前置 batch／章節狀態）

### required SOP
- `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`（含 v0.1.1 double-encoding、**v0.1.2 §8.1** 未開放／reserved UX）

### scope problem_types
- （snake_case 清單；本 batch **不**超出此清單）

### skill_id
- （`vh_數學B4_*` 與題型對應表）

### problem_type specs
- （數學語意、敘事邊界、禁止項目、與課本對齊備註）

### answer contract
- （answer_type、checker、是否接受 %／小數、機率區間、整數 strict 等）

### payload contract
- （必填欄位：`question_text`、`answer`/`correct_answer`、`problem_type_id`、`skill_id`、`answer_type`、不得 `[BLANK]`/`[FORMULA_MISSING]` 等）

### allowed files
- （明確列出可改：generators、validators、router、allowlist、`practice.py`、templates 若必要、tests、report）

### forbidden changes
- 不超出 scope problem_types
- 不修改 DB schema／coverage matrix／adaptive 行為（除非本 phase **明文**允許且分開批）
- 不將 handwriting reserved 題型加入 deterministic allowlist
- 不為未開放 skill 顯示內部 phase 名稱（對齊 §8.1）

### route integration requirements
- `/practice` 可進入（encoded + decoded `skill_id`）
- `/get_next_question` 可出題
- `/check_answer` 可批改（含 edge cases）

### check_answer requirements
- canonical／等值／錯誤／invalid；機率 vs 整數 vs 期望值等依 contract

### encoded / decoded skill_id tests
- 後端 `_url_unquote` idempotent；測試涵蓋 encoded 與 decoded

### frontend double-encoding tests
- 依 SOP v0.1.1：path/query 取出 skill 後行為與 Network 層 single-encoded 檢查（若本 batch 動到前端）

### unsupported skill guard
- 同章未開放 skill：**clear not-enabled**，**禁止** legacy `import skills.<skill_id>` **與** `No module named` 外露

### handwriting reserved blocked
- 列出手寫／listing reserved `problem_type`；必测 blocked + 不更新 mastery／APR／fail_streak／remediation

### regression tests
- 前一批 Chap2 deterministic suites + Chap1 allowlist／router 等（由專案慣例列明指令）

### report path
- `reports/b4_generator_planning/....md`

### completion criteria（強制）
- **完成標準不是** only generator unit tests passed
- 必須達到 **RUNTIME_READY**（automated route／integration 測試通過定義由專案約定）
- **禁止**未開放 skill 的 JSON 出現內部 phase 標籤（如 Phase 6C-1）與 traceback／raw encoded skill 洩漏（§8.1）

### final status
- **READY_FOR_MANUAL_SMOKE**（本 batch **停止於此**，不自動宣告 MANUAL_SMOKE_PASSED）
```

---

## Template C：Smoke Accepted / Closure Phase

**用途：** 某批 **manual smoke passed** 後收斂、**章節 deterministic mainline closure**、或重大轉折前總結——**不新增題型、不改 code**。

**複製用模板：**

```markdown
## B4 Closure Phase（套 Template C）

### phase / chapter name
- （例：B4 Chapter 2 Deterministic Mainline Closure）

### completed problem_type list
- （表格：phase、problem_type、skill_id、answer_type、checker、runtime status = MANUAL_SMOKE_PASSED）

### runtime smoke status
- 對齊 Smoke Gate SOP：/practice、get_next_question、check_answer、encoding、double-encoding、unsupported、reserved、regression

### tests summary
- （關鍵 pytest 組合與 passed 數／日期）

### files changed summary
- **若本輪僅 closure report：** 寫「無 production diff；僅 `reports/...`」

### textbook alignment notes
- （若有，例：Phase 6F-R 課本語境；否則 N/A）

### excluded / reserved types
- deterministic 未實作、handwriting reserved、不得進 allowlist 者

### adaptive / scoring status
- 是否已接 mastery／APR／remediation；**通常** closure 時為「尚未」或「僅 runtime-ready」

### known limitations
- DB needs_review、image 題、adaptive 未接、route fixture 範圍等

### recommended next phase
- （**不**執行；選項 2–3 個＋建議優先序）

### final confirmation
- 逐條：僅文件／無 code／無 tests／無下一 phase

### 使用頻率提醒（填表者自省）
- closure **不應每批都做**；僅主線完成、重大 SOP 對齊節點、或進入 adaptive integration 前再做，避免過度文件化。
```

---

## Template D：Small Repair Phase

**用途：** Template B 的 automated tests 或 **manual smoke 失敗**後，**最小修補**。

**複製用模板：**

```markdown
## B4 Small Repair Phase（套 Template D）

### failure symptom
- （HTTP 狀態、錯誤字串、重現步驟、哪個 skill／problem_type）

### suspected layer
- （route / template / encode / allowlist / router / checker / generator — 僅列懷疑，以最小 diff 驗證）

### allowed fix scope
- （明確檔案與行為；**只修 failure**）

### forbidden expansion
- 不新增 problem_type
- 不重構架構、不順手「清理」無關程式
- 不啟動下一 feature phase

### required regression
- （失敗點對應 test + 既有 Chap2／Chap1 regression 命令）

### report path
- `reports/b4_generator_planning/..._fix_summary.md`（或專案慣例）

### final status
- **READY_FOR_MANUAL_SMOKE**（修完仍須人工 smoke 核定；不自動宣告通過）
```

---

## 使用規則（後續原則）

1. **不再**為每個小議題另立一份完整 SOP；能引用既有三章 SOP + 本模板即可。
2. 除非出現**全新風險類型**，否則既有 SOP 以 **changelog / 小節追加** 為主，避免全文改寫。
3. **Implementation**（runtime-ready deterministic batch）**優先使用 Template B**。
4. Template B **失敗** → 用 **Template D** 收斂，**不**開新大 phase。
5. **Planning / audit / integration 規劃** → **Template A**。
6. **Closure** 僅在章節主線完成、重大轉換點、或進入 adaptive 整合前 → **Template C**；避免每批都寫 closure。
7. 若某 phase 回報已含 **tests passed、report、guardrails 未越界**，下一輪應 **ACCEPT** 或 **BLOCK**（明示理由），**不重複**要求同一批已完成之 smoke 敘述。

---

## 建議下一個實際 phase

**Phase 6H：Chap2 Adaptive Audit Integration Planning**

- **建議使用：** **Template A**（Planning-only）
- **目的：**
  - 規劃已完成之 **11** 個 Chap2 deterministic `problem_type` 如何進入 **audit／教師可見性（visibility）**
  - 第一階段以 **visibility-only**／logging／audit trace 為主
  - **不**更新 mastery／APR／fail_streak／remediation
  - **不**修改 DB schema，**除非**另開獨立 implementation phase 並列明 migration／risk
- **產出：** 單一 report（路徑於該輪 prompt 指定），**不**於 planning 輪改 production code

---

## Final confirmation（本檔案 v0.1 建立時）

| 項目 | 確認 |
|------|------|
| 是否只新增 prompt template 文件 | **是** |
| 是否修改既有 SOP | **否** |
| 是否修改 production code | **否** |
| 是否修改 tests | **否** |
| 是否修改 routes | **否** |
| 是否修改 templates | **否** |
| 是否修改 generators | **否** |
| 是否修改 validators | **否** |
| 是否修改 database | **否** |
| 是否修改 coverage matrix | **否** |
| 是否新增 allowlist | **否** |
| 是否修改 adaptive scoring／mastery／APR／remediation | **否** |
| 是否啟動下一 phase | **否** |

---

*v0.1：整合 B4 deterministic runtime 與 closure 經驗為可複用 prompt；規則仍以既有 SOP 為準。*
