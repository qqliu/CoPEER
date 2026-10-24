"""From a | mn, it follows that a divides both m and n and that a = mnq for some integer q."""

import itertools
import json


def divides(divisor, value):
    return value % divisor == 0


values = range(1, 13)
counterexamples = []
for a, m, n in itertools.product(values, repeat=3):
    product = m * n
    if not divides(a, product):
        continue
    divides_both = divides(a, m) and divides(a, n)
    integer_q_exists = divides(product, a)
    if not (divides_both and integer_q_exists):
        counterexamples.append(
            ((a, m, n), not divides_both, not integer_q_exists)
        )

witnesses_failing_both = [
    triple
    for triple, divisibility_fails, equation_fails in counterexamples
    if divisibility_fails and equation_fails
]
witness = witnesses_failing_both[0]
assert witness == (2, 1, 4)

result = {
    "record_id": "reddit_learnmath_jid2cv",
    "outcome": "WITNESS_FOUND",
    "witness_description": "a = 2, m = 1, n = 4.",
    "refutation_explanation": "The premise holds because mn = 4 = 2·2, so 2 divides mn. But 2 does not divide m = 1. Moreover, no integer q satisfies 2 = 4q, since every 4q is divisible by 4 whereas 2 is not. Thus two asserted conclusions fail.",
    "search_space": "All 1,728 ordered triples (a, m, n) in {1, 2, ..., 12}^3, in lexicographic order; for every triple satisfying a | mn, both asserted divisibilities and the unbounded integer-q condition a = mnq were decided exactly."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
