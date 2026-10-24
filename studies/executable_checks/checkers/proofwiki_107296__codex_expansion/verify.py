r"""The map s_α ↦ α embeds S into the ordinal β defined as the union of the indices used by the construction."""

import json

REPORT = {
    "record_id": "proofwiki_107296__codex_expansion",
    "verdict": "CONFIRMED",
    "notes": "Exact von Neumann ordinal arithmetic confirms the witness: for S = {s_0}, the union of the sole index 0 is empty, so the image 0 is not in β. The refuted statement has a substantive endpoint error, not a plain typo."
}


def finite_von_neumann_ordinal(index):
    ordinal = frozenset()
    ordinals = []
    for _ in range(index):
        ordinals.append(ordinal)
        ordinal = frozenset(ordinals)
    return ordinal


zero = finite_von_neumann_ordinal(0)
indices = (zero,)
beta_members = set()
for ordinal_index in indices:
    beta_members.update(ordinal_index)
beta = frozenset(beta_members)

assert len(indices) == 1
assert zero == frozenset()
assert beta == zero
assert indices[0] == zero
assert zero not in beta
assert not all(image in beta for image in indices)

print(json.dumps(REPORT, ensure_ascii=False))
