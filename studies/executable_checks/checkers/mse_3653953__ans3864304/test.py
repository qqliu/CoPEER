"""With 5 colors, there will always be a non-conflicting color available to choose, regardless of which non-conflicting sequence of colors have been chosen prior."""

import itertools
import json

RECORD_ID = "mse_3653953__ans3864304"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be named because the quote does not define what "
    "is being colored, when two choices conflict, or which prior sequences "
    "and next-choice states are admissible."
)
REFUTATION_EXPLANATION = (
    "The sweep includes the hypothetical state in which none of the five "
    "colors is available, but the supplied quote gives no conflict relation "
    "or admissibility rules with which to decide whether that state can arise. "
    "Consequently it is not a counterexample to the stated claim, and the "
    "bounded sweep cannot settle the claim."
)
SEARCH_SPACE = (
    "All 32 Boolean availability masks for one hypothetical next choice over "
    "the fixed ordered color labels (0, 1, 2, 3, 4), enumerated "
    "lexicographically by itertools.product((0, 1), repeat=5). This is an "
    "exhaustive sweep of those masks only, not of the undefined coloring "
    "situations or prior sequences quantified over by the claim."
)


def main():
    masks_checked = 0
    empty_mask_seen = False
    for mask in itertools.product((0, 1), repeat=5):
        masks_checked += 1
        if all(value == 0 for value in mask):
            empty_mask_seen = True

    assert masks_checked == 32
    assert empty_mask_seen

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
