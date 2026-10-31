# 單元06 古典機率人工驗收

3+2+8+4 把跨技能共用的 3 個 family 各算了兩次。去重後是 14。Problem Type 與 Domain Operation 在這份矩陣裡是同一個名稱，也是 14。

題目 42、Generator 元件 42、去重 Family 14、Domain Operation 14。跨技能各算一次時 family 成員數是 17。

共用 family：numbered_dice、urn_without_replacement、with_replacement

## 教師須確認

下列項目答案可判，作答形式或模型需要教師點頭。瀏覽器上的 MathJax 尚未驗證，不視為 Runtime PASS。

- 數字編碼：硬幣與出生順序用 0/1 整數，抽取結果用十進位碼，不是文字列舉。
- 相同骰子：題幹與詳解都把骰子編號。12871 是 216 個樣本點、有利 75 個、機率 75/216＝25/72。
- 放回與不放回：12864 依序不放回是 6/20，同時取出是 3/10，約分後相同。12852 三種抽法分開計數。
- 機率 0：12885 第三小題是 0，Checker 接受 0 與 0.0。
- 整數答案：12884 所求是黑球顆數 10，不是機率。

## 42 題清單

| ID | 教材 | Skill | Family | 作答 | 標準答案 | Checker |
|---:|---|---|---|---|---|---|
| 12849 | 例題1 | `gh_SampleSpace` | `coin_sequence_space` | multi_part / multiple_inputs | part_1={0, 1, 2, 3}；part_2=4；part_3={0, 1, 2}；part_4=3 | PASS |
| 12850 | 例題2 | `gh_SampleSpace` | `draw_sample_space` | multi_part / multiple_inputs | part_1={12, 13, 14, 21, 23, 24, 31, 32, 34, 41, 42, 43}；part_2=12；part_3={12, 13, 14, 23, 24, 34}；part_4=6 | PASS |
| 12851 | 隨堂練習1 | `gh_SampleSpace` | `coin_sequence_space` | multi_part / multiple_inputs | part_1={0, 1, 2, 3, 4, 5, 6, 7}；part_2=8；part_3={0, 1, 2, 3}；part_4=4 | PASS |
| 12852 | 隨堂練習2 | `gh_SampleSpace` | `draw_sample_space` | multi_part / multiple_inputs | part_1={123, 132, 213, 231, 312, 321}；part_2=6；part_3={11, 12, 13, 21, 22, 23, 31, 32, 33}；part_4=9；part_5={12, 13, 23}；part_6=3 | PASS |
| 12853 | 6習題 基礎題1 | `gh_SampleSpace` | `coded_named_events` | multi_part / multiple_inputs | part_1={0, 1, 2, 3}；part_2={0, 1, 2}；part_3={1, 2} | PASS |
| 12854 | 6習題 基礎題2 | `gh_SampleSpace` | `coded_named_events` | multi_part / multiple_inputs | part_1={1, 4, 5}；part_2={0}；part_3={2, 3, 6, 7} | PASS |
| 12855 | 例題3 | `gh_Event` | `two_dice_event_sets` | multi_part / multiple_inputs | part_1={46, 55, 56, 64, 65, 66}；part_2={11, 22, 33, 44, 55, 66}；part_3={55, 66}；part_4={11, 22, 33, 44, 46, 55, 56, 64, 65, 66} | PASS |
| 12856 | 例題4 | `gh_Event` | `event_complement_mutex` | multi_part / multiple_inputs | part_1={0, 3}；part_2=A；part_3=A | PASS |
| 12857 | 隨堂練習3 | `gh_Event` | `two_dice_event_sets` | multi_part / multiple_inputs | part_1={16, 25, 34, 43, 52, 61}；part_2={26, 34, 43, 62}；part_3={34, 43}；part_4={16, 25, 26, 34, 43, 52, 61, 62} | PASS |
| 12858 | 隨堂練習4 | `gh_Event` | `event_complement_mutex` | multi_part / multiple_inputs | part_1={0}；part_2=B；part_3=A | PASS |
| 12859 | 6習題 基礎題3 | `gh_Event` | `event_complement_mutex` | single_choice / single_choice | B | PASS |
| 12860 | 例題5 | `gh_DefinitionOfClassicalProbability` | `single_draw` | multi_part / multiple_inputs | part_1=1/6；part_2=1/2 | PASS |
| 12861 | 例題6 | `gh_DefinitionOfClassicalProbability` | `coin_count` | multi_part / multiple_inputs | part_1=1/2；part_2=3/8 | PASS |
| 12862 | 例題7 | `gh_DefinitionOfClassicalProbability` | `coin_count` | rational / short_answer | 1/2 | PASS |
| 12863 | 例題8 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=1/9；part_2=1/6 | PASS |
| 12864 | 例題9 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | multi_part / multiple_inputs | part_1=3/10；part_2=3/10 | PASS |
| 12865 | 例題10 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=5/9；part_2=5/12 | PASS |
| 12866 | 隨堂練習5 | `gh_DefinitionOfClassicalProbability` | `single_draw` | multi_part / multiple_inputs | part_1=1/13；part_2=1/4 | PASS |
| 12867 | 隨堂練習6 | `gh_DefinitionOfClassicalProbability` | `with_replacement` | multi_part / multiple_inputs | part_1=5/9；part_2=2/9 | PASS |
| 12868 | 隨堂練習7 | `gh_DefinitionOfClassicalProbability` | `coin_count` | multi_part / multiple_inputs | part_1=1/8；part_2=3/8 | PASS |
| 12869 | 隨堂練習8 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=5/18；part_2=5/18 | PASS |
| 12870 | 隨堂練習9 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | multi_part / multiple_inputs | part_1=3/5；part_2=3/5 | PASS |
| 12871 | 隨堂練習10 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | rational / short_answer | 25/72 | PASS |
| 12872 | 6習題 觀念澄清1 | `gh_DefinitionOfClassicalProbability` | `classical_claim` | single_choice / single_choice | B | PASS |
| 12873 | 6習題 觀念澄清2 | `gh_DefinitionOfClassicalProbability` | `classical_claim` | single_choice / single_choice | B | PASS |
| 12874 | 6習題 觀念澄清3 | `gh_DefinitionOfClassicalProbability` | `classical_claim` | single_choice / single_choice | A | PASS |
| 12875 | 6習題 基礎題4 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=1/6；part_2=5/12 | PASS |
| 12876 | 6習題 基礎題5 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=1/4；part_2=1/6 | PASS |
| 12877 | 6習題 基礎題6 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | multi_part / multiple_inputs | part_1=9/20；part_2=9/10 | PASS |
| 12878 | 6習題 基礎題7 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | multi_part / multiple_inputs | part_1=3/5；part_2=4/5 | PASS |
| 12879 | 6習題 基礎題8 | `gh_DefinitionOfClassicalProbability` | `single_draw` | rational / short_answer | 2/3 | PASS |
| 12880 | 6習題 基礎題9 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | rational / short_answer | 119/190 | PASS |
| 12881 | 6習題 進階題10 | `gh_DefinitionOfClassicalProbability` | `numbered_dice` | multi_part / multiple_inputs | part_1=91/216；part_2=25/216 | PASS |
| 12882 | 6習題 進階題11 | `gh_DefinitionOfClassicalProbability` | `urn_without_replacement` | rational / short_answer | 3/7 | PASS |
| 12883 | 6習題 進階題12 | `gh_DefinitionOfClassicalProbability` | `password_permutation` | multi_part / multiple_inputs | part_1=1/24；part_2=7/8 | PASS |
| 12884 | 6習題 進階題13 | `gh_DefinitionOfClassicalProbability` | `solve_composition` | rational / short_answer | 10 | PASS |
| 12885 | 例題11 | `gh_PropertiesOfProbability` | `probability_algebra` | multi_part / multiple_inputs | part_1=2/3；part_2=2/3；part_3=0 | PASS |
| 12886 | 例題12 | `gh_PropertiesOfProbability` | `urn_without_replacement` | rational / short_answer | 2/3 | PASS |
| 12887 | 例題13 | `gh_PropertiesOfProbability` | `numbered_dice` | rational / short_answer | 4/9 | PASS |
| 12888 | 隨堂練習11 | `gh_PropertiesOfProbability` | `probability_algebra` | multi_part / multiple_inputs | part_1=4/5；part_2=5/6 | PASS |
| 12889 | 隨堂練習12 | `gh_PropertiesOfProbability` | `urn_without_replacement` | rational / short_answer | 4/5 | PASS |
| 12890 | 隨堂練習13 | `gh_PropertiesOfProbability` | `with_replacement` | rational / short_answer | 13/18 | PASS |

## 代表題（每個 Family 的教材參數，以及另一個抽樣）

### 12849 `coin_sequence_space`

- Skill：`gh_SampleSpace`
- Problem Type / Domain Operation：`coin_outcome_space`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_4 等價寫法 3.0：接受
- MathJax 括號：成對

擲一枚公正硬幣 2 次，依序觀察正反面。正面記為 $1$、反面記為 $0$，並把這 2 次的結果寫成整數，最先擲出的是最高位。
(1) 寫出全部樣本點組成的集合。
(2) 求這個樣本空間的樣本點個數。
(3) 若改為只記錄正面出現的次數，寫出此時的樣本空間。
(4) 求上一小題的樣本點個數。

標準答案：part_1={0, 1, 2, 3}；part_2=4；part_3={0, 1, 2}；part_4=3

解題：
- (1) 依序記錄 2 次，樣本點對應 0 到 3，共 4 個，且彼此等可能。
- (2) 樣本點個數為 2^2 = 4。
- (3) 這個觀察所能出現的值組成另一個樣本空間。
- (4) 此樣本空間有 3 個樣本點。

請人工確認：樣本點編成整數：正面為 1、反面為 0，最先擲出的是最高位。學生寫的是編碼後的集合，不是「正正、正反」四個詞。

另一個抽樣：

擲一枚公正硬幣 3 次，依序觀察正反面。正面記為 $1$、反面記為 $0$，並把這 3 次的結果寫成整數，最先擲出的是最高位。
(1) 寫出全部樣本點組成的集合。
(2) 求這個樣本空間的樣本點個數。
(3) 若改為只記錄正面出現的次數，寫出此時的樣本空間。
(4) 求上一小題的樣本點個數。

標準答案：part_1={0, 1, 2, 3, 4, 5, 6, 7}；part_2=8；part_3={0, 1, 2, 3}；part_4=4

### 12850 `draw_sample_space`

- Skill：`gh_SampleSpace`
- Problem Type / Domain Operation：`draw_outcome_space`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_4 等價寫法 6.0：接受
- MathJax 括號：成對

袋中有標號 $1$、$2$、$3$、$4$ 的球各一顆，每球被取出的機會均等。
(1) 依序取 2 次、每次取出後不放回。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(2) 求這個樣本空間的樣本點個數。
(3) 同時取 2 個，不計順序。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(4) 求這個樣本空間的樣本點個數。

標準答案：part_1={12, 13, 14, 21, 23, 24, 31, 32, 34, 41, 42, 43}；part_2=12；part_3={12, 13, 14, 23, 24, 34}；part_4=6

解題：
- (1) 依序取 2 次、每次取出後不放回的樣本點寫成十進位碼，共 12 個。
- (2) 個數為 12，與樣本點集合的大小相同。
- (3) 同時取 2 個，不計順序的樣本點寫成十進位碼，共 6 個。
- (4) 個數為 6，與樣本點集合的大小相同。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

袋中有標號 $2$、$5$、$7$、$8$ 的球各一顆，每球被取出的機會均等。
(1) 依序取 3 次、每次取出後不放回。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(2) 求這個樣本空間的樣本點個數。
(3) 同時取 2 個，不計順序。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(4) 求這個樣本空間的樣本點個數。

標準答案：part_1={257, 258, 275, 278, 285, 287, 527, 528, 572, 578, 582, 587, 725, 728, 752, 758, 782, 785, 825, 827, 852, 857, 872, 875}；part_2=24；part_3={25, 27, 28, 57, 58, 78}；part_4=6

### 12852 `draw_sample_space`

- Skill：`gh_SampleSpace`
- Problem Type / Domain Operation：`draw_outcome_space`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_6 等價寫法 3.0：接受
- MathJax 括號：成對

袋中有標號 $1$、$2$、$3$ 的球各一顆，每球被取出的機會均等。
(1) 依序取 3 次、每次取出後不放回。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(2) 求這個樣本空間的樣本點個數。
(3) 取後放回，依序取 2 次。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(4) 求這個樣本空間的樣本點個數。
(5) 同時取 2 個，不計順序。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(6) 求這個樣本空間的樣本點個數。

標準答案：part_1={123, 132, 213, 231, 312, 321}；part_2=6；part_3={11, 12, 13, 21, 22, 23, 31, 32, 33}；part_4=9；part_5={12, 13, 23}；part_6=3

解題：
- (1) 依序取 3 次、每次取出後不放回的樣本點寫成十進位碼，共 6 個。
- (2) 個數為 6，與樣本點集合的大小相同。
- (3) 取後放回，依序取 2 次的樣本點寫成十進位碼，共 9 個。
- (4) 個數為 9，與樣本點集合的大小相同。
- (5) 同時取 2 個，不計順序的樣本點寫成十進位碼，共 3 個。
- (6) 個數為 3，與樣本點集合的大小相同。

請人工確認：三種抽法都編成十進位碼。要確認題幹把不放回、放回、不計順序分開，學生不會把三種樣本空間混成一種。

另一個抽樣：

袋中有標號 $1$、$3$、$6$ 的球各一顆，每球被取出的機會均等。
(1) 依序取 3 次、每次取出後不放回。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(2) 求這個樣本空間的樣本點個數。
(3) 取後放回，依序取 2 次。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(4) 求這個樣本空間的樣本點個數。
(5) 同時取 2 個，不計順序。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。
(6) 求這個樣本空間的樣本點個數。

標準答案：part_1={136, 163, 316, 361, 613, 631}；part_2=6；part_3={11, 13, 16, 31, 33, 36, 61, 63, 66}；part_4=9；part_5={13, 16, 36}；part_6=3

### 12853 `coded_named_events`

- Skill：`gh_SampleSpace`
- Problem Type / Domain Operation：`coded_event_sets`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_3 等價寫法 {2, 1}：接受
- MathJax 括號：成對

一個家庭有 2 個小孩，以出生順序區別，每個小孩是男生或女生的機會均等。男生記為 $1$、女生記為 $0$，較早出生的是最高位。
(1) 寫出「全部樣本點」的樣本點集合。
(2) 寫出「至少有 1 個女生」的樣本點集合。
(3) 寫出「恰有 1 個女生」的樣本點集合。

標準答案：part_1={0, 1, 2, 3}；part_2={0, 1, 2}；part_3={1, 2}

解題：
- (1) 符合條件的樣本點有 4 個。
- (2) 符合條件的樣本點有 3 個。
- (3) 符合條件的樣本點有 2 個。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

一個家庭有 3 個小孩，以出生順序區別，每個小孩是男生或女生的機會均等。男生記為 $1$、女生記為 $0$，較早出生的是最高位。
(1) 寫出「全部樣本點」的樣本點集合。
(2) 寫出「至少有 1 個女生」的樣本點集合。
(3) 寫出「恰有 1 個女生」的樣本點集合。

標準答案：part_1={0, 1, 2, 3, 4, 5, 6, 7}；part_2={0, 1, 2, 3, 4, 5, 6}；part_3={3, 5, 6}

### 12855 `two_dice_event_sets`

- Skill：`gh_Event`
- Problem Type / Domain Operation：`dice_event_sets`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_4 等價寫法 {66, 65, 64, 56, 55, 46, 44, 33, 22, 11}：接受
- MathJax 括號：成對

同時擲兩粒公正骰子，將兩粒編號區別。把結果寫成兩位數，十位是第一粒的點數、個位是第二粒的點數。設 A 為「點數和大於 $9$」，B 為「兩粒點數相同」。
(1) 寫出 A 的樣本點集合。
(2) 寫出 B 的樣本點集合。
(3) 寫出 A∩B 的樣本點集合。
(4) 寫出 A∪B 的樣本點集合。

標準答案：part_1={46, 55, 56, 64, 65, 66}；part_2={11, 22, 33, 44, 55, 66}；part_3={55, 66}；part_4={11, 22, 33, 44, 46, 55, 56, 64, 65, 66}

解題：
- (1) 事件 A 有 6 個樣本點。
- (2) 事件 B 有 6 個樣本點。
- (3) A∩B 有 2 個樣本點。
- (4) A∪B 有 10 個樣本點。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

同時擲兩粒公正骰子，將兩粒編號區別。把結果寫成兩位數，十位是第一粒的點數、個位是第二粒的點數。設 A 為「兩粒點數都大於 $2$」，B 為「點數和大於 $9$」。
(1) 寫出 A 的樣本點集合。
(2) 寫出 B 的樣本點集合。
(3) 寫出 A∩B 的樣本點集合。
(4) 寫出 A∪B 的樣本點集合。

標準答案：part_1={33, 34, 35, 36, 43, 44, 45, 46, 53, 54, 55, 56, 63, 64, 65, 66}；part_2={46, 55, 56, 64, 65, 66}；part_3={46, 55, 56, 64, 65, 66}；part_4={33, 34, 35, 36, 43, 44, 45, 46, 53, 54, 55, 56, 63, 64, 65, 66}

### 12856 `event_complement_mutex`

- Skill：`gh_Event`
- Problem Type / Domain Operation：`event_relation`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_1 等價寫法 {3, 0}：接受
- MathJax 括號：成對

擲一枚公正硬幣 2 次，正面記為 $1$、反面記為 $0$，最先擲出的是最高位。設 A 為「恰有 1 個正面」，B 為「恰有 0 個正面」。
(1) 寫出 A 的補事件 A' 的樣本點集合。
(2) A 與 B 是否互斥？選擇「是」或「否」。
(3) A 與 A' 是否互斥？選擇「是」或「否」。

標準答案：part_1={0, 3}；part_2=A；part_3=A

解題：
- (1) A' 有 2 個樣本點。
- (2) A 與 B 互斥表示沒有共同樣本點。
- (3) A 與 A' 沒有共同樣本點。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

擲一枚公正硬幣 3 次，正面記為 $1$、反面記為 $0$，最先擲出的是最高位。設 A 為「至少有 1 個正面」，B 為「恰有 1 個正面」。
(1) 寫出 A 的補事件 A' 的樣本點集合。
(2) A 與 B 是否互斥？選擇「是」或「否」。
(3) A 與 A' 是否互斥？選擇「是」或「否」。

標準答案：part_1={0}；part_2=B；part_3=A

### 12859 `event_complement_mutex`

- Skill：`gh_Event`
- Problem Type / Domain Operation：`event_relation`
- 作答：single_choice，single_choice，checker `choice_label_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

同時擲兩粒公正骰子，將兩粒編號區別。設 A 為「第一粒是偶數」，B 為「點數和是奇數」。A 與 B 是否互斥？

標準答案：B

解題：
- 兩事件互斥表示交集是空集合。

請人工確認：互斥以 A＝是、B＝否作答。第一粒是偶數且點數和是奇數可以同時發生，所以答案是 B。

另一個抽樣：

同時擲兩粒公正骰子，將兩粒編號區別。設 A 為「第一粒是偶數」，B 為「第一粒是奇數」。A 與 B 是否互斥？

標準答案：A

### 12860 `single_draw`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`uniform_draw_probability`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_2 等價寫法 0.5：接受
- MathJax 括號：成對

擲一粒公正骰子一次，6 面的點數為 1 到 6，每面等可能。求下列機率。
(1) 出現 $6$ 點的機率。
(2) 點數屬於 $2$、$3$、$5$ 的機率。

標準答案：part_1=1/6；part_2=1/2

解題：
- (1) 每一個結果等可能，機率為 1/6。
- (2) 每一個結果等可能，機率為 1/2。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

擲一粒公正骰子一次，6 面的點數為 1 到 6，每面等可能。求下列機率。
(1) 出現 $5$ 點的機率。
(2) 點數屬於 $2$、$3$、$4$、$6$ 的機率。

標準答案：part_1=1/6；part_2=2/3

### 12861 `coin_count`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`coin_count_probability`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_1 等價寫法 0.5：接受
- MathJax 括號：成對

公正硬幣可區別每次的結果（正面與反面等可能）。求下列事件的機率。
(1) 擲 2 次，恰有 1 個正面的機率。
(2) 擲 3 次，恰有 2 個正面的機率。

標準答案：part_1=1/2；part_2=3/8

解題：
- (1) 恰有 1 個正面的序列有 C(2,1) = 2 種，全部 4 種，機率 1/2。
- (2) 恰有 2 個正面的序列有 C(3,2) = 3 種，全部 8 種，機率 3/8。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

公正硬幣可區別每次的結果（正面與反面等可能）。求下列事件的機率。
(1) 擲 3 次，恰有 2 個正面的機率。
(2) 擲 4 次，恰有 3 個正面的機率。

標準答案：part_1=3/8；part_2=1/4

### 12863 `numbered_dice`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`dice_count_probability`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

同時擲 2 粒各有 6 面（點數 1 到 6）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
(1) 點數和等於 $9$ 的機率。
(2) 點數和等於 $7$ 的機率。

標準答案：part_1=1/9；part_2=1/6

解題：
- (1) 已編號、等可能的樣本點 36 個，有利 4 個，機率 4/36 = 1/9。
- (2) 已編號、等可能的樣本點 36 個，有利 6 個，機率 6/36 = 1/6。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

同時擲 2 粒各有 6 面（點數 1 到 6）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
(1) 點數和等於 $10$ 的機率。
(2) 點數和等於 $2$ 的機率。

標準答案：part_1=1/12；part_2=1/36

### 12864 `urn_without_replacement`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`urn_draw_probability`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

一批物品有紅球 3 個、白球 2 個，每件被取出的機會均等。從中取出 2 件。求下列機率。
(1) 依序取出、不放回，其中紅球 2 個的機率。
(2) 同時取出，其中紅球 2 個的機率。

標準答案：part_1=3/10；part_2=3/10

解題：
- (1) 依序取出、不放回的等可能取法 20 個，有利 6 個，機率 6/20 = 3/10。
- (2) 同時取出、不計順序的等可能取法 10 個，有利 3 個，機率 3/10。

請人工確認：依序不放回是 6/20＝3/10，同時取出是 3/10。兩種數法的分母不同，約分後機率相同。

另一個抽樣：

一批物品有紅球 5 個、白球 2 個，每件被取出的機會均等。從中取出 2 件。求下列機率。
(1) 依序取出、不放回，其中紅球 2 個的機率。
(2) 同時取出，其中紅球 2 個的機率。

標準答案：part_1=10/21；part_2=10/21

### 12867 `with_replacement`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`replacement_count_probability`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

袋中有標號 1、2、3 的球各一顆。每次取出一球後放回，每球每次被取出的機會均等。求下列機率。
(1) 重複 2 次，至少有 1 次出現第 3 種結果的機率。
(2) 重複 3 次，恰有 2 次出現第 3 種結果的機率。

標準答案：part_1=5/9；part_2=2/9

解題：
- (1) 放回（或各自選擇）的樣本點有 9 個，有利 5 個，機率 5/9。
- (2) 放回（或各自選擇）的樣本點有 27 個，有利 6 個，機率 6/27 = 2/9。

請人工確認：確認題幹的隨機條件與標準答案講的是同一件事，且沒有把教材沒有的機率模型加進去。

另一個抽樣：

袋中有標號 1、2、3、4、5、6 的球各一顆。每次取出一球後放回，每球每次被取出的機會均等。求下列機率。
(1) 重複 2 次，至少有 2 次出現第 6 種結果的機率。
(2) 重複 4 次，恰有 0 次出現第 6 種結果的機率。

標準答案：part_1=1/36；part_2=625/1296

### 12871 `numbered_dice`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`dice_count_probability`
- 作答：rational，short_answer，checker `rational_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

同時擲 3 粒各有 6 面（點數 1 到 6）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
恰有 1 粒出現 $6$ 點的機率。

標準答案：25/72

解題：
- 已編號、等可能的樣本點 216 個，有利 75 個，機率 75/216 = 25/72。

請人工確認：教材寫「三粒相同的公正骰子」。元件把骰子編號，樣本空間是 216。恰有一粒 6 點的有利結果是 75，機率 75/216＝25/72。若改成不區分骰子，各結果就不再等可能。

另一個抽樣：

同時擲 3 粒各有 9 面（點數 1 到 9）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
恰有 2 粒出現 $7$ 點的機率。

標準答案：8/243

### 12872 `classical_claim`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`classical_claim`
- 作答：single_choice，single_choice，checker `choice_label_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

下列敘述對的打「○」，錯的打「×」。
袋中有大小相同的紅球、白球各若干顆。從中取出一球，取到紅球的機率為 $\frac{1}{2}$。

標準答案：B

解題：
- 只知道兩色都有、不知道顆數，不能推出機率是 1/2。

請人工確認：「各若干顆」沒有給出紅白球的顆數，不能推出機率是 1/2。答案是 ×，選項 B。

另一個抽樣：

下列敘述對的打「○」，錯的打「×」。
袋中有紅球 7 顆、白球 6 顆，每球被取出的機會均等。從中取出一球，取到紅球的機率為 $\frac{1}{2}$。

標準答案：B

### 12883 `password_permutation`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`password_guess`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

一組密碼密碼是由 1、3、5、7 這 4 個不同數字排成的，而且每一組排列出現的機會均等。
(1) 一次就猜對的機率是多少？
(2) 若連續輸入 3 次互不相同的錯誤密碼就會被鎖定，求被鎖定的機率。

標準答案：part_1=1/24；part_2=7/8

解題：
- (1) 4 個不同符號的排列有 24 個，有利 1 個，機率 1/24。
- (2) 前 3 次都猜錯才被沒收。等可能排列 24 個，有利 21 個，機率 21/24 = 7/8。

請人工確認：一次猜中：24 個排列中有利 1 個，機率 1/24。連續三次互不相同的錯誤密碼就鎖定：有利 21 個，機率 21/24＝7/8。

另一個抽樣：

一組密碼密碼是由 3 個不同數字排成的，而且每一組排列出現的機會均等。
(1) 一次就猜對的機率是多少？
(2) 若連續輸入 2 次互不相同的錯誤密碼就會被鎖定，求被鎖定的機率。

標準答案：part_1=1/6；part_2=2/3

### 12884 `solve_composition`

- Skill：`gh_DefinitionOfClassicalProbability`
- Problem Type / Domain Operation：`solve_urn_count`
- 作答：rational，short_answer，checker `rational_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；等價寫法 10.0：接受
- MathJax 括號：成對

袋中有 5 顆白球和 n 顆黑球。從袋中同時取出兩球，每球被取出的機會均等，已知兩球同為白球的機率是 $\frac{2}{21}$，求 n 的值。

標準答案：10

解題：
- 由 C(5,2)/C(5+n,2) = 2/21 解得 n = 10。

請人工確認：所求是黑球顆數 n＝10，不是機率。白球 5 顆、兩白球機率 2/21 時，正整數解只有 10。

另一個抽樣：

袋中有 6 顆白球和 n 顆黑球。從袋中同時取出兩球，每球被取出的機會均等，已知兩球同為白球的機率是 $\frac{1}{14}$，求 n 的值。

標準答案：15

### 12885 `probability_algebra`

- Skill：`gh_PropertiesOfProbability`
- Problem Type / Domain Operation：`probability_algebra`
- 作答：multi_part，multiple_inputs，checker `multi_part_answer_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；part_3 等價寫法 0.0：接受
- MathJax 括號：成對

設 A、B 為樣本空間的事件，$P(A)$ = $\frac{1}{3}$、$P(B)$ = $\frac{1}{2}$。
(1) 求 $P(A')$。
(2) 已知 $P(A\cap B)$ = $\frac{1}{6}$，求 $P(A\cup B)$。
(3) 已知 $P(A\cup B)$ = $\frac{5}{6}$，求 $P(A\cap B)$。

標準答案：part_1=2/3；part_2=2/3；part_3=0

解題：
- (1) 依機率性質得 2/3。
- (2) 依機率性質得 2/3。
- (3) 依機率性質得 0。

請人工確認：第三小題的交集機率是 0。判分接受 0，也接受等價的 0.0。

另一個抽樣：

設 A、B 為樣本空間的事件，$P(A)$ = $\frac{2}{5}$、$P(B)$ = $\frac{1}{4}$。
(1) 求 $P(A')$。
(2) 已知 $P(A\cap B)$ = $\frac{1}{6}$，求 $P(A\cup B)$。
(3) 已知 $P(A\cup B)$ = $\frac{29}{60}$，求 $P(A\cap B)$。

標準答案：part_1=3/5；part_2=29/60；part_3=1/6

### 12887 `numbered_dice`

- Skill：`gh_PropertiesOfProbability`
- Problem Type / Domain Operation：`dice_count_probability`
- 作答：rational，short_answer，checker `rational_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

同時擲 3 粒各有 6 面（點數 1 到 6）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
至少有兩粒點數相同的機率。

標準答案：4/9

解題：
- 已編號、等可能的樣本點 216 個，有利 96 個，機率 96/216 = 4/9。

請人工確認：至少兩粒點數相同：已編號的 216 個樣本點中有 96 個，96/216＝4/9。這與教材補事件 1−5/9 相同。

另一個抽樣：

同時擲 2 粒各有 4 面（點數 1 到 4）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。
每粒點數都不同的機率。

標準答案：3/4

### 12890 `with_replacement`

- Skill：`gh_PropertiesOfProbability`
- Problem Type / Domain Operation：`replacement_count_probability`
- 作答：rational，short_answer，checker `rational_checker`
- Checker：標準答案 接受；錯誤答案 拒絕；此答案型別沒有另一種自動等價寫法
- MathJax 括號：成對

4 人各從 6 個社團中任選一個參加，每人的選擇互不影響，每個社團等可能。求下列機率。
至少有兩人選擇相同社團的機率。

標準答案：13/18

解題：
- 放回（或各自選擇）的樣本點有 1296 個，有利 936 個，機率 936/1296 = 13/18。

請人工確認：四人各自從 6 個社團選一個，樣本點 6^4＝1296。至少兩人相同的有利結果是 936，936/1296＝13/18。

另一個抽樣：

3 人各從 3 個社團中任選一個參加，每人的選擇互不影響，每個社團等可能。求下列機率。
至少有兩人選擇相同社團的機率。

標準答案：7/9

## 圖形

42 題入庫題幹都沒有「如圖／下表」，正式列的 image_assets 為 0。DOCX 的 170 個 wmf 與 2 個 emf 是 MathType 方程式，不是題圖。另外 6 張 jpeg（郵票人像、撲克牌、球袋、水餃、慶生）是課文插圖，題幹已經寫出計算所需的數字，解題不必讀圖。PDF 只有第 1、9、12 頁出現「如圖／右圖」，分別在章首灑藍釉缽、課文把白球編號的說明，以及例題9詳解的編號示意，不在 42 題題幹裡。PDF 上大量向量是方程式字形，不是缺漏的數據圖或表格。

DOCX 媒體 {'.wmf': 170, '.emf': 2, '.jpeg': 6}，drawing 標記 24。
PDF 嵌入影像頁：[{'page': 6, 'embedded_images': 1}, {'page': 16, 'embedded_images': 2}, {'page': 18, 'embedded_images': 1}]。圖形用語：[{'page': 1, 'cues': ['如圖']}, {'page': 9, 'cues': ['如圖']}, {'page': 12, 'cues': ['右圖']}]。

## 尚未驗證

tmp 裡的 42 個 generate.py 有載入 42 個，與目前 domain 的教材參數不一致的有 無。瀏覽器 MathJax 尚未驗證。
