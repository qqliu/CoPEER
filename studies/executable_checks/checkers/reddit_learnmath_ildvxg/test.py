"""The proposed g is a function from [0,1) into P(N)."""

import json
from fractions import Fraction
from itertools import combinations

RECORD_ID = "reddit_learnmath_ildvxg"
WITNESS_DESCRIPTION = (
    "x=1/10 has the two valid decimal expansions 0.1000... and 0.0999.... "
    "The rule gives {1, 100, 1000, ...} from the first and "
    "{0, 99, 999, ...} from the second."
)
REFUTATION_EXPLANATION = (
    "These outputs differ: 1 belongs to the first set, while the second set "
    "contains only 0 at prefix length 1 and 10^k-1 for k>=2 at the displayed "
    "later prefix lengths, so it does not contain 1. Thus the rule assigns "
    "two values to the same input and is not a function."
)
SEARCH_SPACE = (
    "All 153 unordered pairs of the 18 eventually constant streams 0.d000... "
    "and 0.(d-1)999... for d=1,...,9, in fixed listed order; values were "
    "compared exactly as Fractions and differing images were certified "
    "symbolically."
)


def decimal_value(stream):
    head_digit, repeated_tail, unused_label = stream
    return Fraction(head_digit, 10) + Fraction(repeated_tail, 90)


def separating_element(left, right):
    if left[1] == 0 and right[1] == 9:
        terminating, repeating_nines = left, right
    elif left[1] == 9 and right[1] == 0:
        terminating, repeating_nines = right, left
    else:
        return None

    separator = terminating[0]
    nines_head = repeating_nines[0]

    # The separator occurs as the length-one prefix of the terminating stream.
    # For the other stream, the length-one prefix differs. Every permitted
    # prefix of length n>=3 equals (nines_head+1)*10**(n-1)-1. Its value at
    # n=3 already exceeds the separator, and subsequent values increase.
    absent_from_other_image = (
        nines_head != separator
        and (nines_head + 1) * (10 ** 2) - 1 > separator
    )
    if absent_from_other_image:
        return separator
    return None


streams = []
for digit in range(1, 10):
    streams.append((digit, 0, "0." + str(digit) + "000..."))
    streams.append((digit - 1, 9, "0." + str(digit - 1) + "999..."))

checked_pairs = 0
witnesses = []
for left, right in combinations(streams, 2):
    checked_pairs += 1
    if decimal_value(left) != decimal_value(right):
        continue
    separator = separating_element(left, right)
    if separator is not None:
        witnesses.append((left, right, separator))

if checked_pairs != 153:
    raise AssertionError("the declared finite search space was not fully swept")
if not witnesses:
    raise AssertionError("the exhaustive bounded search found no witness")

first_left, first_right, first_separator = witnesses[0]
if (
    decimal_value(first_left) != Fraction(1, 10)
    or decimal_value(first_right) != Fraction(1, 10)
    or first_separator != 1
):
    raise AssertionError("unexpected first witness")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
