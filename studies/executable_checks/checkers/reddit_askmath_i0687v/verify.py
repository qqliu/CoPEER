r"""For all complex numbers z1,...,zn, |z1+...+zn|^2 <= |z1|+...+|zn|."""

import json
from math import isqrt

record_id = "reddit_askmath_i0687v"
expected_notes = (
    "Exact integer arithmetic verifies the witness: for n=1 and z1=-2, "
    "the left side is 4 and the right side is 2, so 4 <= 2 is false. "
    "The statement is substantively false as written, not plainly a typo "
    "from the supplied evidence."
)

witness = ((-2, 0),)
sum_real = sum(real for real, imaginary in witness)
sum_imaginary = sum(imaginary for real, imaginary in witness)
left_side = sum_real ** 2 + sum_imaginary ** 2

right_side = 0
all_moduli_exact = True
for real, imaginary in witness:
    modulus_squared = real ** 2 + imaginary ** 2
    modulus = isqrt(modulus_squared)
    if modulus ** 2 != modulus_squared:
        all_moduli_exact = False
    right_side += modulus

confirmed = (
    len(witness) == 1
    and witness[0] == (-2, 0)
    and all_moduli_exact
    and left_side == 4
    and right_side == 2
    and left_side > right_side
)

verdict = "CONFIRMED" if confirmed else "CANNOT_REPRODUCE"
notes = expected_notes if confirmed else (
    "The reported witness could not be reproduced with exact integer arithmetic. "
    "The statement is substantively false as written, not plainly a typo from "
    "the supplied evidence."
)
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
