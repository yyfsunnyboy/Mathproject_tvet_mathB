# B3 Ch1 Answer-Arity Runtime Audit

total_examples = 74

## Inventory
- single_answer = 37
- multi_answer_2 = 16
- multi_answer_3 = 2
- multi_answer_4plus = 0
- mcq = 19

## Acceptance
- arity_pass = 74
- arity_fail = 0
- render_pass = 74
- render_fail = 0
- submit_checker_pass = 74
- submit_checker_fail = 0

## By Skill
- `1_1_1`: single=0 m2=3 m3=0 m4+=0 mcq=0 PASS=3 FAIL=0
- `1_1_2`: single=6 m2=3 m3=0 m4+=0 mcq=4 PASS=13 FAIL=0
- `1_1_3`: single=2 m2=0 m3=0 m4+=0 mcq=0 PASS=2 FAIL=0
- `1_1_4`: single=0 m2=4 m3=1 m4+=0 mcq=0 PASS=5 FAIL=0
- `1_1_5`: single=9 m2=1 m3=0 m4+=0 mcq=4 PASS=14 FAIL=0
- `1_2_1`: single=12 m2=0 m3=1 m4+=0 mcq=6 PASS=19 FAIL=0
- `1_2_2`: single=1 m2=2 m3=0 m4+=0 mcq=1 PASS=4 FAIL=0
- `1_2_3`: single=0 m2=3 m3=0 m4+=0 mcq=0 PASS=3 FAIL=0
- `1_2_4`: single=7 m2=0 m3=0 m4+=0 mcq=4 PASS=11 FAIL=0

## Multi-answer generators

- 11896 `src_11896` expected=2 labels=['\\(\\langle a_n \\rangle = \\langle \\frac{1}{2 n} \\rangle\\)', '\\(\\langle a_n \\rangle = \\langle 2^{n} + 3 \\rangle\\)'] status=PASS
- 11897 `src_11897` expected=2 labels=['\\(\\langle a_n \\rangle = \\langle \\frac{1}{2 n} \\rangle\\)', '\\(\\langle a_n \\rangle = \\langle 2^{n} + 3 \\rangle\\)'] status=PASS
- 11913 `src_11913` expected=2 labels=['\\(\\langle a_n \\rangle = \\langle \\frac{1}{2 n} \\rangle\\)', '\\(\\langle a_n \\rangle = \\langle 2^{n} + 3 \\rangle\\)'] status=PASS
- 11901 `src_11901` expected=2 labels=['他每天增加幾個投球數？', '第12天他投了幾個球？'] status=PASS
- 11915 `src_11915` expected=2 labels=['公差 d', '\\(a_{14}\\) 之值'] status=PASS
- 11923 `src_11923` expected=2 labels=['公差 d', '\\(a_{14}\\) 之值'] status=PASS
- 11906 `src_11906` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{8}\\)'] status=PASS
- 11907 `src_11907` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{8}\\)'] status=PASS
- 11917 `src_11917` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{8}\\)'] status=PASS
- 11922 `src_11922` expected=3 labels=['遞迴關係中的首項 \\(a_1\\)', '遞迴增量：每增加一圖，白色地磚增加幾塊（即 \\(a_n=a_{n-1}+\\,?\\)）', '拼第7個圖需用到幾塊白色地磚'] status=PASS
- 11962 `src_11962` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{8}\\)'] status=PASS
- 11921 `src_11921` expected=2 labels=['阿民坐在第幾排', 'A區共有幾個座位'] status=PASS
- 11950 `src_11950` expected=3 labels=['第2年年底本利和', '第4年年初本金', '第5年年底本利和'] status=PASS
- 11932 `src_11932` expected=2 labels=['正值', '負值'] status=PASS
- 11933 `src_11933` expected=2 labels=['正值', '負值'] status=PASS
- 11934 `src_11934` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{7}\\)'] status=PASS
- 11935 `src_11935` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{7}\\)'] status=PASS
- 11946 `src_11946` expected=2 labels=['一般項 \\(a_n\\)', '\\(a_{7}\\)'] status=PASS

## Mismatched

(none)

## Notes
- Mathematical coverage remains 74/74 SUPPORTED.
- This audit measures practice runtime field contract only.
