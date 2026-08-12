from typing import Any
from agent_skills_v3.vh_數學B1_DivisionPointCoordinates.component_runtime import generate_component
def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_component(source_id=4423, problem_type_id="compute_centroid_coordinates", operation="compute_centroid_coordinates", answer_type="coordinate_pair", presentation_mode="short_answer", checker_key="coordinate_pair_checker", equivalence_type="coordinate_pair_equivalence", generator_key="vh_數學B1_DivisionPointCoordinates:compute_centroid_coordinates:draft_v1", seed=seed, component_id=str(kwargs.get("component_id") or "src_4423"))
