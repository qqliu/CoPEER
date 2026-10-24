"""For every initial set S of sequential primes, the longest consecutive run of integers divisible by some prime in S begins at 2."""

import json


def first_primes(count):
    primes = []
    candidate = 2
    while len(primes) < count:
        is_prime = True
        for divisor in primes:
            if divisor * divisor > candidate:
                break
            if candidate % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


primes = first_primes(5)
period = 1
for prime in primes:
    period *= prime

violations = []
for k in range(1, 6):
    selected = tuple(primes[:k])
    runs = []
    run_start = None

    for number in range(1, period + 2):
        covered = any(number % prime == 0 for prime in selected)
        if covered and run_start is None:
            run_start = number
        elif not covered and run_start is not None:
            runs.append((run_start, number - 1))
            run_start = None

    initial_start, initial_end = next(run for run in runs if run[0] == 2)
    initial_length = initial_end - initial_start + 1
    for start, end in runs:
        if end - start + 1 > initial_length:
            violations.append(
                (k, selected, start, end, initial_start, initial_end)
            )

witness = violations[0]
if witness != (5, (2, 3, 5, 7, 11), 114, 126, 2, 12):
    raise RuntimeError("deterministic search produced an unexpected witness")

result = {
    "record_id": "reddit_mathematics_1lqztlx",
    "outcome": "WITNESS_FOUND",
    "witness_description": "S={2,3,5,7,11}; the maximal covered run 114 through 126 has length 13, exceeding the run 2 through 12 at 2, which has length 11.",
    "refutation_explanation": "For S={2,3,5,7,11}, every integer from 2 through 12 is divisible by a prime in S, while 13 is not. In 114 through 126, the even integers are divisible by 2, 117 and 123 by 3, 115 and 125 by 5, 119 by 7, and 121 by 11. Neither 113 nor 127 is divisible by a prime in S, so 114 through 126 is a maximal run of length 13. Therefore the length-11 run beginning at 2 is not longest.",
    "search_space": "Prime-prefix sets S_k consisting of the first k primes for k=1,2,3,4,5; for each, every integer n from 1 through 2311 was tested. Since 2310=2*3*5*7*11 is a common period and both boundary residues 1 and 2311 are included, this exhaustively enumerates every maximal covered run in one full common period for those five sets."
}

print(json.dumps(result, separators=(",", ":")))
