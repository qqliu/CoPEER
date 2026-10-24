"""The stated two-case split exhausts the possible parity counts of previously odd and previously even neighbors when the new node has odd degree."""

import json
import itertools


def stated_split_holds(previously_odd_count, previously_even_count):
    first_case = (
        previously_odd_count % 2 == 0
        and previously_even_count % 2 == 1
    )
    second_case = (
        previously_even_count % 2 == 1
        and previously_odd_count % 2 == 0
    )
    return first_case or second_case


def main():
    witness = None
    for previously_odd_count, previously_even_count in itertools.product(range(2), repeat=2):
        degree = previously_odd_count + previously_even_count
        if degree % 2 == 1 and not stated_split_holds(
            previously_odd_count, previously_even_count
        ):
            witness = (previously_odd_count, previously_even_count, degree)
            break

    if witness != (1, 0, 1):
        raise AssertionError("deterministic bounded search did not find the expected witness")

    result = {
        "record_id": "reddit_askmath_1v6fw7",
        "outcome": "WITNESS_FOUND",
        "witness_description": "previously_odd_count = 1 and previously_even_count = 0; the new node has degree 1, which is odd.",
        "refutation_explanation": "Both stated cases require an even number of previously odd neighbors and an odd number of previously even neighbors, merely reversing the order in which those conditions are mentioned. The witness has the opposite parity pattern, so neither stated case holds despite the new node having odd degree.",
        "search_space": "All ordered pairs (previously_odd_count, previously_even_count) in {0,1} x {0,1}, visited in lexicographic order, restricted to pairs whose sum is odd."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
