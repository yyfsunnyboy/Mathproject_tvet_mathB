# Vocational Practice Runtime Contract

本文件只記錄已經由程式、regression tests 與 B2 實機驗收證實的共用 practice runtime 規則。

## 1. Scope

適用：

- 技高數學 practice runtime
- B1 / B2 已有架構
- 後續 B3 / B4 應沿用的共用 runtime contract

這不是 B2-only workaround。B2 驗收數字只證明這份 contract 在 B2 上已通過；不表示 B3 / B4 已經完成同等驗收。

## 2. Single-choice contract

技高 single-choice：

- exactly 4 choices
- labels only A / B / C / D
- 1 correct + 3 unique distractors
- correct semantic answer 必須存在於 choices
- frontend 禁止用 slice(0, 4) 假修
- legacy >4 choices 必須在 normalization 層保留正解後重建四項
- 如果 answer 是 label/index，choices reorder 後必須 remap
- short-answer / expression 題不得受此 contract 影響

目前主要 implementation：

- `core/gencode/single_choice_contract.py`
- `core/gencode/choice_contract_validator.py`
- `core/gencode/vocational_choice_contract.py`
- `core/gencode/answer_payload.py`
- `core/gencode/domain_matrix_adapter.py`

## 3. Answer contract

- semantic answer 優先於 presentation label
- expression 題使用既有 algebraic equivalence checker
- practice submission 不可只做字串相等
- wrapper generate 與 practice API assembly 是不同層
- `question_uid` 是 practice API/runtime assembly 負責，不要求 raw skill wrapper 自帶

## 4. Diagram / image routing

三種概念不可混為一談。

### Dynamic triangle

→ scratchpad reference background

### `practice_scratchpad_background` asset

→ scratchpad background

### 一般 question media / textbook asset

→ 依 payload contract 保持既有 renderer

禁止：

- 不要因 triangle 改動，把所有 static images 一律搬到 scratchpad。
- 不要因 static image，把 triangle 搬回 question card。

## 5. Scratchpad layering

reference layer 與 drawing layer 分離。

reference diagram/image：

- 不受 undo 影響
- 不受 redo 影響
- 不受 clear handwriting 影響
- 換題時 reference state 必須 reset
- 新 reference 載入後不得再次被同一換題流程 reset

triangle sizing 已驗證：

- desktop: 約 <=300px / <=32%
- narrow/mobile: 約 <=240px / <=45%

不要再為 B2 重調尺寸，除非有可重現 regression。

## 6. Practice authentication contract

`/get_next_question` 等 authenticated practice API：

- 登入合法使用者 → 200 JSON
- 匿名 → 401 JSON

不要回 302 login HTML，再讓 frontend 把它當 JSON parse。

不要移除 login protection。

practice page permission 與 question API permission 不得互相矛盾。

## 7. Session contract

practice session 必須 bounded。

已驗證真實 Chrome session：

- iteration 1 = 3246 bytes
- iteration 10 = 3332 bytes
- iteration 20 = 3258 bytes
- iteration 30 = 3288 bytes
- observed max = 3351 bytes

目前沒有持續成長。recent question history 等 session state 必須維持 bounded。

不要因目前數值而進行 server-side session 大重構。只有實際重現 cookie overflow 才重新處理。

## 8. B2 acceptance baseline

Runtime audit：

- 21 B2 skills
- 420 generated samples
- 0 generation failures
- 34 single/multiple-choice samples，全部 exactly 4 choices
- 171 short-answer samples，全部沒有 choices
- 20 dynamic diagrams
- 24 static images
- 376 no-image

Browser / submission：

- B2 2.1.2: 20 questions PASS
- B2 2.2.4: 20 questions PASS
- correct single-choice submit PASS
- wrong single-choice submit PASS
- correct expression submit PASS
- wrong expression submit PASS
- algebraically equivalent answer PASS
- triangle handwriting / undo / redo / clear PASS
- static scratchpad image PASS
- no-image PASS
- authenticated network responses PASS
- browser console no relevant exception

Final regression：78 passed，0 failed。

Commit：`8a0809c40fe904c7bc156c4b7125ca1d5408eb3d`

Message：`fix: harden B2 practice choices and diagram rendering`

## 9. Known coverage exception

保留：

- diagram → no diagram
- no diagram → diagram

狀態：component test PASS；browser not naturally reachable in current B2 production sequence。

這不是目前已知 product bug。

禁止為補 browser coverage 而：

- 插假題
- 改 production sequence
- 修改 generator
- 建立 production-only testing branch

只有未來 production sequence 真正可達時，才補 browser acceptance。

已在 browser 通過的相鄰情境是：有圖→有圖、無圖→無圖。

## 10. Rules for future chapter imports

新增下一章節 / B3 / B4 時，不要重新發明 practice contract。

新 generator 必須直接符合：

- vocational MCQ = 4 choices
- existing answer contract
- existing practice API contract
- existing scratchpad/image routing
- existing validators

新章節導入重點應放在：

- curriculum mapping
- component/problem_type
- domain functions
- generator correctness
- chapter-specific diagrams
- chapter-specific validators

不要重新修改已穩定的 B2 practice runtime，除非新章節揭露真正的共用 regression。


## 11. Visual Asset Acceptance Contract

適用：textbook PDF visual enrichment（`enrich_textbook_examples_with_pdf_visuals` / `notes.image_assets` / student practice image attach）。

### Core rule

**Asset existence is not sufficient evidence of visual correctness.**

下列任一成立，**不得**把 mapping 靜默當成 student-ready accepted：

- PNG 檔存在 / 可讀
- `bbox` 欄位存在
- `has_image=True` 曾被寫入

Low-confidence 或結構上可疑的 PDF visual mapping，必須標成 review / rejected，不可當 accepted student asset。

### Acceptance states

沿用既有 `notes` / `image_assets` 欄位，不平行發明第二套 schema：

| Field | Meaning |
|---|---|
| `image_assets[].visual_status` | `accepted` \| `needs_review` \| `rejected` |
| `image_assets[].visual_review_reasons` | 結構原因列表 |
| `notes.visual_status` / `notes.needs_image_review` | 題級 gate（與 asset 對齊） |

Legacy assets 若缺少 `visual_status`，為相容視為 accepted（不得倒過來把舊圖整批藏掉）。

### Deterministic gates（production；禁止 example_id / chapter hardcode）

1. **Question boundary** — crop 不可實質跨越下一題 authoritative anchor；search band 不可無界向下擴張進頁尾。
2. **Shared asset ownership** — 不可只因 same bbox / same SHA / nearby visual 就跨題 reuse。需有近乎相同 figure stem 等證據（合法例：例/隨堂同幹）。可疑共用 → `suspicious_shared_asset` → needs_review。
3. **Multi-figure completeness** — 題幹含「圖（一）/圖（二）」等時，不可在只掛單一子圖時標為完整 accepted。
4. **Contamination** — crop 與 PDF text-layer 明顯重疊「熟習度自評 / 輸入訊息 / 解」等非本題區域 → reject 或 needs_review。
5. **Prefer review over guess** — 系統不確定時，允許 `needs_review`；禁止 `wrong mapping + accepted`。

### Student runtime

`list_student_image_assets_from_notes` 只暴露 accepted student-ready assets；`needs_review` / `rejected` 不得進入學生作答畫面。

### Implementation anchors

- `core/textbook_pdf_visual_acceptance.py`
- `core/textbook_pdf_visual.py`（classify / enrich gate）
- `core/question_image_assets.py`（student list gate）
- regression：`tests/test_b2_ch3_visual_pipeline_hardening.py`
- Ch1 vs Ch3 診斷：`reports/b2_visual_pipeline_ch1_vs_ch3.md`
