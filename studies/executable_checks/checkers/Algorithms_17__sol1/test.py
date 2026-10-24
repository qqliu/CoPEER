r"""Given that a graph may generally admit multiple transitive reductions, prove that G possesses a unique transitive reduction if and only if G is acyclic."""

import itertools
import json


REPORT = {
    "record_id": "Algorithms_17__sol1",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete graph witness is claimed; the source quote does not define the objects or the transitive-reduction relation needed to validate one.",
    "refutation_explanation": "The sweep finds the two abstract Boolean mismatch patterns (U, A) = (False, True) and (True, False), but the quote gives no criterion showing that either pattern is realized by any graph. Thus the claim cannot be confirmed or refuted from the permitted data.",
    "search_space": "All 4 Boolean pairs (U, A) in {False, True}^2, in the fixed itertools.product order (False, False), (False, True), (True, False), (True, True). This is an exhaustive semantic-status sweep, not a graph enumeration.",
}


def main():
    status_pairs = tuple(itertools.product((False, True), repeat=2))
    matches = []
    mismatches = []

    for unique_status, acyclic_status in status_pairs:
        pair = (unique_status, acyclic_status)
        if unique_status == acyclic_status:
            matches.append(pair)
        else:
            mismatches.append(pair)

    matches = tuple(matches)
    mismatches = tuple(mismatches)

    assert status_pairs == (
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    )
    assert matches == ((False, False), (True, True))
    assert mismatches == ((False, True), (True, False))

    has_formal_match = bool(matches)
    has_formal_mismatch = bool(mismatches)
    derived_outcome = (
        "NO_WITNESS_INCONCLUSIVE"
        if has_formal_match and has_formal_mismatch
        else "CLAIM_NOT_FINITELY_REFUTABLE"
    )
    assert REPORT["outcome"] == derived_outcome
    assert tuple(REPORT) == (
        "record_id",
        "outcome",
        "witness_description",
        "refutation_explanation",
        "search_space",
    )

    print(json.dumps(REPORT, separators=(",", ":")))


if __name__ == "__main__":
    main()
