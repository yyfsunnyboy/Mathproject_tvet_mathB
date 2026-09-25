# B2 Ch3 GenCode Inventory

Source: `instance/kumon_math.db` (`skills_info` + `textbook_examples`), 2026-09-25.

## Summary

| Metric | Value |
|---|---|
| Skills | 15 |
| Examples | 95 |
| Domain | `vector.plane` (new) |
| Diagram-first (3-1) | 4 skills / 27 examples → intentional skip |
| Algebraic/coordinate (3-2, 3-3) | 11 skills / 68 examples |

## Skills

| skill_id | display_name | section | examples | domain binding | capability posture | topology summary | image dependency | answer types |
|---|---|---|---:|---|---|---|---|---|
| vh_數學B2_SubSection_3_1_1 | 向量定義 | 3-1 向量的作圖 | 3 | vector.plane | intentional_skip (diagram) | figure-based vector identity / expression | yes (textbook figure) | multi-part / MCQ |
| vh_數學B2_SubSection_3_1_2 | 向量的加法作圖 | 3-1 | 3 | vector.plane | intentional_skip | path-sum simplification on figure | yes | multi-part |
| vh_數學B2_SubSection_3_1_3 | 向量的減法作圖 | 3-1 | 7 | vector.plane | intentional_skip | path-difference on figure | yes | multi-part / MCQ |
| vh_數學B2_SubSection_3_1_4 | 向量的實數積作圖 | 3-1 | 14 | vector.plane | intentional_skip | scalar multiple / midpoint combo on figure | yes | multi-part / MCQ |
| vh_數學B2_SubSection_3_2_1 | 向量的坐標表示法 | 3-2 | 11 | vector.plane | supported core + 1 skip | A components+mag; B equal vectors; C AB+mag; D parallelogram; E perimeter MCQ; mixed unknown endpoint skip | mostly text; 1 application figure | multi-part / expression / MCQ |
| vh_數學B2_SubSection_3_2_2 | 向量加減的坐標表示法 | 3-2 | 15 | vector.plane | supported + 1 skip | add/sub; point-segment combo; triangle chain; parallelogram; linear combo; chain-closure MCQ skip | text | expression / multi-part / MCQ |
| vh_數學B2_SubSection_3_2_3 | 向量實數積的坐標表示法 | 3-2 | 2 | vector.plane | intentional_skip | solve unknown point from combo; collinear ratio MCQ | text | expression / MCQ |
| vh_數學B2_SubSection_3_2_4 | 向量實數積的基本性質 | 3-2 | 3 | vector.plane | supported + 1 skip | linear combination; unknown-vector equation skip | text | expression / MCQ |
| vh_數學B2_SubSection_3_2_5 | 向量的平行 | 3-2 | 4 | vector.plane | supported + 1 skip | parallel parameter; parallel-then-magnitude MCQ skip | text | expression / MCQ |
| vh_數學B2_SubSection_3_2_6 | 單位向量 | 3-2 | 5 | vector.plane | supported + 1 skip | unit / scaled direction; unit-identification MCQ skip | text | expression / multi-part / MCQ |
| vh_數學B2_SubSection_3_3_1 | 向量的夾角 | 3-3 | 4 | vector.plane | supported + 2 skip | cosine from coordinates; narrative navigation / angle-quality MCQ skip | mixed | expression / MCQ |
| vh_數學B2_SubSection_3_3_2 | 向量內積的定義 | 3-3 | 5 | vector.plane | supported + 4 skip | mag+angle → dot; regular-polygon / identity multipart skip | mixed | expression / multi-part |
| vh_數學B2_SubSection_3_3_3 | 向量內積的坐標表示法 | 3-3 | 9 | vector.plane | supported + 3 skip | coordinate dot; cosine; diagram-plot / midpoint / param-eq skip | mixed | expression / MCQ |
| vh_數學B2_SubSection_3_3_4 | 兩向量的垂直 | 3-3 | 4 | vector.plane | supported + 1 skip | perpendicular parameter; composite perp expression skip | text | expression / multi-part |
| vh_數學B2_SubSection_3_3_5 | 向量內積的性質 | 3-3 | 6 | vector.plane | supported + 3 skip | mag+angle identities; exam diagram / expand / inverse-angle skip | mixed | expression / multi-part / MCQ |

## Capability groups

1. **Diagram construction (3-1)** — figure / geometric vector algebra without coordinates → not auto-generated.
2. **Coordinate representation (3-2-1)** — components, equality, directed segment, parallelogram, perimeter.
3. **Vector arithmetic (3-2-2)** — add/sub, segment combos, triangle chain, linear combo.
4. **Scalar multiple (3-2-3/4)** — linear combinations; some equation/collinear topologies deferred.
5. **Parallel / unit (3-2-5/6)** — parallel parameter; unit / scaled direction.
6. **Dot product family (3-3)** — definition via mag∠, coordinate dot, cosine, perpendicular.

## skill → family → operation map (supported)

| Family | Operation |
|---|---|
| components_magnitude | `compute_vector_components_and_magnitude` |
| equal_vectors | `solve_equal_vector_coordinates` |
| directed_segment | `compute_directed_segment_and_magnitude` |
| parallelogram_vertex | `solve_parallelogram_fourth_vertex` |
| triangle_perimeter_mcq | `compute_triangle_perimeter_from_two_vectors` |
| vector_add_sub | `compute_vector_sum_difference` |
| point_segment_combo | `compute_point_vectors_linear_combination` |
| triangle_chain | `compute_triangle_chain_and_perimeter` |
| linear_combo | `compute_vector_linear_combination` |
| scalar_multiple | `compute_scalar_multiple_coordinates` |
| parallel_param | `solve_parallel_vector_parameter` |
| unit_vector | `compute_unit_vector` |
| scaled_direction | `compute_scaled_direction_vector` |
| dot_coords | `compute_dot_product_coordinates` |
| dot_mag_angle | `compute_dot_product_from_magnitudes_angle` |
| cosine_from_dot | `compute_cosine_of_angle_from_dot` |
| perpendicular_param | `solve_perpendicular_vector_parameter` |
