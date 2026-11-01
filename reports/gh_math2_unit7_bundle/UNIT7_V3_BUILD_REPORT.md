# 普高數學2 單元07 數學期望值 — GenCode V3 建置報告

- 範圍：curriculum `general`、volume `數學2`、Skill `gh_MathematicalExpectation`、textbook_examples 12891–12911（21 題）。
- 狀態：**PACKAGE_READY**（Bundle `ready_for_human_review`）。未 Promotion、未 Publish、未寫入正式 DB。

## 產物

| 項目 | 位置 |
|---|---|
| 候選 Domain 套件 | `agent_domains_candidate/mathematical_expectation/` |
| Sandbox Gate 測試 | `tests/gencode/test_gh_math2_unit7_expectation_sandbox.py` |
| Review Bundle | `reports/domain_operation_workspaces/capability_discrete_mathematical_expectation_1a088637/revision_0001/` |
| 隔離演練 | `reports/gh_math2_unit7_bundle/rehearse_unit7.py` → `rehearsal_unit7_report.json` |
| 路由層檢查 | `reports/gh_math2_unit7_bundle/isolated_server.py api` → `runtime_api_report.json` |
| 顯示預覽 | `reports/gh_math2_unit7_bundle/display_preview.py` → `tmp/gh_math2_unit7_isolated/display_preview.html` |

Domain `discrete.mathematical_expectation`：11 個 operation、12 個 family。每個答案都由「窮舉等可能結果／分布」與「公式（二項、超幾何計數、期望值線性）」兩種方法計算，兩者不一致即拒絕出題。

## 覆蓋（21/21，無 deferred）

| family | operation | 題目 |
|---|---|---|
| die_payout | die_payout_expectation | 12891 例1、12903 基礎1 |
| coin_payout | coin_payout_expectation | 12894 例4、12896 隨堂1 |
| urn_value_sum | urn_draw_expectation | 12892 例2、12897 隨堂2 |
| urn_count_expectation | urn_draw_expectation | 12893 例3、12898 隨堂3、12906 基礎4 |
| urn_event_payout | urn_draw_expectation | 12904 基礎2、12905 基礎3 |
| fair_game | two_dice_match_game / single_die_game | 12899 隨堂4、12907 基礎5 |
| insurance_expectation | insurance_expectation | 12895 例5、12908 基礎6 |
| expectation_decision | decision_by_expectation | 12900 隨堂5 |
| expectation_claim | expectation_claim | 12901、12902 觀念澄清 |
| guess_score_expectation | multiple_choice_guess_expectation | 12909 進階7 |
| lottery_expectation | lottery_expectation | 12910 進階8 |
| prize_draw_comparison | prize_ball_expectation | 12911 進階9 |

Seed 0 與教材一致：例1 20、例2 320、例3 3/5、例4 −5 與 0、例5 2000；隨堂 15、160、9/7、(−115/6、甲、7)、乙地；觀念澄清 ○、×；基礎 35、60、22800、12/5、(19/6、不公平)、2000；進階 17/8、29、(③ 3300 元、是、1400)。

## Gate 結果

| Gate | 結果 |
|---|---|
| Sandbox pytest（21 component × 50 seeds，獨立暴力 oracle、Checker 正確收／錯誤拒、等價式、答案欄數、子題標記、DB 綁定） | 45/45 PASS |
| Python 3.11 編譯 | PASS |
| 每個 component 變體數 | 20（distinct surfaces 20/20） |
| 隔離演練：暫存 store promotion → 正式 Phase 2 → tracker | 21/21 `verified`，0 failure |
| 隔離演練：Phase 3 publish（sandbox root） | `production_published`；smoke／staging／production smoke 皆 passed |
| 學生端 facade 120 seeds | 21 題皆被出到，0 problem |
| 路由層 `/get_next_question` + `/check_answer`（DB 複本） | 21/21，0 failure，無答案洩漏 |
| 前端 MathJax（實際 index.html 題幹函式 + MathJax 3） | 42 張卡片，0 錯誤，無殘留 `$`；多小題列數正確 |
| 正式路徑寫入掃描 | 空（configs、core/domain/promoted、skills、agent_skills_v3、正式 DB 未變） |
| Variation audit | **WARN** `unsafe_dynamic`：18 dynamic；12900、12901、12902 為兩選項單選，觸發「single choice 必須 4 選項」規則 |

Variation WARN 與單元5（人工核可為 WARN，不改為 PASS）、單元6 相同：該規則為技高四選一 MCQ 契約，不適用於 ○／× 與甲地／乙地兩選項題。未修改共用稽核邏輯。

## 需人工複核

1. 12899：教材 (1) 一題兩問（期望值＋對誰有利），拆成 (1) 期望值、(2) 對誰有利（甲／乙／雙方公平）、(3) 公平金額，小題編號與課本不同。
2. 12911：(1) 選項以 A–E 呈現（課本 ①–⑤）；課本 (2)「正確嗎？若正確，增加多少」拆成 (2) 是／否、(3) 增加金額。
3. 12909：題幹補上「每個選項猜對與猜錯的機會均等」，並以「第 1、2 個選項」取代 (1)(2)，避免前端把括號數字誤判為子題。
4. 12896：題幹明寫「全無正面時沒有所得」（課本省略此情形）。
5. 12907 (2)：以「公平／不公平」作答；部分變體的先付金額恰等於期望值，答案為「公平」。
6. 標準答案以最簡分數儲存（如 −115/6），但 Checker 依數值判斷：等值分數（−230/12）、有限小數（2.125）皆接受；循環小數的四捨五入值（−19.17）不接受，須輸入分數；帶單位（20元）不接受（共用 Checker 行為，未修改）。
7. 詳解為純文字（如 3/8、×），未使用 LaTeX，與單元5 已核可的做法相同。

## 尚待人工決定

- 是否核准 revision 0001 進行 Promotion／Publish（屆時另備部署腳本：backup → promote → rebuild → publish → verify-live → accept）。
- 本輪建置與驗證未重啟任何服務。正式 Promotion 後若要讓執行中的服務載入新的 promoted 套件，可能需要重啟 Flask 5001（單元6 部署即授權重啟 5001，5000／Cloudflare 未動），須於發布授權時一併確認。
