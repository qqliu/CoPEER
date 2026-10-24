"""The x-axis is transformed by L(x,y)=(x,x+y) into the line x+y=0."""

import json


def transform(x, y):
    return (x, x + y)


def main():
    candidates = [(x, 0) for x in range(-3, 4)]
    violations = []

    for point in candidates:
        image = transform(point[0], point[1])
        if image[0] + image[1] != 0:
            violations.append((point, image, image[0] + image[1]))

    point, image, coordinate_sum = violations[0]
    assert point == (-3, 0)
    assert image == (-3, -3)
    assert coordinate_sum == -6

    result = {
        "record_id": "proofwiki_120506__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The x-axis point (-3,0) maps under L to (-3,-3), and (-3)+(-3)=-6, not 0.",
        "refutation_explanation": "An image of the x-axis under L would have to consist entirely of points satisfying x+y=0. The image L(-3,0)=(-3,-3) does not satisfy that equation, so the claimed transformed line is incorrect.",
        "search_space": "All 7 integer points (x,0) with -3 <= x <= 3, tested in increasing x order using exact integer arithmetic."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
