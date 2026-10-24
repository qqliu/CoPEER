r"""Thus, for example, if for some $e\in S$ you have $e\leq n-m$, then you get that $c(G_n(S))=1$."""

import json

RECORD_ID = "mse_5107936__ans5108003"
TARGET_CLAIM = "Thus, for example, if for some $e\\in S$ you have $e\\leq n-m$, then you get that $c(G_n(S))=1$."
SOURCE_QUOTE = "Thus, for example, if for some $e\\in S$ you have $e\\leq n-m$, then you get that $c(G_n(S))=1$."

WITNESS_DESCRIPTION = "No concrete witness can be certified from the supplied text."
REFUTATION_EXPLANATION = (
    "The quote merely repeats the claim. It does not define c, G_n(S), m, "
    "the admissible domains of n, e, and S, or how to evaluate c(G_n(S)); "
    "therefore the antecedent and conclusion cannot be jointly evaluated "
    "under any supplied interpretation."
)
SEARCH_SPACE = (
    "Exactly one supplied (target_claim, source_quote) pair was exhaustively "
    "audited. No numerical or structural assignments were searched because "
    "the supplied text specifies no admissible domains or interpretations for them."
)

candidate_space = ((TARGET_CLAIM, SOURCE_QUOTE),)
outcome = None
for claim, quote in candidate_space:
    if claim == quote:
        outcome = "NO_WITNESS_INCONCLUSIVE"

assert outcome is not None
result = {
    "record_id": RECORD_ID,
    "outcome": outcome,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))
