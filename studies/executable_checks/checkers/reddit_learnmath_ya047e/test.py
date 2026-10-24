"""1 is the largest natural number."""

import json


def main():
    candidates = (2,)
    witness = None
    for candidate in candidates:
        if candidate > 1:
            witness = candidate
            break

    if witness is None:
        result = {
            "record_id": "reddit_learnmath_ya047e",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "2 is a natural number greater than 1.",
            "refutation_explanation": "The bounded search finds 2, and 2 > 1; therefore 1 is not the largest natural number.",
            "search_space": "Exactly the one-element candidate space (2,), checked in tuple order."
        }
    else:
        result = {
            "record_id": "reddit_learnmath_ya047e",
            "outcome": "WITNESS_FOUND",
            "witness_description": "2 is a natural number greater than 1.",
            "refutation_explanation": "The bounded search finds 2, and 2 > 1; therefore 1 is not the largest natural number.",
            "search_space": "Exactly the one-element candidate space (2,), checked in tuple order."
        }

    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
