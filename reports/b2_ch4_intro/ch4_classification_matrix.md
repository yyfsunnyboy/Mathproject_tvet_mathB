# B2 第4章 題型分類矩陣（完整）

來源：`skill_curriculum` + facade `GENERATOR_SPECS` + Runtime inventory + 10-seed 參數抽樣。

| Skill | Source ID | 題型名稱 | problem_type_id | Generator | Checker | Y | 狀態 |
|---|---|---|---|---|---|---:|---|
| `SubSection_4_1_1` | 11890 | 圓心與切線條件求圓（MCQ） | `circle_center_tangent_to_line` | `src_11890` | `choice_label_checker` | 9 | LIMITED |
| `SubSection_4_1_1` | 11843 | 同半徑／原點條件圓 | `circle_equal_radius_at_origin` | `src_11843` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11830,11831,11844,11891 | 直徑端點求圓方程式 | `circle_from_diameter_endpoints` | `src_11830, src_11831, src_11844, src_11891` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11886 | 原點為圓心且過兩線交點（MCQ） | `circle_origin_through_lines_intersection` | `src_11886` | `choice_label_checker` | 9 | LIMITED |
| `SubSection_4_1_1` | 11887 | 同圓心且面積比例求圓（MCQ） | `circle_same_center_scaled_area` | `src_11887` | `choice_label_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11826,11827,11841 | 由標準式讀圓心與半徑 | `identify_center_radius_from_standard` | `src_11826, src_11827, src_11841` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11828 | 圓軌跡方程式語意 | `interpret_circular_locus_equation` | `src_11828` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11850,11877 | 圓的平移與縮放 | `translate_and_scale_circle` | `src_11850, src_11877` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_1` | 11829,11842 | 依條件寫圓方程式 | `write_circle_equations_from_conditions` | `src_11829, src_11842` | `expression_checker` | 9 | PASS |
| `SubSection_4_1_2` | 11840 | circle_center_on_axis_area | `circle_center_on_axis_area` | `src_11840` | `choice_label_checker` | 10 | LIMITED |
| `SubSection_4_1_2` | 11838,11839,11848,11892 | circle_through_three_points | `circle_through_three_points` | `src_11838, src_11839, src_11848, src_11892` | `expression_checker` | 10 | PASS |
| `SubSection_4_1_2` | 11846 | classify_general_circle_graph | `classify_general_circle_graph` | `src_11846` | `expression_checker` | 10 | PASS |
| `SubSection_4_1_2` | 11888 | compute_circle_area_from_general | `compute_circle_area_from_general` | `src_11888` | `expression_checker` | 10 | PASS |
| `SubSection_4_1_2` | 11876 | evaluate_center_radius_expression | `evaluate_center_radius_expression` | `src_11876` | `choice_label_checker` | 10 | LIMITED |
| `SubSection_4_1_2` | 11832,11833,11834,11835,11845 | identify_center_radius_from_general | `identify_center_radius_from_general` | `src_11832, src_11833, src_11834, src_11835, src_11845` | `expression_checker` | 10 | PASS |
| `SubSection_4_1_2` | 11889 | identify_circle_from_product_form | `identify_circle_from_product_form` | `src_11889` | `expression_checker` | 10 | LIMITED |
| `SubSection_4_1_2` | 11836,11837,11847 | solve_circle_parameter_range | `solve_circle_parameter_range` | `src_11836, src_11837, src_11847` | `expression_checker` | 10 | PASS |
| `SubSection_4_1_2` | 11893 | solve_circle_parameter_range_mcq | `solve_circle_parameter_range_mcq` | `src_11893` | `choice_label_checker` | 10 | LIMITED |
| `SubSection_4_1_2` | 11849 | 圓的平移與縮放 | `translate_and_scale_circle` | `src_11849` | `expression_checker` | 10 | PASS |
| `SubSection_4_2_1` | 11851,11852,11866 | classify_point_vs_circles_multipart | `classify_point_vs_circles_multipart` | `src_11851, src_11852, src_11866` | `expression_checker` | 3 | PASS |
| `SubSection_4_2_1` | 11884 | identify_point_on_circle_mcq | `identify_point_on_circle_mcq` | `src_11884` | `expression_checker` | 3 | PASS |
| `SubSection_4_2_1` | 11875 | solve_point_circle_parameter_range | `solve_point_circle_parameter_range` | `src_11875` | `expression_checker` | 3 | PASS |
| `SubSection_4_2_2` | 11853 | classify_line_circle_relation | `classify_line_circle_relation` | `src_11853` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11878,11882 | classify_line_circle_relation_mcq | `classify_line_circle_relation_mcq` | `src_11878, src_11882` | `choice_label_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11854,11867 | classify_lines_vs_circle_multipart | `classify_lines_vs_circle_multipart` | `src_11854, src_11867` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11857,11858,11870 | compute_chord_length | `compute_chord_length` | `src_11857, src_11858, src_11870` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11874 | compute_storm_path_length_in_circle | `compute_storm_path_length_in_circle` | `src_11874` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11881 | compute_triangle_center_chord_area | `compute_triangle_center_chord_area` | `src_11881` | `choice_label_checker` | 12 | LIMITED |
| `SubSection_4_2_2` | 11869 | count_line_circle_intersections | `count_line_circle_intersections` | `src_11869` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11883 | solve_axis_tangent_parameter | `solve_axis_tangent_parameter` | `src_11883` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11879 | solve_diameter_chord_parameter_mcq | `solve_diameter_chord_parameter_mcq` | `src_11879` | `choice_label_checker` | 12 | LIMITED |
| `SubSection_4_2_2` | 11855 | solve_line_circle_parameter_range | `solve_line_circle_parameter_range` | `src_11855` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11868 | solve_line_circle_relation_ranges_multipart | `solve_line_circle_relation_ranges_multipart` | `src_11868` | `expression_checker` | 12 | PASS |
| `SubSection_4_2_2` | 11856,11880 | solve_line_circle_tangent_parameter | `solve_line_circle_tangent_parameter` | `src_11856, src_11880` | `choice_label_checker, expression_checker` | 12 | PASS |
| `SubSection_4_2_3` | 11895 | compute_tangents_from_point_quad_area | `compute_tangents_from_point_quad_area` | `src_11895` | `choice_label_checker` | 5 | LIMITED |
| `SubSection_4_2_3` | 11859,11860,11871 | tangent_at_point_on_circle | `tangent_at_point_on_circle` | `src_11859, src_11860, src_11871` | `expression_checker` | 5 | PASS |
| `SubSection_4_2_3` | 11885 | tangent_at_point_on_circle_mcq | `tangent_at_point_on_circle_mcq` | `src_11885` | `choice_label_checker` | 5 | PASS |
| `SubSection_4_2_3` | 11861,11872 | tangents_parallel_to_line | `tangents_parallel_to_line` | `src_11861, src_11872` | `expression_checker` | 5 | PASS |
| `SubSection_4_2_3` | 11862 | tangents_perpendicular_to_line | `tangents_perpendicular_to_line` | `src_11862` | `expression_checker` | 5 | PASS |
| `SubSection_4_2_4` | 11894 | compute_tangent_segment_length_mcq | `compute_tangent_segment_length_mcq` | `src_11894` | `choice_label_checker` | 3 | LIMITED |
| `SubSection_4_2_4` | 11863,11864,11873 | compute_tangent_segment_lengths | `compute_tangent_segment_lengths` | `src_11863, src_11864, src_11873` | `expression_checker` | 3 | PASS |
| `SubSection_4_2_4` | 11865 | count_line_vs_two_circles_intersections | `count_line_vs_two_circles_intersections` | `src_11865` | `choice_label_checker` | 3 | LIMITED |
