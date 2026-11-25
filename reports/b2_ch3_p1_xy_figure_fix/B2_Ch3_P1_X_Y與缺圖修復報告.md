# B2 第3章 P1：X/Y 未顯示＋如圖缺圖／LaTeX 修復報告

**日期**：2026-11-23  
**範圍**：B2 第3章 15 個 allowlist SubSection；重點 `3_1_3`、`3_1_4`  
**狀態**：工程修復完成，**暫停第3章封板／不進入第4章**，等待教師驗收  
**本輪**：不 commit、不 push；正式 DB 唯讀；Flask 5000／Cloudflare 未動；5001 已受控重啟載入新碼

---

## 1. 第3章 X/Y 為何未顯示（Root Cause）

**雙重原因（皆已證實）：**

1. **部署／進程不一致（主因）**  
   磁碟上 `B2_TYPE_MASTERY_PILOT_SKILL_IDS` 已含第3章 15 個 Skill，隔離測試 59/59 PASS；但當時 Flask **5001 進程未重載**新版 `practice_type_mastery.py`，live 頁面仍走舊連對語意 → UI 顯示「🔥 連續答對：暫無門檻」。

2. **資料流缺口（次因，已修）**  
   `practice.py` 在部分路徑（含 guest／未寫 mastery 列）雖可能命中 allowlist，但 `pass_target` 仍為 0 時，模板對 `progress_mode=streak` 會落到「暫無門檻」。已改為：**allowlist 技能一律 `progress_mode=problem_type_mastery`**（不依賴登入才切 mode）；guest demo 以 `list_required_problem_types` 填 Y、X=0，不寫 DB。

**非原因**：Skill ID 拼字錯誤、allowlist 漏列、Y=0 偽裝完成（修復後 15/15 皆 Y≥1）。

**SOP**：`VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §12.8 已補「Allowlist 變更後須重載 Flask；隔離 PASS ≠ live 驗收」。

---

## 2. 15 個 Skill 實際進度模式與 Y

來源：重啟後 live HTTP 探針 `live_5001_probe.json`＋pilot inventory（皆 `problem_type_mastery`）。

| Skill | UI | Y |
|-------|----|---|
| `vh_數學B2_SubSection_3_1_1` | 已掌握題型 0/2 | 2 |
| `3_1_2` | 0/1 | 1 |
| `3_1_3` | 0/1 | 1 |
| `3_1_4` | 0/6 | 6 |
| `3_2_1` | 0/6 | 6 |
| `3_2_2` | 0/6 | 6 |
| `3_2_3` | 0/2 | 2 |
| `3_2_4` | 0/2 | 2 |
| `3_2_5` | 0/2 | 2 |
| `3_2_6` | 0/2 | 2 |
| `3_3_1` | 0/3 | 3 |
| `3_3_2` | 0/3 | 3 |
| `3_3_3` | 0/5 | 5 |
| `3_3_4` | 0/2 | 2 |
| `3_3_5` | 0/4 | 4 |

對照：第2章 `2_1_1`、第1章具名銳角三角 live 仍為 X/Y（未回歸成連對）。

---

## 3. `3_1_3`、`3_1_4` Source ID

| Skill | 代表 TE | 教材錨點 | 說明 |
|-------|---------|----------|------|
| `3_1_3` | **11735**（另有 11736–11738、11746–11747 等綁定） | 例3／`vocational_math_B2_3-1_example_003_005` | 題幹含「如圖」；PDF crop 已匯入 |
| `3_1_4` | **11739**（另有 11740–11744、11748–11753 等） | 例5／`vocational_math_B2_3-1_example_005_009` | 題幹含「如圖」；PDF crop 已匯入 |

教師回報的「PQ＋QR」／「求 k₁、k₂」屬 **Generator 變體**（同 Skill 題型庫），非 TE 原文逐字重現。

---

## 4. 原始教材圖形是否存在

**存在。**  
`image_assets`（`pdf_visual_crop`）路徑例：

- `uploads/question_assets/vocational/longteng/數學B2/ch03_向量/sec_3-1_向量的作圖/textbook_example_例3_vocation_fig1.png`（TE 11735）
- 同目錄例5／隨堂練習等 crop（TE 11739 等）

檔案、SHA-256、bbox 已記入 `figure_source_probe.json`。

---

## 5. 缺圖發生在哪一層

| 層級 | 結論 |
|------|------|
| Source／匯入 | **正常**（PDF crop 在庫） |
| Generator | **有帶出** `visual_spec`（箭頭／點／軸）；隨機變體路徑**刻意不重用** TE PNG（避免與參數化圖形不一致） |
| Canvas／前端 | **故障點**：`isVisualSpecRenderable` 舊邏輯只認 lines／curves，**純 arrows 的 `free_vectors` 判定不可繪** → 手寫區空白 |

修復：`static/js/visual_spec.js` 將可解析起迄點的 `arrows` 視為 drawable。  
圖片仍只畫在手寫／繪圖 Canvas，**未**搬到題幹上方。

---

## 6. 向量公式是否正確

- **Bug**：`sanitize_trivial_vector_coefficients` 把 `k_1\vec{…}` 誤當「係數 1」→ 顯示成 `k_\vec{…}`。  
- **修**：正則 lookbehind 排除 `_`／字母；Generator 顯式使用 `k_{1}`／`k_{2}` LaTeX。  
- **Live**：`3_1_4` 題幹可見 \(\vec{u}=k_1\vec{v}\)、\(\vec{w}=k_2\vec{v}\)（或同構的 a/b、OP/OQ 模板，含 \(\vec{c}=k_2\vec{a}\) 變體）。  
- **Source TE 11739 原文**為正六邊形填空倍數關係，與 scalar-fill 變體**題型同 Skill、敘述不同**；Checker 依各變體 canonical，未發現箭頭作用在錯誤字母的殘留。

---

## 7. 修改檔案

| 檔案 | 變更 |
|------|------|
| `core/routes/practice.py` | allowlist → 固定 mastery mode；guest 填 Y |
| `static/js/visual_spec.js` | arrows 可 render |
| `core/gencode/resources/rational_display.py` | 下標安全 trivial-coeff |
| `core/domain/vector_plane_gap_coverage.py` | `k_{1}`／`k_{2}` 題幹 |
| `tests/gencode/test_rational_display_resource.py` | 回歸 |
| `tests/test_practice_visual_spec_rendering.py` | 回歸 |
| `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` | §12.8 live 重載 Gate |

證據目錄：`reports/b2_ch3_p1_xy_figure_fix/`（含 `evidence/*.png`、probe JSON）。

---

## 8. 修復前後真實瀏覽器畫面

**修復前（教師／早期 5001）**

- `3_1_3`／`3_1_4`：連續答對：暫無門檻；手寫區無向量圖。  
- （進程未載入 Ch3 allowlist／arrows 不可繪）

**修復後（本機 5001，已截圖）**

- `evidence/evidence_3_1_3_after.png`：✅ 已掌握題型 **0/1**；Canvas 有 A/B/C 向量圖。  
- `evidence/evidence_3_1_4_after.png`：✅ **0/6**；Canvas 有幾何圖。  
- `evidence/evidence_3_1_4_k1k2_after.png`：✅ **0/6**；\(k_1\)/\(k_2\) LaTeX 正常；Canvas 有 u/v/w（或 OP/OQ/OR）箭頭。

---

## 9. 回歸結果

| 項目 | 結果 |
|------|------|
| Ch3 type-mastery pilot | **59/59 PASS**（既有最新戳記 20261123_135630） |
| `test_rational_display_resource`＋`test_practice_visual_spec_rendering` | **17 passed** |
| Live 15 Skill UI mode | **15/15** `problem_type_mastery`，Y 與 inventory 一致 |
| 真實瀏覽器 `3_1_3`／`3_1_4` | X/Y＋Canvas 圖＋LaTeX **PASS** |
| 正答增 mastery／同型不重複／答錯不清零／assisted／MsgBox／導航／跨學生隔離 | **沿用既有 Ch3 pilot 契約測試**（本輪未重跑全套行為腳本）→ 標記 **PASS（prior gate）** |
| 390px／1180×820 版面 | **NOT_TESTED**（本輪未做 viewport 重測） |
| 第3章其餘「如圖」題型全掃 Canvas | **部分**：Generator 探針多數 `has_visual_spec=true`；`src_11818` 題幹**無**「如圖」且無圖 → 可接受。TE PNG 未強制掛上隨機變體（設計取捨） |

---

## 10. BLOCKED／人工處置

| 項目 | 狀態 |
|------|------|
| 正式 DB／Publish 變更 | **未執行**（無需；修復為 runtime／前端／顯示層） |
| 將 TE PNG 強制覆寫到所有 Generator 變體 | **不建議／未做**（與參數化 `visual_spec` 衝突）；若教師要求「必須與課本同一張圖」需另案核准 |
| B2 第3章工程封板 | **暫停**，待教師在 5001 目視驗收 |
| 進入第4章 | **停止，不自動展開** |
| Flask 5001 | 已重啟載入本輪碼；驗收後若再改 allowlist 須再重載 |

---

## 結案六項（精簡）

1. **Root cause**：5001 未載入 Ch3 allowlist＋arrows 不可繪＋`k_1` 被 trivial-coeff 吃掉。  
2. **修復**：重載＋mode/Y 資料流＋`visual_spec` arrows＋下標安全 LaTeX。  
3. **驗證**：15 Skill live X/Y；兩問題 Skill 真實瀏覽器有圖；17 單元測試 PASS。  
4. **未做**：commit／push、正式發布、第4章、整冊重建。  
5. **SOP**：僅最小補 §12.8 live 重載 Gate。  
6. **下一步**：教師 5001 驗收後再決定是否封板。
