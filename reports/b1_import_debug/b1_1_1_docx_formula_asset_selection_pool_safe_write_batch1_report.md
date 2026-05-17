# DOCX Formula Asset Selection Pool Dry-run Report
- volume: `數學B1`
- section: `1-1 數線與絕對值`
- dry_run: `False`
- title_filters: `['1-1習題基礎題1', '1-1習題基礎題3', '隨堂練習2']`

## id=3902 1-1習題 基礎題1 [source_type=basic_exercise | needs_review=true | dedupe=bfe48ece9c53c66e]
- db_problem_text: `數線上，若 [FORMULA_IMAGE_1] = 8，試求 x 之 x 值。`
- placeholder_tokens: `['[FORMULA_IMAGE_1]']`
- expected_placeholder_classes: `{'[FORMULA_IMAGE_1]': 'formula_abs_x'}`
- current_record_assets: `[{'filename': '1-1數線與絕對值_1-1習題基礎題1_1_4703a8b1_image76.png', 'placeholder_token': '[FORMULA_IMAGE_1]', 'placeholder_index': 1}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', 'placeholder_token': '[FORMULA_IMAGE_2]', 'placeholder_index': 2}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_3_b4279b87_image81.png', 'placeholder_token': '[FORMULA_IMAGE_3]', 'placeholder_index': 3}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_4_b175ca53_image82.png', 'placeholder_token': '[FORMULA_IMAGE_4]', 'placeholder_index': 4}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_5_dd5dccdc_image83.png', 'placeholder_token': '[FORMULA_IMAGE_5]', 'placeholder_index': 5}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_6_b9fa887a_image84.png', 'placeholder_token': '[FORMULA_IMAGE_6]', 'placeholder_index': 6}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_7_cd8de44d_image85.png', 'placeholder_token': '[FORMULA_IMAGE_7]', 'placeholder_index': 7}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_8_716eba35_image86.png', 'placeholder_token': '[FORMULA_IMAGE_8]', 'placeholder_index': 8}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_9_1188b215_image88.png', 'placeholder_token': '[FORMULA_IMAGE_9]', 'placeholder_index': 9}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_10_ab7c6bff_image89.png', 'placeholder_token': '[FORMULA_IMAGE_10]', 'placeholder_index': 10}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_11_aa6dc023_image90.png', 'placeholder_token': '[FORMULA_IMAGE_11]', 'placeholder_index': 11}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_12_d071a974_image91.png', 'placeholder_token': '[FORMULA_IMAGE_12]', 'placeholder_index': 12}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_13_f59ced32_image92.png', 'placeholder_token': '[FORMULA_IMAGE_13]', 'placeholder_index': 13}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_14_086d8d4d_image93.png', 'placeholder_token': '[FORMULA_IMAGE_14]', 'placeholder_index': 14}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_15_82e19f2b_image94.png', 'placeholder_token': '[FORMULA_IMAGE_15]', 'placeholder_index': 15}, {'filename': '1-1數線與絕對值_1-1習題基礎題1_16_ee5efa29_image95.png', 'placeholder_token': '[FORMULA_IMAGE_16]', 'placeholder_index': 16}]`
- section_pool_candidate_matches: `[{'token': '[FORMULA_IMAGE_1]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}]`
- rejected_assets_summary: `{'diagram_not_allowed': 114, 'class_mismatch': 109}`
- rejected_assets_samples: `[{'filename': '1-1數線與絕對值_例1_1_08a06f34_image1.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_2_79f5db19_image2.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_3_27c71b19_image3.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_4_581e2172_image4.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_5_fbfbaef2_image5.png', 'class': 'formula_fraction', 'reason': 'class_mismatch'}]`
- selected_replacements: `{'[FORMULA_IMAGE_1]': '|x|'}`
- proposed_problem_text: `數線上，若 |x| = 8，試求 x 之值。`
- cross_record_asset_used: `False`
- action: `proposed_update`
- reason: `placeholder_replaced`
- safety_status: `safe_to_write`
- write_recommendation: `yes`
- write_blocked_reason: ``

## id=3905 隨堂練習2 [source_type=in_class_practice | linked_example=例2 | needs_review=true | dedupe=f1c72785691c30b1]
- db_problem_text: `試求下列不等式之解：(1) [FORMULA_IMAGE_1] ≤ 6 (2) [FORMULA_IMAGE_2] > 5`
- placeholder_tokens: `['[FORMULA_IMAGE_1]', '[FORMULA_IMAGE_2]']`
- expected_placeholder_classes: `{'[FORMULA_IMAGE_1]': 'formula_abs_x', '[FORMULA_IMAGE_2]': 'formula_abs_x'}`
- current_record_assets: `[{'filename': '1-1數線與絕對值_隨堂練習2_1_08a06f34_image1.png', 'placeholder_token': '[FORMULA_IMAGE_1]', 'placeholder_index': 1}, {'filename': '1-1數線與絕對值_隨堂練習2_2_79f5db19_image2.png', 'placeholder_token': '[FORMULA_IMAGE_2]', 'placeholder_index': 2}, {'filename': '1-1數線與絕對值_隨堂練習2_3_27c71b19_image3.png', 'placeholder_token': '[FORMULA_IMAGE_3]', 'placeholder_index': 3}]`
- section_pool_candidate_matches: `[{'token': '[FORMULA_IMAGE_1]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}, {'token': '[FORMULA_IMAGE_2]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}]`
- rejected_assets_summary: `{'diagram_not_allowed': 228, 'class_mismatch': 218, 'already_used': 1}`
- rejected_assets_samples: `[{'filename': '1-1數線與絕對值_例1_1_08a06f34_image1.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_2_79f5db19_image2.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_3_27c71b19_image3.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_4_581e2172_image4.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_5_fbfbaef2_image5.png', 'class': 'formula_fraction', 'reason': 'class_mismatch'}]`
- selected_replacements: `{'[FORMULA_IMAGE_1]': '|x|', '[FORMULA_IMAGE_2]': '|x|'}`
- proposed_problem_text: `試求下列不等式之解：(1) |x| ≤ 6 (2) |x| > 5`
- cross_record_asset_used: `True`
- action: `proposed_update`
- reason: `placeholder_replaced`
- safety_status: `safe_to_write`
- write_recommendation: `yes`
- write_blocked_reason: ``

## id=3906 1-1習題 基礎題3 [source_type=basic_exercise | needs_review=true | dedupe=b7e4c9ff03a562f9]
- db_problem_text: `試求下列不等式之解：(1) [FORMULA_IMAGE_1] ≤ 8 (2) [FORMULA_IMAGE_2] > 10 (3) [FORMULA_IMAGE_3] < 7 (4) [FORMULA_IMAGE_4] ≥ 12`
- placeholder_tokens: `['[FORMULA_IMAGE_1]', '[FORMULA_IMAGE_2]', '[FORMULA_IMAGE_3]', '[FORMULA_IMAGE_4]']`
- expected_placeholder_classes: `{'[FORMULA_IMAGE_1]': 'formula_abs_x', '[FORMULA_IMAGE_2]': 'formula_abs_x', '[FORMULA_IMAGE_3]': 'formula_abs_x', '[FORMULA_IMAGE_4]': 'formula_abs_x'}`
- current_record_assets: `[{'filename': '1-1數線與絕對值_1-1習題基礎題3_1_4703a8b1_image76.png', 'placeholder_token': '[FORMULA_IMAGE_1]', 'placeholder_index': 1}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', 'placeholder_token': '[FORMULA_IMAGE_2]', 'placeholder_index': 2}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_3_b4279b87_image81.png', 'placeholder_token': '[FORMULA_IMAGE_3]', 'placeholder_index': 3}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_4_b175ca53_image82.png', 'placeholder_token': '[FORMULA_IMAGE_4]', 'placeholder_index': 4}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_5_dd5dccdc_image83.png', 'placeholder_token': '[FORMULA_IMAGE_5]', 'placeholder_index': 5}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_6_b9fa887a_image84.png', 'placeholder_token': '[FORMULA_IMAGE_6]', 'placeholder_index': 6}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_7_cd8de44d_image85.png', 'placeholder_token': '[FORMULA_IMAGE_7]', 'placeholder_index': 7}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_8_716eba35_image86.png', 'placeholder_token': '[FORMULA_IMAGE_8]', 'placeholder_index': 8}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_9_1188b215_image88.png', 'placeholder_token': '[FORMULA_IMAGE_9]', 'placeholder_index': 9}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_10_ab7c6bff_image89.png', 'placeholder_token': '[FORMULA_IMAGE_10]', 'placeholder_index': 10}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_11_aa6dc023_image90.png', 'placeholder_token': '[FORMULA_IMAGE_11]', 'placeholder_index': 11}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_12_d071a974_image91.png', 'placeholder_token': '[FORMULA_IMAGE_12]', 'placeholder_index': 12}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_13_f59ced32_image92.png', 'placeholder_token': '[FORMULA_IMAGE_13]', 'placeholder_index': 13}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_14_086d8d4d_image93.png', 'placeholder_token': '[FORMULA_IMAGE_14]', 'placeholder_index': 14}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_15_82e19f2b_image94.png', 'placeholder_token': '[FORMULA_IMAGE_15]', 'placeholder_index': 15}, {'filename': '1-1數線與絕對值_1-1習題基礎題3_16_ee5efa29_image95.png', 'placeholder_token': '[FORMULA_IMAGE_16]', 'placeholder_index': 16}]`
- section_pool_candidate_matches: `[{'token': '[FORMULA_IMAGE_1]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}, {'token': '[FORMULA_IMAGE_2]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}, {'token': '[FORMULA_IMAGE_3]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}, {'token': '[FORMULA_IMAGE_4]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}]`
- rejected_assets_summary: `{'diagram_not_allowed': 456, 'class_mismatch': 436, 'already_used': 6}`
- rejected_assets_samples: `[{'filename': '1-1數線與絕對值_例1_1_08a06f34_image1.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_2_79f5db19_image2.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_3_27c71b19_image3.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_4_581e2172_image4.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_5_fbfbaef2_image5.png', 'class': 'formula_fraction', 'reason': 'class_mismatch'}]`
- selected_replacements: `{'[FORMULA_IMAGE_1]': '|x|', '[FORMULA_IMAGE_2]': '|x|', '[FORMULA_IMAGE_3]': '|x|', '[FORMULA_IMAGE_4]': '|x|'}`
- proposed_problem_text: `試求下列不等式之解：(1) |x| ≤ 8 (2) |x| > 10 (3) |x| < 7 (4) |x| ≥ 12`
- cross_record_asset_used: `True`
- action: `proposed_update`
- reason: `placeholder_replaced`
- safety_status: `safe_to_write`
- write_recommendation: `yes`
- write_blocked_reason: ``

## Summary
- processed_records: `3`
- records_with_formula_assets: `3`
- formula_assets_total: `35`
- readable_assets: `233`
- pix2tex_success: `92`
- pix2tex_low_quality: `141`
- section_pool_assets: `233`
- classified_assets: `233`
- diagram_assets: `114`
- formula_assets: `119`
- selected_replacements: `7`
- proposed_updates: `3`
- partial_proposed_updates: `0`
- blocked_by_class_mismatch: `1526`
- updated_records: `3`
- safe_proposed_update_records: `3`
- safe_partial_update_records: `0`
- skipped_mojibake_records: `0`
- blocked_mojibake_outputs: `0`
- unsafe_records: `0`
- still_missing_formula: `16`

## Safe Write Candidates
- id=3902 | source_description=`1-1習題 基礎題1 [source_type=basic_exercise | needs_review=true | dedupe=bfe48ece9c53c66e]` | canonical_title=`1-1習題 基礎題1` | action=`proposed_update` | selected_replacements=`{'[FORMULA_IMAGE_1]': '|x|'}` | still_has_formula_missing=`False` | write_recommendation=`yes`
- id=3905 | source_description=`隨堂練習2 [source_type=in_class_practice | linked_example=例2 | needs_review=true | dedupe=f1c72785691c30b1]` | canonical_title=`隨堂練習2` | action=`proposed_update` | selected_replacements=`{'[FORMULA_IMAGE_1]': '|x|', '[FORMULA_IMAGE_2]': '|x|'}` | still_has_formula_missing=`False` | write_recommendation=`yes`
- id=3906 | source_description=`1-1習題 基礎題3 [source_type=basic_exercise | needs_review=true | dedupe=b7e4c9ff03a562f9]` | canonical_title=`1-1習題 基礎題3` | action=`proposed_update` | selected_replacements=`{'[FORMULA_IMAGE_1]': '|x|', '[FORMULA_IMAGE_2]': '|x|', '[FORMULA_IMAGE_3]': '|x|', '[FORMULA_IMAGE_4]': '|x|'}` | still_has_formula_missing=`False` | write_recommendation=`yes`

## Suggested safe write commands
python scripts\docx_formula_asset_pix2tex_backfill.py --volume "數學B1" --section "1-1 數線與絕對值" --title "1-1習題 基礎題1" --title "1-1習題 基礎題3" --title "隨堂練習2" --write --formula-ocr-backend pix2tex --confidence-threshold 0.85 --report "reports/b1_import_debug/b1_1_1_docx_formula_asset_selection_pool_safe_write_report.md"
