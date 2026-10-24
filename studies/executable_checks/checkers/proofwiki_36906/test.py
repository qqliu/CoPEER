"""The proof claims that because S = {m, m+1, ..., m+n-1} contains a multiple of j for each j = 1..n, the product of the elements of S can be regrouped as (k_1 * 1)(k_2 * 2)...(k_n * n), i.e. the n elements of S can be matched one-to-one with the factors 1, 2, ..., n so that each element is a multiple of its assigned factor. This simultaneous/distinct-representative regrouping does not follow from the cited lemma and is false in general."""

import itertools
import json


def premise_holds(elements, n):
    return all(any(element % factor == 0 for element in elements)
               for factor in range(1, n + 1))


def matching_exists(elements, n):
    return any(
        all(assignment[factor - 1] % factor == 0
            for factor in range(1, n + 1))
        for assignment in itertools.permutations(elements)
    )


counterexamples = []
for n in range(1, 5):
    for m in range(1, 11):
        elements = tuple(range(m, m + n))
        if premise_holds(elements, n) and not matching_exists(elements, n):
            counterexamples.append((n, m, elements))

witness = counterexamples[0]
assert witness == (3, 5, (5, 6, 7))

result = {
    "record_id": "proofwiki_36906",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n = 3, m = 5, and S = {5, 6, 7}.",
    "refutation_explanation": "S contains a multiple of every j in {1, 2, 3}: 5 is a multiple of 1, while 6 is a multiple of both 2 and 3. Nevertheless, no one-to-one assignment exists, because 6 is the only element of S divisible by 2 and also the only element divisible by 3, so the distinct factors 2 and 3 would both have to be assigned the same element.",
    "search_space": "Exhaustively swept all 40 pairs (n, m) with 1 <= n <= 4 and 1 <= m <= 10. For every corresponding S = {m, ..., m+n-1}, the program checked the multiple-existence premise for every j from 1 through n and, whenever it held, enumerated all n! permutations of S as possible one-to-one assignments to factors 1 through n."
}
print(json.dumps(result, separators=(",", ":")))
