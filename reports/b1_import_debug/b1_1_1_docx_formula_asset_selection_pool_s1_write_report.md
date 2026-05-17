# DOCX Formula Asset Selection Pool Dry-run Report
- volume: `數學B1`
- section: `1-1 數線與絕對值`
- dry_run: `False`
- title_filters: `['隨堂練習1']`

## id=3901 隨堂練習1 [source_type=in_class_practice | linked_example=例1 | needs_review=true | dedupe=60aa79ec0cab7703]
- db_problem_text: `數線上，若 [FORMULA_IMAGE_1] = 4，試求 x 之 x 值。[FORMULA_IMAGE_2]`
- placeholder_tokens: `['[FORMULA_IMAGE_1]', '[FORMULA_IMAGE_2]']`
- expected_placeholder_classes: `{'[FORMULA_IMAGE_1]': 'formula_abs_x', '[FORMULA_IMAGE_2]': 'unknown'}`
- current_record_assets: `[{'filename': '1-1數線與絕對值_隨堂練習1_1_08a06f34_image1.png', 'placeholder_token': '[FORMULA_IMAGE_1]', 'placeholder_index': 1}, {'filename': '1-1數線與絕對值_隨堂練習1_2_79f5db19_image2.png', 'placeholder_token': '[FORMULA_IMAGE_2]', 'placeholder_index': 2}, {'filename': '1-1數線與絕對值_隨堂練習1_3_27c71b19_image3.png', 'placeholder_token': '[FORMULA_IMAGE_3]', 'placeholder_index': 3}]`
- section_pool_candidate_matches: `[{'token': '[FORMULA_IMAGE_1]', 'expected_class': 'formula_abs_x', 'matches': ['1-1數線與絕對值_1-1習題基礎題1_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題2_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題3_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題4_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題5_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題6_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題7_2_14b9340a_image80.png', '1-1數線與絕對值_1-1習題基礎題8_2_14b9340a_image80.png']}, {'token': '[FORMULA_IMAGE_2]', 'expected_class': 'unknown', 'matches': []}]`
- rejected_assets_summary: `{'diagram_not_allowed': 228, 'class_mismatch': 109, 'unsupported_expected_class': 118, 'already_used': 1}`
- rejected_assets_samples: `[{'filename': '1-1數線與絕對值_例1_1_08a06f34_image1.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_2_79f5db19_image2.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_3_27c71b19_image3.png', 'class': 'unknown_formula', 'reason': 'class_mismatch'}, {'filename': '1-1數線與絕對值_例1_4_581e2172_image4.png', 'class': 'diagram_or_picture', 'reason': 'diagram_not_allowed'}, {'filename': '1-1數線與絕對值_例1_5_fbfbaef2_image5.png', 'class': 'formula_fraction', 'reason': 'class_mismatch'}]`
- selected_replacements: `{'[FORMULA_IMAGE_1]': '|x|'}`
- proposed_problem_text: `數線上，若 |x| = 4，試求 x 之值。[FORMULA_IMAGE_2]`
- cross_record_asset_used: `True`
- action: `partial_proposed_update`
- reason: `placeholder_replaced`
- safety_status: `safe_to_write`
- write_recommendation: `yes`
- write_blocked_reason: ``

## Summary
- processed_records: `1`
- records_with_formula_assets: `1`
- formula_assets_total: `3`
- readable_assets: `233`
- pix2tex_success: `92`
- pix2tex_low_quality: `141`
- section_pool_assets: `233`
- classified_assets: `233`
- diagram_assets: `114`
- formula_assets: `119`
- selected_replacements: `1`
- proposed_updates: `0`
- partial_proposed_updates: `1`
- blocked_by_class_mismatch: `218`
- updated_records: `1`
- safe_proposed_update_records: `0`
- safe_partial_update_records: `1`
- skipped_mojibake_records: `0`
- blocked_mojibake_outputs: `0`
- unsafe_records: `0`
- still_missing_formula: `16`

## Safe Write Candidates
- id=3901 | source_description=`隨堂練習1 [source_type=in_class_practice | linked_example=例1 | needs_review=true | dedupe=60aa79ec0cab7703]` | canonical_title=`隨堂練習1` | action=`partial_proposed_update` | selected_replacements=`{'[FORMULA_IMAGE_1]': '|x|'}` | still_has_formula_missing=`False` | write_recommendation=`yes`

## Suggested safe write commands
python scripts\docx_formula_asset_pix2tex_backfill.py --volume "數學B1" --section "1-1 數線與絕對值" --title "隨堂練習1" --write --formula-ocr-backend pix2tex --confidence-threshold 0.85 --report "reports/b1_import_debug/b1_1_1_docx_formula_asset_selection_pool_safe_write_report.md"
