r"""Let  $n,k\in\mathbb{N}$ with $n\geq$ lcm$(1,\ldots,k)$, and let $\pi(x):=\sum_{p\leq x} 1$ be the number of primes not greater than $x$. Then in the interval $[n,n+k]$ there are at least $k+1-\pi(k)$ integers $n_i$  with a prime factor $p_i>k$."""

import json


def greatest_common_divisor(a, b):
    while b:
        a, b = b, a % b
    return a


def least_common_multiple_through(limit):
    accumulated = 1
    for candidate in range(1, limit + 1):
        accumulated = accumulated // greatest_common_divisor(accumulated, candidate) * candidate
    return accumulated


def prime(number):
    if number < 2:
        return False
    trial = 2
    while trial * trial <= number:
        if number % trial == 0:
            return False
        trial += 1
    return True


def contains_large_prime_factor(number, threshold):
    factor = 2
    residue = number
    while factor * factor <= residue:
        if residue % factor == 0:
            if factor > threshold:
                return True
            while residue % factor == 0:
                residue //= factor
        factor += 1
    return residue > threshold


k = 1
n = 1
hypothesis_bound = least_common_multiple_through(k)
prime_total = sum(1 for candidate in range(2, k + 1) if prime(candidate))
required_total = k + 1 - prime_total
interval = tuple(range(n, n + k + 1))
qualifying = tuple(value for value in interval if contains_large_prime_factor(value, k))

assert hypothesis_bound == 1
assert n >= hypothesis_bound
assert prime_total == 0
assert required_total == 2
assert interval == (1, 2)
assert qualifying == (2,)
assert len(qualifying) < required_total

result = {
    "record_id": "mse_2128949__ans2583979",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms k=1, n=1 satisfies the hypothesis, while [1,2] has only one qualifying integer against a required two. This is plainly a boundary typo/oversight (the equality case in n>=lcm), not a substantive counterexample to the likely intended strict-bound statement.",
}
print(json.dumps(result, separators=(",", ":")))
