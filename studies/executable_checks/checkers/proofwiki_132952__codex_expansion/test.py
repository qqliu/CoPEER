"""The displayed construction with coefficient a_i defines a single polynomial P satisfying P(x_i)=a_i for every i."""

import json

RECORD_ID = "proofwiki_132952__codex_expansion"
SOURCE_QUOTE = r":$\ds \map P{x_i} = \sum_{j \mathop = 0}^n a_i \delta_{i j} = a_i$"
SUPPLIED_CONCRETE_INSTANCES = ()

witness = None
for candidate in SUPPLIED_CONCRETE_INSTANCES:
    witness = candidate
    break

assert witness is None

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness can be certified from the supplied data.",
    "refutation_explanation": "The quote gives only an indexed equality. It does not supply the construction of P, a value of n, concrete nodes or coefficients, a definition of delta_{ij}, compatibility conditions on repeated nodes, or a degree bound. Consequently, existence of one polynomial cannot be checked and failure cannot be certified.",
    "search_space": "All concrete polynomial instances supplied by the permitted data: exactly 0 instances. The empty finite space was swept exhaustively; this is inconclusive rather than evidence for the claim.",
}

print(json.dumps(result, separators=(",", ":")))
