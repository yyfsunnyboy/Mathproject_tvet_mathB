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

### 3.1 Vector-valued keyboard input

When the expected answer is **vector-valued** (directed segment, basis /
symbolic vector expression, or `answer_shape` in
`{directed_segment, vector_expression, ...}`), shared answer normalization
must accept unambiguous keyboard-friendly forms before grading:

- Directed segment: `BC`, `->BC`, `BC->`, `vec(BC)`, `\vec{BC}`,
  `\overrightarrow{BC}` all normalize to the same segment; direction matters
  (`BC` ≠ `CB`).
- Symbolic vectors: `a`, `a+b`, `2a-b`, `(1/2)a+b` and equivalent parseable
  forms are accepted; students must not be required to type `\vec{a}+\vec{b}`.

Do **not** globally treat every two-letter token or letter symbol as a vector.
Coercion is gated by expected-answer / schema context. Scalar and ordinary
algebra answers stay on the generic math path.

Invalid input may mention hints such as「可直接輸入 BC 表示向量 BC」;
semantically valid keyboard forms must **PASS**, not return「答案格式不正確」.

## 3.2 Directed-segment drawing answers

For construction-style questions where a directed vector drawing is a valid
answer (`drawing_check.enabled` / `answer_shape: directed_segment_drawing`),
structured geometric checking is preferred over generic AI interpretation:

- expected endpoints come from the canonical directed-segment answer
- student strokes are compared to authoritative visual labeled points
- AI may be used only as a fallback for ambiguous drawings (optional)

Keyboard-equivalent answers (e.g. `AC` for `\overrightarrow{AC}`) remain
available via §3.1 and must not be removed.

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

## 9.1 Textbook exercise coverage（GenCode requirement）

Textbook exercise coverage is a GenCode requirement.

Formal source questions include examples, in-class practice,
exercises, basic/advanced problems, self-assessment,
and past examination questions.

An intentional skip may be used as a temporary engineering disposition,
but does not count as completed chapter coverage.

Coverage must preserve the source problem's core reasoning topology,
not merely its broad mathematical topic.

因此：

- 例題／隨堂／習作／基礎／進階／自我評量／歷屆考題皆進入 coverage matrix
- `diagram` / `MCQ` / `application` / `composite` / `past exam` 不得因工程困難永久 `intentional_skip`
- 多題可共用同一 generator family，但每題 `source_example_id` 必須可追溯到 faithful family／capability／coverage evidence
- 章節狀態僅在 `covered == total_source` 且 `blocked == 0` 時可標 CLOSED；否則為 PARTIAL

## 9.2 Student-runtime production readiness（beyond source coverage）

Source coverage alone does not constitute production readiness.

A published GenCode family must be genuinely parameterized for repeated
student practice:

- Same explicit seed → reproducible same question
- Different explicit seeds → parameterized meaningful variation
- Normal student next-question → new production generation state
  (must not replay a fixed seed, cached payload, or fixed-template instance)
- Runtime `problem_type` coverage ≠ type_rotation health; a usable Y does not prove
  students can reach unmastered types or see parameter change
- Distinct `question_uid` alone is **not** diversity evidence — compare stem
  parameters / math signature
- Diagram-backed items: stem numbers, `visual_spec`/asset labels, oracle and
  checker must stay synchronized; PDF crops with baked-in numbers must not be
  reused when parameters change

For MCQ, choices, answer mapping and checker behavior are part of the
student runtime contract. Choice text containing TeX must remain MathJax-
delimited through serialization; vocational MCQ remains exactly 4 choices.
Do not convert MCQ families to text input to bypass UI contract issues.

For multi-part questions, every input must have explicit student-visible
meaning (`display_label` / `label`). Internal keys (`k1`, `alpha`, `sin`,
`cos`, `tan`, `sum`, `elevation`, …) may exist in the payload but must not
be the only student-facing label. Component assembly must not overwrite an
already-humanized Domain/Adapter `display_label` with the raw key; trig
ratio fields that ask for angle θ must show complete meaning such as
`$\sin\theta$` / `sinθ`, not bare `sin`. Frontend label resolution prefers
`display_label` → `math_label` → `label` → `prompt`.

For vector-valued free-response answers, keyboard-friendly notation is part
of the student runtime contract (see §3.1): directed-segment and symbolic
vector oracles must accept practical typed forms without requiring LaTeX.

For diagram-backed GenCode, coverage requires semantic and pedagogical
fidelity between:

- problem stem
- parameters
- visual payload
- input contract
- answer

A renderable diagram alone does not constitute coverage.
Generated diagrams should expose the minimum sufficient mathematical
structure and must not dump unrelated generator geometry.

### 9.3 Student-facing inline math typography

Student-facing inline math inside the same semantic surface (problem stem,
MCQ choices, multipart labels, correct-answer feedback) must use **one**
consistent rendering/typography contract:

- Canonical practice-page renderer: MathJax 3 SVG (`tex-svg`)
- Shared surface wrapper: `.practice-math-surface`
- Shared styles: `static/css/practice_math_typography.css`
- One base typography scale (`font-size: 100%` on inline `mjx-container`)
- Baseline owned by MathJax inline `vertical-align` — do **not** force
  `vertical-align: middle !important` on practice math containers
- Do not mix incompatible inline render paths in one stem
  (e.g. MathJax + KaTeX + raw styled spans) unless intentionally
  normalized under this contract

Generated content may not expose renderer-specific differences in font
scale or baseline to students. This is a shared practice invariant for
B2 / B3 / B4 — not a chapter exception.

Student-facing **compound / nested fractions** in stems (e.g. trig expressions
with squared terms in both numerator and denominator) must ship as delimited
stacked TeX (`\frac` / `\displaystyle\frac`), not ASCII slash prose such as
`(1-sin²(π/4))/(1+sin²(π/4))`. Do not convert every `/` globally; prefer
fixing the generator stem (or a shared display formatter) for the specific
math atom.

### 9.4 Multipart subquestion structure

For multipart questions, **subquestion structure is semantic data** and must
be preserved from generation through student rendering.

- Prefer the shared `stem_structure` contract:
  `{ "prompt": "...", "items": [ { "group_label": "(1)", "text": "..." }, ... ] }`
- `problem_text` / `question_text` may be generated for compatibility, but
  must **not** be the only source of truth for multipart boundaries.
- Formatting / whitespace alone must not be the sole representation of
  subquestion boundaries (MathJax adjacency can erase bare `(2)` / `(3)`
  markers that live between inline math spans).
- Each answer field must expose both:
  - subquestion identity (`group_label`, e.g. `(1)`)
  - answer meaning (`display_label`, e.g. `圓心` / `圖形` / `C1 關係`)
  when needed for student comprehension.
- Do not reconstruct item boundaries from flattened text with digit regex
  when structured items already exist.


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
-（若該冊採用題型掌握制）§12 的掌握／導航契約，不得另建平行晉級系統

不要重新修改已穩定的 B2 practice runtime，除非新章節揭露真正的共用 regression。
B2～B4 **尚未**自動改用 §12 題型掌握制；擴冊前須逐冊驗收，不得默認複製 B1 晉級規則。


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
6. **Separate Skill placement from visual pairing** — 題幹／圖不符時，必須先分開判定「題型是否掛錯 Skill／problem_type」與「PDF crop／asset 是否錯配或跨題 residual」。不得只換圖而保留錯誤 Registry；也不得把不同數學概念硬塞進同一 `problem_type_id`。

### Student runtime

`list_student_image_assets_from_notes` 只暴露 accepted student-ready assets；`needs_review` / `rejected` 不得進入學生作答畫面。

### Implementation anchors

- `core/textbook_pdf_visual_acceptance.py`
- `core/textbook_pdf_visual.py`（classify / enrich gate）
- `core/question_image_assets.py`（student list gate）
- regression：`tests/test_b2_ch3_visual_pipeline_hardening.py`
- Ch1 vs Ch3 診斷：`reports/b2_visual_pipeline_ch1_vs_ch3.md`


## 12. B1 Generator problem-type mastery & learning navigation（2026-11-22）

本節記錄 **技高數學 B1** 已由程式與自動化測試驗證的學生練習晉級契約。  
證據報告（不得把 NOT_TESTED 寫成已驗收）：

- `reports/gencode_closed_loop/B1_ProblemType_Mastery_改造報告.md`
- `reports/gencode_closed_loop/B1_SkillCompletion_MsgBox_報告.md`
- `reports/gencode_closed_loop/B1_Completion_SameChapter_Navigation_報告.md`
- `reports/gencode_closed_loop/B1_Nav_SkipCompleted_ChapterEncourage_報告.md`
- 自動化：略過／補缺 14/14、結構導航 13/13、完成旗標 16/16 PASS  
- **仍待人工**：真人瀏覽器／iPad 互動驗收

實作錨點：`core/practice_type_mastery.py`、`core/gencode/services/generator_problem_type_inventory.py`、`student_problem_type_mastery`、`templates/index.html`（完成 MsgBox）。

### 12.1 Textbook Generator coverage

- 每一道教材例題應有符合原始數學結構的 Generator；相同題型可共用 Generator family／component。
- 覆蓋須保真題幹推理拓樸（見 §9.1）；不得只覆蓋寬泛主題。
- Outline／習題來源類型不得自動建成 Skill；空殼／inactive Skill 不得當學生過關目標。

### 12.2 Problem-type counting（X/Y 的 Y）

- Y＝該 Skill **Runtime 實際可用**、去重後的 `problem_type_id` 數（`usable_problem_type_ids`）。
- **禁止**用教材例題數、Generator Python 檔案數、component 檔案數、V3 eligible 來源數或舊「連續答對門檻」冒充 Y。
- 相同 `problem_type_id` 的多個 component 只算一種題型。
- 學生端不可選用的題型不得計入目前過關分母。

### 12.3 Mastery rule（X/Y 的 X）

- 學生在正常練習中，對某一 `problem_type_id` **獨立答對**一次 → 該題型 `MASTERED`。
- Multipart：必須整題 `overall_correct`（所有 parts 皆正確）才算該次答對；部分小題正確不得提前 MASTERED。有序多值 part（如 `a、b` 之值）的友善輸入格式見數學答案檢核原則「有序多值答案」。
- 學生端顯示「已掌握題型 X/Y」；數字必須來自後端真實進度。
- 答錯：記錄錯誤；**不清除**其他已掌握題型；不要求全 Skill 重來。
- AI 提示／分步／看過解答後的答對 **不算** MASTERED；須以**新的同型變化題**再獨立答對。
- **手寫**：自行手寫＋首次 AI 檢查辨識全對＋正式 `/check_answer` 通過 → 與 Textbox 獨立答對相同，可 MASTERED。純 OCR／AI 檢查不 mark assisted；`/chat_ai` 或 `/analyze_handwriting` 助教提示／診斷後同題改對則不算。
- 同一題型重複答對不重複累加 X；不得只憑同一題型答對 Y 次就判定 Skill 完成。
- Y＝0 不得自動晉級；顯示「暫無可練習題型」。

### 12.4 Persistence

- 權威表：`student_problem_type_mastery`（per user × skill × problem_type）。
- 不得把舊 `Progress.consecutive_correct` 直接換算成 MASTERED。
- 題型新增：舊掌握保留，新題型待完成；題型下線：歷史保留，但不再計入目前 Y。
- 不同學生進度必須隔離。

### 12.5 Skill-complete MsgBox

- 僅當本次作答使 Skill 由未完成→完成，且 DB commit 成功（`skill_just_completed`）才顯示。
- 重整頁面、重複提交、已完成 Skill 重練 → **不**重複彈出。
- **不自動跳轉**；學生按主按鈕後才導航；次要按鈕「留在目前技能／留在本章」。

### 12.6 Learning navigation（Curriculum order）

正式順序來源：`skill_curriculum`＋`get_chapters_by_curriculum_volume`／`chapter_natural_sort_key`；章內 `section → display_order`（與章複習一致）。不得用 Skill ID 字母序或檔案時間。

完成目前 Skill 後，對**該生**查找下一目標：

1. 同章、目前之後的第一個**未完成**可練習 Skill →「繼續挑戰：{技能名}」
2. 後面都完成 → 同章前面未完成補缺（`same_chapter_backfill`）
3. 同章適用 Skill 皆完成 → 章節完成鼓勵；主按鈕「前往下一章」
4. 後續章節亦略過已完成，找第一個未完成
5. 本冊適用 Skill 皆完成 → 本冊完成鼓勵；「返回學習儀表板」

自動推薦須排除：inactive、Outline、無 Runtime 可用題型之空殼、學生端不可練習者（例如 NumberLine inactive、SubSection332 空殼）。不可把它們假設為已掌握，也不可因此永久卡關。

### 12.7 Free review of completed skills

- 允許學生主動進入已完成 Skill 繼續出題作答。
- 保留已掌握 X/Y；答錯不撤銷既有 MASTERED（錯題仍可進錯題本）。
- 不再次觸發首次完成鼓勵；可提供「前往下一個未完成技能」操作。
- 不得強制學生離開已完成 Skill；暫時離開未完成 Skill 亦不把跳過當成完成。

### 12.8 Scope & non-goals

- §12 預設範圍：**B1 full**。B3／B4 維持既有連對／Skill 卡語意，未經逐冊驗收不得默認套用。
- **B2 試點 allowlist（`B2_TYPE_MASTERY_PILOT_SKILL_IDS`）**：
  - 第1章具名：8 個 Skill。
  - 第1章 A 類練習 SubSection（教師 2026-11-22 核准）：`1_3_1`、`1_3_2`、`1_3_4`～`1_3_7`、`1_4_3`、`1_4_4`（皆有 TE＋facade＋Y≥1）。掌握紀錄仍按 `(user, skill, problem_type)`；跨 Skill 共用同一 `problem_type_id` 不自動計入、亦不把舊連對換算成 MASTERED。
  - 第2章：5 個具 Runtime 可用題型的練習 SubSection（`2_1_1`、`2_1_2`、`2_2_3`、`2_2_4`、`2_2_5`）；第2章無另立具名 Skill。`2_2_1`／`2_2_2` inactive 組織節點不納入。
  - 第3章：15 個練習 SubSection（`3_1_1`～`3_1_4`、`3_2_1`～`3_2_6`、`3_3_1`～`3_3_5`；皆 TE＋facade＋Y≥1，2026-11-23 品質抽樣通過）；第3章無另立具名 Skill。
  - 第4章：6 個練習 SubSection（`4_1_1`、`4_1_2`、`4_2_1`～`4_2_4`；皆 TE＋facade＋Y≥1，2026-11-23 導入）；第4章無另立具名 Skill。Vocational MCQ 須保證四選一完整可見（長方程式優先單欄，避免 2×2 裁切 B/D）。
  - 其餘 B2（inactive／空殼）仍用連對語意。
- **Allowlist 變更後**：學生端 Flask（含 5001）須載入新版 `practice_type_mastery.py` 才會切換 X/Y；僅跑隔離腳本 PASS 不能代替 live 頁面驗收。變更後若頁面仍顯示「連續答對／暫無門檻」，先確認進程是否已重載 allowlist。
- 試點不得把 `Progress.consecutive_correct` 換算成 `student_problem_type_mastery` MASTERED。
- `vh_數學B2_SubSection_1_4_1`／`1_4_2`：無 TE／facade／可用題型的空殼，治理上應 inactive，不得當學生過關目標，亦不得納入掌握制 allowlist。
- 不新增排行榜、扣分、懲罰或強迫連對機制。
- 不平行發明第二套晉級系統；變更應落在本契約與既有 GenCode V3 Lean／Specification／PipelineFlow。
