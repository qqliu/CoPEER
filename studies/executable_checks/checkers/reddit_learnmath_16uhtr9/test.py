"""Showing a property for one natural number n and its successor n+1 does not imply that the property holds for every natural number merely because those two numbers have opposite parity."""

import itertools
import json

DOMAIN = tuple(range(6))
N_VALUES = tuple(range(5))
TABLES = tuple(itertools.product((False, True), repeat=len(DOMAIN)))

bounded_violations = []
checks = 0
for n in N_VALUES:
    premise_count = 0
    nonuniversal_count = 0
    for table in TABLES:
        checks += 1
        opposite_parity = (n % 2) != ((n + 1) % 2)
        if opposite_parity and table[n] and table[n + 1]:
            premise_count += 1
            if not all(table):
                nonuniversal_count += 1
    if premise_count != 0 and nonuniversal_count == 0:
        bounded_violations.append(n)

assert checks == 320
assert bounded_violations == []

result = {
    "record_id": "reddit_learnmath_16uhtr9",
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": "No counterexample was found in the bounded search: for every tested adjacent pair, at least one Boolean property was true at that pair and false elsewhere in the bounded domain.",
    "refutation_explanation": "Within the finite model, opposite parity never made truth at n and n+1 force truth throughout the domain. This is exhaustive only for the stated bounded space and is not exhaustive evidence about every natural number or every possible property.",
    "search_space": "All 64 Boolean-valued property tables on the exact domain {0,1,2,3,4,5}, tested for each n in {0,1,2,3,4} with successor n+1: exactly 320 ordered (n, property table) checks in increasing-n and itertools.product order."
}
print(json.dumps(result, separators=(",", ":")))
