# B2 P1：纜車題欄位標籤／空白提交／AI 數學誤判

日期：2026-11-22  
Skill：`vh_數學B2_TrigonometricFunctionsOfAcuteAngles`（TE 11584）

## 1. 三項 Root Cause

### A. 答案欄位顯示 `elevation`／`小題2`
- 11584 的 `b2_12` calls 未提供 `_out(..., label=...)`，組裝時用內部 key 當 label。
- `elevation` 無底線，humanize 未視為 internal → 直接外洩。
- `horizontal_projection` 被 humanize 成「小題 2」。
- Adaptive 前端用 `part.label || part.key`，未優先 `display_label`。

正式 Checker 本身數學判定正確；此為 **display metadata** 問題。

### B. 空白文字框出現「部分小題答錯」
產品契約：
- **送出答案** → 只讀文字欄（`collectCurrentAnswer`）→ `/check_answer`
- **AI 檢查** → 白板 OCR → `/api/practice/ai-check-handwriting` → 再以辨識結果呼叫 `/check_answer`；錯了才進 `/analyze_handwriting`

空白 multipart 各 part `reason=missing_part`，卻仍顯示「部分小題答錯」，讓人以為手寫已被正式判錯。

### C. AI 對 `450√2` 要求重算
正式 Checker：**PASS**（`450√2` ≡ `450*sqrt(2)`；`500+450√2` ≡ `500+450*sqrt(2)`）。

真正問題：
1. OCR 無 `(1)(2)` 標記時（例如 `a; b` 或兩行），multipart 正規化失敗 → `/check_answer` FAIL。
2. Tutor 端 `_handwriting_expected_answer` 對 dict 用 `str(dict)`，最後一行無法與 `450√2` 等價比對 → 誤判需重算。

## 2. 欄位修復結果

顯示改為：
- `(1) B 站海拔（公尺）`
- `(2) 兩站水平距離（公尺）`

keys 仍為 `elevation` / `horizontal_projection`（Checker 契約不變）。

## 3. 文字提交 vs 手寫流程（現行）

| 動作 | 讀取 | 正式紀錄 | 說明 |
|---|---|---|---|
| 送出答案 | 文字欄 | 是（可計 mastery） | 空白 →「尚未填寫…」並提示改按 AI 檢查 |
| AI 檢查 | 白板影像 | OCR 後經 `/check_answer`；vision／tutor 會 mark assisted | 不另建平行判分；以權威 Checker 為準 |

## 4. AI 數學誤判修復證據

- OCR：`500+450√2; 450√2` 與換行兩行可映射並 DET PASS
- `_handwriting_multipart_oracle_match` → True
- structured analysis `status=correct` / `multipart_oracle_checker`
- expected 顯示為標籤化多行，不再是 `str(dict)`

## 5. 回歸

- `scripts/test_b2_p1_cable_labels_ai.py` → **ALL_PASS**
- `scripts/test_b2_ch1_type_mastery_pilot.py` → **10/10 PASS**
- Checker good／unicode／wrong／blank／partial：PASS

## 6. 瀏覽器驗收

Flask 5001 已受控重啟以載入新碼。  
完整真人手寫 Canvas 流程：**NOT_TESTED**（需登入後實際書寫；自動化僅覆蓋 OCR 正規化與 Checker／analysis oracle）。

## 7. SOP 增補

- `docs/AI_TUTOR_CONVERSATION_CONTRACT.md`：multipart OCR 映射、禁止 `str(dict)` expected、vision／tutor 計 assisted。

未 commit／push；未動 5000／Cloudflare；未清學生紀錄。
