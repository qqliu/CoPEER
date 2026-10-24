"""The composite-preservation calculation may replace J applied to ⟨k' ∘ k, id_* ∘ id_*⟩ by J applied to ⟨k ∘ k', id_*⟩ using the identity-morphism law."""

import itertools
import json

RECORD_ID = "proofwiki_147960__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "On X={0,1}, let k be the constant-zero map (0,0), let k' be the swap map (1,0), and let J be the identity on ordered pairs. Then k' ∘ k=(1,1), while k ∘ k'=(0,0)."
REFUTATION_EXPLANATION = "The identity law does give id_X ∘ id_X=id_X, but it does not reverse the first composite. Thus J(⟨k' ∘ k,id_X ∘ id_X⟩)=((1,1),(0,1)) and J(⟨k ∘ k',id_X⟩)=((0,0),(0,1)), which are unequal."
SEARCH_SPACE = "Exhaustively swept all 16 ordered pairs (k,k') of the four functions X→X for X={0,1}, in lexicographic image-tuple order, with id_X=(0,1) and J fixed as the identity on ordered pairs."

X = (0, 1)
IDENTITY = (0, 1)
ALL_MAPS = tuple(itertools.product(X, repeat=2))


def compose(outer, inner):
    return tuple(outer[inner[x]] for x in X)


def J(ordered_pair):
    return ordered_pair


witnesses = []
checked = 0
for k in ALL_MAPS:
    for k_prime in ALL_MAPS:
        checked += 1
        left = J((compose(k_prime, k), compose(IDENTITY, IDENTITY)))
        right = J((compose(k, k_prime), IDENTITY))
        if left != right:
            witnesses.append((k, k_prime, left, right))

assert checked == 16
assert compose(IDENTITY, IDENTITY) == IDENTITY
assert witnesses
assert witnesses[0] == (
    (0, 0),
    (1, 0),
    ((1, 1), (0, 1)),
    ((0, 0), (0, 1)),
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
