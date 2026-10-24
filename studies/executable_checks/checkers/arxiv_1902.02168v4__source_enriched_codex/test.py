"""For the stated values a=222 and b=224, the difference b-a equals 12."""

import json


def main():
    cases = ((222, 224, 12),)
    witness = None
    for a, b, claimed_difference in cases:
        actual_difference = b - a
        if actual_difference != claimed_difference:
            witness = (a, b, claimed_difference, actual_difference)
            break

    if witness is None:
        outcome = "NO_WITNESS_EXHAUSTIVE"
        witness_description = "No counterexample was found in the singleton finite space."
        refutation_explanation = "The tested singleton did not violate the claimed equality."
    else:
        a, b, claimed_difference, actual_difference = witness
        outcome = "WITNESS_FOUND"
        witness_description = (
            "The concrete assignment a=222 and b=224 is a witness: exact integer "
            "subtraction gives b-a=224-222=2."
        )
        refutation_explanation = (
            "The claim asserts that b-a equals 12, but for the stated values it equals "
            "2; since 2 != 12, the claim is false."
        )

    result = {
        "record_id": "arxiv_1902.02168v4__source_enriched_codex",
        "outcome": outcome,
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": "Exhaustively swept the singleton finite space {(a,b,claimed_difference)=(222,224,12)}.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
