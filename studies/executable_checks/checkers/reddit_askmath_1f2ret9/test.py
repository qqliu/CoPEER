"""The proof of theorem 1 applies its ε/|C| argument to every constant C, including C=0."""

import json


def main():
    candidates = (0,)
    witness = None
    for constant in candidates:
        denominator = abs(constant)
        if denominator == 0:
            witness = constant
            break

    if witness is None:
        raise AssertionError("The explicitly included candidate C=0 was not detected")

    result = {
        "record_id": "reddit_askmath_1f2ret9",
        "outcome": "WITNESS_FOUND",
        "witness_description": "C=0, for which |C|=0 and the displayed bound ε/|C| is undefined.",
        "refutation_explanation": "The claim explicitly includes C=0, but substituting C=0 makes the denominator |C| equal to zero. Therefore the quoted ε/|C| argument cannot be applied to that constant.",
        "search_space": "The singleton integer space C ∈ {0}, swept exhaustively in fixed tuple order.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
