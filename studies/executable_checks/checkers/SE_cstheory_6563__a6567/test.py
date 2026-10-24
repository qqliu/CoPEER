"""For a pawn there are at most 3 moves, 14 for a rook, 8 for a knight, 14 for a bishop, 28 for a queen and 8 for a king, for a total of 132 possible moves."""

import itertools
import json

record_id = "SE_cstheory_6563__a6567"
bounds = (3, 14, 8, 14, 28, 8)
target_total = 132

coefficient_space = tuple(itertools.product((0, 1), repeat=len(bounds)))
subset_totals = tuple(
    sum(coefficient * bound for coefficient, bound in zip(coefficients, bounds))
    for coefficients in coefficient_space
)

assert len(coefficient_space) == 64
assert all(bound >= 0 for bound in bounds)
assert target_total not in subset_totals

outcome = "NO_WITNESS_INCONCLUSIVE"
witness_description = "No concrete witness can be derived from the supplied quote."
refutation_explanation = "The quote gives numerical upper bounds but supplies neither chess-move definitions nor the piece multiplicities used to obtain 132. The arithmetic sanity sweep finds that 132 is not a sum using each listed bound zero or one times, but that does not refute an unspecified weighted total."
search_space = "Exhaustively swept all 64 coefficient vectors in {0,1}^6 applied to the six listed bounds (3, 14, 8, 14, 28, 8), and checked all six bounds for nonnegativity; no chess positions were searchable from the supplied data."

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
