#!/usr/bin/env python3
"""Exact standalone witness check for Mittou Conjecture 13; no dependencies."""
from fractions import Fraction
import json


def check():
    expected = {
        1225: [1, 5, 7, 25, 35, 49, 175, 245, 1225],
        3025: [1, 5, 11, 25, 55, 121, 275, 605, 3025],
    }
    witnesses = []
    for n, ordered in expected.items():
        divisors = [d for d in range(1, n + 1) if n % d == 0]
        assert divisors == ordered
        even = sum(d for i, d in enumerate(divisors, start=1) if i % 2 == 0)
        odd = sum(d for i, d in enumerate(divisors, start=1) if i % 2 == 1)
        ratio = Fraction(even, odd)
        assert ratio == Fraction(108, 481) and 0 < ratio < 1
        witnesses.append({"n": n, "divisors": divisors, "E": even, "O": odd, "ratio": str(ratio)})
    assert 1225 == 5**2 * 7**2 and 3025 == 5**2 * 11**2 and 1225 != 3025
    assert witnesses[0]["E"] * witnesses[1]["O"] == witnesses[1]["E"] * witnesses[0]["O"] == 1090908
    return {"result": "PASS", "witnesses": witnesses, "common_ratio": "108/481", "conjectured_maximum_members": 1, "verified_members": 2}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
