"""For every natural number x, x+2 < -x²+x³."""

import json


def main():
    candidates = range(1, 2)
    witness = None
    for x in candidates:
        left = x + 2
        right = -(x ** 2) + (x ** 3)
        if not left < right:
            witness = x
            break

    if witness == 1:
        result = {
            "record_id": "reddit_mathematics_14r91pk",
            "outcome": "WITNESS_FOUND",
            "witness_description": "x = 1 is a natural number and is a counterexample.",
            "refutation_explanation": "At x = 1, x+2 = 3 while -x²+x³ = -(1²)+(1³) = 0, so the claimed strict inequality becomes 3 < 0, which is false.",
            "search_space": "The explicitly bounded finite space {1}, swept exhaustively in increasing order."
        }
    else:
        result = {
            "record_id": "reddit_mathematics_14r91pk",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found in {1}.",
            "refutation_explanation": "The sole candidate satisfied the claimed inequality.",
            "search_space": "The explicitly bounded finite space {1}, swept exhaustively in increasing order."
        }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
