"""Practice answer surface must obey the formal question-type contract.

Drawing questions (free_response_drawing_checker / drawing answer_type /
canvas presentation) render a disabled, greyed text box with a drawing hint
and grade through the visual path; short answer, MCQ and multipart keep their
existing surfaces. Routing is contract-driven only (no skill_id / stem text).
"""
from __future__ import annotations

import ast
import copy
import importlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "index.html"
DRAWING_CHECKER_SRC = ROOT / "core" / "checkers" / "free_response_drawing_checker.py"
DRAWING_HINT = "請在下方作圖區作答"
LINEAR_SKILL = "vh_數學B1_LinearFunction"


def _source() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def _function_body(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    brace = source.index("{", start)
    depth = 0
    for idx in range(brace, len(source)):
        if source[idx] == "{":
            depth += 1
        elif source[idx] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : idx + 1]
    raise AssertionError(f"function body not found: {name}")


def _js_string_array(body: str, name: str) -> set[str]:
    match = re.search(rf"const {name} = \[([^\]]*)\]", body)
    assert match, name
    return set(re.findall(r"'([^']+)'", match.group(1)))


def _backend_drawing_sets() -> tuple[set[str], set[str]]:
    tree = ast.parse(DRAWING_CHECKER_SRC.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "is_drawing_answer_contract")
    found: dict[str, set[str]] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and isinstance(node.comparators[0], ast.Set):
            found[node.left.id] = {elt.value for elt in node.comparators[0].elts}
    return found["answer_type"], found["presentation_mode"]


# --------------------------------------------------------------------------- frontend routing


def test_drawing_guard_mirrors_backend_drawing_contract() -> None:
    body = _function_body(_source(), "isDrawingQuestion")
    answer_types, presentation_modes = _backend_drawing_sets()

    assert _js_string_array(body, "DRAWING_ANSWER_TYPES") == answer_types
    assert _js_string_array(body, "DRAWING_PRESENTATION_MODES") == presentation_modes
    assert "contract.checker_key === 'free_response_drawing_checker'" in body
    assert "equivalence === 'drawing_equivalence'" in body
    assert "ui.response_mode === 'drawing'" in body


@pytest.mark.parametrize(
    "name",
    ["isDrawingQuestion", "resolveDrawingUiContract", "applyDrawingUiContract", "applyMultiPartUiContract"],
)
def test_answer_surface_routing_has_no_skill_or_stem_hardcode(name: str) -> None:
    body = _function_body(_source(), name)
    stem_matchers = ("includes('畫", 'includes("畫', "/畫", "includes('圖", 'includes("圖', "resolveQuestionText")
    for forbidden in ("skill_id", "LinearFunction", "vh_數學", "question_text", "problem_type", *stem_matchers):
        assert forbidden not in body, f"{name} must stay contract-driven ({forbidden!r})"


def test_drawing_question_disables_text_input_with_drawing_hint() -> None:
    source = _source()
    resolve = _function_body(source, "resolveDrawingUiContract")
    apply = _function_body(source, "applyDrawingUiContract")

    assert "textInputEnabled: drawing ? (ui.text_input_enabled === true)" in resolve
    assert "normalSubmitEnabled: drawing ? (ui.normal_submit_enabled === true)" in resolve
    assert "answerInput.disabled = !uiContract.textInputEnabled;" in apply
    assert "answerInput.readOnly = !uiContract.textInputEnabled;" in apply
    assert "(drawing || isDrawingQuestion(cq)) && !uiContract.textInputEnabled" in apply
    assert 'answerInput.classList.toggle("answer-input--drawing", drawingSurface);' in apply
    drawing_branch = apply[apply.index("if (drawingSurface) {") : apply.index("} else if (!uiContract.textInputEnabled) {")]
    assert f'answerInput.placeholder = "{DRAWING_HINT}";' in drawing_branch
    assert 'answerInput.value = "";' in drawing_branch
    assert DRAWING_HINT not in apply[apply.index("} else if (!uiContract.textInputEnabled) {") :]
    assert "submitBtn.disabled = !uiContract.normalSubmitEnabled;" in apply
    assert "#answer-input.answer-input--drawing" in source


def test_single_field_surface_defers_to_drawing_contract_before_enabling() -> None:
    body = _function_body(_source(), "applyMultiPartUiContract")
    choice_branch = body.index("if (isChoice) {")
    drawing_branch = body.index("} else if (isDrawingQuestion(currentPayload)) {")
    generic_enable = body.index("answerInput.disabled = false;")

    assert choice_branch < drawing_branch < generic_enable
    assert "applyDrawingUiContract();" in body[drawing_branch:generic_enable]
    assert "answerInput.readOnly = false;" in body[generic_enable:]


def test_load_question_generic_enable_does_not_override_drawing_contract() -> None:
    body = _function_body(_source(), "loadQuestion")
    step = body.index("if (data.answer_type === 'handwriting') {")
    guard = body.index("} else if (!isDrawingQuestion(data)) {", step)
    enable = body.index("answerInput.disabled = false;", step)
    reapply = body.index("applyMultiPartUiContract(data);", step)

    assert step < guard < enable < reapply
    assert "} else {\n                        answerInput.disabled = false;" not in body[step:reapply]


def test_frontend_snapshot_keeps_formal_ui_contract() -> None:
    body = _function_body(_source(), "snapshotPracticeQuestion")
    assert "ui_contract: payload.ui_contract" in body
    assert "answer_contract: payload.answer_contract" in body


def test_drawing_question_uses_visual_grading_path() -> None:
    source = _source()
    submit_body = _function_body(source, "setupSubmit")
    ai_body = _function_body(source, "setupAIButton")
    payload_body = _function_body(source, "buildDrawingCheckAnswerPayload")

    assert submit_body.index("submitDrawingAnswerFromCanvas('submit-button')") < submit_body.index("fetch('/check_answer'")
    assert ai_body.index("submitDrawingAnswerFromCanvas('ai-check-button')") < ai_body.index("fetch('/analyze_handwriting'")
    assert 'answer: "[drawing]"' in payload_body
    assert "composite_image_data_url" in payload_body
    assert "expected_drawing_spec" not in payload_body


# --------------------------------------------------------------------------- runtime payload contract


def _deliver(skill_id: str, component_id: str, seed: int = 11) -> dict:
    import core.routes.practice as practice
    from core.legacy_generator_adapter import normalize_runtime_value

    mod = importlib.import_module(f"skills.{skill_id}")
    data = practice._canonicalize_route_payload(normalize_runtime_value(mod.generate(level=1, seed=seed, component_id=component_id)))
    data = practice._normalize_gencode_runtime_payload(dict(data), skill_id=skill_id)
    return practice._finalize_practice_question_api_fields(data, skill_id=skill_id)


def _merged_ui(payload: dict) -> dict:
    ac = payload.get("answer_contract") or {}
    nested = ac.get("ui_contract") if isinstance(ac.get("ui_contract"), dict) else {}
    top = payload.get("ui_contract") if isinstance(payload.get("ui_contract"), dict) else {}
    return {**nested, **top}


def _is_drawing(payload: dict) -> bool:
    from core.checkers.free_response_drawing_checker import is_drawing_answer_contract

    return is_drawing_answer_contract(payload.get("answer_contract") or {}, payload)


@pytest.mark.parametrize(
    ("component_id", "problem_type_id"),
    [
        ("src_4433", "draw_constant_function_graph"),
        ("src_4448", "draw_constant_function_graph"),
        ("src_4434", "draw_linear_function_graph"),
        ("src_4449", "draw_linear_function_graph"),
    ],
)
def test_drawing_payload_carries_disabled_text_input_contract(component_id: str, problem_type_id: str) -> None:
    payload = _deliver(LINEAR_SKILL, component_id)
    ui = _merged_ui(payload)

    assert payload["problem_type_id"] == problem_type_id
    assert _is_drawing(payload)
    assert ui.get("response_mode") == "drawing"
    assert ui.get("text_input_enabled") is False
    assert ui.get("normal_submit_enabled") is False
    assert ui.get("ai_check_required") is True
    assert payload["answer_contract"]["checker"] == "free_response_drawing_checker"
    assert payload["answer_contract"]["expected_drawing_spec"]["drawing_type"] == "line_graph"
    assert not payload.get("choices")


# (skill, component, expected surface) — representative B1–B4 non-drawing contracts.
NON_DRAWING_MATRIX = [
    ("vh_數學B2_ArcLengthAndAreaOfSector", "src_11624", "short"),
    ("vh_數學B3_PlainHeading_3_2_2", "src_12124", "short"),
    ("vh_數學B1_AbsoluteValueInequality", "src_4499", "choice"),
    ("vh_數學B3_PlainHeading_3_2_2", "src_12065", "choice"),
    ("vh_數學B4_CentralTendencyMeasures", "src_3887", "choice"),
    ("vh_數學B1_LinearFunction", "src_4516", "choice"),
    ("vh_數學B2_AngleMeasurementAndConversion", "src_11606", "multipart"),
    ("vh_數學B4_CumulativeFrequencyTablesAndGraphs", "src_3830", "multipart"),
    ("vh_數學B1_LinearFunction", "src_4424", "multipart"),
]


@pytest.mark.parametrize(("skill_id", "component_id", "surface"), NON_DRAWING_MATRIX)
def test_non_drawing_contracts_keep_their_surface(skill_id: str, component_id: str, surface: str) -> None:
    payload = _deliver(skill_id, component_id)
    ui = _merged_ui(payload)
    parts = (payload.get("answer_contract") or {}).get("parts") or []

    assert not _is_drawing(payload)
    assert ui.get("response_mode") != "drawing"
    assert not payload.get("expected_drawing_spec")
    if surface == "choice":
        assert len(payload.get("choices") or []) == 4
    elif surface == "multipart":
        keys = [str(p.get("key") or "") for p in parts]
        assert len(keys) >= 2 and all(keys) and len(keys) == len(set(keys))
        assert ui.get("text_input_enabled") is not False
        assert not payload.get("choices")
    else:
        assert ui.get("text_input_enabled") is not False
        assert not parts
        assert not payload.get("choices")


# --------------------------------------------------------------------------- executed frontend routing


def _node() -> str | None:
    node = shutil.which("node")
    if node:
        return node
    candidates = sorted((Path.home() / ".cache" / "codex-runtimes").glob("*/dependencies/node/bin/node.exe"))
    return str(candidates[0]) if candidates else None


def _function_source(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    body = _function_body(source, name)
    return source[start : source.index(body, start) + len(body)]


ROUTING_FUNCTIONS = (
    "getTableQuestionModel", "isTableFillQuestion", "resolveMultiPartFields", "isMultiPartQuestion",
    "getChoiceItems", "isChoiceQuestionPayload", "snapshotPracticeQuestion", "getMergedUiContract",
    "isDrawingQuestion", "resolveAiCheckRequired", "resolveDrawingUiContract",
    "applyAnalyzeButtonVisibility", "applyDrawingUiContract", "applyMultiPartUiContract",
)

HARNESS = r"""
const makeEl = () => {
  const cls = new Set();
  return {
    disabled: false, readOnly: false, hidden: false, value: 'typed', placeholder: '', title: '',
    style: { display: '', removeProperty() {} }, attrs: {},
    classList: {
      add: (c) => cls.add(c), remove: (c) => cls.delete(c), contains: (c) => cls.has(c),
      toggle: (c, on) => (on ? cls.add(c) : cls.delete(c)),
    },
    setAttribute(k, v) { this.attrs[k] = v; }, removeAttribute(k) { delete this.attrs[k]; },
  };
};
const window = {};
const document = { getElementById: () => null };
const answerInput = makeEl(), submitBtn = makeEl(), analyzeBtn = makeEl();
const subquestionsContainer = null;
let currentQuestion = null;
let renderedFieldKeys = [];
const noop = () => {};
const clearTableQuestionState = noop, renderTableQuestion = noop, clearSubquestionInputs = noop, scheduleResizeCanvas = noop;
const resolveQuestionText = (p) => String((p && p.question_text) || '');
const resolvePracticeResponseLevel = () => 1;
const getSkillId = () => '';
function renderSubquestionInputs(payload) {
  renderedFieldKeys = resolveMultiPartFields(payload).map((f) => f.key);
  answerInput.style.display = 'none'; answerInput.disabled = true; answerInput.value = '';
}
__FUNCTIONS__
function loadQuestionAnswerSurface(data) {
  currentQuestion = snapshotPracticeQuestion(data);
  answerInput.value = 'typed';
  applyMultiPartUiContract(data);
  applyDrawingUiContract();
  __STEP5__
}
const out = JSON.parse(require('fs').readFileSync(0, 'utf8')).map((payload) => {
  renderedFieldKeys = [];
  loadQuestionAnswerSurface(payload);
  return {
    isDrawing: isDrawingQuestion(currentQuestion), disabled: answerInput.disabled, readOnly: answerInput.readOnly,
    value: answerInput.value, placeholder: answerInput.placeholder, display: answerInput.style.display,
    drawingClass: answerInput.classList.contains('answer-input--drawing'),
    submitDisabled: submitBtn.disabled, analyzeHidden: analyzeBtn.hidden, fieldKeys: renderedFieldKeys,
  };
});
process.stdout.write(JSON.stringify(out));
"""


def _run_frontend_routing(payloads: list[dict]) -> list[dict]:
    node = _node()
    if not node:
        pytest.skip("Node.js runtime not available")
    source = _source()
    load_body = _function_body(source, "loadQuestion")
    step_start = load_body.index("if (data.answer_type === 'handwriting') {")
    step_end = load_body.index("applyMultiPartUiContract(data);", step_start) + len("applyMultiPartUiContract(data);")
    script = HARNESS.replace("__FUNCTIONS__", "\n".join(_function_source(source, n) for n in ROUTING_FUNCTIONS))
    script = script.replace("__STEP5__", load_body[step_start:step_end])
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "answer_surface_harness.js"
        script_path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            [node, str(script_path)],
            input=json.dumps(payloads, ensure_ascii=False, default=str),
            check=True, capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def routed_surfaces() -> dict[str, dict]:
    cases = {
        "drawing_constant": _deliver(LINEAR_SKILL, "src_4433"),
        "drawing_linear": _deliver(LINEAR_SKILL, "src_4434"),
        "short_b2": _deliver("vh_數學B2_ArcLengthAndAreaOfSector", "src_11624"),
        "short_b3": _deliver("vh_數學B3_PlainHeading_3_2_2", "src_12124"),
        "choice_b1": _deliver("vh_數學B1_AbsoluteValueInequality", "src_4499"),
        "choice_b4": _deliver("vh_數學B4_CentralTendencyMeasures", "src_3887"),
        "multipart_b2": _deliver("vh_數學B2_AngleMeasurementAndConversion", "src_11606"),
        "multipart_graph_b1": _deliver(LINEAR_SKILL, "src_4424"),
    }
    names = list(cases)
    # Replay drawing -> short answer on the same DOM to prove the drawing lock is released.
    sequence = names + ["drawing_constant", "short_b2"]
    results = _run_frontend_routing([cases[n] for n in sequence])
    surfaces = dict(zip(names, results[: len(names)]))
    surfaces["after_drawing_short"] = results[-1]
    surfaces["_payloads"] = cases
    return surfaces


@pytest.mark.parametrize("case", ["drawing_constant", "drawing_linear"])
def test_executed_routing_drawing_disables_text_input(routed_surfaces, case: str) -> None:
    s = routed_surfaces[case]
    assert s["isDrawing"] is True
    assert s["disabled"] is True and s["readOnly"] is True
    assert s["value"] == ""
    assert s["placeholder"] == DRAWING_HINT
    assert s["display"] == ""
    assert s["drawingClass"] is True
    assert s["submitDisabled"] is True
    assert s["analyzeHidden"] is False


@pytest.mark.parametrize("case", ["short_b2", "short_b3", "after_drawing_short"])
def test_executed_routing_short_answer_keeps_enabled_input(routed_surfaces, case: str) -> None:
    s = routed_surfaces[case]
    assert s["isDrawing"] is False
    assert s["disabled"] is False and s["readOnly"] is False
    assert s["placeholder"] == "請在此輸入答案"
    assert s["display"] == ""
    assert s["drawingClass"] is False
    assert s["submitDisabled"] is False


@pytest.mark.parametrize("case", ["choice_b1", "choice_b4"])
def test_executed_routing_choice_hides_text_input(routed_surfaces, case: str) -> None:
    s = routed_surfaces[case]
    assert s["isDrawing"] is False
    assert s["display"] == "none" and s["disabled"] is True
    assert s["drawingClass"] is False
    assert s["submitDisabled"] is False


@pytest.mark.parametrize("case", ["multipart_b2", "multipart_graph_b1"])
def test_executed_routing_multipart_keeps_part_keys(routed_surfaces, case: str) -> None:
    s = routed_surfaces[case]
    parts = routed_surfaces["_payloads"][case]["answer_contract"]["parts"]
    assert s["isDrawing"] is False
    assert s["display"] == "none"
    assert s["drawingClass"] is False
    assert s["submitDisabled"] is False
    assert s["fieldKeys"] == [str(p["key"]) for p in parts]


def test_text_answer_cannot_substitute_for_drawing() -> None:
    from core.gencode.answer_grading import grade_answer_for_current_question
    from core.gencode.answer_payload import refresh_runtime_question_session

    payload = _deliver(LINEAR_SKILL, "src_4433", seed=4433)
    constant = payload["answer_contract"]["expected_drawing_spec"]["y_intercept"]
    current = refresh_runtime_question_session(copy.deepcopy(payload), skill_id=LINEAR_SKILL)
    res = grade_answer_for_current_question({"answer": f"y={constant}"}, current, LINEAR_SKILL)

    assert res.get("correct") is not True
    assert res.get("checker") == "free_response_drawing_checker"
