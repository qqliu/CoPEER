r"""Then $1=a^k=g^{km}$ so $km=p-1$ since $g$ is a generator."""

import json

REPORT = {
    "record_id": "mse_2180059__ans2180072",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation validates the witness: modulo 5, 2 is a generator, 3=2^3 has least positive order 4, and 2^(4*3)=1 while 4*3=12 != 4=p-1. The refuted statement is a substantive logical error, not plainly a typo: being a generator implies p-1 divides km, not that km equals p-1."
}


def modular_power(base, exponent, modulus):
    assert isinstance(exponent, int) and exponent >= 0
    result = 1
    factor = base % modulus
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = (result * factor) % modulus
        factor = (factor * factor) % modulus
        remaining //= 2
    return result


p = 5
g = 2
m = 3
k = 4

assert p > 1
assert all(p % divisor != 0 for divisor in range(2, p))
assert {modular_power(g, exponent, p) for exponent in range(1, p)} == set(range(1, p))

a = modular_power(g, m, p)
assert a == 3
assert modular_power(a, k, p) == 1
assert all(modular_power(a, exponent, p) != 1 for exponent in range(1, k))
assert modular_power(g, k * m, p) == 1
assert (k * m) % (p - 1) == 0
assert k * m == 12
assert p - 1 == 4
assert k * m != p - 1
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
