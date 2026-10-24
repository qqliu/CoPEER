r"""Multiplying b > 0 by the negative integer a preserves the inequality and yields ab > 0."""

import json


def main():
    a = -1
    b = 1
    product = a * b
    valid_witness = a < 0 and b > 0 and product == -1 and not (product > 0)
    verdict = "CONFIRMED" if valid_witness else "REFUTED_WITNESS_INVALID"
    notes = (
        "Exact integer recomputation at a = -1 and b = 1 gives ab = -1, so b > 0 holds while ab > 0 fails. "
        "The refuted statement is a substantive sign error, not plainly a typo."
        if valid_witness
        else
        "The reported witness did not independently satisfy the assumptions and negate the conclusion. The refuted statement would be substantive, not plainly a typo."
    )
    result = {
        "record_id": "reddit_learnmath_20itsx",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
