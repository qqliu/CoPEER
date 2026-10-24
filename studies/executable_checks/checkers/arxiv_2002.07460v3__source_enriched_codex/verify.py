r"""For every nonzero Gaussian integer z representing a similarity rotation R of Z[i] by multiplication by z/|z|, the denominator of R with respect to Z[i] equals |z|."""

import json

record_id = "arxiv_2002.07460v3__source_enriched_codex"
confirmed_notes = "Exact arithmetic confirms that z=2 has |z|=2 and induces the identity rotation, whose Gaussian-lattice denominator is 1. Thus this concrete instance violates the asserted equality. The refuted statement is substantive as written, not plainly a typo; it omits a primitive or otherwise normalized choice of z."
invalid_notes = "The reported witness could not be validated by exact arithmetic. The refuted statement would be substantive as written, not plainly a typo."


def gaussian_multiply(left, right):
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c)


def integer_scale(factor, value):
    return (factor * value[0], factor * value[1])


z = (2, 0)
length = 2
basis = ((1, 0), (0, 1))

nonzero = z != (0, 0)
length_is_exact = length > 0 and length * length == z[0] * z[0] + z[1] * z[1]
normalized_action_is_identity = all(
    gaussian_multiply(z, vector) == integer_scale(length, vector)
    for vector in basis
)

admissible_positive_integer_scales = tuple(
    scale
    for scale in range(1, length + 1)
    if all(
        integer_scale(scale, vector)[0] == scale * vector[0]
        and integer_scale(scale, vector)[1] == scale * vector[1]
        for vector in basis
    )
)
denominator = min(admissible_positive_integer_scales)
witness_refutes_claim = (
    nonzero
    and length_is_exact
    and normalized_action_is_identity
    and denominator == 1
    and denominator != length
)

if witness_refutes_claim:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_notes

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
