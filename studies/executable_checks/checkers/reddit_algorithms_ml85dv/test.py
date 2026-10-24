"""The stated CPU schedule can give every enumerated algorithm its prescribed share while reserving one half of CPU time for enumeration."""

import json
from fractions import Fraction
from itertools import combinations

RECORD_ID = "reddit_algorithms_ml85dv"
RESERVED = Fraction(1, 2)
CAPACITY = Fraction(1, 1)
INDICES = (0, 1)

violations = []
for subset_size in range(len(INDICES) + 1):
    for chosen in combinations(INDICES, subset_size):
        required = RESERVED
        for n in chosen:
            required += Fraction(1, 2 * (n + 1) ** 2)
        if required > CAPACITY:
            violations.append((chosen, required))

expected_witness = ((0, 1), Fraction(9, 8))
if not violations or violations[0] != expected_witness:
    raise RuntimeError("deterministic exhaustive search did not find the expected witness")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": "The bounded subset {0, 1}: reserve 1/2 of the CPU, give A_0 its prescribed 1/2, and give A_1 its prescribed 1/8.",
    "refutation_explanation": "These simultaneous requirements total 1/2 + 1/2 + 1/8 = 9/8, which exceeds the entire CPU capacity 1 by 1/8. Thus the stated shares for A_0 and A_1 cannot both be supplied while one half is reserved for enumeration.",
    "search_space": "All 4 subsets of the bounded index set {0, 1}, enumerated first by subset size and then lexicographically; for each subset, exact Fraction arithmetic checks whether reserved time 1/2 plus the prescribed shares 1/(2(n+1)^2) exceeds CPU capacity 1."
}
print(json.dumps(result, separators=(",", ":")))
