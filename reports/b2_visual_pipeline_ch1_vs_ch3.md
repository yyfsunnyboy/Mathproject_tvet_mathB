# B2 Visual Pipeline — Ch1 Success vs Ch3 FAIL-11

## Verdict

Ch1「能工作」與 Ch3「出現 11 個錯圖」**不是單一原因**。三者同時存在，但主因排序為：

1. **A. Orchestration gap（主因之一）** — Ch1 以 audited / manual `MOUNT_PLAN` 為正式掛載路徑；scoped import **刻意跳過**自動 `PDF_VISUAL`；Ch3 依賴自動 `enrich_textbook_examples_with_pdf_visuals` heuristic 直接寫入 student-ready assets。
2. **B. Algorithm gap（主因之一）** — 同一套 classify / right-cluster / band-expand / union 在 Ch3 向量圖密集排版下選錯 candidate 或跨題 union。
3. **C. Validation gap（決定性放大）** — 只要 PNG 存在 + `notes.image_assets` 寫入 + `has_image=True`，就被當成成功；**沒有 acceptance gate**，錯圖會靜默進入學生端。

> 結論：Ch1 成功 ≠ algorithm 已正確；而是 **人工/審計掛載 + 跳過自動掛載** 避開了 heuristic 風險。Ch3 把同一 heuristic 當正式路徑，又缺少 gate，才出現 FAIL-11。

---

## Stage comparison

| Stage | Ch1 | Ch3 | Same? | Evidence |
|---|---|---|---|---|
| scoped import | section scoped；`allow_phase4` 路徑下 **PDF_VISUAL skipped**（`scoped image candidates require review`） | 同樣 scoped skip；之後另跑 backfill enrich | Partial | `textbook_importer_v3_pipeline.py` `elif scoped: … stage=PDF_VISUAL skipped` |
| PDF_VISUAL handling | 不依賴 pipeline 自動 mount | backfill 呼叫 `enrich_textbook_examples_with_pdf_visuals` | No | Ch3 backfill session vs Ch1 `scripts/pdf_visual_mount_b2_1_1.py` |
| enrich call | 少數；多數 `match_method=audited_B2_1-*_pdf_sha256` / `ordered_figure_cue` | 幾乎全自動 `unique_phrase+order` / `shared_phrase+order`（修復前） | No | DB provenance：Ch1 audited\*；Ch3 unique/shared_phrase |
| question anchor | 人工 plan 對頁碼/題號 | PDF text-layer phrase match | Partial | Ch3 LaTeX `overline` 曾需 `normalize_query_text` 才能 match |
| candidate visual selection | MOUNT_PLAN 指定 bbox | soft/right-cluster / area-rank | No | FAIL-11：11732 航線圖、11795 輸入 UI |
| right-cluster | 人工裁切 | `cx>=0.45w` bonus + band 向下擴張 | No | `classify_and_detect_visuals` 原 `rb[3]+200/280/320` |
| region/band construction | N/A（plan） | `assign_question_regions` 至下一題；但 search band 可越界 | No | 11753 進自評表；11732 `next_y=None` 長帶 |
| bbox compacting | 人工含標籤 | compact score 偏好過緊 | Partial | 11751 / 11817 切標籤 |
| shared asset/dedupe | 審計允許的共用 | 僅因同 bbox/相近視覺就 reuse | No | 11748≠11749、11751≠11752；對照合法 11741/11742 |
| notes.image_assets write | audited mount → student-ready | enrich 成功即 `has_image=True`, `needs_image_review=False` | Same bug class | `upsert_notes_image_asset`（硬化前） |
| post-import mount/enrich | **正式路徑是 mount script** | **正式路徑變成 auto enrich** | No | `pdf_visual_mount_b2_1_1.py` vs Ch3 enrich backfill |
| QA / acceptance gate | 人工 contact sheet / audited SHA | 僅「檔案可讀」；無 wrong-mapping gate | No | `qa_manual.json` FAIL 11；硬化前無 `visual_status` |

---

## A / B / C（不可混談）

### A. Orchestration gap

- Ch1：scoped import **不自動掛圖**；成功資產來自 **audited mount plan**。
- Ch3：在自動 enrich backfill 後把 heuristic 結果直接當 production student assets。
- 這解釋「為什麼 Ch1 看起來 pipeline OK」——其實成功的不是同一條 orchestration。

### B. Algorithm gap

兩章若都跑同一 `classify_and_detect_visuals`，Ch3 layout 仍會觸發：

| Pattern | Examples | First wrong decision |
|---|---|---|
| F1 wrong nearby visual | 11732, 11795 | candidate selection / soft-right pick |
| F2 multi-question crop | 11736, 11744, 11806 | union / tall band / right-cluster merge |
| F3 invalid shared asset | 11748, 11751/11752 | ownership / dedupe without stem evidence |
| F4 label clipping | 11751, 11817 | over-compact bbox |
| F5 incomplete multi-figure | 11804 | single subfigure accepted |
| F6 contamination | 11753, 11795 | band into 自評表 / UI |

### C. Validation gap

- 硬化前：`asset exists ∧ PNG readable ∧ bbox exists` ⇒ 視為成功。
- 沒有 `visual_status` / `visual_review_reasons`，錯圖不會被擋在 student-ready 之外。
- 這是 FAIL-11 能進 runtime 的最後一哩。

---

## What hardening changes (this round)

- Production guards（layout/ownership/boundary/confidence；**無** `example_id` / `chapter` hardcode）
- `notes` / asset 層 `visual_status` + `visual_review_reasons`
- Student list 跳過 `needs_review` / `rejected`
- Dry-run 目標：`wrong_accepted = 0`（寧可 review，不要猜）
