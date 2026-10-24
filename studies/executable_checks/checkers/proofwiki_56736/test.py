"""The proof asserts that the primes in (118, 157) of the form 4m + 1 are exactly 137, 139, 157. This enumeration is false: 139 is not of the form 4m + 1 (139 = 4*34 + 3), and 149 = 4*37 + 1, which IS of that form, is omitted. The proof also contradicts itself, having stated three lines earlier that 139 = 4 * 35 - 1."""

import json


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


asserted = [137, 139, 157]
actual = []
for candidate in range(119, 157):
    if is_prime(candidate) and candidate % 4 == 1:
        actual.append(candidate)

assert actual == [137, 149]
assert actual != asserted
assert is_prime(139) and 139 % 4 == 3
assert is_prime(149) and 149 % 4 == 1

result = {
    "record_id": "proofwiki_56736",
    "outcome": "WITNESS_FOUND",
    "witness_description": "139 is listed but satisfies 139 = 4*34 + 3, while 149 is prime and satisfies 149 = 4*37 + 1 but is omitted.",
    "refutation_explanation": "An exhaustive scan of every integer n with 118 < n < 157 finds exactly [137, 149] as the primes congruent to 1 modulo 4, contradicting the asserted enumeration [137, 139, 157].",
    "search_space": "All 38 integers n from 119 through 156 inclusive; primality was decided exactly by testing every integer divisor d from 2 through the largest d with d*d <= n."
}
print(json.dumps(result, separators=(",", ":")))
