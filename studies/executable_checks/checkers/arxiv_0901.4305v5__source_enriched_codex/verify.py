r"""In any imaginary quadratic number field, if a unit is congruent to 1 modulo a prime ideal above a rational prime p≥3, then the unit equals 1."""

import json

RECORD_ID = "arxiv_0901.4305v5__source_enriched_codex"
CONFIRMED_NOTES = (
    "Exact arithmetic confirms the witness in Q(sqrt(-3)): omega is a "
    "nontrivial unit, (1-omega) is a prime ideal above 3, and omega is "
    "congruent to 1 modulo it. The refuted statement is substantive, not "
    "plainly a typo."
)
INVALID_NOTES = (
    "The exact witness checks failed, so the reported counterexample is invalid; "
    "the status of the statement cannot be decided from this witness."
)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def multiply(x, y):
    # Polynomial multiplication followed by reduction with X^2 + X + 1.
    raw = [0, 0, 0]
    for i in range(2):
        for j in range(2):
            raw[i + j] += x[i] * y[j]
    coefficient = raw.pop()
    raw[1] -= coefficient
    raw[0] -= coefficient
    return (raw[0], raw[1])


def is_prime_integer(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def is_squarefree(n):
    n = abs(n)
    divisor = 2
    while divisor * divisor <= n:
        if n % (divisor * divisor) == 0:
            return False
        divisor += 1
    return True


def residue(x, p):
    # In the quotient by (1-omega), omega maps to 1.
    return (x[0] + x[1]) % p


def quotient_is_field(p):
    for nonzero in range(1, p):
        has_inverse = False
        for candidate in range(1, p):
            if (nonzero * candidate) % p == 1:
                has_inverse = True
        if not has_inverse:
            return False
    return True


def coordinates_in_principal_ideal(x):
    # Solving (1-omega)(u+v*omega)=x gives
    # v=(a+b)/3 and u=a-v. Thus the solution is integral exactly when
    # a+b is divisible by 3.
    a, b = x
    total = a + b
    if total % 3 != 0:
        return None
    v = total // 3
    u = a - v
    return (u, v)


def main():
    one = (1, 0)
    omega = (0, 1)
    generator = (1, -1)
    p = 3

    # X^2+X+1 has negative, squarefree discriminant -3. Hence its quadratic
    # order is the full ring of integers of an imaginary quadratic field.
    discriminant = 1 - 4
    maximal_imaginary_order = discriminant < 0 and is_squarefree(discriminant)

    omega_squared = multiply(omega, omega)
    unit_check = multiply(omega, omega_squared) == one
    nontrivial_check = omega != one
    congruence_check = add(omega, neg(one)) == neg(generator)

    # Check that reduction omega -> 1 is multiplicative on all coefficient
    # residue classes. Its kernel is then (1-omega), as certified by the exact
    # coordinate solver above, and its image is the field with three elements.
    homomorphism_check = True
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    x = (a, b)
                    y = (c, d)
                    if residue(multiply(x, y), p) != (
                        residue(x, p) * residue(y, p)
                    ) % p:
                        homomorphism_check = False

    kernel_check = True
    for a in range(-9, 10):
        for b in range(-9, 10):
            x = (a, b)
            coordinates = coordinates_in_principal_ideal(x)
            in_kernel = residue(x, p) == 0
            if (coordinates is not None) != in_kernel:
                kernel_check = False
            if coordinates is not None and multiply(generator, coordinates) != x:
                kernel_check = False

    proper_ideal = residue(one, p) != 0 and residue(generator, p) == 0
    lies_above_p = residue((p, 0), p) == 0
    for integer in range(1, p):
        if residue((integer, 0), p) == 0:
            lies_above_p = False

    prime_ideal_check = (
        is_prime_integer(p)
        and p >= 3
        and quotient_is_field(p)
        and homomorphism_check
        and kernel_check
        and proper_ideal
        and lies_above_p
    )

    confirmed = (
        maximal_imaginary_order
        and unit_check
        and nontrivial_check
        and congruence_check
        and prime_ideal_check
    )

    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED" if confirmed else "REFUTED_WITNESS_INVALID",
        "notes": CONFIRMED_NOTES if confirmed else INVALID_NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
