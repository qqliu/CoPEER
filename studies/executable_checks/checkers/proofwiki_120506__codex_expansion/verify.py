r"""The x-axis is transformed by L(x,y)=(x,x+y) into the line x+y=0."""

import json


def main():
    original = (-3, 0)
    if original[1] != 0:
        raise AssertionError("witness is not on the x-axis")

    first = original[0]
    second = original[0] + original[1]
    image = (first, second)
    coordinate_sum = image[0] + image[1]

    if image != (-3, -3):
        raise AssertionError("incorrect image recomputation")
    if coordinate_sum != -6 or coordinate_sum == 0:
        raise AssertionError("witness does not refute the proposed line")
    if image[0] - image[1] != 0:
        raise AssertionError("actual image-line check failed")

    result = {
        "record_id": "proofwiki_120506__codex_expansion",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation confirms that (-3,0) is on the x-axis, L(-3,0)=(-3,-3), and the image has coordinate sum -6, so it is not on x+y=0. The refuted statement is plainly a sign typo: the actual image line is x-y=0."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
