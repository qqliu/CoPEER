"""In particular, Agatha can cheat on at most a $p$ fraction of nodes, and we can arrange that this changes the final count by at most $pn$."""

import itertools
import json

RECORD_ID = "SE_cs_68932__a68963"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be specified from the quote alone."
REFUTATION_EXPLANATION = (
    "The quote does not define Agatha, nodes, cheating, the final count, the "
    "quantifiers or domains of p and n, or what arrangements are allowed. "
    "Assigning semantics to those terms would invent data, so the bounded "
    "sweep contains no formally checkable counterexample candidates and is "
    "inconclusive."
)
SEARCH_SPACE = (
    "Exactly itertools.product(range(0), repeat=1): the empty Cartesian "
    "product factor yields 0 candidates, all of which are exhaustively "
    "visited. This empty sweep reflects the absence of defined semantic "
    "candidates and is not evidence that the claim is true."
)


def main():
    visited = 0
    for _candidate in itertools.product(range(0), repeat=1):
        visited += 1
    assert visited == 0
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), sort_keys=False))


if __name__ == "__main__":
    main()
