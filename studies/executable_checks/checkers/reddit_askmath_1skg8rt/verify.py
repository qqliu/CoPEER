"""For all real x and z, if sin(x)=sin(z), then x=2kπ+z for some integer k."""

import json

record_id = "reddit_askmath_1skg8rt"
notes = "The witness is valid: sin(0)=sin(π)=0 exactly, while 0=2kπ+π would imply 2k=-1, impossible for integer k. The refuted statement is substantive: it omits the second sine-solution family x=(2k+1)π-z, rather than containing a plain typo."

# Represent each witness value exactly by its integer coefficient of π.
x_coefficient = 0
z_coefficient = 1

# Exact identity: sin(nπ)=0 for every integer n.
def sine_of_integer_multiple_of_pi(coefficient):
    if type(coefficient) is not int:
        raise TypeError("coefficient must be an integer")
    return 0

premise_holds = (
    sine_of_integer_multiple_of_pi(x_coefficient)
    == sine_of_integer_multiple_of_pi(z_coefficient)
)

# Since π is nonzero, x=2kπ+z is equivalent to x_coefficient-z_coefficient=2k.
difference = x_coefficient - z_coefficient
integer_k_exists = difference % 2 == 0

if not premise_holds or integer_k_exists:
    raise AssertionError("reported witness was not independently verified")

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
