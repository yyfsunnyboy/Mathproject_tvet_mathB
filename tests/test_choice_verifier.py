from core.verifiers.choice_verifier import verify


def test_choice_verifier() -> None:
    out = verify()
    assert out["success"] is True
    assert out["cases_total"] >= 8
    assert out["cases_passed"] == out["cases_total"]

