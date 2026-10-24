"""For every positive integer a, the fraction 2a/(a+1) is not reducible."""

import json
from math import gcd

RECORD_ID = "reddit_mathematics_16ovrt9"
SEARCH_SPACE = "All positive integers a with 1 <= a <= 100, checked in increasing order."

witnesses = []
for a in range(1, 101):
    numerator = 2 * a
    denominator = a + 1
    if gcd(numerator, denominator) > 1:
        witnesses.append((a, numerator, denominator))

if not witnesses:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No counterexample was found.",
        "refutation_explanation": "Every fraction checked had relatively prime numerator and denominator.",
        "search_space": SEARCH_SPACE,
    }
else:
    a, numerator, denominator = witnesses[0]
    common_divisor = gcd(numerator, denominator)
    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": "a = 1 gives the fraction 2/2, whose numerator and denominator have greatest common divisor 2.",
        "refutation_explanation": "Since gcd(2, 2) = 2 > 1, the fraction 2a/(a+1) is reducible when a = 1, contradicting the universal claim.",
        "search_space": SEARCH_SPACE,
    }

print(json.dumps(result, sort_keys=False))
