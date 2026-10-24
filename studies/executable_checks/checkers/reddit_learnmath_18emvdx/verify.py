r"""The displayed equality chain for x + y is valid for arbitrary integers k and j, including the step that replaces 2j by 2k."""

import json


def main():
    k = -2
    j = -1

    x = 2 * k + 1
    y = 2 * j + 1
    unreplaced = x + y
    replaced = 2 * k + 2 * k + 2

    established = (
        isinstance(k, int)
        and isinstance(j, int)
        and unreplaced == -4
        and replaced == -6
        and unreplaced != replaced
    )

    if established:
        verdict = "CONFIRMED"
        notes = "Exact integer recomputation at k = -2, j = -1 gives (2k + 1) + (2j + 1) = -4 but 2k + 2k + 2 = -6, so the asserted equality fails. In the displayed chain, replacing 2j with 2k is plainly a typo; the correct middle expression is 2k + 2j + 2."
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "The reported witness could not be established by exact integer recomputation."

    result = {
        "record_id": "reddit_learnmath_18emvdx",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
