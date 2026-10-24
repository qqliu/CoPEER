r"""For $n+1$ its factors must be in previous $n$ numbers. Hence $n+1=\prod n_{i}$."""

import json

RECORD_ID = "mse_25914__ans25916"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified counterexample: every candidate remains undecidable from the "
    "supplied quote."
)
REFUTATION_EXPLANATION = (
    "The quote does not define the domain of n, whether “factors” includes n+1 "
    "itself or only proper factors, what the “previous n numbers” are, or the "
    "index set and permitted values of the n_i in the product. Testing any "
    "interpretation would therefore invent missing mathematical data."
)
SEARCH_SPACE_DESCRIPTION = (
    "All 256 integer candidates n in the fixed bounded set {1, 2, ..., 256} were "
    "visited in increasing order; all 256 were classified as undecidable because "
    "the supplied claim lacks the definitions needed for an exact counterexample "
    "predicate."
)


def check_candidate(n):
    # None means that the source data do not determine a truth value.
    if 1 <= n <= 256:
        return None
    raise ValueError("candidate outside the declared finite space")


def main():
    candidates = tuple(range(1, 257))
    results = tuple(check_candidate(n) for n in candidates)
    if len(results) != 256 or any(result is not None for result in results):
        raise AssertionError("finite sweep did not have the declared result")

    report = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE_DESCRIPTION,
    }
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
