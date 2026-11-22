# B1 Skill 完成 MsgBox — 同章節優先導航修正報告

**日期**：2026-11-22  
**範圍**：僅 B1 完成 MsgBox 下一步導航  
**狀態**：實作完成，等待人工驗收

---

## 1. 原本下一個 Skill 的選取方式

`resolve_next_b1_practice_skill` 以整冊 `volume` 扁平掃描，排序為：

`chapter 字串升冪 → display_order → id`

問題：

- `display_order` 是**節內**序號，不是章內全域序。
- 會把不同節（1-1／1-2／1-3）依 display_order 交錯，例如  
  `AbsoluteValueInequality` 被錯連到同 display_order 的 `VertexFormOfQuadraticFunction`。
- 沒有「同章優先／章末才換章／冊末回儀表板」的 `nav_kind` 語意。

## 2. 真正的 Curriculum 排序資料來源

| 用途 | 來源 |
|---|---|
| 冊／章列表 | `skill_curriculum`（`curriculum=vocational`, `volume=數學B1`） |
| 章排序 | `core.utils.get_chapters_by_curriculum_volume` → `chapter_natural_sort_key` |
| 章內 Skill 排序 | 與章複習相同：`section` 數字元組 → `display_order` → `skill_id`（對齊 `_chapter_review_ordered_sections`） |
| 可練習過濾 | `is_b1_type_mastery_skill`（排除 outline／SubSection）＋ `SkillInfo.is_active`＋ Runtime 可用題型數 > 0 |

**未**使用 Skill ID 字母序、檔案時間或自行重排 Curriculum。

## 3. 修改的檔案

- `core/practice_type_mastery.py` — 重寫導航解析（`same_chapter`／`next_chapter`／`volume_complete`／`fallback_dashboard`）
- `core/routes/practice.py` — 回傳 `next_nav_kind`、`next_button_label`、`next_target_url`
- `core/practice_student_payload.py` — 白名單補欄位
- `templates/index.html` — 動態主按鈕文案；次要按鈕「留在目前技能」
- `scripts/test_b1_completion_navigation.py`、`scripts/test_b1_skill_completion_msgbox.py`

## 4. 三種導航結果（真實 B1 Curriculum）

| 情境 | 範例 | 結果 |
|---|---|---|
| 同章中間 | AbsoluteValueInequality | → AbsoluteValueInequalityExpansion（同章 1）「繼續挑戰下一個技能」 |
| 同章跳過不可用 | Expansion 之後 | 跳過 NumberLine(inactive)／outline → CartesianCoordinateSystemEstablishment |
| 章末換章 | QuadraticInequalitySolution（第1章最後可練） | → SlopeOfALine（第2章第一可練）「前往下一章節」 |
| 冊末 | RationalEquation（第3章最後可練） | → 儀表板「返回學習儀表板」 |

## 5. 跳過不可用 Skill 的驗證

測試已確認不會選入：

- inactive：`NumberLine`、`FunctionConcept`
- outline：`outline_vocational_數學B1_*`
- 空殼：`SubSection332`（無可用 Generator 題型）

## 6. MsgBox 按鈕及跳轉測試

- 導航單元測試：**12/12 PASS**
- 完成旗標回歸：**16/16 PASS**
- 仍不自動跳轉；需按主按鈕才導航；「留在目前技能」只關閉 Modal

證據：

- `reports/gencode_closed_loop/b1_completion_navigation_latest.json`
- `reports/gencode_closed_loop/b1_skill_completion_msgbox_latest.json`

## 7. 是否影響 B2～B4

否。非 B1 回 `fallback_dashboard`／不進本題型掌握完成 UI。

## 8. 實際瀏覽器驗收狀態

自動化已覆蓋導航決策與 UI 文案標記；**真人桌面／iPad 點擊導航仍待人工驗收**。

---

**核心原則已落地：同章節優先、章末才換章、學生按下按鈕才導航。停止等待人工驗收。**
