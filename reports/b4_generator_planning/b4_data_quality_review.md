# B4 Phase 1.5 資料品質檢查報告

## 1. 檢查目的

本階段只做資料品質盤點，不修資料、不拆 subskill、不定義 problem_type。主要目的在於篩選出可以直接進入 Phase 2（拆解 subskill）的乾淨技能，並標記需要人工介入的異常題目。

## 2. 無題目 skill 清單

| skill_id | skill_ch_name | chapter | section | 建議處理方式 |
| --- | --- | --- | --- | --- |
| vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | 3 統計 | 3-1 統計的基本概念 | 需補教材題目 |


## 3. needs_review 高風險 skill 清單

| skill_id | skill_ch_name | total_question_count | needs_review_count | needs_review_ratio | 風險說明 |
| --- | --- | --- | --- | --- | --- |
| vh_數學B4_MultiplicationPrinciple | 乘法原理 | 10 | 4 | 40.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_PermutationOfDistinctObjects | 相異物的排列 | 18 | 10 | 55.6% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 6 | 3 | 50.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_Combination | 組合 | 7 | 7 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | 3 | 3 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_BinomialTheorem | 二項式定理 | 12 | 5 | 41.7% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_BasicConceptsOfSets | 集合的基本概念 | 10 | 5 | 50.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_SampleSpaceAndEvents | 樣本空間與事件 | 13 | 7 | 53.8% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_ConditionalProbability | 條件機率 | 5 | 3 | 60.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_IndependentEvents | 獨立事件 | 4 | 3 | 75.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_ProbabilityDefinition | 機率的定義 | 15 | 4 | 26.7% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_ProbabilityOperations | 機率的運算 | 9 | 9 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_ProbabilityProperties | 機率的性質 | 7 | 5 | 71.4% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_MathematicalExpectation | 數學期望值 | 5 | 5 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_SamplingMethods | 抽樣方法 | 15 | 7 | 46.7% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 5 | 4 | 80.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 4 | 3 | 75.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 4 | 4 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3 | 3 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | 11 | 4 | 36.4% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_DispersionMeasures | 離散趨勢量數 | 5 | 3 | 60.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 8 | 8 | 100.0% | 大量題目標記為需人工審閱，可能含有非標準描述 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | 6 | 4 | 66.7% | 大量題目標記為需人工審閱，可能含有非標準描述 |


## 4. formula_missing 題目清單

| skill_id | skill_ch_name | example_id | source_type | source_description | problem_text 摘要 | answer 摘要 | 建議處理方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| vh_數學B4_ProbabilityDefinition | 機率的定義 | 3713 | textbook_example | 例題 5 [source_type=textbook_example | needs_review=true | dedupe=7f0361ee8cb142f2] | 例5 熱舞社含甲、乙等共有10人，今從中任選3人參加比賽。假... | 1/15 | 回看原始教材 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 3854 | basic_exercise | 3-3習題 基礎題 7 [source_type=basic_exercise | needs_review=true | dedupe=c12c187b88d48af4] | 已知一組資料的算術平均數為 5，標準差為 4，試求下列各組資... | 略 | 回看原始教材 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 3855 | exam_practice | 113統測B [source_type=exam_practice | needs_review=true | dedupe=4c5fafa164909d3f] | 某公司全體員工隔年月薪皆增加 5000 元。已知調薪前平均為... | A (依線性變換原理) | 回看原始教材 |


## 5. answer 空白或 answer 為「略」的題目

| skill_id | skill_ch_name | example_id | source_type | source_description | problem_text 摘要 | answer | 風險說明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 3613 | in_class_practice | 隨堂練習7 [source_type=in_class_practice | linked_example=例題7 | needs_review=true | dedupe=720be6dedd7bd1e8] | 右圖為一棋盤式街道圖，現有一人由 A 出發走到 B 或 C ... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_IndependentEvents | 獨立事件 | 3738 | exam_practice | 110統測A [source_type=exam_practice | needs_review=true | dedupe=d95acecbdad928e6] | 已知下表為小楓跟小道兩人在多場比賽中的戰績紀錄。若投球命中率... | 需依表格數據計算 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_SamplingSurvey | 抽樣調查 | 3788 | textbook_practice | 動動手 [source_type=textbook_practice | needs_review=true | dedupe=69116360dd3ddaa7] | 在下列各題中，請連結正確的母群體與樣本。 (1)學生會想訪問... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3831 | in_class_practice | 隨堂練習 3 [source_type=in_class_practice | linked_example=例題 3 | dedupe=031bf22e466b2711] | 試完成下方之累積次數分配表（數據略）。 | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3832 | in_class_practice | 隨堂練習 5 [source_type=in_class_practice | linked_example=例題 5 | dedupe=6df8d4d4d487c615 | needs_review=true] | 已知某班英文期末考成績的以上累積次數分配折線圖如右，試問：(... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3833 | basic_exercise | 3-2習題 基礎題6 [source_type=basic_exercise | needs_review=true | dedupe=79915e5a9b25b556] | 已知某班國文期中考成績的以下累積次數分配折線圖如右，試問：(... | 需視圖表數據而定 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | 3821 | exam_practice | 108統測A [source_type=exam_practice | needs_review=true | dedupe=9f8f532fb7697508] | 國內自某年至某年藥妝零售業每年銷售額如長條圖，而其中某年藥妝... |  | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 3823 | in_class_practice | 隨堂練習 1 [source_type=in_class_practice | linked_example=例題 1 | dedupe=32dc663de4a51e55 | needs_review=true] | 會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3827 | in_class_practice | 隨堂練習 2 [source_type=in_class_practice | linked_example=例題 2 | dedupe=b800ed2bf57ee0ae | needs_review=true] | 會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3828 | basic_exercise | 3-2習題 基礎題3 [source_type=basic_exercise | dedupe=6de5a52f28b234b6 | needs_review=true] | 某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3884 | self_assessment | 自我評量 5 [source_type=self_assessment | needs_review=true | dedupe=ea1b9ba056e5dd6e] | 某班英文段考成績的以上累積次數分配折線圖如右，試問：以60分... |  | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3885 | self_assessment | 自我評量 6 [source_type=self_assessment | needs_review=true | dedupe=56e07a5d86d9c2fb] | 接續上題，成績在70～80分有多少人？ (A) 20 (B)... |  | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3886 | self_assessment | 自我評量 7 [source_type=self_assessment | needs_review=true | dedupe=3cb786f0c54798b7] | 依某公司40名員工的年齡繪製以下累積次數分配折線圖如右所示，... |  | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_DispersionMeasures | 離散趨勢量數 | 3847 | basic_exercise | 3-3習題 基礎題 4 [source_type=basic_exercise | dedupe=985c61666147771d] | 某籃球隊身高：(1)女生：182, 175, 175, 18... | 略 | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 3894 | self_assessment | 自我評量 15 [source_type=self_assessment | needs_review=true | dedupe=6668f703d75ed95e] | 若將75，65，58，80，72每個數都乘以後再加9，則所得... |  | 缺乏標準答案，無法供 generator 驗證 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 3854 | basic_exercise | 3-3習題 基礎題 7 [source_type=basic_exercise | needs_review=true | dedupe=c12c187b88d48af4] | 已知一組資料的算術平均數為 5，標準差為 4，試求下列各組資... | 略 | 缺乏標準答案，無法供 generator 驗證 |


## 6. 圖片 / 表格 / 圖表依賴題目

| skill_id | skill_ch_name | example_id | source_type | source_description | 命中的關鍵字 | problem_text 摘要 | 建議處理方式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| vh_數學B4_AdditionPrinciple | 加法原理 | 3619 | in_class_practice | 隨堂練習2 [source_type=in_class_practice | linked_example=例題2 | dedupe=75c04f8d280c75a6] | 表 | 某校游泳校隊是由6位高一學生、5位高二學生及4位高三學生所組... | 暫不進入自動 generator |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 3611 | textbook_example | 例題7 [source_type=textbook_example | dedupe=23cc5d81e8df42c9] | 附圖 | 附圖擷取高雄市五福路到三多路間的街道圖（4x3 棋盤格），若... | 暫不進入自動 generator |
| vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | 3613 | in_class_practice | 隨堂練習7 [source_type=in_class_practice | linked_example=例題7 | needs_review=true | dedupe=720be6dedd7bd1e8] | 右圖 | 右圖為一棋盤式街道圖，現有一人由 A 出發走到 B 或 C ... | 暫不進入自動 generator |
| vh_數學B4_CombinationApplications | 組合的應用 | 3650 | textbook_example | 例題5 [source_type=textbook_example | dedupe=2cabbe3280d2f22c] | 右圖 | 右圖為一正六邊形，試求下列各題： (1) 請問正六邊形的對角... | 暫不進入自動 generator |
| vh_數學B4_IndependentEvents | 獨立事件 | 3738 | exam_practice | 110統測A [source_type=exam_practice | needs_review=true | dedupe=d95acecbdad928e6] | 表 | 已知下表為小楓跟小道兩人在多場比賽中的戰績紀錄。若投球命中率... | 暫不進入自動 generator |
| vh_數學B4_ProbabilityDefinition | 機率的定義 | 3711 | textbook_example | 例題 3 [source_type=textbook_example | needs_review=true | dedupe=8d68161697a77abd] | 表 | 同樂會班上分甲、乙兩隊，每隊派一代表同時擲兩顆公正骰子一次，... | 暫不進入自動 generator |
| vh_數學B4_SamplingMethods | 抽樣方法 | 3790 | textbook_example | 例題1 [source_type=textbook_example | dedupe=f018debd88c4b894] | 表 | 下列分別是採用何種抽樣方法？ (1)某校舉辦愛心園遊會，主辦... | 暫不進入自動 generator |
| vh_數學B4_SamplingMethods | 抽樣方法 | 3791 | in_class_practice | 隨堂練習1 [source_type=in_class_practice | linked_example=例題1 | dedupe=b141a5e711bcebb2] | 表 | 下列抽樣的方法，分別是採用何種抽樣方法？ (1)電視歌唱節目... | 暫不進入自動 generator |
| vh_數學B4_SamplingMethods | 抽樣方法 | 3795 | basic_exercise | 3-1習題 基礎題4 [source_type=basic_exercise | dedupe=f7ffb165475cf01b] | 表 | 全校一年級共10個班，編班方式為常態分班，若隨機抽取一個班級... | 暫不進入自動 generator |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3830 | textbook_example | 例題 5 [source_type=textbook_example | dedupe=8fd34466d74dd9ed | needs_review=true] | 折線圖, 圖片, 累積次數, 圖片待補 | 已知某班數學期中考成績的以下累積次數分配折線圖如下，試問：(... | 暫不進入自動 generator |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3831 | in_class_practice | 隨堂練習 3 [source_type=in_class_practice | linked_example=例題 3 | dedupe=031bf22e466b2711] | 累積次數, 表 | 試完成下方之累積次數分配表（數據略）。 | 暫不進入自動 generator |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3832 | in_class_practice | 隨堂練習 5 [source_type=in_class_practice | linked_example=例題 5 | dedupe=6df8d4d4d487c615 | needs_review=true] | 折線圖, 圖片, 累積次數, 圖片待補 | 已知某班英文期末考成績的以上累積次數分配折線圖如右，試問：(... | 暫不進入自動 generator |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3833 | basic_exercise | 3-2習題 基礎題6 [source_type=basic_exercise | needs_review=true | dedupe=79915e5a9b25b556] | 折線圖, 圖片, 累積次數, 圖片待補 | 已知某班國文期中考成績的以下累積次數分配折線圖如右，試問：(... | 暫不進入自動 generator |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3834 | basic_exercise | 3-2習題 基礎題10 [source_type=basic_exercise | needs_review=true | dedupe=769d172a50bfe0d7] | 圖片, 累積次數, 圖片待補, 表 | 某班有40位同學，第一次期中考數學成績的次數分配表及以下累積... | 暫不進入自動 generator |
| vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | 3821 | exam_practice | 108統測A [source_type=exam_practice | needs_review=true | dedupe=9f8f532fb7697508] | 圖片待補, 圓形圖, 長條圖, 表, 圖表, 圖片 | 國內自某年至某年藥妝零售業每年銷售額如長條圖，而其中某年藥妝... | 暫不進入自動 generator |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 3822 | textbook_example | 例題 1 [source_type=textbook_example | dedupe=decb313265e7104d | needs_review=true] | 圖片, 圖片待補, 表 | 國貿科三年甲班40人英文模擬考成績資料如下：32、38、41... | 暫不進入自動 generator |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 3823 | in_class_practice | 隨堂練習 1 [source_type=in_class_practice | linked_example=例題 1 | dedupe=32dc663de4a51e55 | needs_review=true] | 圖片, 圖片待補, 表 | 會計科三年甲班45人數學模擬考成績資料如下（略），試將此班依... | 暫不進入自動 generator |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 3825 | basic_exercise | 3-2習題 基礎題2 [source_type=basic_exercise | dedupe=75ae10f958ff45a0 | needs_review=true] | 圖片, 圖片待補, 表 | 某公司企劃部員工20人，年齡資料如下：25、26、27、28... | 暫不進入自動 generator |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3826 | textbook_example | 例題 2 [source_type=textbook_example | dedupe=43a9b4f7c2e16bd6 | needs_review=true] | 折線圖, 圖片待補, 表, 直方圖, 圖片 | 國貿科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的... | 暫不進入自動 generator |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3827 | in_class_practice | 隨堂練習 2 [source_type=in_class_practice | linked_example=例題 2 | dedupe=b800ed2bf57ee0ae | needs_review=true] | 折線圖, 圖片待補, 表, 直方圖, 圖片 | 會計科三年甲班模擬考某科成績的次數分配表如下，試畫出其對應的... | 暫不進入自動 generator |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3828 | basic_exercise | 3-2習題 基礎題3 [source_type=basic_exercise | dedupe=6de5a52f28b234b6 | needs_review=true] | 折線圖, 圖片待補, 表, 直方圖, 圖片 | 某女中二年八班同學的體重次數分配表如下，試畫出其對應的直方圖... | 暫不進入自動 generator |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 3829 | advanced_exercise | 3-2習題 進階題9 [source_type=advanced_exercise | dedupe=9107dd03efcf2853 | needs_review=true] | 圖片, 直方圖, 圖片待補 | 某幼兒園班上25位小朋友身高分布之直方圖如右。今班上轉出一位... | 暫不進入自動 generator |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3884 | self_assessment | 自我評量 5 [source_type=self_assessment | needs_review=true | dedupe=ea1b9ba056e5dd6e] | 折線圖, 圖片, 累積次數 | 某班英文段考成績的以上累積次數分配折線圖如右，試問：以60分... | 暫不進入自動 generator |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3885 | self_assessment | 自我評量 6 [source_type=self_assessment | needs_review=true | dedupe=56e07a5d86d9c2fb] | 圖片, 累積次數 | 接續上題，成績在70～80分有多少人？ (A) 20 (B)... | 暫不進入自動 generator |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 3886 | self_assessment | 自我評量 7 [source_type=self_assessment | needs_review=true | dedupe=3cb786f0c54798b7] | 折線圖, 圖片, 累積次數 | 依某公司40名員工的年齡繪製以下累積次數分配折線圖如右所示，... | 暫不進入自動 generator |
| vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | 3890 | self_assessment | 自我評量 11 [source_type=self_assessment | needs_review=true | dedupe=f070c2107ebc9330] | 表 | 某生各科的測驗成績與相應的上課時數如下表。若以上課時數為權數... | 暫不進入自動 generator |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | 3859 | advanced_exercise | 3-3習題 進階題 9 [source_type=advanced_exercise | needs_review=true | dedupe=48237cd59cf88ead] | 直方圖 | 某年統測，甲、乙兩科成績直方圖如圖所示，下列敘述何者正確？(... | 暫不進入自動 generator |


## 7. Phase 2 暫緩 skill 建議清單

| skill_id | skill_ch_name | 暫緩原因 | 後續處理建議 |
| --- | --- | --- | --- |
| vh_數學B4_ProbabilityDefinition | 機率的定義 | formula_missing_count > 0 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_SamplingMethods | 抽樣方法 | formula_missing_count > 0 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_SamplingSurvey | 抽樣調查 | answer 空白或略的題目比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | total_question_count = 0 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 圖片/圖表依賴比例高、answer 空白或略的題目比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | 圖片/圖表依賴比例高、answer 空白或略的題目比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 圖片/圖表依賴比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 圖片/圖表依賴比例高、answer 空白或略的題目比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 圖片/圖表依賴比例高、answer 空白或略的題目比例高 | 需人工介入補充資料或視為純概念節點 |
| vh_數學B4_LinearTransformationOfData | 資料的線性變換 | formula_missing_count > 0 | 需人工介入補充資料或視為純概念節點 |


## 8. Phase 2 可優先處理 skill 建議清單

| skill_id | skill_ch_name | chapter | section | 理由 |
| --- | --- | --- | --- | --- |
| vh_數學B4_FactorialNotation | 階乘記法 | 1 排列組合 | 1-1 加法原理與乘法原理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_MultiplicationPrinciple | 乘法原理 | 1 排列組合 | 1-1 加法原理與乘法原理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_TreeDiagramCounting | 樹狀圖 | 1 排列組合 | 1-1 加法原理與乘法原理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_PermutationOfDistinctObjects | 相異物的排列 | 1 排列組合 | 1-2 直線排列 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_PermutationWithRepetition | 重複排列 | 1 排列組合 | 1-3 重複排列 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_RepeatedPermutation | 重複排列 | 1 排列組合 | 1-3 重複排列 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_Combination | 組合 | 1 排列組合 | 1-4 組合 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_CombinationApplications | 組合的應用 | 1 排列組合 | 1-4 組合 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_CombinationDefinition | 組合的定義與計算 | 1 排列組合 | 1-4 組合 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_CombinationProperties | 組合的性質 | 1 排列組合 | 1-4 組合 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | 1 排列組合 | 1-5 二項式定理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_BinomialTheorem | 二項式定理 | 1 排列組合 | 1-5 二項式定理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_PascalTriangle | 巴斯卡三角形 | 1 排列組合 | 1-5 二項式定理 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_BasicConceptsOfSets | 集合的基本概念 | 2 機率 | 2-1 樣本空間與事件 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_SampleSpaceAndEvents | 樣本空間與事件 | 2 機率 | 2-1 樣本空間與事件 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_ConditionalProbability | 條件機率 | 2 機率 | 2-2 機率的運算 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_ProbabilityOperations | 機率的運算 | 2 機率 | 2-2 機率的運算 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_ProbabilityProperties | 機率的性質 | 2 機率 | 2-2 機率的運算 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_ApplicationsOfExpectation | 數學期望值的應用 | 2 機率 | 2-3 數學期望值 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_MathematicalExpectation | 數學期望值 | 2 機率 | 2-3 數學期望值 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_MathematicalExpectationDefinition | 數學期望值的定義與計算 | 2 機率 | 2-3 數學期望值 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | 3 統計 | 3-3 統計量分析 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | 3 統計 | 3-3 統計量分析 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_OpinionPollInterpretation | 民意調查的解讀 | 3 統計 | 3-3 統計量分析 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_VarianceAndStandardDeviation | 變異數與標準差 | 3 統計 | 3-3 統計量分析 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |
| vh_數學B4_WeightedMean | 加權平均數 | 3 統計 | 3-3 統計量分析 | total_question_count > 0, formula_missing_count = 0, answer 大多完整, 圖片依賴少 |


## 9. Phase 1.5 結論

整體而言，B4 資料中約有 26 個 skill 資料相對乾淨，具備足夠的題目且無圖表依賴，可優先進入 Phase 2 拆解 subskill。
需注意有 3 題出現公式遺失，以及 27 題高度依賴圖表或表格，這部分涉及的 10 個 skill 應暫緩自動出題設計，
建議先行人工回看教材以補齊圖片、公式或視為僅作概念節點。
目前 B4 資料初步整理後，足以讓無問題的 skill 進行後續的拆解工作，為 generator 建立打好基礎。
