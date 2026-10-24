"""Consider a flow network G containing a directed edge u ->v. Prove that if there exists a minimum (s, t)-cut (S, T) where u in S and v in T, then it is impossible for there to exist a minimum cut (S, T ) satisfying u in T and v in S."""

import itertools
import json

REPORT = {
    "record_id": "Algorithms_24__sol2",
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": "No counterexample was found in the bounded space: for every searched network, the cuts with S={s,u} and S={s,v} were not both minimum.",
    "refutation_explanation": "The bounded search is negative, not a refutation of the universal claim. Every assignment satisfies the exact identity C({s,u}) + C({s,v}) = C({s}) + C({s,u,v}) + c(u,v) + c(v,u); since c(u,v)=1, the two oppositely oriented cuts cannot both be minimum in this space.",
    "search_space": "All 2,048 capacity functions on the 12 ordered pairs of distinct labeled vertices (s,u,v,t), with c(u,v)=1 and every other capacity in {0,1}; for each network, all four (s,t)-cuts S={s} union X for X contained in {u,v} were evaluated exactly in mask order 0,1,2,3.",
}

vertices = ("s", "u", "v", "t")
ordered_edges = tuple(
    (tail, head)
    for tail in vertices
    for head in vertices
    if tail != head
)
variable_edges = tuple(edge for edge in ordered_edges if edge != ("u", "v"))


def cut_capacity(capacities, side_s):
    return sum(
        capacities[edge]
        for edge in ordered_edges
        if edge[0] in side_s and edge[1] not in side_s
    )


first_witness = None
for bits in itertools.product((0, 1), repeat=len(variable_edges)):
    capacities = {edge: 0 for edge in ordered_edges}
    capacities[("u", "v")] = 1
    for edge, bit in zip(variable_edges, bits):
        capacities[edge] = bit

    cut_values = []
    for mask in range(4):
        side_s = {"s"}
        if mask & 1:
            side_s.add("u")
        if mask & 2:
            side_s.add("v")
        cut_values.append(cut_capacity(capacities, side_s))

    identity_left = cut_values[1] + cut_values[2]
    identity_right = (
        cut_values[0]
        + cut_values[3]
        + capacities[("u", "v")]
        + capacities[("v", "u")]
    )
    if identity_left != identity_right:
        raise AssertionError("directed-cut identity failed")

    minimum_value = min(cut_values)
    if cut_values[1] == minimum_value and cut_values[2] == minimum_value:
        first_witness = (bits, tuple(cut_values))
        break

actual_outcome = (
    "WITNESS_FOUND" if first_witness is not None else "NO_WITNESS_EXHAUSTIVE"
)
if actual_outcome != REPORT["outcome"]:
    raise AssertionError((actual_outcome, first_witness))

print(json.dumps(REPORT, separators=(",", ":")))
