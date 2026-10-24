"""Then any prime divisor of $d$ must be a prime greater than $n$, so $d$ must be a prime greater than $n$ and equivalent to $1$ modulo $4$."""

import json


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def prime_divisors(value):
    remaining = value
    divisors = []
    candidate = 2
    while candidate * candidate <= remaining:
        if remaining % candidate == 0:
            divisors.append(candidate)
            while remaining % candidate == 0:
                remaining //= candidate
        candidate += 1
    if remaining > 1:
        divisors.append(remaining)
    return tuple(divisors)


def main():
    counterexamples = []
    for n in range(1, 13):
        for d in range(2, 501):
            divisors = prime_divisors(d)
            premise = all(prime > n for prime in divisors)
            conclusion = is_prime(d) and d > n and d % 4 == 1
            if premise and not conclusion:
                counterexamples.append((n, d, divisors))

    composite_counterexamples = [
        item for item in counterexamples if not is_prime(item[1])
    ]
    witness = composite_counterexamples[0]
    assert witness == (1, 4, (2,))

    result = {
        "record_id": "mse_4580215__ans4585306",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 1 and d = 4. The only prime divisor of 4 is 2, and 2 > 1; nevertheless, 4 is composite and 4 % 4 = 0, not 1.",
        "refutation_explanation": "The premise that every prime divisor of d is greater than n does not force d itself to be prime or congruent to 1 modulo 4. The pair (n, d) = (1, 4) satisfies the stated premise and violates both asserted conclusions.",
        "search_space": "All 5,988 ordered integer pairs (n, d) with 1 <= n <= 12 and 2 <= d <= 500 were checked in increasing n-then-d order, using exact trial division. The reported witness is the first checked counterexample for which d is composite."
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
