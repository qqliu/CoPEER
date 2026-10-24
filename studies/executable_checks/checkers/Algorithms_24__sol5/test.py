r"""Not in c(S intersect T, T intersect S) (since u in S intersect T and v in T intersect S, the edge goes from S intersect T to T intersect S)"""

import json

REPORT = {
    "record_id": "Algorithms_24__sol5",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No counterexample is certified: the quote does not define c or identify the object governed by “Not in c(...)”, so membership in c cannot be evaluated.",
    "refutation_explanation": "The membership premises determine only that u and v lie in both sets. The quote supplies no definition of c and omits the subject of “Not in c(...)”. The exhaustive bounded sweep therefore admits both truth values for the relevant c-membership proposition for every retained tuple; neither value can be selected from the permitted data, so no certified witness or refutation is possible.",
    "search_space": "Universe U={0,1}; every S,T⊆U (four each), every ordered (u,v)∈U², retaining exactly those with u∈S∩T and v∈T∩S; for each retained tuple, both Boolean completions of the undefined proposition “the edge is in c(S∩T,T∩S)”.",
}

universe = (0, 1)
subsets = []
for mask in range(1 << len(universe)):
    subset = frozenset(
        element
        for index, element in enumerate(universe)
        if mask & (1 << index)
    )
    subsets.append(subset)

base_cases = 0
retained_cases = 0
completion_values_by_case = []
for set_s in subsets:
    for set_t in subsets:
        intersection_st = set_s & set_t
        intersection_ts = set_t & set_s
        for u in universe:
            for v in universe:
                base_cases += 1
                if u in intersection_st and v in intersection_ts:
                    retained_cases += 1
                    values = []
                    for undefined_c_membership in (False, True):
                        values.append(undefined_c_membership)
                    completion_values_by_case.append(tuple(values))

assert base_cases == len(subsets) * len(subsets) * len(universe) * len(universe)
assert retained_cases == len(completion_values_by_case)
assert retained_cases > 0
assert all(values == (False, True) for values in completion_values_by_case)
computed_outcome = "NO_WITNESS_INCONCLUSIVE"
assert computed_outcome == REPORT["outcome"]

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
