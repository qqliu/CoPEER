"""The resampling identity asserts that the second moment of the martingale increment equals twice the second moment of its difference under an independent resampling of the block E_i."""

import json


RECORD_ID = "arxiv_0707.3837v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness is available: the supplied quote defines no probability "
    "space, function f, random configuration r, block E_i, or sigma-fields on which "
    "the two moments can be evaluated."
)
REFUTATION_EXPLANATION = (
    "The quote states a symbolic equality but supplies no concrete admissible "
    "instances or definitions from which exact moment values can be computed. "
    "The empty supplied-instance space is exhausted, but that cannot confirm or "
    "refute the identity."
)
SEARCH_SPACE = (
    "All concrete numerical moment pairs supplied by source_quote, represented as "
    "(martingale_increment_second_moment, resampled_difference_second_moment): "
    "the empty tuple, containing exactly 0 pairs."
)

# Each pair would contain exact values (left moment, resampled moment).  The source
# supplies no such concrete pair, so this explicitly bounded space has size zero.
SUPPLIED_MOMENT_PAIRS = ()
witness = None
for left_moment, resampled_moment in SUPPLIED_MOMENT_PAIRS:
    if left_moment != 2 * resampled_moment:
        witness = (left_moment, resampled_moment)
        break

assert witness is None

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
