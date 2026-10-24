"""For every integer n, there exists a nonnegative integer m such that 3^m + 1 ≤ |2n| ≤ 3^(m+1) − 1."""

import json

RECORD_ID = "proofwiki_74347__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = "Exact arithmetic confirms n = 0 is a counterexample: |2n| = 0, while for every nonnegative m, 3^m + 1 >= 2. The refuted statement has a substantive domain error (apparently omitting n != 0), not a plain typo."


def verify_witness():
    n = 0
    magnitude = abs(n + n)

    base = 3
    unit = 1
    minimum_left_side = unit + unit

    # For every nonnegative integer m, 3^m is a product of m copies of
    # base, starting from unit. Since base >= unit, induction under integer
    # multiplication gives 3^m >= unit, hence 3^m + 1 >= 2.
    base_case_holds = unit >= unit
    induction_preserves_bound = base >= unit and unit >= 0
    universal_lower_bound = base_case_holds and induction_preserves_bound

    return (
        n == 0
        and magnitude == 0
        and universal_lower_bound
        and minimum_left_side > magnitude
    )


def main():
    if not verify_witness():
        raise AssertionError("independent exact verification failed")
    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()
