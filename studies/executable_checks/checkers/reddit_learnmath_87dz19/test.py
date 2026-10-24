r"""For every A in K, either ⋃X is a subset of A or A is a subset of ⋃X."""

import json


def subset_from_mask(items, mask):
    return frozenset(item for index, item in enumerate(items) if mask & (1 << index))


base = (0, 1, 2)
base_subsets = tuple(subset_from_mask(base, mask) for mask in range(1 << len(base)))
first_witness = None

for a_mask in range(1 << len(base)):
    a_set = base_subsets[a_mask]
    k_items = base + (a_set,)
    for family_mask in range(1 << len(base_subsets)):
        family = tuple(
            base_subsets[index]
            for index in range(len(base_subsets))
            if family_mask & (1 << index)
        )
        union_x = frozenset(element for member in family for element in member)
        for k_mask in range(1 << len(k_items)):
            k_set = subset_from_mask(k_items, k_mask)
            premises_hold = union_x.issubset(k_set) and a_set in k_set
            conclusion_holds = union_x.issubset(a_set) or a_set.issubset(union_x)
            if premises_hold and not conclusion_holds and first_witness is None:
                first_witness = (a_mask, family_mask, k_mask, a_set, union_x, k_set)

assert first_witness is not None
assert first_witness[:3] == (1, 4, 10)

result = {
    "record_id": "reddit_learnmath_87dz19",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Let X={{1}}, so ⋃X={1}; let A={0}; and let K={1,{0}}. Then ⋃X⊆K and A∈K.",
    "refutation_explanation": "The required alternatives both fail: 1∈⋃X but 1∉A, so ⋃X is not a subset of A; and 0∈A but 0∉⋃X, so A is not a subset of ⋃X.",
    "search_space": "Exhaustively swept all 32,768 triples formed by A⊆{0,1,2}, X⊆P({0,1,2}), and K⊆({0,1,2}∪{A}), in increasing bit-mask order, checking triples satisfying ⋃X⊆K and A∈K."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
