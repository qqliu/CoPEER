r"""If $a_n$ is a sequence satisfying a linear recurrence then $\limsup_{n \to \infty} \sqrt[n]{|a_n|} = r$ exists and is equal to the absolute value of the largest root of the characteristic polynomial of the recurrence. The above argument (suitably tightened up) shows that $\lim_{n \to \infty} \sqrt[n]{v_n} = 1$, so the roots of the characteristic polynomial have absolute value $\le 1$."""

import json

record_id = "mse_4318153__ans4555433"
verdict = "CONFIRMED"
notes = "Exact recomputation confirms the witness: a_n=(-1)^n satisfies the stated recurrence, its growth limsup is 1, and the recurrence's characteristic roots are -1 and -2, with largest modulus 2. The refuted statement is substantive, not plainly a typo; it omits the possibility that the sequence has zero coefficient on a dominant characteristic root (or that the recurrence is nonminimal)."

q = -1
coefficient_previous = -3
coefficient_second_previous = -2

# For the nonzero geometric sequence a_n=q^n, multiplying the recurrence
# identity by the inverse-free common factor reduction gives this exact
# condition, independent of n.
recurrence_identity = (
    q * q
    == coefficient_previous * q + coefficient_second_previous
)
if not recurrence_identity:
    raise AssertionError("the reported sequence does not satisfy the recurrence")

# The characteristic polynomial is x^2-c1*x-c2. Verify its two roots
# directly and verify their sum and product give every coefficient.
roots = (-2, -1)
for root in roots:
    polynomial_value = (
        root * root
        - coefficient_previous * root
        - coefficient_second_previous
    )
    if polynomial_value != 0:
        raise AssertionError("reported characteristic root is invalid")

if roots[0] == roots[1]:
    raise AssertionError("the two verified quadratic roots must be distinct")
if roots[0] + roots[1] != coefficient_previous:
    raise AssertionError("root sum does not reproduce the polynomial")
if roots[0] * roots[1] != -coefficient_second_previous:
    raise AssertionError("root product does not reproduce the polynomial")

largest_root_modulus = max(abs(roots[0]), abs(roots[1]))
if largest_root_modulus != 2:
    raise AssertionError("incorrect largest root modulus")

# Since |q|=1, |q^n| is identically 1 for every positive integer n.
# Its nonnegative nth root is therefore identically 1, so its limsup is 1.
sequence_growth_limsup = abs(q)
if sequence_growth_limsup != 1:
    raise AssertionError("incorrect sequence growth")
if sequence_growth_limsup == largest_root_modulus:
    raise AssertionError("the claimed equality was not refuted")

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
