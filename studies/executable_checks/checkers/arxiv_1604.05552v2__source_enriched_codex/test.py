"""Nontrivial common truncated arcs at P for every positive order imply that P is not isolated in X ∩ Y."""

import itertools
import json

RECORD_ID = "arxiv_1604.05552v2__source_enriched_codex"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No finite witness is produced: checking common truncated arcs through any "
    "fixed order does not establish their existence for every positive order."
)
REFUTATION_EXPLANATION = (
    "A counterexample would have to make P isolated in X ∩ Y while satisfying "
    "the premise for every positive integer m. The quote supplies neither a "
    "finite reduction of that unbounded premise nor bounded encodings of X, Y, "
    "Z, P, and their arc spaces, so an exhaustive finite search cannot certify "
    "such a counterexample."
)
SEARCH_SPACE = (
    "Exhaustively swept all 512 Boolean prefixes consisting of one isolation "
    "value and eight common-arc values for the fixed orders m = 1, 2, ..., 8, "
    "in lexicographic order with False before True. The unique prefix with "
    "isolation true and all eight common-arc values true remains undecided for "
    "orders m > 8 and is not a counterexample."
)

BOUND = 8
examined = 0
undecided_prefixes = 0
for values in itertools.product((False, True), repeat=BOUND + 1):
    examined += 1
    isolated = values[0]
    common_through_bound = values[1:]
    if isolated and all(common_through_bound):
        undecided_prefixes += 1

assert examined == 512
assert undecided_prefixes == 1

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
