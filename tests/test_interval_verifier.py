from core.verifiers.interval_verifier import verify


def test_interval_verifier() -> None:
    out = verify()
    assert out["success"] is True
    assert out["cases_total"] >= 6
    assert out["cases_passed"] == out["cases_total"]

