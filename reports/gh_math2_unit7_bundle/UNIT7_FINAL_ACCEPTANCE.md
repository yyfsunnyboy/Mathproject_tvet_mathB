# 普高數學2 單元07 — 發布前最終人工語意驗收（revision 0001）

- 驗收對象：`capability_discrete_mathematical_expectation_1a088637/revision_0001`（`ready_for_human_review`）；Bundle 內三個套件檔的 SHA-256 與 `agent_domains_candidate/mathematical_expectation/` 完全一致。
- 依據：權威教材 `textbook_import/uploaded_sources/general/數學2/6ccf4aeb4b77_單元07-數學期望值.pdf`（第 135 頁進階題）與同名 DOCX、正式 DB 題目、Generator 實際輸出（seed 0）、共用 Checker 判分結果。
- 證據腳本：`tmp/gh_math2_unit7_isolated/acceptance_evidence.py`（唯讀，不寫 DB）。

## 結論

| 項目 | 結果 |
|---|---|
| 1. 12899 三小題拆分 | PASS |
| 2. 12911 A–E 與 ①–⑤ | PASS |
| 3. 12909 新增機率說明 | **FAIL（需最小修正）** |
| 4. 12896 零收入補充 | PASS |
| 5. 分數答案 Checker 行為 | PASS |
| Variation WARN（12900／12901／12902） | ACCEPTED_WITH_REASON |

- HUMAN_ACCEPTANCE：**BLOCKED**（第 3 項）
- REVISION：0001（不建議以此 revision 發布）
- VARIATION_WARN：ACCEPTED_WITH_REASON
- PROMOTION_READY：**NO**

## 逐項證據

### 1. 12899
- 原題：(1)「乙所得金額的期望值為多少元？這個遊戲對誰有利？」(2)「將規則(b)中的 30 元改為多少元時，此遊戲對雙方都公平？」——公平金額是原題 (2) 明確的提問。
- Generator：(1) 期望值、(2) 對誰有利（甲／乙／雙方公平）、(3)「將『點數不同時乙須付給甲 30 元』中的金額改為多少元時，此遊戲對雙方都公平？」；規則 (a)(b) 內容完整寫入題幹。
- 答案：−115/6、甲、7（10×21/36 − 30×30/36 = −115/6；210 = 30x ⇒ x = 7）。(2) 填「乙」或「雙方公平」皆被判錯。

### 2. 12911
- 原題 ①2800 ②3000 ③3300 ④3500 ⑤3800；Generator seed 0 為 A 2800、B 3000、C 3300、D 3500、E 3800，順序一一對應；正解 C = ③（(1000+2000+3000+7200)/4 = 3300）。A、B、D、E 均被判錯。
- 原題 (2)「宣稱正確嗎？若正確，增加多少？」拆為 (2) 是／否（正解：是）與 (3) 增加金額（4700 − 3300 = 1400）。各獎額互不相同時，兩球中的最大值不小於任一球，期望值必增加，Domain 也檢查增加量 > 0，所以「若正確」的條件恆成立，語意等價。

### 3. 12909（不通過）
- 原題全文只有「其餘 3 個選項則隨意猜測，求此考生在該題得分的期望值」。教材第 135 頁、DOCX 與 DB 都沒有本題解答或答案（`detailed_solution` 為空），計分規則也沒有提到任何機率。
- Generator 題幹新增「（每個選項猜對與猜錯的機會均等）」：這是教材沒有寫出的機率陳述，不符合「不得自行增加未經證實的機率假設」。
- 答案 17/8 是把「隨意猜測」解讀為「其餘選項每種作答組合等可能」所得的結果；此解讀與教材其他題處理「完全靠運氣選取」（12905）時採等可能的慣例一致，但本題沒有可直接引用的教材解答。
- 最小修正（未執行，待核可）：只刪除題幹括號，恢復教材原句「其餘 N 個選項則隨意猜測」；數學模型與答案不變。修正位置是 adapter `_guess()` 的一行字串，之後依既有流程重建 sandbox、重跑該單元 Gate，並以 revision 0002 重新產生 Bundle。
- 另一選項：若老師能提供本題的官方解答並確認 17/8，則可保留現行措辭。

### 4. 12896
- 原題只列出 3／2／1 個正面「可得」30／20／10 元，沒有提到 0 個正面的收付，即該情形所得為 0。Generator 明寫「全無正面時沒有所得」，所得函數相同，期望值都是 (30·1 + 20·3 + 10·3 + 0·1)/8 = 15，數學定義等價。

### 5. 分數答案（共用 Checker，未修改）
| canonical | 接受 | 拒絕 |
|---|---|---|
| 3/5 | 3/5、6/10、0.6、.6、0.60 | 0.5、5/3 |
| 17/8 | 17/8、34/16、2.125 | 2.13、2 1/8 |
| 9/7 | 9/7、18/14、9／7 | 1.2857、1.29、1.285714285714 |
| −115/6 | −115/6、−230/12、−115/6（全形負號） | −19.17、−19.1666666667、115/6 |
| 20 | 20、20.0 | 20元、21 |

符合《數學答案檢核原則 v1.12.1》：依數值比較、允許等價分數。循環小數的近似值不等於真值，因此被拒絕。帶單位的輸入被拒絕屬於共用 Checker 的既有行為，本單元不修改。

### Variation WARN
- 12900 原題問「應選擇在何地建廠」，只有甲、乙兩地；12901、12902 原題要求「對的打○，錯的打×」。三題都是合法的二選一／是非題。
- 稽核訊息：`Single choice must have 4 choices, got 2`。該規則屬於技高四選一 MCQ 契約，不適用於這三題；保留 WARN 與例外理由，不修改全域規範（與單元5 核可的做法相同）。

---

# Revision 0002 — 12909 最小修正

- 新 Bundle：`revision_0002/`（`ready_for_human_review`，bundle SHA-256 `b1f92e17…88a3ce`）；`revision_0001/` 保留未動，其演練與路由報告另存為 `rehearsal_unit7_report_rev0001.json`、`runtime_api_report_rev0001.json`。
- 比對腳本：`tmp/gh_math2_unit7_isolated/compare_revisions.py`。

## 程式差異（revision_0001 → revision_0002）

只改 `mathematical_expectation_adapter.py` 的 `_guess()`；`mathematical_expectation_domain.py`、`__init__.py` 完全相同。
- 刪除「（每個選項猜對與猜錯的機會均等）」。
- 「確定第 1、2 個選項」恢復為教材的「確定選項 (1) 與 (2)」，選項編號以 `\left( n \right)` 置於數學式內（與已修復的 DB 題目同格式），前端不會判成小題。
- 「未作答」恢復為教材的「未做答」。

Payload 逐一比對（21 題 × 20 個變體）：只有 12909 的 20 個變體不同，且只有題幹欄位（question_text）改變，答案與答案契約完全相同；其他 20 題的所有變體逐一相同。dryrun 的 63 個 component 檔案雜湊值全部不變（題幹在執行時才由 adapter 產生）。

## 12909 題幹一致性：PASS

seed 0 題幹去掉 `$`、`\left( \right)` 和空白後，與教材第 135 頁原文逐字相同（測試 `test_guess_stem_keeps_textbook_wording`）；50 個 seed 都不含「機會均等」；前端預覽沒有拆出小題（12909 小題數為 0），路由層 `stem_items = 0`、只有一個作答欄。

## 12909 答案 17/8 與模型假設

教材明確提供的條件：
1. 每題 5 個選項，至少一個正確。
2. 計分規則：全對 5 分、錯 1 個 3 分、錯 2 個 1 分、錯 2 個以上或全部未做答 0 分。
3. 考生已確定選項 (1)、(2) 正確。
4. 其餘 3 個選項「隨意猜測」。教材沒有提供本題解答或答案。

Generator 採用的建模假設（教材未明文寫出）：
- A1：考生把 (1)、(2) 作答為正確，所以這兩項不會答錯。
- A2：「隨意猜測」解讀為其餘 3 個選項各自以相同機會選或不選（8 種作答組合等可能、彼此獨立）。這是此類題目的通常數學解讀，也和教材 12905「完全靠運氣選取」採等可能的處理一致。

驗證：在 A2 之下，對其餘 3 個選項所有 8 種可能的「真實答案」逐一窮舉 8 種作答組合，每一種真實答案的期望值都是 17/8（= 5·1/8 + 3·3/8 + 1·3/8），所以答案不需知道真實答案即可唯一確定（測試 `test_guess_answer_is_the_same_for_every_hidden_answer_key`）。這只證明 A2 下答案唯一，不代表教材已寫出 A2。

需要額外假設的證據：若改成「每個猜測選項以 1/3 機會被選」且其餘 3 個選項實際上都不正確，期望值是 82/27，不等於 17/8。所以沒有 A2 就沒有唯一答案。

**待教師確認語意事項**：本題答案 17/8 依賴 A2（「隨意猜測」= 每個選項選或不選等可能）。題幹忠實保留教材原文，沒有寫出 A2。請教師確認此解讀與預期答案一致。

## Gate 結果（revision 0002）

| Gate | 結果 |
|---|---|
| Sandbox Math Gate（含 12909 兩項專項測試；21 題 × 50 seeds 獨立 oracle、Checker 正確收／錯誤拒） | 47/47 PASS |
| Coverage | 21/21，無 deferred |
| Python 3.11 編譯 | PASS |
| 隔離演練：promotion → Phase 2 → tracker | 21/21 `verified` |
| Phase 3 publish（sandbox）／smoke／staging smoke／production smoke | `production_published`／passed／passed／passed |
| 學生端 facade 120 seeds | 0 problem |
| 路由層 `/get_next_question` + `/check_answer` | 21/21，0 failure，無答案洩漏 |
| 前端 MathJax | 42 張卡片 0 錯誤，無殘留 `$` |
| Variation Audit | WARN 不變：18 dynamic，12900／12901／12902 兩選項（ACCEPTED_WITH_REASON） |
| 正式路徑寫入／正式 DB | 無寫入；tracker 0、21 題完好 |

## 結論（revision 0002）

- HUMAN_ACCEPTANCE：**BLOCKED**（僅剩 12909 建模假設 A2 待教師確認；題幹問題已修正）
- REVISION：0002
- VARIATION_WARN：ACCEPTED_WITH_REASON
- PACKAGE_READY：**YES**
- 可提交教師最終確認：**YES**
- PROMOTION_READY：NO（教師確認 A2 後即可改為 YES，不需再改程式）

# 正式發布（2026-11-01，revision 0002）

## 發布授權與例外

專案負責人於 2026-11-01 在對話中明確授權「先發布 21 題、再由使用者在學生練習頁實際驗收」，不等 A2 教師確認。授權寫入 `revision_0002/promotion_bundle.json` 的 `review` 區塊（`record_approval.py`），紀錄檔 `deploy_unit7_rev2_approval_record.json`：

- `approval_kind`：`project_owner_publish_authorization`；`teacher_signoff`：`false`。
- 接受：12899／12911／12896 先前人工驗收 PASS、既有分數 Checker 測試、12900／12901／12902 二選一 Variation WARN。
- **12909 A2：`pending_teacher_confirmation`，`textbook_explicit: false`**。發布不代表 A2 已驗證；教師確認前，上方「待教師確認語意事項」仍然有效。

Bundle 檔案 sha256：核准前 `b1f92e17…88a3ce`，核准後 `050aaeb0…de0289d`；canonical bundle sha256 `a714bd66…f6411e`（registry revision `promoted-a714bd66521e`）。

## 發布 Gate（`deploy_unit7.py`）

| 步驟 | 結果 |
|---|---|
| precheck（唯讀） | PASS：Bundle 雜湊符合、Stage 1 READY、12900 表格與 12909 問句修復仍在、無進行中的 orchestrator job、寫入鎖空閒 |
| backup | `backups/math2_unit7_mathematical_expectation/20261101_180124/`（DB、tracker 全表、store、fixed config、已發布 Skill，372 檔 SHA256SUMS） |
| promote | PASS：11 operations、smoke 21 案例 |
| quarantine | 無舊元件需移出 |
| rebuild（正式 Phase 2） | 21/21 `verified`，每題 20 seeds 驗證 0 失敗，與演練一致 |
| publish（正式 Phase 3） | `production_published`，21 元件，smoke／staging／production smoke 全 passed；Variation 同演練（18 dynamic + 3 個二選一 WARN） |
| verify-live | PASS：manifest 21/21、12 families、11 operations、promoted 套件與 Bundle 一致、受保護 Skill 與教材未變 |
| accept（全新程序、DB 副本、真實練習路由） | PASS：21/21 出題、route v3、7 題多小題結構正確、對錯判分正確、格式提示無答案、gh_Event／gh_Combination 正常 |
| live 5001 | 21/21 由新 Generator 出題；12909 問句完整、12900 表格、12899 三小題作答欄正常，MathJax 0 錯誤 |

已知的平台既有行為（不是本單元造成，本輪未修改）：所有已發布的 V3 Skill，`/get_next_question` 的 JSON 回應都帶有 `correct_answer` 與 `answer_contract.semantic_answer`。學生畫面不顯示，格式提示也不含答案，但瀏覽器開發者工具看得到。

## 服務狀態

- Flask 5001：已重新載入（新程序在 18:03 啟動），單元7 已生效。
- Waitress 5000（PID 26876，16:59 啟動）：**尚未生效**。promoted domain 只在程序啟動時註冊，5000 要等負責人用既有方式重啟後才會載入單元7。Agent 沒有重啟 5000，也沒有動 Cloudflare。
