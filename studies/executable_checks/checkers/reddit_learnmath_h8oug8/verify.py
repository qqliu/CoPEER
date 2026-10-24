"""The specialization s=1/n and r=1/(n+1) for an integer n covers arbitrary rational pairs r<s and therefore establishes the universal conclusion."""

import json
from math import gcd

REPORT = {
    "record_id": "reddit_learnmath_h8oug8",
    "verdict": "CONFIRMED",
    "notes": "Exact integer cross-multiplication confirms that s=1/2 uniquely forces n=2, which would force r=1/3 rather than the witness r=1/4. The refuted coverage statement is substantive, not plainly a typo.",
}


def main():
    r_numerator, r_denominator = 1, 4
    s_numerator, s_denominator = 1, 2

    assert r_denominator > 0 and s_denominator > 0
    assert gcd(r_numerator, r_denominator) == 1
    assert gcd(s_numerator, s_denominator) == 1
    assert r_numerator * s_denominator < s_numerator * r_denominator

    assert s_numerator != 0
    assert s_denominator % s_numerator == 0
    forced_n = s_denominator // s_numerator
    assert forced_n == 2
    assert forced_n != 0
    assert s_numerator * forced_n == s_denominator

    generated_r_numerator = 1
    generated_r_denominator = forced_n + 1
    assert generated_r_denominator == 3
    assert r_numerator * generated_r_denominator != generated_r_numerator * r_denominator

    assert list(REPORT) == ["record_id", "verdict", "notes"]
    print(json.dumps(REPORT, separators=(",", ":")))


if __name__ == "__main__":
    main()
