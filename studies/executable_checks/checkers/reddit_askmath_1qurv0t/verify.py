r"""Every prime number is one more or one less than a multiple of 6."""

import json

record_id = "reddit_askmath_1qurv0t"
verdict = "CONFIRMED"
notes = "Confirmed exactly: 2 is prime and divmod(2, 6) gives remainder 2, whereas integers one more or less than a multiple of 6 have remainder 1 or 5. The refuted statement is substantive as written, not plainly a typo; it needs an exception such as primes greater than 3."

witness = 2
modulus = 6
is_prime = witness >= 2 and all(
    witness % divisor != 0 for divisor in range(2, witness)
)
quotient, remainder = divmod(witness, modulus)
is_one_away = remainder == 1 or remainder == modulus - 1

if not is_prime:
    raise AssertionError("The proposed witness is not prime")
if is_one_away:
    raise AssertionError("The proposed witness satisfies the claim")
if quotient * modulus + remainder != witness:
    raise AssertionError("Exact division reconstruction failed")

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
