r"""Darboux integrability makes every inequality in the displayed chain an equality for the given partition P."""

import json

RECORD_ID = "proofwiki_2882__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be formed from the supplied data because it "
    "specifies neither f, its domain, the partition P, nor the displayed "
    "inequalities."
)
REFUTATION_EXPLANATION = (
    "The quote asserts that unspecified inequalities are equalities but omits "
    "every object needed to evaluate them. The empty bounded sweep therefore "
    "finds no witness but cannot confirm or refute the claim."
)
SEARCH_SPACE = (
    "Exactly the empty tuple of fully specified instances constructible solely "
    "from the supplied quote: 0 instances were checked."
)

instances = ()
checked = 0
for instance in instances:
    checked += 1
assert checked == 0

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
