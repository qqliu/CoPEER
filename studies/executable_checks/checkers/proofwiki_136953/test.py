r"""In the second eqn block the proof asserts f^\to \circ f^\gets = (f^\gets \circ f^\to) \circ id_{P(T)}, citing 'Identity Mapping is Right Identity', and then applies 'Composition of Mappings is Associative' to turn (f^\gets \circ f^\to) \circ (f^\to \circ (f^\to)^{-1}) into ((f^\to \circ f^\gets) \circ f^\to) \circ (f^\to)^{-1}. Both steps silently swap the order of the composite f^\gets \circ f^\to, and the cited right-identity theorem's precondition (the identity must be on the domain of the mapping it postcomposes) fails."""

import json
from itertools import permutations

TO = r"f^\to"
GETS = r"f^\gets"
INVERSE_TO = r"(f^\to)^{-1}"


def parenthesizations(sequence):
    if len(sequence) == 1:
        return (sequence[0],)
    results = []
    for split in range(1, len(sequence)):
        left_terms = parenthesizations(sequence[:split])
        right_terms = parenthesizations(sequence[split:])
        for left in left_terms:
            for right in right_terms:
                results.append(("circ", left, right))
    return tuple(results)


# Right-identity elimination cannot change the order of the non-identity factors.
orders = tuple(permutations((TO, GETS), 2))
left_order = (TO, GETS)
right_order_after_identity_elimination = (GETS, TO)
right_identity_can_produce_left = any(
    order == left_order
    for order in orders
    if order == right_order_after_identity_elimination
)

# Associativity ranges over every binary parenthesization but preserves leaf order.
association_source_order = (GETS, TO, TO, INVERSE_TO)
association_closure = parenthesizations(association_source_order)
claimed_association_result = (
    "circ",
    ("circ", ("circ", TO, GETS), TO),
    INVERSE_TO,
)
association_can_produce_claimed_result = any(
    term == claimed_association_result for term in association_closure
)

assert len(orders) == 2
assert len(association_closure) == 5
assert not right_identity_can_produce_left
assert not association_can_produce_claimed_result

result = {
    "record_id": "proofwiki_136953",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete counterexample: the finite syntactic sweep detects the order reversals, but the supplied data does not define f^\\to, f^\\gets, their domains/codomains, or which interpretations are admissible.",
    "refutation_explanation": "The cited rewrites preserve factor order, so the displayed strings support the order-swap criticism. However, whether the right-identity precondition fails is a typing question that cannot be decided from the quote: the domain/codomain of f^\\gets \\circ f^\\to is absent. Consequently no semantic witness can honestly refute or verify the full target claim.",
    "search_space": "Exhaustive syntactic sweep of the 2 permutations of the two composition symbols in the displayed equality and all 5 binary parenthesizations of the four-factor word in the associativity step. No semantic interpretations of f^\\to or f^\\gets were swept, because the supplied data gives no definitions or domain/codomain declarations.",
}
print(json.dumps(result, separators=(",", ":")))
