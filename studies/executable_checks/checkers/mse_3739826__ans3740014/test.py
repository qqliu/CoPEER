r"""$k\geq 5$ and $A':=\{0,2\}\cup[4,2k+2]$;"""

import json

RECORD_ID = "mse_3739826__ans3740014"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is definable: the quote supplies only the condition k >= 5 "
    "and a definition of A', but no asserted property whose failure would "
    "constitute a counterexample."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep can instantiate the supplied definition exactly, but "
    "the source gives no proposition about A' to test. Therefore neither a "
    "witness nor exhaustive evidence for the claim can be produced."
)
SEARCH_SPACE = (
    "All 96 integer parameters k in {5,6,...,100}; for each k, the uniquely "
    "defined pair (k,A') was constructed with A' = {0,2} union the integer "
    "interval {4,5,...,2k+2}. This finite sweep is illustrative only because "
    "no counterexample predicate is supplied."
)


def main():
    swept = []
    for k in range(5, 101):
        a_prime = {0, 2}
        for value in range(4, 2 * k + 3):
            a_prime.add(value)
        expected = {
            value
            for value in range(0, 2 * k + 3)
            if value == 0 or value == 2 or 4 <= value <= 2 * k + 2
        }
        if a_prime != expected:
            raise AssertionError("exact definition encoding failed")
        swept.append((k, a_prime))

    if len(swept) != 96:
        raise AssertionError("bounded space was not swept exactly")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
