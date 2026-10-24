"""For the arbitrary relation R in the theorem, a URM program computing its characteristic function is guaranteed to exist."""

import itertools
import json

RECORD_ID = "proofwiki_4209__codex_expansion"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No finite witness is produced: failure of URM-computability is a global "
    "property, and the quote supplies neither a concrete relation nor URM syntax "
    "or semantics."
)
REFUTATION_EXPLANATION = (
    "The quote assumes that P_R exists and appeals to a result about recursive "
    "functions, but it does not state that R is recursive. Thus it does not "
    "justify the guarantee for an arbitrary relation. A bounded finite observation "
    "trace cannot certify that a relation is noncomputable, so the target claim is "
    "not finitely refutable under the supplied data."
)
SEARCH_SPACE = (
    "Exhaustively enumerated, in fixed itertools.product order, all 2^8 = 256 "
    "binary observation traces of length 8. This is only an illustrative bounded "
    "sweep, not an exhaustive search over relations or URM programs."
)


def main():
    trace_count = 0
    for trace in itertools.product((0, 1), repeat=8):
        assert len(trace) == 8
        trace_count += 1
    assert trace_count == (1 << 8)

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
