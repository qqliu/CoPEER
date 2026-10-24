r"""The proof claims that for arbitrary field F, a^2 + b^2 != 0 exactly when (a,b) != (0,0), hence every nonzero element of E = F x F has a multiplicative inverse (a/(a^2+b^2), -b/(a^2+b^2)), and correspondingly (line 0128) that a c - b d = 0 and a d + b c = 0 with (c,d) != (0,0) forces a = b = 0. Both steps, and hence the main claim that E is always a field, fail whenever -1 is a square in F."""

import json

record_id = "proofwiki_96564"
confirmed_notes = "Exact arithmetic in F = Z/5Z verifies that (1,2) is nonzero with 1^2 + 2^2 = 0, and that the nonzero pairs (1,2) and (1,3) have product (0,0). Thus E has nonzero zero divisors and is not a field. The refuted statement is substantive, not plainly a typo."
invalid_notes = "The reported witness did not satisfy all required identities under exact arithmetic. The refuted statement would be substantive, not plainly a typo."

modulus = 5
residues = range(modulus)
is_prime = modulus >= 2 and all(modulus % divisor != 0 for divisor in range(2, modulus))
nonzero_inverses_exist = all(
    any((value * candidate) % modulus == 1 for candidate in residues)
    for value in range(1, modulus)
)

first = (1, 2)
second = (1, 3)
a, b = first
c, d = second

minus_one_is_square = (b * b) % modulus == (-1) % modulus
isotropic_nonzero = first != (0, 0) and (a * a + b * b) % modulus == 0
second_is_nonzero = second != (0, 0)
product_real = (a * c - b * d) % modulus
product_imaginary = (a * d + b * c) % modulus
zero_divisor_witness = (
    first != (0, 0)
    and second_is_nonzero
    and product_real == 0
    and product_imaginary == 0
)

confirmed = (
    is_prime
    and nonzero_inverses_exist
    and minus_one_is_square
    and isotropic_nonzero
    and zero_divisor_witness
)
verdict = "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID"
notes = confirmed_notes if confirmed else invalid_notes
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
