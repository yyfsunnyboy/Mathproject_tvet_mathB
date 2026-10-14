# B2 2-1 scoped import final dry-run

唯讀 dry-run。`target_source_types` 為 opt-in 四類；`allow_phase4=False`。未寫入 production DB。

- 來源：`textbook_import/source/vocational/math_B2/第二章 2-1 正弦定理與餘弦定理-課本.docx`
- 工作複本與 `_Latex.docx` 寫在暫存目錄，不覆蓋原始教材
- 詳細 JSON：`reports/b2_2_1_scoped_import_dryrun.json`

## Target question summary

| source_type | count |
|---|---:|
| textbook_example | 5 |
| in_class_practice | 5 |
| self_assessment | 0 |
| exam_practice | 1 |
| **target total** | **11** |
| textbook_exercise | 8 |
| advanced_exercise | 2 |
| **non-target total** | **10** |
| parser question blocks | 21 |

這份課本 DOCX 沒有自我評量；自我評量通常是獨立來源。

## Formula summary

整份 DOCX：MathType OLE 185 全部轉換成功；Word EQ 5 全部成功。

Scoped gate 只看 target 題塊：

| 項目 | 值 |
|---|---:|
| required_formula_count | 73 |
| required_formula_success | 73 |
| required_formula_failed | 0 |
| non_required_formula_count | 117 |
| non_required_formula_failed | 0 |
| unresolved_formula_scope_count | 0 |

73 是目前這份教材 + Phase 2 parser 題塊範圍的自然結果，不是硬編碼。例 2 含解答續表，該題 `formula_count = 13`。

整份文件公式失敗不會阻擋 scoped import；required 失敗才會 FAIL。本次 required / unresolved 皆為 0。

## Image summary

Target 題塊獨立圖片候選：5。MathType preview / WMF / EMF 已排除。5 張皆 `needs_review=True`。

| # | label | paragraph | filename | 備註 |
|---:|---|---:|---|---|
| 1 | 例1 | 23 | image25.jpeg | 例1 題塊內 |
| 3 | 例2 | 62 | image59.jpeg | 落在例2 span（含解答續表），需人工核圖 |
| 5 | 例3 | 78 | image78.jpeg | 落在例3 span（含解答），需人工核圖 |
| 7 | 例4 | 122 | image117.jpeg | 落在例4 span（含解答），需人工核圖 |
| 11 | 113統測B | 142 | image138.jpeg | 統測題塊起始段 |

與更早的結構盤點相比，關聯題塊有變化：目前 parser 把隨堂練習 4/5 收成單一段落，因此舊盤點裡「隨堂練習 5 標題段」那張圖不再掛在該練習上。本輪不改 image pipeline，只保留 candidate metadata 與 `needs_review`。

## WOULD_WRITE

| 狀態 | 數量 |
|---|---:|
| YES | 11 |
| BLOCKED_FORMULA | 0 |
| NO | 10 |

| # | source_type | label | section | preview | formulas | images | WOULD_WRITE |
|---:|---|---|---|---|---:|---:|---|
| 1 | textbook_example | 例1 | 2-1 | 在△ABC中，已知 \(\overline{AB}=4\)、\(\overline{AC}=\sqrt{3}\) 且 | 9 | 1 | YES |
| 2 | in_class_practice | 隨堂練習1 | 2-1 | 在△ABC中，已知 \(a=2\sqrt{3}\)、\(b=6\) 且 \(\angle C=30^\circ\) | 3 | 0 | YES |
| 3 | textbook_example | 例2 | 2-1 | 在△ABC中，若 \(\angle A=45^\circ\)，\(\angle B=60^\circ\)，且 \(b=3\sqrt{6}\) | 13 | 1 | YES |
| 4 | in_class_practice | 隨堂練習2 | 2-1 | 在△ABC中，若 \(\angle B=30^\circ\)，\(\angle C=120^\circ\)，且 \(b=6\) | 3 | 0 | YES |
| 5 | textbook_example | 例3 | 2-1 | △ABC中，已知 \(\angle A=60^\circ\)，\(a=6\)，\(b=2\sqrt{6}\) | 13 | 1 | YES |
| 6 | in_class_practice | 隨堂練習3 | 2-1 | △ABC中，已知 \(a=2\sqrt{3}\)，\(b=2\sqrt{2}\)，\(\angle A=60^\circ\) | 4 | 0 | YES |
| 7 | textbook_example | 例4 | 2-1 | 在△ABC中，已知 \(b=5\)、\(c=3\) 且 \(\angle A=120^\circ\) | 11 | 1 | YES |
| 8 | in_class_practice | 隨堂練習4 | 2-1 | 在△ABC中，已知 \(b=1+\sqrt{3}\)、\(c=2\) 且 \(\angle A=30^\circ\) | 3 | 0 | YES |
| 9 | textbook_example | 例5 | 2-1 | 設△ABC的三邊長 \(a=7\)、\(b=5\)、\(c=3\) | 8 | 0 | YES |
| 10 | in_class_practice | 隨堂練習5 | 2-1 | 設△ABC的三邊長 \(a=3\)、\(b=8\)、\(c=7\) | 4 | 0 | YES |
| 11 | exam_practice | 113統測B | 2-1 | 小仲規劃從A地直線出發到C地… | 2 | 1 | YES |
| 12 | textbook_exercise | 2-1習題 基礎題 1 | 2-1 | 設 \(\Delta\) 表示△ABC的面積… | 16 | 0 | NO |
| 13 | textbook_exercise | 2-1習題 基礎題 2 | 2-1 | 在△ABC中，已知 \(b=6\)、\(c=4\) 且 \(\angle A=60^\circ\) | 3 | 0 | NO |
| 14 | textbook_exercise | 2-1習題 基礎題 3 | 2-1 | 在△ABC中，已知 \(b=8\sqrt{2}\)、\(\angle A=45^\circ\) | 3 | 0 | NO |
| 15 | textbook_exercise | 2-1習題 基礎題 4 | 2-1 | 在△ABC中，已知 \(a=4\)、\(b=2\sqrt{6}\) | 4 | 0 | NO |
| 16 | textbook_exercise | 2-1習題 基礎題 5 | 2-1 | 在△ABC中，若 \(a=2\)、\(b=\sqrt{2}\) | 4 | 0 | NO |
| 17 | textbook_exercise | 2-1習題 基礎題 6 | 2-1 | 設△ABC的三邊長 \(a=7\)、\(b=8\)、\(c=5\) | 4 | 0 | NO |
| 18 | textbook_exercise | 2-1習題 基礎題 7 | 2-1 | 設△ABC的三邊長 \(a=\sqrt{3}\)、\(b=2\sqrt{3}\)、\(c=3\) | 4 | 0 | NO |
| 19 | textbook_exercise | 2-1習題 基礎題 8 | 2-1 | 設△ABC中，a、b、c為三邊長，若 \(a^2-(b+c)^2=-bc\) | 3 | 0 | NO |
| 20 | advanced_exercise | 2-1習題 進階題 9 | 2-1 | 如圖，國外某一湖泊… | 3 | 0 | NO |
| 21 | advanced_exercise | 2-1習題 進階題 10 | 2-1 | 歐洲某大城市…Wi-Fi 基地臺 | 3 | 0 | NO |

## Anomalies

- scoped pre-scan 的 `skill_id` 為 null：唯讀模式不做 skill lookup / persistence，屬預期。
- 正式匯入前，例 2 / 例 3 / 例 4 解答段圖片仍需人工確認是否為題目必要圖。
- 舊盤點曾寫 67 個 target formulas；parser 納入例 2 解答續表後為 73。本次仍為 73，未硬修。
- 現存教材旁若有舊 `_Latex.docx` 帶 `[MATH_PARSE_FAILED_*]`，那是舊轉換產物。本次 application interpreter 對原始 DOCX 為 185/185 成功。

## DB side-effect check

Production `instance/kumon_math.db`：

| 項目 | before | after |
|---|---|---|
| SHA-256 | `07e2e66b880719dd318054e38215b47e432d143adac945e6914895b07e632deb` | 相同 |
| skills_info | 539 | 539 |
| skill_curriculum | 548 | 548 |
| textbook_examples | 4329 | 4329 |
| 全部 table names + row counts | 一致 | 一致 |

**NO CHANGE**

Pipeline 在 scoped + `allow_phase4=False` 於 FORMULA_CONVERSION 後早退，不進 CURRICULUM_BINDING / Phase 2 persist / DB_WRITE。

## Runtime

- `sys.executable`: `C:\Users\Owner\anaconda3\python.exe`
- olefile: `C:\Users\Owner\anaconda3\Lib\site-packages\olefile\__init__.py`
- converter: `core/textbook_mathtype_converter.py`（in-process，無 subprocess、未硬寫 `python`/`python3`）
