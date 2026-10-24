r'''The composite-preservation calculation may replace J applied to ⟨k' ∘ k, id_* ∘ id_*⟩ by J applied to ⟨k ∘ k', id_*⟩ using the identity-morphism law.'''

import json

record_id = "proofwiki_147960__codex_expansion"
k = (0, 0)
k_prime = (1, 0)
identity = (0, 1)
domain = range(2)

def after(first, second):
    images = []
    for element in domain:
        images.append(first[second[element]])
    return tuple(images)

def identity_J(pair):
    return pair

forward = after(k_prime, k)
reversed_order = after(k, k_prime)
identity_composite = after(identity, identity)
left = identity_J((forward, identity_composite))
right = identity_J((reversed_order, identity))

established = (
    forward == (1, 1)
    and reversed_order == (0, 0)
    and identity_composite == identity
    and left == ((1, 1), (0, 1))
    and right == ((0, 0), (0, 1))
    and left != right
)

if established:
    verdict = "CONFIRMED"
    notes = "Exact recomputation gives k' ∘ k = (1,1), k ∘ k' = (0,0), and id_* ∘ id_* = id_*, so identity J yields unequal ordered pairs. The statement is false as written, but the reversed composite in the cited calculation is plainly a typographical error rather than a substantive identity-law consequence."
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The exact recomputation did not establish the reported inequality; the alleged reversed composite appears to be a typographical issue."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
