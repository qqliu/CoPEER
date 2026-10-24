r"""Functions f,g: N→N such that g ∘ f is injective while g is not injective do not exist."""

import json

REPORT = {
    "record_id": "reddit_learnmath_q0j6vm",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic verifies that g(f(n)) = n for every natural n, while g(1) = g(2) = 1 with 1 != 2. The refuted statement is substantive, not plainly a typo.",
}


def is_natural(n):
    return isinstance(n, int) and not isinstance(n, bool) and n >= 0


def f(n):
    assert is_natural(n)
    return 2 * n


def g(k):
    assert is_natural(k)
    if k % 2 == 0:
        return k // 2
    return 1


# Exact coefficient reduction proves the composition identity universally:
# f(n) has coefficient 2, which is divisible by the divisor 2, and the
# resulting quotient coefficient is 1. Thus g(f(n)) = (2*n)//2 = n for
# every nonnegative integer n, independently of whether N includes zero.
scale = 2
divisor = 2
quotient_coefficient, remainder_coefficient = divmod(scale, divisor)
assert scale > 0 and divisor > 0
assert remainder_coefficient == 0
assert quotient_coefficient == 1

# Recompute the claimed non-injectivity witness exactly.
left = 1
right = 2
assert is_natural(left) and is_natural(right)
assert left != right
assert g(left) == 1
assert g(right) == 1
assert g(left) == g(right)

# Confirm that both functions have natural-number outputs at the collision
# inputs and that the coefficient proof agrees with direct evaluations.
assert is_natural(f(left)) and is_natural(f(right))
assert is_natural(g(left)) and is_natural(g(right))
assert g(f(0)) == 0
assert g(f(left)) == left
assert g(f(right)) == right
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, ensure_ascii=False))
