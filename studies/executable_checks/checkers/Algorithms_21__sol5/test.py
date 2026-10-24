#!/usr/bin/env python3
"""
Counterexample search for record Algorithms_21__sol5.

TARGET CLAIM (quoted verbatim from the proof, unicode minus normalized):
    "Base case (n = 1): G1 has no edges, R(1) = 0 = 21 -1"

The trailing "21 -1" is a plaintext mangling of a superscript expression; the
intended reading is almost certainly "2^1 - 1" (the proof is asserting a
closed form R(n) = 2^n - 1 and checking it at n = 1).

What is finitely checkable here WITHOUT inventing data:
  - "G1 has no edges" and "R(1) = 0" refer to objects (G_n, R) that the quoted
    text does not define, so those clauses cannot be independently recomputed.
  - BUT the claim chains an equality "0 = 2^1 - 1" (in whatever parse of the
    mangled "21 -1"). That is a pure arithmetic identity, decidable with exact
    integer arithmetic. If it fails under EVERY plausible parse of "21 -1",
    the quoted sentence is internally false regardless of what G_n and R are:
    it asserts that the number 0 equals the value of the expression, and no
    parse of the expression yields 0.

Search space (exhaustive over all plausible parses of the mangled token
"21 -1", i.e. every way a superscript could have been dropped, plus literal
and product readings):
    P1: literal          21 - 1        = 20
    P2: 2^1 - 1          (superscript on the middle '1')   = 1
    P3: 2^(1-1)          (superscript on '1-1')            = 1
    P4: 2*1 - 1          ('^' read as implicit product)    = 1
    P5: 2^1 * (-1)       (degenerate juxtaposition)        = -2
    P6: 2^(1) - 1        same as P2                        = 1

A parse is a NON-counterexample only if its exact value equals 0 (the value
the claim asserts, "R(1) = 0 = <expr>"). The program checks every parse with
exact ints; floats are never used.

Verdict: if no parse evaluates to 0, the equality "0 = 21 -1" is false under
every reading -> WITNESS_FOUND (the witness is the claimed equation itself
at n = 1, with the exact value of each parse shown).
"""

from fractions import Fraction

RECORD_ID = "Algorithms_21__sol5"

# Deterministic, fixed-order list of (label, exact value) for every plausible
# parse of the mangled token "21 -1".
PARSES = [
    ("literal '21 - 1'",                     Fraction(21 - 1)),
    ("'2^1 - 1' (intended superscript)",     Fraction(2**1 - 1)),
    ("'2^(1-1)' (superscript spans '1-1')",  Fraction(2**(1 - 1))),
    ("'2*1 - 1' (implicit product)",         Fraction(2 * 1 - 1)),
    ("'2^1 * (-1)' (juxtaposition)",         Fraction(2**1 * (-1))),
    ("'2^(1) - 1'",                          Fraction(2**1 - 1)),
]

ASSERTED_VALUE = Fraction(0)  # the claim says R(1) = 0 = <expr>


def main():
    print(f"Record: {RECORD_ID}")
    print("Claim under test: 'R(1) = 0 = 21 -1'  (i.e. the number 0 equals")
    print("the value of the mangled expression '21 -1' under some parse).")
    print()

    satisfying = []
    for label, value in PARSES:  # fixed iteration order, deterministic
        ok = (value == ASSERTED_VALUE)
        print(f"  parse {label:40s} -> exact value {value}  "
              f"{'== 0 (claim holds)' if ok else '!= 0 (claim fails)'}")
        if ok:
            satisfying.append((label, value))

    print()
    if satisfying:
        print("NO_WITNESS: at least one parse makes the asserted equality true:")
        for label, value in satisfying:
            print(f"  {label} = {value}")
    else:
        print("WITNESS_FOUND")
        print("Witness: the claim's own equation at n = 1: it asserts 0 = 2^1 - 1,")
        print("but 2^1 - 1 = 1 (exact integer arithmetic), and NO plausible parse")
        print("of the mangled token '21 -1' evaluates to 0:")
        for label, value in PARSES:
            print(f"  {label} = {value}  (!= 0)")
        print("Hence the chained equality 'R(1) = 0 = 2^1 - 1' is false: whatever")
        print("R(1) is, it cannot equal both 0 and 1. The correct base-case value")
        print("for a closed form 2^n - 1 at n = 1 is 1, not 0 (0 would match")
        print("2^n - 2 or 2^(n-1) - 1 instead).")


if __name__ == "__main__":
    main()
