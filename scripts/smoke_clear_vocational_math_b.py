from app import app
from core.routes.admin import _hard_clear_vocational_math_b_core, _vocational_math_b_remaining_check


def main():
    with app.app_context():
        print("=== DRY RUN ===")
        dry = _hard_clear_vocational_math_b_core(execute=False)
        print(dry)

        print("=== EXECUTE ===")
        executed = _hard_clear_vocational_math_b_core(execute=True)
        print(executed)

        print("=== VERIFY ===")
        remaining = _vocational_math_b_remaining_check()
        print(remaining)
        all_clean = all(int(v or 0) == 0 for v in remaining.values())
        print({"all_clean": all_clean})
        assert all_clean is True, f"Not clean yet: {remaining}"


if __name__ == "__main__":
    main()
