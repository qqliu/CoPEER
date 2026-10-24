"""If f:X→Y is injective, then there exists g:Y→X such that g∘f=id_X."""

import itertools
import json

RECORD_ID = "reddit_learnmath_13vpgw3"
WITNESS_DESCRIPTION = (
    "X=∅, Y={0}, and f is the unique empty function f:∅→{0}. "
    "It is injective, but no function g:{0}→∅ exists."
)
REFUTATION_EXPLANATION = (
    "The injectivity hypothesis holds vacuously because X is empty. "
    "However, a left inverse would have to be a total function from the "
    "nonempty set Y={0} to the empty set X, and no such function exists. "
    "Thus the asserted existence of g fails."
)
SEARCH_SPACE = (
    "All canonical finite sets X={0,...,nx-1} and Y={0,...,ny-1} with "
    "nx,ny∈{0,1,2}; for every pair, every total function f:X→Y was "
    "enumerated, and for each injective f every total function g:Y→X was "
    "enumerated and checked for g(f(x))=x at every x∈X."
)


def is_injective(function_values):
    return len(set(function_values)) == len(function_values)


def is_left_inverse(f_values, g_values):
    return all(g_values[f_values[x]] == x for x in range(len(f_values)))


def main():
    counterexamples = []

    for nx in range(3):
        for ny in range(3):
            for f_values in itertools.product(range(ny), repeat=nx):
                if not is_injective(f_values):
                    continue

                all_g_values = tuple(
                    itertools.product(range(nx), repeat=ny)
                )
                left_inverses = tuple(
                    g_values
                    for g_values in all_g_values
                    if is_left_inverse(f_values, g_values)
                )
                if not left_inverses:
                    counterexamples.append((nx, ny, f_values))

    first = counterexamples[0]
    assert first == (0, 1, ())

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
