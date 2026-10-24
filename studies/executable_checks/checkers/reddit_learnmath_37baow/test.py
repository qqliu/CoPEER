"""No function f: P(A) --> P(A) can be surjective."""

import itertools
import json


def main():
    first_witness = None
    functions_checked = 0

    for n in range(3):
        power_size = 1 << n
        codomain = tuple(range(power_size))
        for outputs in itertools.product(codomain, repeat=power_size):
            functions_checked += 1
            if set(outputs) == set(codomain) and first_witness is None:
                first_witness = (n, outputs)

    assert functions_checked == 261
    assert first_witness == (0, (0,))

    result = {
        "record_id": "reddit_learnmath_37baow",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take A = ∅. Then P(A) = {∅}, and the unique function f with f(∅) = ∅ is surjective.",
        "refutation_explanation": "Its image is {∅} = P(A), so it is surjective, directly contradicting the assertion that no such function can be surjective.",
        "search_space": "All functions P(A) -> P(A) for the canonical finite sets A = {0,...,n-1} with n in {0,1,2}: 1^1 + 2^2 + 4^4 = 261 functions, enumerated in lexicographic order as output tuples."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
