r"""For every initial set S of sequential primes, the longest consecutive run of integers divisible by some prime in S begins at 2."""

import json


def is_prime(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


primes = []
candidate = 2
while len(primes) < 5:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1

S = tuple(primes)
assert S == (2, 3, 5, 7, 11)


def covered(number):
    return any(number % prime == 0 for prime in S)


def maximal_run_containing(seed):
    assert covered(seed)
    left = seed
    right = seed
    while covered(left - 1):
        left -= 1
    while covered(right + 1):
        right += 1
    return left, right


initial_run = maximal_run_containing(2)
witness_run = maximal_run_containing(120)

assert initial_run == (2, 12)
assert witness_run == (114, 126)
assert not covered(1)
assert not covered(13)
assert not covered(113)
assert not covered(127)
assert all(covered(number) for number in range(2, 13))
assert all(covered(number) for number in range(114, 127))

initial_length = initial_run[1] - initial_run[0] + 1
witness_length = witness_run[1] - witness_run[0] + 1
assert initial_length == 11
assert witness_length == 13
assert witness_length > initial_length

REPORT = {
    "record_id": "reddit_mathematics_1lqztlx",
    "verdict": "CONFIRMED",
    "notes": "The statement is substantively false, not plainly a typo: for the initial prime set {2,3,5,7,11}, the maximal covered run 114–126 has length 13, strictly longer than the length-11 maximal run 2–12."
}

print(json.dumps(REPORT, separators=(",", ":")))
