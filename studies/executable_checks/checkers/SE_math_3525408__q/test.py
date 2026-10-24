"""when $P_j$ hits a vertex, $v$, on a previous maximal path, it must follow along with that path to its end or reverse course
   along that path to its beginning"""

import json

TARGET_CLAIM = (
    "when $P_j$ hits a vertex, $v$, on a previous maximal path, it must "
    "follow along with that path to its end or reverse course\n"
    "   along that path to its beginning"
)
SOURCE_QUOTE = TARGET_CLAIM

WITNESS_DESCRIPTION = (
    "No counterexample can be certified from the supplied quote alone."
)
REFUTATION_EXPLANATION = (
    "The quote supplies no definitions of P_j, maximal path, previous, hits, "
    "follow along, end, beginning, or reverse course, and gives no ambient "
    "graph or path-construction rules. Consequently it does not determine "
    "which finite objects are admissible or how to decide whether an object "
    "violates the claim."
)
SEARCH_SPACE = (
    "Exactly one supplied-data case was swept: the ordered pair "
    "(target_claim, source_quote), whose two entries are identical. No "
    "mathematical graph/path instances were enumerated because the quote "
    "specifies no admissible instance space or decidable semantics."
)


def main():
    bounded_cases = ((TARGET_CLAIM, SOURCE_QUOTE),)
    identical_entries = True
    examined = 0
    for target_claim, source_quote in bounded_cases:
        examined += 1
        if target_claim != source_quote:
            identical_entries = False
    if examined != 1 or not identical_entries:
        raise AssertionError("unexpected supplied-data case")

    result = {
        "record_id": "SE_math_3525408__q",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
