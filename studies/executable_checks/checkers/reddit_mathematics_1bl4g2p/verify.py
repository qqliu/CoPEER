r"""For every prime p, (2^(p-1))(2^p-1) is a perfect number."""

import json

REPORT = {
    "record_id": "reddit_mathematics_1bl4g2p",
    "verdict": "CONFIRMED",
    "notes": "Exact independent recomputation confirms p=11 is prime, 2^11-1=23*89, N=2096128, and the sum of N's proper positive divisors is 2325392, so N is not perfect. The refuted statement is substantive, not plainly a typo; it omits the necessary condition that 2^p-1 be prime."
}


def prime_by_trial(n):
    if n < 2:
        return False
    candidate = 2
    while candidate * candidate <= n:
        if n % candidate == 0:
            return False
        candidate += 1
    return True


p = 11
assert prime_by_trial(p)
mersenne = (2 ** p) - 1
assert mersenne == 2047
assert mersenne == 23 * 89
assert prime_by_trial(23)
assert prime_by_trial(89)

number = (2 ** (p - 1)) * mersenne
assert number == 2096128
assert number == (2 ** 10) * 23 * 89

all_divisors = {
    (2 ** exponent) * (23 ** use_23) * (89 ** use_89)
    for exponent in range(11)
    for use_23 in range(2)
    for use_89 in range(2)
}
assert len(all_divisors) == 44
assert number in all_divisors
assert all(number % divisor == 0 for divisor in all_divisors)

proper_sum = sum(divisor for divisor in all_divisors if divisor != number)
assert proper_sum == 2325392
assert proper_sum != number

print(json.dumps(REPORT, separators=(",", ":")))
