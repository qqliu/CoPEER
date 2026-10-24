"""Since nodes are expanded in ascending order of $f(n)$ you know that no other node is more promising than the current one."""

import json

source_supplied_concrete_instances = ()
examined = 0
witness = None

for instance in source_supplied_concrete_instances:
    examined += 1
    witness = instance

assert examined == 0
assert witness is None

result = {
    "record_id": "SE_cs_16065__a16089",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be evaluated because the source supplies no nodes, f-values, or definition of \"more promising\".",
    "refutation_explanation": "The claim does not define how \"more promising\" is related to f(n), nor does it supply a concrete search instance. Consequently, no counterexample predicate can be evaluated without inventing absent definitions or data.",
    "search_space": "Exactly the empty set of source-supplied concrete node-expansion instances (0 instances) was swept exhaustively."
}

print(json.dumps(result, separators=(",", ":")))
