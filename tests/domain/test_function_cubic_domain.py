"""function.cubic_graph: each operation's independent validator accepts the computed answer and rejects tampering."""

from __future__ import annotations

import copy

import pytest

from agent_domains_candidate.function_cubic import cubic_domain as D
from agent_domains_candidate.function_cubic.cubic_specs import COMPONENTS


def _matrix(op, givens):
    return D.build_cubic_graph_matrix(domain_operation=op, constraints=givens)


def _valid(matrix):
    return getattr(D, f"validate_{matrix['domain_operation']}_matrix")(matrix)


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_source_variant_validates(cid):
    _skill, op, source, _sampler = COMPONENTS[cid]
    assert _valid(_matrix(op, source))


def _tamper(matrix, path, value):
    bad = copy.deepcopy(matrix)
    node = bad["answer"]
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return bad


def test_center_form_rejects_wrong_values():
    m = _matrix("cubic_center_form", {"items": [{"kind": "to_form", "coeffs": [1, 3, 5, 6]}]})
    assert _valid(m)
    assert not _valid(_tamper(m, ["items", 0, "h", "canonical"], "1"))
    assert not _valid(_tamper(m, ["items", 0, "p", "canonical"], "5"))
    shift = _matrix("cubic_center_form", {"items": [{"kind": "shift", "form": {"a": 1, "p": -2, "h": -1, "k": 5}, "dx": 3, "dy": -4, "power": 1}]})
    assert shift["answer"]["items"][0]["asked_coeff"]["canonical"] == "10" and _valid(shift)
    assert not _valid(_tamper(shift, ["items", 0, "asked_coeff", "canonical"], "9"))
    overlap = _matrix("cubic_center_form", {"items": [{"kind": "translation_overlap", "f": {"a": 1, "p": -4, "h": 0, "k": 0}, "g": {"a": 1, "p": -3, "h": 1, "k": 1}}]})
    assert overlap["answer"]["items"][0]["overlap"] is False and _valid(overlap)
    assert not _valid(_tamper(overlap, ["items", 0, "overlap"], True))


def test_conditions_reject_wrong_values():
    m = _matrix("cubic_from_conditions", {"items": [{"kind": "symmetric_pair_origin", "A": [1, 25], "B": [7, 7], "C_x": 9}]})
    assert _valid(m) and m["answer"]["items"][0]["s"]["canonical"] == "81"
    assert not _valid(_tamper(m, ["items", 0, "s", "canonical"], "80"))
    assert not _valid(_tamper(m, ["items", 0, "center", "x"], "3"))
    with pytest.raises(ValueError):
        _matrix("cubic_from_conditions", {"items": [{"kind": "center_zero_linear", "center": [0, 1]}]})


def test_statements_reject_flipped_truths_and_undecidable_free_parameters():
    st = [{"kind": "center_is", "x": 4, "y": 5}, {"kind": "odd_function"}, {"kind": "global_extremum", "claim": "none"}]
    m = _matrix("cubic_statements", {"subject": {"type": "form", "a": 2, "p": 3, "h": 4, "k": 5}, "statements": st})
    assert m["answer"]["truths"] == [True, False, True] and _valid(m)
    assert not _valid(_tamper(m, ["truths"], [True, True, True]))
    with pytest.raises(ValueError):  # truth would depend on the free parameters c, d
        _matrix("cubic_statements", {"subject": {"type": "free_cd", "coeffs": [3, -5]}, "statements": [{"kind": "local_line", "x0": 1, "m": 1, "n": 0}]})


def test_matching_rejects_a_mislabelled_figure():
    funcs = [{"coeffs": [-1, 0, 0, 0]}, {"coeffs": [2, 0, 0, 0]}, {"coeffs": [-2, 0, 0, 0]}]
    m = _matrix("cubic_curve_matching", {"kind": "match", "functions": funcs, "order": [1, 2, 0], "window": {"x": 2, "y": 8}})
    assert _valid(m) and m["answer"]["assignment"] == [3, 1, 2]
    assert not _valid(_tamper(m, ["assignment"], [1, 2, 3]))
    swapped = copy.deepcopy(m)
    swapped["answer"]["gammas"][0]["points"] = swapped["answer"]["gammas"][1]["points"]  # Γ1 secretly drawn as Γ2's curve
    assert not _valid(swapped)
    with pytest.raises(ValueError):
        _matrix("cubic_curve_matching", {"kind": "match", "functions": [{"coeffs": [1, 0, 0, 0]}, {"coeffs": [1, 0, 0, 0]}], "order": [0, 1], "window": {"x": 2, "y": 8}})
