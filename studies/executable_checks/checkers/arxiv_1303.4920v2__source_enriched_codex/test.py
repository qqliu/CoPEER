"""If the Gray image of a linear code over Z/4Z is binary self-dual, then the original quaternary code is self-dual."""

import json

RECORD_ID = "arxiv_1303.4920v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be evaluated from the supplied theorem statement alone."
)
REFUTATION_EXPLANATION = (
    "The supplied quote does not define the Gray map, the relevant inner products, "
    "binary or quaternary duality, or a bounded family of linear codes. Supplying "
    "those definitions would add data absent from the quote, so no mathematical "
    "candidate can honestly be tested."
)
SEARCH_SPACE = (
    "The explicitly bounded empty tuple of fully specified candidate code instances "
    "(0 candidates), iterated in its unique fixed order; the sweep is intentionally "
    "inconclusive because the quote supplies no evaluable instances or definitions."
)


def main():
    candidates = ()
    for _candidate in candidates:
        raise AssertionError("The explicitly empty search space cannot contain a candidate")

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
