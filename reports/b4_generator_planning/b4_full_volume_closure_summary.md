# B4 Full-volume Closure Summary

## 1. Scope and Guardrails

本輪 (Phase B4-Final) 專司 B4 全冊之 Closure 總結與狀態封存。嚴格遵守以下限制：
- 不改 code
- 不改 tests
- 不改 DB
- 不新增 generator
- 不接新的 adaptive
- 不新增 SOP

---

## 2. B4 Volume Structure Confirmation

經各階段盤點與查證，B4 實際的教材章節結構如下：
- Chapter 1：排列組合
- Chapter 2：機率
- Chapter 3：統計
- Chapter 4：不存在 / 無教材 evidence

**說明**：Phase 8A 已經確認 Chap4 因缺乏教材 evidence 觸發了 BLOCK 條件。既然 B4 實質僅有前三章，因此 B4 全冊開發主線可於此階段安全進入 closure。

---

## 3. Chapter 1 Closure Summary

- deterministic runtime-ready 主線已完成。
- chapter mode / adaptive practice 既有主線已完成。
- 保留 handwriting / free-response / listing 等不具備單一機器判斷標準之題型政策。
- **已知限制**：樹狀圖、窮舉法等依賴作圖與手寫過程的題型被列入保留 (reserved) 範圍。
*(based_on_existing_phase_reports_and_sop_context)*

---

## 4. Chapter 2 Closure Summary

- deterministic full skill coverage 已完成。
- 17 個 deterministic problem_type 已完成。
- adaptive chapter mode v0.1 已完成並封存。
- audit logging / teacher visibility 已完成。
- prerequisite/remediation map planning 已完成。
- **status**：ACCEPTED WITH KNOWN LIMITATIONS

**已知限制**：
- 補救仍以 session-local / rule-map assisted 為主。
- 尚未正式接 APR / PPO / AKT。
- 尚未 formal mastery write-back。
- handwriting / listing / free-response 題型保留為 reserved。

---

## 5. Chapter 3 Closure Summary

- deterministic mainline 已完成核心純數值統計技能。
- **status**：ACCEPTED WITH RESERVED SCOPE

**已完成 skills**：
- `vh_數學B4_CentralTendencyMeasures`
- `vh_數學B4_WeightedMean`
- `vh_數學B4_VarianceAndStandardDeviation`
- `vh_數學B4_LinearTransformationOfData`
- `vh_數學B4_DispersionMeasures`

**剩餘技能處置**：
- `needs_textbook_alignment`：如抽樣方法、常態分配等需校準語義界線。
- `not_suitable_now`：如抽樣調查、統計基本概念（來源證據不足）。
- `reserved / future_ai_judged`：如統計圖表判讀、累積次數分配表編製、繪圖等。

**說明 Chap3 不接 adaptive_practice 的原因**：
- 剩餘技能包含大量圖表、表格、作圖及開放式解釋。
- 若強行串接 adaptive，演算法極容易推送不可批改的題型，進而導致流程卡死。

---

## 6. B4 Deterministic Runtime-ready Scope

目前 B4 已完成的 deterministic runtime-ready 類別總覽：

| chapter | status | completed deterministic scope | adaptive status | reserved scope | notes |
|---|---|---|---|---|---|
| Chap1 | Completed | 排列組合相關 deterministic 題型 | Integrated | enumeration, listing, tree diagram, handwriting | 具備完整 adaptive 流程 |
| Chap2 | ACCEPTED WITH KNOWN LIMITATIONS | 17 個 deterministic problem_type | v0.1 Completed | handwriting, listing, free-response | 具備基礎補救機制與 teacher visibility |
| Chap3 | ACCEPTED WITH RESERVED SCOPE | 統計核心純數值 problem_type | Not Integrated | chart, drawing, full table, open-response, needs alignment | 不接 adaptive，避開無法批改題型 |
| Chap4 | BLOCK | 無 (教材範圍不存在) | N/A | N/A | 因無教材 evidence 終止 |

---

## 7. Reserved / Future AI-judged Scope

全冊統一列出 reserved 與未來由 AI 批改之題型類別：
- tree diagram / listing / enumeration 題型
- handwriting / proof / explanation 題型
- chart reading
- histogram / line chart drawing
- full frequency table construction
- image-dependent 題型
- table-heavy 題型
- open-response interpretation 題型

**政策**：
- 僅供展示 (visibility-only)
- 不進 deterministic allowlist
- 不進 mastery / APR 計算
- 留待未來 AI-judged / teacher review 技術成熟後另開 phase 處理

---

## 8. Adaptive / APR / Mastery Status

**目前已完成**：
- Chap2 adaptive chapter mode v0.1
- UI progress / trajectory / audit / teacher visibility 的基礎閉環

**尚未正式完成**：
- 全冊 formal mastery write-back
- APR / PPO / AKT 正式 routing
- 全域 prerequisite remediation graph
- handwriting / AI-judged scoring integration

**未來方向**：
- 需等 B1–B4 與國中前置技能更完整建置後，再統一規劃全域 prerequisite / remediation graph。
- APR 演算法應先採行 dry-run / preview 模式，確認穩定後再正式寫入影響學生權重。

---

## 9. SOP Lessons Learned

回顧 B4 開發過程所沉澱的重要 SOP 原則：
- **Runtime-ready 驗收標準**：不只是 generator 能跑即可，必須確實接通 `/practice` / `get_next_question` / `check_answer` API。
- **邊界防護**：frontend encoded / decoded skill_id 為必測項目；not-enabled / reserved UX 不得外洩系統內部的 phase 狀態。
- **Adaptive 驗證**：adaptive chapter mode 必須驗證入口連結、start diagnosis 行為及 UI state。
- **題型多樣性**：scenario diversity 必須在 tests 中自動化檢查，不得依賴人工大量連按。
- **人工測試推遲**：manual smoke 應延後到 chapter-level 或 volume-level，只做少量代表性檢查以節省人工成本。
- **自動化補強**：small repair 應先補足 automated regression test 後，再進行 code 的修復。

---

## 10. Recommended Next Project Direction

以下為針對未來專案走向之建議及優先順序：

- **Option A (建議首選)**：B1–B3 content planning / import / deterministic coverage
  - *理由*：往回擴建，能有效補足 B4 補救教學 (Remediation) 所需的前置技能池。
- **Option B (強烈推薦)**：國中 prerequisite content planning
  - *理由*：建立堅實的基礎知識圖譜，長期來看最有助於精準補救教學與優化 APR routing。
- **Option C**：B5 或下一冊 textbook evidence planning
  - *理由*：向前延伸高中/高職教材的覆蓋廣度。
- **Option D**：B4 reserved / AI-judged planning
  - *理由*：僅在短期強烈需要圖表/表格/手寫能力時才啟動，不建議作為優先事項。

**明確推薦**：
強烈建議優先執行 B1–B3 或國中 prerequisite planning，以擴建系統的知識根基；而不應繼續硬修 B4 之 reserved 題型。

---

## 11. Final Closure Status

**B4 full-volume deterministic/adaptive development baseline = CLOSED AS v0.1**

**說明**：
B4 已完成可安全 deterministic 的主要內容與部分 adaptive chapter mode。未能完成的內容多屬於 reserved / future_ai_judged 或 prerequisite pool 不足之範疇，皆屬已知限制而非技術 blocker，專案可順利邁入下一個發展階段。

---

## 12. Final Confirmation

- 是否只新增 closure report：**是**
- 是否修改 production code：**否**
- 是否修改 tests：**否**
- 是否修改 DB：**否**
- 是否新增 generator：**否**
- 是否修改 adaptive scoring / mastery / APR / PPO：**否**
- 是否接新的 adaptive_practice：**否**
- 是否新增題型：**否**
- 是否啟動下一 phase：**否**
- 是否新增 SOP：**否**
