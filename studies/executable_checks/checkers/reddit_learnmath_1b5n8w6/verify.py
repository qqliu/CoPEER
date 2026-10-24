r"""The only positive integer that can divide both an odd number and an even number is 1."""

import json

record_id = "reddit_learnmath_1b5n8w6"
divisor = 3
odd_number = divisor
even_number = divisor + divisor

witness_is_valid = (
    divisor > 0
    and divisor != 1
    and odd_number > 0
    and even_number > 0
    and odd_number % 2 == 1
    and even_number % 2 == 0
    and odd_number % divisor == 0
    and even_number % divisor == 0
)

if witness_is_valid:
    verdict = "CONFIRMED"
    notes = (
        "Exact arithmetic confirms the witness: 3 is positive and greater than 1, "
        "3 is odd, 6 is even, and 3 divides both 3 and 6. The refuted statement "
        "is substantively false, not plainly a typo."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "The reported witness does not satisfy the literal claim's conditions. "
        "The refuted statement is substantively mathematical, not plainly a typo."
    )

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
