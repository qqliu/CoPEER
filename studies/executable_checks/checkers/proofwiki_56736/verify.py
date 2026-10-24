r"""The proof asserts that the primes in (118, 157) of the form 4m + 1 are exactly 137, 139, 157. This enumeration is false: 139 is not of the form 4m + 1 (139 = 4*34 + 3), and 149 = 4*37 + 1, which IS of that form, is omitted. The proof also contradicts itself, having stated three lines earlier that 139 = 4 * 35 - 1."""

import json

upper = 156
prime_flags = [True] * (upper + 1)
prime_flags[0] = False
prime_flags[1] = False
factor = 2
while factor * factor <= upper:
    if prime_flags[factor]:
        multiple = factor * factor
        while multiple <= upper:
            prime_flags[multiple] = False
            multiple += factor
    factor += 1

matching = tuple(
    number
    for number in range(119, 157)
    if prime_flags[number] and number % 4 == 1
)

established = (
    matching == (137, 149)
    and prime_flags[139]
    and 139 == 4 * 34 + 3
    and prime_flags[149]
    and 149 == 4 * 37 + 1
    and not (118 < 157 < 157)
    and matching != (137, 139, 157)
)

if established:
    verdict = "CONFIRMED"
    notes = "Exact sieve recomputation gives [137, 149] for primes n with 118 < n < 157 and n congruent to 1 modulo 4. Thus 139 has the wrong residue, 149 is omitted, and 157 is outside the open interval. The false enumeration is plainly a typo—apparently 139 for 149—rather than a substantive mathematical error."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The exact integer recomputation did not validate the reported witness."

print(json.dumps({
    "record_id": "proofwiki_56736",
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
