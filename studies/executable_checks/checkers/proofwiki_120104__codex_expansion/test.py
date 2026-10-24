"""Absolute net convergence of the generalized sum indexed over all natural numbers to r implies that the series indexed from n=1 is absolutely convergent to the same value r."""

import json


def main():
    # No concrete mathematical instances or operative definitions are supplied.
    candidates = ()
    examined = 0
    for _candidate in candidates:
        examined += 1

    assert examined == 0
    result = {
        "record_id": "proofwiki_120104__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete counterexample can be evaluated from the supplied data.",
        "refutation_explanation": "The target claim and source quote provide no definitions of absolute net convergence or generalized summation and no concrete sequence or value r. Inventing those missing semantics would violate the blind-data constraint, so the claim cannot be tested for a counterexample from the supplied information.",
        "search_space": "The empty set of concrete mathematical instances supplied by the target claim and source quote; exactly 0 candidates were swept."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
