r'''The proof asserts that for an integer a, cont(b n q f) = a * cont(n f), i.e. that pulling an integer scalar a out of the content multiplies the content by a itself. This is false when a (or b) is negative, since the content of an integer polynomial is the GCD of its coefficients and is nonnegative; the correct identity is cont(a g) = |a| cont(g). The proof never splits on the sign of a or b, and the same omission propagates to the final line cont(q f) = (a/b)(1/n) cont(n f) = q cont f.'''

import json


def nonnegative_gcd(x, y):
    x = abs(x)
    y = abs(y)
    while y != 0:
        x, y = y, x % y
    return x


def polynomial_content(coefficients):
    divisor = 0
    for coefficient in coefficients:
        divisor = nonnegative_gcd(divisor, coefficient)
    return divisor


integer_scalar = -1
polynomial = (-1,)
scaled_polynomial = tuple(integer_scalar * coefficient for coefficient in polynomial)
original_content = polynomial_content(polynomial)
scaled_content = polynomial_content(scaled_polynomial)
assert polynomial == (-1,)
assert scaled_polynomial == (1,)
assert original_content == 1
assert scaled_content == 1
assert integer_scalar * original_content == -1
assert scaled_content != integer_scalar * original_content
assert scaled_content == abs(integer_scalar) * original_content

result = {
    "record_id": "proofwiki_25056",
    "verdict": "CONFIRMED",
    "notes": "Independent exact recomputation confirms the witness: for a = -1 and g = -1, the nonnegative coefficient GCD gives cont(g) = 1 and cont(a g) = cont(1) = 1, while a * cont(g) = -1. Thus the asserted identity fails. This is a substantive sign omission, not plainly a typo.",
}
print(json.dumps(result, separators=(",", ":")))
