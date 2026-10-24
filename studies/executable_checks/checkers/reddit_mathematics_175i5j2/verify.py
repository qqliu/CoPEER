"""From (a - b)^2 = (b - a)^2, taking square roots implies a - b = b - a."""

import json


def main():
    a = -2
    b = -1
    first_difference = a - b
    second_difference = b - a
    first_square = first_difference * first_difference
    second_square = second_difference * second_difference

    assert first_difference == -1
    assert second_difference == 1
    assert first_square == 1
    assert second_square == 1
    assert first_square == second_square
    assert first_difference != second_difference

    result = {
        "record_id": "reddit_mathematics_175i5j2",
        "verdict": "CONFIRMED",
        "notes": "The witness is valid over the integers (and hence the reals). The refuted statement is substantive, not plainly a typo: taking square roots yields absolute values, so equality of squares does not imply equality of the signed bases."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
