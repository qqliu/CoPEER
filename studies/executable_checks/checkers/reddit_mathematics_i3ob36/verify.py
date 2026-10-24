"""Assuming only that n is interesting, if n+1 is non-interesting, then n+1 is the smallest non-interesting natural number."""

import json

REPORT = {
    "record_id": "reddit_mathematics_i3ob36",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation validates the witness n = 2: 2 is interesting, 3 is non-interesting, and the non-interesting natural 1 is smaller than 3. The refuted statement is substantive as written, not plainly a typo; it lacks any assumption that all naturals below n are interesting.",
}

n = 2
non_interesting_naturals = frozenset({1, 3})

def is_natural(value):
    return type(value) is int and value >= 0

def is_non_interesting(value):
    return is_natural(value) and value in non_interesting_naturals

def is_interesting(value):
    return is_natural(value) and value not in non_interesting_naturals

successor = n + 1
premise = is_interesting(n) and is_non_interesting(successor)
smaller_counterexample = 1
smallest_conclusion = all(
    successor <= value
    for value in non_interesting_naturals
    if is_natural(value)
)
claimed_implication = (not premise) or smallest_conclusion

assert is_natural(n)
assert successor == 3
assert premise
assert is_non_interesting(smaller_counterexample)
assert smaller_counterexample < successor
assert not smallest_conclusion
assert not claimed_implication
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
