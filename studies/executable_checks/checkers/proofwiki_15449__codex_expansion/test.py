"""The Combined Sum Rule for Real Sequences is applicable to the measure-value sequences in the countable-additivity calculation."""

import json

SOURCE_QUOTE = r"""0042 | {{eqn | r = \sum_{n \mathop \in \N} a \map \mu {E_n} + b \map \nu {E_n}
0043 |       | c = [[Combined Sum Rule for Real Sequences]]
0044 | }}"""

WITNESS_DESCRIPTION = (
    "No concrete witness can be evaluated: the quote gives only a symbolic "
    "sum and names a rule."
)
REFUTATION_EXPLANATION = (
    "The quote does not define the measure-value sequences, give their terms, "
    "or state conditions governing the named rule. Thus applicability cannot "
    "be checked, and neither a counterexample nor validation follows from the "
    "supplied data."
)
SEARCH_SPACE = (
    "Exhaustively inspected the one supplied symbolic calculation (a singleton "
    "space); it contains zero concrete sequence/value assignments, so this "
    "bounded sweep is syntactic and inconclusive."
)

# The sole quoted calculation is represented together with all concrete
# sequence/value assignments it supplies. That assignment tuple is empty.
bounded_space = ((SOURCE_QUOTE, ()),)
witness = None
for quoted_calculation, supplied_assignments in bounded_space:
    for assignment in supplied_assignments:
        witness = (quoted_calculation, assignment)
        break
    if witness is not None:
        break

if witness is not None:
    raise AssertionError("The source representation unexpectedly supplied data")

result = {
    "record_id": "proofwiki_15449__codex_expansion",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
