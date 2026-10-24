r"""**Base case**: Let $V(G)=\{v_1,v_2\}$, then the most edges the graph can have is $\frac{2(2-1)}{2}=1$, so this means $E(G)=\{v_1 v_2\}$, and $deg.v_1 = deg.v_2=1$"""

import json

RECORD_ID = "SE_math_3308067__q"
WITNESS = "The graph with V(G)={v1,v2} and E(G)=empty set; deg(v1)=deg(v2)=0."
EXPLANATION = (
    "Having at most one edge does not imply having exactly one edge. "
    "The empty simple undirected graph on the two stated vertices has 0 edges, "
    "so E(G) is not {v1v2} and both degrees are 0 rather than 1."
)
SPACE = (
    "All simple undirected loopless graphs on the fixed labeled vertex set "
    "{v1,v2}: the 2 subsets of the single possible edge {v1v2}, examined "
    "in mask order 0,1."
)

possible_edge = ("v1", "v2")
found = None

for mask in range(2):
    edges = () if mask == 0 else (possible_edge,)
    degree_v1 = sum(1 for edge in edges if "v1" in edge)
    degree_v2 = sum(1 for edge in edges if "v2" in edge)
    claimed_edge_set = edges == (possible_edge,)
    claimed_degrees = degree_v1 == 1 and degree_v2 == 1
    if not (claimed_edge_set and claimed_degrees):
        found = (edges, degree_v1, degree_v2)
        break

if found == ((), 0, 0):
    outcome = "WITNESS_FOUND"
    witness_description = WITNESS
    refutation_explanation = EXPLANATION
else:
    outcome = "NO_WITNESS_EXHAUSTIVE"
    witness_description = "No counterexample was found."
    refutation_explanation = "Every candidate in the stated finite space satisfied the claimed edge set and degrees."

result = {
    "record_id": RECORD_ID,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": SPACE,
}
print(json.dumps(result, separators=(",", ":")))
