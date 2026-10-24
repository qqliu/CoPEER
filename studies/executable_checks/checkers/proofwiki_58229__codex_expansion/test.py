"""For the substitution t = π(x-a)/(b-a), the normalization integral equals π/(b-a) times the corresponding integral over [0,π]."""

import json
from fractions import Fraction

record_id = "proofwiki_58229__codex_expansion"
witness_description = (
    "Take a=0, b=1, n=1, and α_1=1. The corresponding integrand is "
    "sin²(t). Its transformed integral is 1/2, whereas the claimed "
    "normalization gives π²/2."
)
refutation_explanation = (
    "With t=π(x-a)/(b-a), the Jacobian is dx=(b-a)/π dt, so the "
    "multiplier must be (b-a)/π. For [a,b]=[0,1], ∫_0^π sin²(t) "
    "dt=π/2, making the actual x-integral 1/2. The claimed factor gives "
    "π²/2, which is greater than 9/2 because π>3, and therefore cannot "
    "equal 1/2."
)
search_space = (
    "The program exhaustively sweeps the two fixed candidates a=0, "
    "b∈{1,2}, n=1, α=(1,), using the exact identity "
    "∫_0^π sin²(t)dt=π/2 and the exact bound π>3; it reports the first "
    "witness in the fixed order b=1, then b=2."
)

# For n=1 and α_1=1, the integral over [0,π] is exactly π/2.
# If L=b-a, the Jacobian makes the actual integral L/2. The claimed
# expression is π²/(2L), whose exact lower bound from π>3 is 9/(2L).
candidates = ((0, 1, 1, (1,)), (0, 2, 1, (1,)))
witnesses = []
for a, b, n, alpha in candidates:
    length = b - a
    actual = Fraction(length, 2)
    claimed_lower_bound = Fraction(9, 2 * length)
    if claimed_lower_bound > actual:
        witnesses.append((a, b, n, alpha))

assert witnesses
assert witnesses[0] == (0, 1, 1, (1,))

result = {
    "record_id": record_id,
    "outcome": "WITNESS_FOUND",
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
