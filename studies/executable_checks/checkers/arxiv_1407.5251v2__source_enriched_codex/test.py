"""For all irreducible generic smooth representations of GL(n), their normalized essential Whittaker vectors have the same restriction to the mirabolic subgroup P_n."""

import json

RECORD_ID = "arxiv_1407.5251v2__source_enriched_codex"
CASES = ()

for _case in CASES:
    raise AssertionError("No concrete cases are supplied by the permitted data")

result = {
    "record_id": RECORD_ID,
    "outcome": "CLAIM_NOT_FINITELY_REFUTABLE",
    "witness_description": "No concrete witness is available from the supplied source data.",
    "refutation_explanation": "The claim quantifies over all irreducible generic smooth representations of GL(n) and equality of their Whittaker-vector restrictions on P_n. The quote supplies no finite encoding, bounded family of representations, or finite domain of group elements, so the claim is not finitely checkable or refutable here without inventing definitions or data.",
    "search_space": "The empty tuple of concrete representation instances supplied by the quote; exactly 0 instances are swept in fixed tuple order."
}
print(json.dumps(result, separators=(",", ":")))
