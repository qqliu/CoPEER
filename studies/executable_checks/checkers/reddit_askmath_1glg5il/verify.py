r"""For all sets A, B, and C, A - (B - C) = (A - C) ∪ (A ∩ B)."""

import json


def main():
    element = 0
    set_a = frozenset((element,))
    set_b = frozenset()
    set_c = frozenset((element,))

    b_minus_c = frozenset(item for item in set_b if item not in set_c)
    left = frozenset(item for item in set_a if item not in b_minus_c)
    a_minus_c = frozenset(item for item in set_a if item not in set_c)
    a_intersect_b = frozenset(item for item in set_a if item in set_b)
    right = a_minus_c.union(a_intersect_b)

    expected_left = frozenset((element,))
    expected_right = frozenset()
    if left != expected_left or right != expected_right or left == right:
        raise AssertionError("independent witness recomputation failed")

    result = {
        "record_id": "reddit_askmath_1glg5il",
        "verdict": "CONFIRMED",
        "notes": "For A = {0}, B = empty, and C = {0}, exact set computation gives left = {0} and right = empty. The witness is valid. The refuted statement is substantive as written, not plainly a typo, although exchanging B and C on the right produces a true identity."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
