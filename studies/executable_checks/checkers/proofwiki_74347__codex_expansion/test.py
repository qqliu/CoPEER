"""For every integer n, there exists a nonnegative integer m such that 3^m + 1 ≤ |2n| ≤ 3^(m+1) − 1."""

import json

RECORD_ID = "proofwiki_74347__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "n = 0."
REFUTATION_EXPLANATION = (
    "For n = 0, |2n| = 0. For every nonnegative integer m, 3^m is at least 1, "
    "so 3^m + 1 is at least 2 and therefore cannot be at most 0. Thus no "
    "permitted m exists."
)
SEARCH_SPACE = (
    "The singleton bounded space of candidate integers n = {0} was swept in fixed order. "
    "Its sole candidate was checked exactly; the nonexistence of m is certified for all "
    "nonnegative integers m by 3^m + 1 >= 2 > |2*0| = 0."
)


def is_counterexample(n):
    value = abs(2 * n)
    if value != 0:
        return False
    # For every m >= 0, 3**m >= 1, hence 3**m + 1 >= 2 > value.
    return 3 ** 0 + 1 > value


def main():
    witness = None
    for n in range(0, 1):
        if is_counterexample(n):
            witness = n
            break

    if witness != 0:
        raise AssertionError("the exhaustive singleton search did not find n = 0")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
