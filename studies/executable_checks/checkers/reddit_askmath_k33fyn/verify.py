"""The proof may apply the stated prime-factorization theorem to every odd integer x and obtain the displayed nonempty product of primes."""

import json


def is_prime(integer):
    if integer < 2:
        return False
    trial = 2
    while trial * trial <= integer:
        if integer % trial == 0:
            return False
        trial += 1
    return True


def positive_prime_divisors(integer):
    found = []
    candidate = 2
    while candidate <= integer:
        if integer % candidate == 0 and is_prime(candidate):
            found.append(candidate)
        candidate += 1
    return tuple(found)


record_id = "reddit_askmath_k33fyn"
verdict = "CONFIRMED"
notes = "Exact recomputation confirms x = 1 is odd and has no positive prime divisor; moreover, every nonempty product of primes is at least 2, so it cannot equal 1. The refuted statement has a substantive missing-domain hypothesis (such as x > 1), not a plainly typographical error."

witness = 1
assert witness % 2 == 1
assert positive_prime_divisors(witness) == ()

least_prime_value = 2
assert is_prime(least_prime_value)
assert least_prime_value > witness
assert all(not is_prime(candidate) for candidate in range(0, least_prime_value))

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
