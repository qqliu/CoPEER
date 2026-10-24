r"""Lemma 2. If C1 and C2 are minimal edge cuts with C1 intersect C2 = emptyset, then C1 = C2."""

import json

REPORT = {
    "record_id": "Algorithms_33__sol5",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No certified witness. The sweep contains a disjoint unequal pair C1={0} and C2={1}, but the quote gives no way to certify either set as a minimal edge cut.",
    "refutation_explanation": "The claim does not specify an ambient graph or define \"minimal edge cut,\" including what minimality means. Exact set relations can be checked, but the premise that C1 and C2 are minimal edge cuts cannot be evaluated without adding data or a definition.",
    "search_space": "Every ordered pair (C1, C2) of subsets of the fixed labeled universe {0, 1}, generated in increasing two-bit-mask order; only nonemptiness, disjointness, and equality are evaluated.",
}

UNIVERSE = (0, 1)
MASK_LIMIT = 1 << len(UNIVERSE)
visited = 0
relation_candidates = []

for left_mask in range(MASK_LIMIT):
    c1 = frozenset(
        UNIVERSE[index]
        for index in range(len(UNIVERSE))
        if left_mask & (1 << index)
    )
    for right_mask in range(MASK_LIMIT):
        c2 = frozenset(
            UNIVERSE[index]
            for index in range(len(UNIVERSE))
            if right_mask & (1 << index)
        )
        visited += 1
        if c1 and c2 and c1.isdisjoint(c2) and c1 != c2:
            relation_candidates.append((left_mask, right_mask))

assert visited == MASK_LIMIT * MASK_LIMIT
assert relation_candidates
assert relation_candidates[0] == (1, 2)
assert REPORT["outcome"] == "NO_WITNESS_INCONCLUSIVE"

print(json.dumps(REPORT, separators=(",", ":")))
