"""The displayed unweighted ℓ² formula defines a metric d₂ on all of the Hilbert cube I^ω."""

import itertools
import json

RECORD_ID = "proofwiki_113885__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take x=(0,0,...) and y=(1,1,...). For every positive integer N, "
    "the Nth partial sum is N, so the displayed series diverges."
)
REFUTATION_EXPLANATION = (
    "Both constant endpoint sequences lie in the Hilbert cube I^ω, but the "
    "displayed unweighted sum is not finite for this pair. Its square root "
    "therefore is not a real-valued distance, so the formula does not define "
    "a metric on all of I^ω."
)
SEARCH_SPACE = (
    "All 4 ordered pairs (x,y) of constant endpoint sequences x_k=a and "
    "y_k=b with (a,b) in {0,1}^2. For each pair, divergence was decided "
    "exactly from the identity S_N=N(a-b)^2; the complete four-pair space "
    "was swept in fixed lexicographic order."
)


def main():
    witnesses = []
    scanned = 0
    for a, b in itertools.product((0, 1), repeat=2):
        scanned += 1
        squared_difference = (a - b) ** 2
        # For these constant sequences, the exact Nth partial sum is
        # N * squared_difference. It is unbounded exactly when this
        # positive integer coefficient is nonzero.
        if squared_difference > 0:
            witnesses.append((a, b))

    assert scanned == 4
    assert witnesses == [(0, 1), (1, 0)]

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=False))


if __name__ == "__main__":
    main()
