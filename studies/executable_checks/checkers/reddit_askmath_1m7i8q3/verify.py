r"""In Case 1, the condition x ∈ A implies F(A ∪ B) = F(A)."""

import json


def image(elements, function_table):
    result = set()
    for element in elements:
        result.add(function_table[element])
    return frozenset(result)


def main():
    universe_x = frozenset((0, 1))
    universe_y = frozenset((0, 1))
    a_set = frozenset((0,))
    b_set = frozenset((1,))
    chosen_x = 0
    function_table = {0: 0, 1: 1}

    is_total_function = (
        frozenset(function_table.keys()) == universe_x
        and frozenset(function_table.values()).issubset(universe_y)
    )
    union_image = image(a_set.union(b_set), function_table)
    a_image = image(a_set, function_table)
    witness_valid = (
        is_total_function
        and chosen_x in a_set
        and union_image == frozenset((0, 1))
        and a_image == frozenset((0,))
        and union_image != a_image
    )

    if witness_valid:
        verdict = "CONFIRMED"
        notes = "Exact recomputation validates the concrete witness: 0 ∈ A, F(A ∪ B) = {0, 1}, and F(A) = {0}. The refuted statement is a substantive logical error, not plainly a typo."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "Exact recomputation does not validate the reported witness. The alleged issue cannot be classified as an established substantive refutation."

    print(json.dumps({
        "record_id": "reddit_askmath_1m7i8q3",
        "verdict": verdict,
        "notes": notes
    }, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
