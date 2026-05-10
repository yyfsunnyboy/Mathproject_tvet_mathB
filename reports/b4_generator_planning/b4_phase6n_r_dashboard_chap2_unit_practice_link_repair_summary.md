# B4 Phase 6N-R — Dashboard Chap2 Unit Practice Link Repair
## Repair Summary

**Phase:** 6N-R  
**Date:** 2026-05-10  
**Status:** ✅ READY_FOR_MANUAL_SMOKE  
**Scope:** Dashboard「2 機率」單元練習按鈕連結修正（最小修改）

---

## 1. Failure Symptom

在 `/dashboard?view=curriculum&curriculum=vocational&volume=數學B4` 頁面，  
點擊「2 機率」章節的「單元練習」按鈕，URL 錯誤導向：

```
/adaptive_practice?mode=single&skill_ids=2+機率
```

而非 Phase 6N 已完成的 chapter mode：

```
/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice
```

`mode=single&skill_ids=2+機率` 是舊版 fallback，無法觸發 Chap2 diagnostic flow。

---

## 2. Root Cause

`templates/dashboard.html` 第 455 行，「單元練習」按鈕的 Jinja2 ternary 條件：

```jinja2
{# BEFORE (buggy) #}
{{ url_for(..., mode='chapter', chapter_id='1', ...)
   if curriculum == 'vocational' and volume == '數學B4' and ch.display.startswith('1')
   else url_for(..., mode='single', skill_ids=ch.raw) }}
```

只有 `ch.display.startswith('1')` 分支（Chap1），Chap2 直接 fallback 到 `mode='single'`。  
Phase 6N 完成了 Chap2 的 chapter mode 接入，但 **dashboard 的連結條件沒有更新**。

---

## 3. Files Changed

| 檔案 | 修改內容 |
|------|----------|
| `templates/dashboard.html` (line 455) | 在 Chap1 和 single-fallback 之間加入 `elif ch.display.startswith('2')` 分支 |
| **NEW** `tests/test_b4_chap2_phase6n_r_dashboard_link.py` | 22 項連結邏輯測試 |
| **NEW** `reports/b4_generator_planning/b4_phase6n_r_dashboard_chap2_unit_practice_link_repair_summary.md` | 本報告 |

**未修改：**
- Phase 6N 所有新增檔案
- `core/routes/practice.py`（resolver 不需再改）
- `core/routes/adaptive_api.py`（endpoint 不需再改）
- 所有 generators / validators / DB schema

---

## 4. Link Before / After

### Before（錯誤）
```
/adaptive_practice?mode=single&skill_ids=2+機率
```

### After（正確）
```
/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice
```

### Chapter 1（未改變）
```
/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&learning_mode=teaching&practice_kind=unit_practice
```

---

## 5. Template Diff（精確）

```diff
- {{ url_for('practice.adaptive_practice_page', mode='chapter', curriculum=curriculum, volume=volume, chapter_id='1', learning_mode='teaching', practice_kind='unit_practice')
-    if curriculum == 'vocational' and volume == '數學B4' and ch.display.startswith('1')
-    else url_for('practice.adaptive_practice_page', mode='single', skill_ids=ch.raw) }}
+ {{ url_for('practice.adaptive_practice_page', mode='chapter', curriculum=curriculum, volume=volume, chapter_id='1', learning_mode='teaching', practice_kind='unit_practice')
+    if curriculum == 'vocational' and volume == '數學B4' and ch.display.startswith('1')
+    else url_for('practice.adaptive_practice_page', mode='chapter', curriculum=curriculum, volume=volume, chapter_id='2', learning_mode='teaching', practice_kind='unit_practice')
+    if curriculum == 'vocational' and volume == '數學B4' and ch.display.startswith('2')
+    else url_for('practice.adaptive_practice_page', mode='single', skill_ids=ch.raw) }}
```

---

## 6. Tests Run

| 測試文件 | 通過數 |
|---------|--------|
| `test_b4_chap2_phase6n_r_dashboard_link.py` (新增) | 22 |
| `test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py` | 44 |

**合計：66 passed, 0 failed**

---

## 7. Regression Result

| 批次 | 結果 |
|------|------|
| Phase 6N-R dashboard link tests (22) | ✅ 全部通過 |
| Phase 6N chapter mode integration tests (44) | ✅ 全部通過 |

---

## 8. Manual Smoke Checklist

- [ ] 開啟 `/dashboard?view=curriculum&curriculum=vocational&volume=數學B4`
- [ ] 點擊「2 機率」章節的「單元練習」按鈕
- [ ] 確認 URL 為 `/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=2&learning_mode=teaching&practice_kind=unit_practice`
- [ ] 頁面顯示「單元練習：2 機率」
- [ ] 可按「開始診斷」啟動 Chap2 diagnostic flow
- [ ] 確認「1 排列組合」的「單元練習」按鈕仍正確（`chapter_id=1`）
- [ ] 確認其他非 B4 章節的「單元練習」按鈕仍使用 `mode=single`

---

## 9. Final Confirmation

| 問題 | 答案 |
|------|------|
| 是否只修 Chap2 dashboard 單元練習連結 | ✅ 是（只改 dashboard.html 1 行） |
| 是否改 Chap2 adaptive flow | ❌ 否 |
| 是否改 Chap1 chapter mode | ❌ 否（測試確認） |
| 是否新增題型 | ❌ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ❌ 否 |
| 是否修改 DB schema | ❌ 否 |
| 是否啟動下一 phase | ❌ 否 |

---

**完成狀態：READY_FOR_MANUAL_SMOKE**
