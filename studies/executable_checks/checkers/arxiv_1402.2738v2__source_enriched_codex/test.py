"""Every ideal lattice from an imaginary quadratic number field is semi-stable."""

import json

RECORD_ID = "arxiv_1402.2738v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness found; the supplied source contains no concrete value of D "
    "or concrete ideal I to test."
)
REFUTATION_EXPLANATION = (
    "The quote does not define the ideal-lattice construction or the predicate "
    "semi-stable, so it supplies no exact criterion with which a Python program "
    "could decide whether any candidate violates the claim."
)
SEARCH_SPACE = (
    "The empty finite set of concrete (D, I) instances explicitly supplied by "
    "the source quote; all mentioned quantities are symbolic."
)


def main():
    concrete_instances = ()
    checked = 0
    for _candidate in concrete_instances:
        checked += 1
    assert checked == len(concrete_instances) == 0

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
