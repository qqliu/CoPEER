r"""$$g(n) = \displaystyle n^{\log_b a} \log_b^k n \; \sum_{j=0}^{\log_b{n-1}}  \left(\frac{a}{b^{\log_b a}}\right)^j = n^{\log_b a} \log_b^{k +1} n.$$"""

import json
from fractions import Fraction

RECORD_ID = "SE_cs_1957__a2388"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "a=1, b=4, n=2, k=1. Here log_4(a)=0, log_4(n)=1/2, and "
    "log_4(n-1)=0, so the finite sum has the single j=0 term."
)
REFUTATION_EXPLANATION = (
    "The geometric ratio is 1, making the left-hand side 1/2, while the "
    "right-hand side is 1/4; hence the stated equality fails."
)
SEARCH_SPACE = (
    "All 81 tuples (c,q,r,k) in {2,3,4} x {1,2,3} x {1,2,3} x "
    "{1,2,3} were inspected in lexicographic loop order, with a=1, "
    "b=c^q, n=c^r. Exactly 9 tuples had n-1=c^s for some s in "
    "{0,1,2,3} with q dividing s (so the sum's upper limit s/q was a "
    "nonnegative integer); all 9 were evaluated exactly."
)


def bounded_power_exponent(base, value):
    power = 1
    for exponent in range(4):
        if power == value:
            return exponent
        power *= base
    return None


raw_count = 0
admissible_count = 0
witnesses = []

for c in range(2, 5):
    for q in range(1, 4):
        b = c ** q
        for r in range(1, 4):
            n = c ** r
            s = bounded_power_exponent(c, n - 1)
            for k in range(1, 4):
                raw_count += 1
                if s is None or s % q != 0:
                    continue

                admissible_count += 1
                a = 1
                log_b_a = Fraction(0, 1)
                log_b_n = Fraction(r, q)
                upper = Fraction(s, q)
                ratio = Fraction(1, 1)

                geometric_sum = Fraction(0, 1)
                for j in range(int(upper) + 1):
                    geometric_sum += ratio ** j

                common_factor = Fraction(n ** int(log_b_a), 1)
                lhs = common_factor * (log_b_n ** k) * geometric_sum
                rhs = common_factor * (log_b_n ** (k + 1))

                if lhs != rhs:
                    witnesses.append((a, b, n, k, lhs, rhs))

assert raw_count == 81
assert admissible_count == 9
assert witnesses
assert witnesses[0] == (
    1,
    4,
    2,
    1,
    Fraction(1, 2),
    Fraction(1, 4),
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
