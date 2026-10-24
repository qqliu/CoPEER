r"""Line 0035 equates the preceding sum of square roots of squared component errors with the sum of the squared absolute component errors."""

import json


def exact_square_root(value):
    if value < 0:
        raise ValueError("negative radicand")
    candidate = 0
    while candidate * candidate < value:
        candidate += 1
    if candidate * candidate != value:
        raise ValueError("radicand is not a perfect square")
    return candidate


def main():
    component_errors = (-3,)
    preceding_total = 0
    squared_absolute_total = 0

    for error in component_errors:
        square = error * error
        preceding_total += exact_square_root(square)
        magnitude = -error if error < 0 else error
        squared_absolute_total += magnitude * magnitude

    assert preceding_total == 3
    assert squared_absolute_total == 9
    assert preceding_total != squared_absolute_total

    result = {
        "record_id": "proofwiki_66731__codex_expansion",
        "verdict": "CONFIRMED",
        "notes": "Exact integer recomputation at error -3 gives sqrt((-3)^2) = 3 and |-3|^2 = 9, so the equality fails. The refuted statement is substantive as written; the evidence does not establish that it is plainly a typo.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
