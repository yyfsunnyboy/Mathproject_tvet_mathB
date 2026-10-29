# 普高數學2 Unit 5（組合）GenCode V3 — 教師驗收頁

**狀態：等待教師核准**（Bundle `ready_for_human_review`；未 Promotion／Publish、未合併 staged proof、未動正式 DB／設定）

證據來源（唯讀，未重建）：`UNIT5_REVIEW_REPORT.md`、`review_samples.json`、`rehearsal_unit5_report.json`、
`teacher_acceptance_evidence.json`（由 `teacher_acceptance_evidence.py` 從演練沙盒已發布的 Generator 取樣）。

## 1. 驗收對象

| 項目 | 內容 |
|---|---|
| Bundle | `reports/domain_operation_workspaces/capability_discrete_combinations_5ba1971d/revision_0001/promotion_bundle.json` |
| Bundle SHA-256 | `bbdc6bad00c4f7f046184553f14b8397c1e97989964883edc947f6201d41cd15` |
| Domain | `discrete.combinations`，19 個 operations |
| 套件一致性 | production_package = 候選原始檔 = bundle 記載 SHA；演練發布的 34 個 `generate.py` = 演練報告 SHA |
| `gh_Combination` | 23 列：22 動態 + 1 固定（12834） |
| `gh_BinomialTheorem` | 14 列：12 動態 + 2 固定（12838、12845） |
| 動態覆蓋 | 34/34，演練 Phase 2 tracker 全 `verified`；正式路徑寫入掃描為空 |

## 2. 三題固定題分工

| ID | 教材 | 機制 | 現況（唯讀核對） |
|---|---|---|---|
| 12834 | 進階題12 | 有計分教材原題＋教師核可圖 | 已上線、未變動：(1) ③ (2) 116；choice_label＋integer checker；圖檔存在；題幹 SHA 與正式題列一致 |
| 12838 | 例題9 | 證明，自評（不計分） | 暫存於 `reports/gh_math2_unit5_fixed/staged_proof_entries.json`，**未**進 live；題幹 SHA 與正式題列一致 |
| 12845 | 隨堂練習10 | 證明，自評（不計分） | 同上 |

**例題9** 證明 \(C_0^n+C_1^n+\cdots+C_n^n=2^n\)
- 提示：寫出 \((x+y)^n\) 的展開式 → 以 \(x=1, y=1\) 代入 → 整理得證
- 參考證明：\((x+y)^n=\sum C_r^n x^{n-r}y^r\)；代入得 \((1+1)^n=C_0^n+\cdots+C_n^n\)；左式 \(=2^n\)，得證。

**隨堂練習10** 證明 \(C_0^n-C_1^n+C_2^n-\cdots+(-1)^nC_n^n=0\)
- 提示：寫出展開式 → 以 \(x=1, y=-1\) 代入 → 整理得證
- 參考證明：代入得 \((1-1)^n=C_0^n-C_1^n+\cdots+(-1)^nC_n^n\)；\(n\) 為正整數，左式 \(=0\)，得證。

兩題學生自評一律回傳「不計分」，不產生對錯、連續答對、精熟度或錯題紀錄（`test_gh_unit5_fixed_proofs_staged.py` 3/3 PASS）。

## 3. 代表題（教材原題參數，已人工複算）

| ID | 題幹（摘要） | 答案 | 解析要點 |
|---|---|---|---|
| 12813 | 10 位手球選手選 7 人；(2) 甲乙必恰選一人 | 120；56 | \(C_7^{10}=120\)；\(C_1^2\times C_6^8=2\times28\) |
| 12822 | 五個組合恆等式，多選 | 1,3,4,5 | 對稱、巴斯卡、差、連鎖、曲棍球棒逐項判定；(2) 左式 \(=C_{50}^{100}\ne C_{49}^{100}\) |
| 12828 | 7 男 5 女選 4 人：(1) 2 男 2 女 (2) 至少 1 女 (3) 男女各至少 1 | 210；460；455 | \(21\times10\)；\(495-35\)；\(495-35-5\) |
| 12833 | snoopy 任選 3 字母排列 | 72 | 皆相異 \(10\times6=60\)；o 取 2 個 \(4\times3=12\) |
| 12835 | 寫出 \((x+y)^5\) 展開式 | \(x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4+y^5\) | 逐項 \(C_r^5\) |
| 12836 | 寫出 \((2x-y)^4\) 展開式 | \(16x^4-32x^3y+24x^2y^2-8xy^3+y^4\) | \(C_r^4 2^{4-r}(-1)^r\) |
| 12837 | \((x^2+\frac{2}{x})^6\) 中 \(x^3\) 係數 | 160 | 通項 \(x^{12-3r}\)，\(r=3\)：\(20\times8\) |
| 12843 | \((\sqrt2-1)^5=a+b\sqrt2\) | \(a=-41, b=29\) | 偶次項 \(-20-20-1\)；奇次項 \(4+20+5\) |
| 12846 | 11 人至少派 2 人 | 2036 | \(2^{11}-1-11\) |
| 12848 | \((1+ax)(1+x)^5\) 中 \(x^2\) 係數為 5 | \(a=-1\) | \(10+5a=5\) |

題目、答案、解析三者一致：每題解析由同一 Domain 計算結果產生，並經獨立驗證器（暴力枚舉／巴斯卡三角形／sympy）與 Sandbox 對每個題幹的重新求解核對（109/109 PASS）。

## 4. 判分抽驗（共用 runtime checker，17/17 符合預期）

| 題 | 接受 | 拒絕 |
|---|---|---|
| 12835 展開式 | 項次重排、顯式乘號 | 未展開 \((x+y)^5\)、缺項 |
| 12836 展開式 | — | 符號錯 |
| 12813 多小題 | 全對 | 一小題錯、一小題漏答 |
| 12843 a, b | 全對 | a, b 對調 |
| 12822 複選 | 全對、順序不同 | 漏選、多選 |
| 12848 數值 | \(-1\)、\(-2/2\) | \(1\) |

另：展開式 Checker 專測 22/22 PASS（含分數、小數係數）；演練學生端 80 seeds 標準／等價／錯答 0 誤判。

## 5. 四題○×題審查（12823、12824、12825、12840）

| ID | 題型 | 20 個變體 | 正解分布 |
|---|---|---|---|
| 12823 | 「從 n 人選 k 人的組合數為 \(C_?^n\)」 | 20 種相異題幹 | ○10／×10 |
| 12824 | 「\(C_k^n\times m!=P_k^n\)」 | 20 | ○8／×12 |
| 12825 | 「\(C_a^n=C_b^n\)」 | 20 | ○10／×10 |
| 12840 | 「\((x+y)^n\) 兩項係數相等」 | 20 | ○11／×9 |

**契約**：`single_choice`＋`choice_label_checker`，選項 A=○、B=×。與已上線的 Unit 4 排列，以及其他 12 個已升級 Domain 共用同一個 `TRUE_FALSE_CHOICES` 定義。

**稽核規則逐條重放**（每題 20/20 個變體）：

| 規則 | 結果 |
|---|---|
| 必要欄位齊全 | 20/20 |
| 正解自我判分為對 | 20/20 |
| 選項不重複 | 20/20 |
| 正解標籤在選項中 | 20/20 |
| 反向標籤被拒 | 20/20 |
| 題幹不洩漏答案 | 20/20 |
| **選項須為 4 個** | **0/20**（○× 只有 2 個） |

**審查結論**：

- `unsafe_dynamic` 的唯一成因，是變化稽核的「單選題須 4 個選項」通用規則不適用於二選一的 ○× 題型。其餘稽核規則全部通過，題目變化本身充足：每題 20 種相異題幹，且 ○、× 兩種正解都有。
- 正式發布 Gate 只會因 `static_stem_collapse`，或「必須動態的 Skill 出現 static」而擋下發布；`unsafe_dynamic` 只記錄在發布結果中。這與 Unit 1–4 的先例相同，Unit 4 即帶著同一個標記上線。
- 此標記**保留為警告（WARN），不改為 PASS**，Gate 與門檻均未修改。
- **發布風險：低**。判分正確、不洩漏答案、與已上線題型同一契約。唯一影響是之後的稽核報表會持續顯示此警告。

## 6. 待教師確認事項（非阻擋）

1. **解析排版**：12835、12836、12837、12843 的解析中，有部分算式為純文字寫法，例如 `x^(5−r)`、`1^5×1^0`，沒有排成數學式。數學內容正確。若要改善，需建立 revision_0002 並重跑 Gate；本輪依限制未修改 Generator。
2. **○× 稽核警告**：同第 5 節，請確認接受「警告保留、非阻擋」的處理。

## 7. Promotion／Publish 前置條件

1. 教師核准本 Bundle（revision_0001，SHA-256 如上），並明確授權一次 Promotion＋Publish。
2. 部署前：備份正式 DB 與 promoted store；以核准紀錄寫入 review（核准不由建置腳本代寫）。
3. 執行順序：Promotion → 正式 Phase 2（tracker verified）→ Phase 3 Publish 兩個 Skill → verify-live。
4. 將 `staged_proof_entries.json` 以正式題列重新綁定後合併入 `configs/fixed_textbook_practice.json`。合併後同步更新兩個預發布測試的斷言：
   - `test_gh_unit5_fixed_proofs_staged.py`：原先要求兩題「尚未在 live」；
   - `test_gh_unit5_fixed_advanced12.py::test_other_unit5_rows_are_not_fixed_entries`：固定題應改為 12834、12838、12845。
5. 發布後增量驗收；依 Unit 4 前例，執行中的 Flask 需重啟才會載入新 Skill 綁定，由使用者安排，部署腳本不重啟任何服務。
