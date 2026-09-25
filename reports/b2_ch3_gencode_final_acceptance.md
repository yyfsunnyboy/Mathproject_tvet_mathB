# B2 Ch3 GenCode Final Acceptance

## Summary

- Skills: 15
- Examples: 95
- Eligible published components: 48
- Intentional skips: 47
- Probe needs_capability: 0

## Capability Matrix

| skill | domain | eligible | skip | published | status | unsupported |
|---|---|---:|---:|---:|---|---|
| vh_數學B2_SubSection_3_1_1 | vector.plane | 0 | 3 | 0 | SKIPPED_NO_RESOLVABLE | diagram_vector_construction_unsupported |
| vh_數學B2_SubSection_3_1_2 | vector.plane | 0 | 3 | 0 | SKIPPED_NO_RESOLVABLE | diagram_vector_construction_unsupported |
| vh_數學B2_SubSection_3_1_3 | vector.plane | 0 | 7 | 0 | SKIPPED_NO_RESOLVABLE | diagram_vector_construction_unsupported |
| vh_數學B2_SubSection_3_1_4 | vector.plane | 0 | 14 | 0 | SKIPPED_NO_RESOLVABLE | diagram_vector_construction_unsupported |
| vh_數學B2_SubSection_3_2_1 | vector.plane | 10 | 1 | 10 | READY | vector_mixed_unknown_endpoint_unsupported |
| vh_數學B2_SubSection_3_2_2 | vector.plane | 14 | 1 | 14 | READY | vector_chain_closure_mcq_unsupported |
| vh_數學B2_SubSection_3_2_3 | vector.plane | 0 | 2 | 0 | SKIPPED_NO_RESOLVABLE | vector_collinear_ratio_mcq_unsupported, vector_solve_point_from_combo_unsupported |
| vh_數學B2_SubSection_3_2_4 | vector.plane | 2 | 1 | 2 | READY | vector_solve_unknown_vector_equation_unsupported |
| vh_數學B2_SubSection_3_2_5 | vector.plane | 3 | 1 | 3 | READY | vector_parallel_then_magnitude_mcq_unsupported |
| vh_數學B2_SubSection_3_2_6 | vector.plane | 4 | 1 | 4 | READY | vector_unit_identification_mcq_unsupported |
| vh_數學B2_SubSection_3_3_1 | vector.plane | 2 | 2 | 2 | READY | vector_angle_application_narrative_unsupported, vector_angle_quality_mcq_unsupported |
| vh_數學B2_SubSection_3_3_2 | vector.plane | 1 | 4 | 1 | READY | vector_dot_identity_multipart_unsupported, vector_regular_polygon_dot_unsupported |
| vh_數學B2_SubSection_3_3_3 | vector.plane | 6 | 3 | 6 | READY | vector_dot_diagram_plot_unsupported, vector_dot_midpoint_composite_unsupported, vector_dot_parameter_equation_mcq_unsupported |
| vh_數學B2_SubSection_3_3_4 | vector.plane | 3 | 1 | 3 | READY | vector_perp_composite_expression_unsupported |
| vh_數學B2_SubSection_3_3_5 | vector.plane | 3 | 3 | 3 | READY | vector_dot_exam_diagram_unsupported, vector_dot_identity_solve_angle_unsupported, vector_perp_dot_expand_unsupported |

## Generator Smoke

| skill | components | pass | fail |
|---|---:|---:|---:|
| vh_數學B2_SubSection_3_1_1 | 0 | 0 | 0 |
| vh_數學B2_SubSection_3_1_2 | 0 | 0 | 0 |
| vh_數學B2_SubSection_3_1_3 | 0 | 0 | 0 |
| vh_數學B2_SubSection_3_1_4 | 0 | 0 | 0 |
| vh_數學B2_SubSection_3_2_1 | 10 | 10 | 0 |
| vh_數學B2_SubSection_3_2_2 | 14 | 14 | 0 |
| vh_數學B2_SubSection_3_2_3 | 0 | 0 | 0 |
| vh_數學B2_SubSection_3_2_4 | 2 | 2 | 0 |
| vh_數學B2_SubSection_3_2_5 | 3 | 3 | 0 |
| vh_數學B2_SubSection_3_2_6 | 4 | 4 | 0 |
| vh_數學B2_SubSection_3_3_1 | 2 | 2 | 0 |
| vh_數學B2_SubSection_3_3_2 | 1 | 1 | 0 |
| vh_數學B2_SubSection_3_3_3 | 6 | 6 | 0 |
| vh_數學B2_SubSection_3_3_4 | 3 | 3 | 0 |
| vh_數學B2_SubSection_3_3_5 | 3 | 3 | 0 |

## Notes

- 3-1 diagram skills: registry-bound but all examples intentional_skip.
- Unsupported algebraic/application topologies: intentional_skip with concrete block reasons.
- Published packages under gent_skills_v3/vh_數學B2_SubSection_3_* + practice wrappers under skills/.
- Retained orchestrator unregistered-domain soft-stop; fixed publish success recognition for production_published.
- Gated descriptive-statistics analyzer so it cannot hijack non-statistics registered skills.
