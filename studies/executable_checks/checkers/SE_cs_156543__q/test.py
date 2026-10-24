r"""for any word $\sigma^\prime\in \left(2^{\Xi} \right)^{\omega}$ such that $\hat\sigma$ is a prefix of $\sigma^\prime$, we have that $\sigma^\prime,i \not \Vdash(P1E \wedge P2E) \rightarrow  (\mathsf{F}\, (P1C \vee P2C))$"""

import json
from itertools import product

RECORD_ID = "SE_cs_156543__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness can be named from the supplied quote."
REFUTATION_EXPLANATION = (
    "The quote does not define Xi, hat-sigma, i, the atomic propositions, "
    "their valuations, or the satisfaction relation, and the scope of "
    "not-satisfaction relative to the implication is ambiguous. Abstract "
    "Boolean assignments therefore cannot be realized as admissible infinite "
    "words with the required prefix."
)
SEARCH_SPACE = (
    "All 8 combinations of the 2 possible syntactic scopes of "
    "not-satisfaction and the 4 ordered Boolean pairs (A,B), where A and B "
    "only abbreviate the displayed antecedent and eventuality. This finite "
    "abstraction was swept exhaustively; it is not a sweep of the undefined "
    "infinite-word space."
)

pairs = tuple(product((False, True), repeat=2))
scopes = ("whole_implication", "antecedent_only")
abstract_refutations = []
for scope in scopes:
    for antecedent, eventuality in pairs:
        implication = (not antecedent) or eventuality
        if scope == "whole_implication":
            refutes_abstract_reading = implication
        else:
            refutes_abstract_reading = antecedent and (not eventuality)
        if refutes_abstract_reading:
            abstract_refutations.append((scope, antecedent, eventuality))

assert len(pairs) == 4
assert len(scopes) * len(pairs) == 8
assert abstract_refutations

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
