# B1 學習導航優化報告：略過已完成、同章補缺、章節鼓勵

**日期**：2026-11-22  
**範圍**：僅 B1  
**狀態**：實作完成，等待人工驗收（不進入 B2）

---

## 1. 原本導航方式及問題根因

- 只找「教材順序上的下一個可練習 Skill」。
- **不讀學生掌握狀態**，已完成 Skill 仍會被推薦。
- 章末直接換章，沒有「同章前面遺漏補齊」。
- 沒有章節／本冊完成的不同鼓勵文案。

## 2. 新的下一個未完成 Skill 查找規則

對**目前登入學生**（`user_id`）：

1. 同章、目前 Skill **之後**的第一個未完成可練習 Skill  
2. 若後面都完成 → 同章**之前**的第一個未完成（補缺）  
3. 同章全部完成 → `chapter_complete`，下一章第一個未完成  
4. 後面章節也全部完成 → `volume_complete` → 儀表板  

主按鈕動態文案：`繼續挑戰：{技能中文名}`／`前往下一章`／`返回學習儀表板`。

## 3. Curriculum 排序來源

- 章列表：`get_chapters_by_curriculum_volume` + `chapter_natural_sort_key`
- 章內：`section` 數字序 → `display_order` → `skill_id`（與章複習一致）
- 完成判定：該生 `student_problem_type_mastery` × 現行 Runtime 可用題型

## 4. 已完成略過與自由複習

- 自動導航略過已 MASTERED 全題型的 Skill。
- 主動進入已完成 Skill：可繼續作答；答錯**不撤銷** MASTERED；不重彈首次完成 MsgBox。
- 練習頁提供「前往下一個未完成技能」連結（`review_next_skill_url`）。

## 5. 章節與本冊完成提示

| celebration_kind | 標題 | 主按鈕 | 次按鈕 |
|---|---|---|---|
| skill | 完成這個單元 | 繼續挑戰：… | 留在目前技能 |
| chapter | 完成這一章 | 前往下一章 | 留在本章 |
| volume | 完成本冊 | 返回學習儀表板 | 返回學習儀表板 |

仍僅在 `skill_just_completed`（轉換＋commit）時彈出。

## 6. 空殼／inactive

不進入可練習清單：NumberLine（inactive）、outline、SubSection332（無題型）等。不視為已掌握，也不造成章節卡關。

## 7. 測試結果

| 套件 | 結果 |
|---|---|
| `scripts/test_b1_nav_skip_completed.py` | **14/14 PASS**（略過、補缺、章節／冊完成、學生隔離、UI） |
| `scripts/test_b1_completion_navigation.py` | **13/13 PASS** |
| `scripts/test_b1_skill_completion_msgbox.py` | **16/16 PASS** |

證據：`reports/gencode_closed_loop/b1_nav_skip_completed_latest.json`

瀏覽器／iPad 真人點擊仍待人工驗收。

## 8. B2～B4

不變（非 B1 回 fallback，不進本題型完成 UI）。

## 9. 待人工驗收

1. 完成中間 Skill → 按鈕顯示「繼續挑戰：xxx」且略過已完成  
2. 同章後面都完成、前面有缺 → 回頭補缺  
3. 同章全完成 → 章節鼓勵 MsgBox  
4. 本冊全完成 → 本冊鼓勵  
5. 已完成 Skill 複習答錯進度不歸零、不重彈完成窗  
6. 不自動跳轉；重整不重複彈  
7. iPad Modal 不壓縮手寫區  

---

**修改檔**：`core/practice_type_mastery.py`、`core/routes/practice.py`、`core/practice_student_payload.py`、`templates/index.html`、相關測試腳本。

**停止，等待人工驗收。**
