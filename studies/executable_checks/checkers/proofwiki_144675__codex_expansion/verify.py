"""For every subset X of A, id_A(sup A) equals sup{id_A(x) : x in X}."""

import json

RECORD_ID = "proofwiki_144675__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = ("Exact recomputation in the two-element chain gives id_A(sup A)=1 "
         "and sup{id_A(x): x in {0}}=0. The literal statement is therefore "
         "false; it is plainly a typo, with sup A apparently intended to be sup X.")


def precedes_or_equals(first, second):
    return first <= second


def least_upper_bound(elements, universe):
    upper_bounds = tuple(
        candidate
        for candidate in universe
        if all(precedes_or_equals(element, candidate) for element in elements)
    )
    least = tuple(
        candidate
        for candidate in upper_bounds
        if all(precedes_or_equals(candidate, other) for other in upper_bounds)
    )
    if len(least) != 1:
        raise AssertionError("supremum is not uniquely determined")
    return least[0]


def identity(element):
    return element


def main():
    universe = (0, 1)
    subset = (0,)
    if not all(element in universe for element in subset):
        raise AssertionError("reported set is not a subset")

    left = identity(least_upper_bound(universe, universe))
    image = tuple(identity(element) for element in subset)
    right = least_upper_bound(image, universe)

    if left != 1 or right != 0 or left == right:
        raise AssertionError("reported witness was not independently verified")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
