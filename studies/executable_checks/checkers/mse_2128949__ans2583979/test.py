r"""Let  $n,k\in\mathbb{N}$ with $n\geq$ lcm$(1,\ldots,k)$, and let $\pi(x):=\sum_{p\leq x} 1$ be the number of primes not greater than $x$. Then in the interval $[n,n+k]$ there are at least $k+1-\pi(k)$ integers $n_i$  with a prime factor $p_i>k$."""

import json
from math import gcd


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def prime_count(bound):
    return sum(1 for value in range(2, bound + 1) if is_prime(value))


def lcm_1_to_k(k):
    result = 1
    for value in range(1, k + 1):
        result = result * value // gcd(result, value)
    return result


def has_prime_factor_greater_than(value, bound):
    if value < 2:
        return False
    remaining = value
    divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            if divisor > bound:
                return True
            while remaining % divisor == 0:
                remaining //= divisor
        divisor += 1
    return remaining > bound


record_id = "mse_2128949__ans2583979"
outcome = "WITNESS_FOUND"
witness_description = "The first counterexample in the bounded sweep is k=1, n=1: among [1,2], only 2 has a prime factor greater than 1."
refutation_explanation = "For k=1 and n=1, lcm(1)=1, so the hypothesis n>=lcm(1) holds. Also pi(1)=0, making the claimed lower bound k+1-pi(k)=2. However, 1 has no prime factor and 2 has the prime factor 2>1, so only 1 integer qualifies; 1<2."
search_space = "All integer pairs (k,n) with 1 <= k <= 12 and lcm(1,...,k) <= n <= lcm(1,...,k)+200, swept completely in lexicographic order (k,n)."

first_counterexample = None
for k in range(1, 13):
    lower = lcm_1_to_k(k)
    required = k + 1 - prime_count(k)
    for n in range(lower, lower + 201):
        qualifying = tuple(
            value
            for value in range(n, n + k + 1)
            if has_prime_factor_greater_than(value, k)
        )
        if len(qualifying) < required and first_counterexample is None:
            first_counterexample = (k, n, qualifying, required)

assert first_counterexample == (1, 1, (2,), 2)

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
