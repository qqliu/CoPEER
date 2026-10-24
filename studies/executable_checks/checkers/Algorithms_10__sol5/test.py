#!/usr/bin/env python3
"""
Blind counterexample search for the claim (record Algorithms_10__sol5):

    "so |S| = 1 <= n/2 (assuming n >= 2, otherwise the problem is trivial).
     By the given condition"

The claim's finitely checkable arithmetic content is the inequality

        1 <= n/2        for every integer n >= 2,

i.e. with |S| = 1 as the claim itself stipulates, the set S of size 1 is
claimed to satisfy |S| <= n/2 whenever n >= 2.  (The surrounding objects --
what S is, what "the given condition" says -- are not supplied by the quoted
text, so the only decidable content is this inequality.)

Search: sweep every integer n in [2, 10**6] in increasing order and test,
with exact rational arithmetic (fractions.Fraction; no floats), whether
1 <= n/2 fails.  A witness would be an integer n >= 2 with 1 > n/2,
equivalently n < 2 -- so beyond the swept range the inequality only gets
easier (n/2 is strictly increasing in n), and the bounded sweep is decisive
for the whole range n >= 2 by monotonicity; the exhaustive guarantee we
report, however, is only for the range actually swept.

Deterministic: fixed iteration order, no randomness, stdlib only.
"""

from fractions import Fraction

LO, HI = 2, 10**6  # inclusive sweep bounds for n


def main() -> None:
    witnesses = []
    for n in range(LO, HI + 1):
        # exact test of the claimed inequality |S| = 1 <= n/2
        if Fraction(1) > Fraction(n, 2):
            witnesses.append(n)

    if witnesses:
        n = witnesses[0]
        print("VERDICT: WITNESS_FOUND")
        print(f"  witness: n = {n}")
        print(f"  violation: 1 > {n}/2 = {Fraction(n, 2)}, "
              f"contradicting the claim |S| = 1 <= n/2 for n >= 2")
    else:
        print("VERDICT: NO_WITNESS_EXHAUSTIVE")
        print(f"  swept: every integer n in [{LO}, {HI}] (inclusive), "
              f"{HI - LO + 1} values, in increasing order")
        print("  checked: exact-rational test of 1 <= n/2; no n in the range "
              "violates it")
        print("  note: n/2 is strictly increasing in n, so no n > "
              f"{HI} can violate 1 <= n/2 either (1 <= n/2 iff n >= 2)")


if __name__ == "__main__":
    main()
