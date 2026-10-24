"""prog :: Int → Int
    prog 0 = 0
    prog n = let a = n - 1 ; b = prog a
             in
               if   a + 1 <= (b + 1) * (b + 1)
               then b
               else b + 1"""

import json

RECORD_ID = "SE_cs_97637__a97647"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample is identifiable because the supplied text only defines "
    "prog and states no independently checkable property that prog must satisfy."
)
REFUTATION_EXPLANATION = (
    "For nonnegative inputs the displayed recurrence merely determines values "
    "to check against itself. For negative inputs, repeatedly replacing n by "
    "n - 1 moves away from the sole base case 0, but the source does not specify "
    "whether nontermination, partiality, or a total mathematical interpretation "
    "is intended. Therefore the bounded sweep cannot classify any input as "
    "violating the supplied claim."
)
SEARCH_SPACE = (
    "The finite sweep is exactly: every n in {0,...,100} for the base/recurrence "
    "equation checks, and every pair (n,k) with n in {-100,...,-1} and k in "
    "{0,...,100}, checking whether the predecessor-chain state n-k equals 0."
)


def main():
    values = [0]
    for n in range(1, 101):
        a = n - 1
        b = values[a]
        if a + 1 <= (b + 1) * (b + 1):
            values.append(b)
        else:
            values.append(b + 1)

    assert values[0] == 0
    for n in range(1, 101):
        a = n - 1
        b = values[a]
        expected = b if a + 1 <= (b + 1) * (b + 1) else b + 1
        assert values[n] == expected

    for n in range(-100, 0):
        for k in range(0, 101):
            assert n - k != 0

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
