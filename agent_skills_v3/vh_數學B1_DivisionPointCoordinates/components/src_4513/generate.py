from typing import Any
from agent_skills_v3.vh_數學B1_DivisionPointCoordinates.component_runtime import generate_component
def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_component(source_id=4513, problem_type_id="compute_section_point_distance_from_origin", operation="compute_section_point_distance_from_origin", answer_type="choice", presentation_mode="single_choice", checker_key="choice_label_checker", equivalence_type="choice_label", generator_key="vh_數學B1_DivisionPointCoordinates:compute_section_point_distance_from_origin:draft_v1", seed=seed, component_id=str(kwargs.get("component_id") or "src_4513"))
