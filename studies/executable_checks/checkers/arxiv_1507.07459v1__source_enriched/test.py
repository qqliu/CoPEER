r"""Let \(I=(\mathcal U,\mathcal C)\) be a \(k\)-set-packing instance with \(|\mathcal C|=n\), let \(\varepsilon>0\), and let \(M\subseteq\mathcal C\) be a \(4(1+1/\varepsilon)\log_2 n\)-locally optimal matching (that is, a packing of mutually disjoint sets). Let \(x\) be any feasible solution to the intersecting-family LP, let \(\mathcal F=\{f\in\mathcal C:x_f>0\}\), and let \(\mathcal F_2\) consist of those \(f\in\mathcal F\) that intersect exactly two members of \(M\). Define the auxiliary undirected multigraph \(H\) to have one vertex \(v_m\) for every \(m\in M\) and one edge \(e_f\) for every \(f\in\mathcal F_2\), joining \(v_{m_1}\) and \(v_{m_2}\) when \(m_1,m_2\) are the two members of \(M\) intersected by \(f\); distinct members of \(\mathcal F_2\) may therefore give parallel edges. For every \(X\subseteq V(H)\), let \(\mathcal B_X=\{f\in\mathcal F_2:e_f\in E(H[X])\}\). If \(|E(H[X])|>|X|\), then \(\mathcal B_X\) is an improving set for \(M\): \(\mathcal B_X\) is a packing and, in the intersection graph \(G\) of the packings \(M\) and \(\mathcal B_X\), \(N_G(B_X,M)=N(B_X)\cap M\) and \(\left|(M\cup B_X)\setminus N_G(B_X,M)\right|>|M|\). Equivalently, adding the source sets corresponding to the edges of \(H[X]\) and removing the members of \(M\) that they intersect yields a mutually disjoint solution of larger cardinality."""

import json
from fractions import Fraction
from itertools import combinations

RECORD_ID = "arxiv_1507.07459v1__source_enriched"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No certified witness. The sweep finds the unresolved candidate "
    "U={0,1,2,3,4,5}, M={{0,1,2},{3,4,5}}, and "
    "B={{0,1,3},{0,2,3},{0,3,4}}: its three source sets give three "
    "parallel edges on two vertices and are not a packing, while M is "
    "globally optimal. Assigning each source set weight 1/3 gives positive "
    "exact weights, but feasibility cannot be certified from the supplied data."
)
REFUTATION_EXPLANATION = (
    "The source quote never defines the constraints of the intersecting-family "
    "LP. Consequently the required hypothesis that x is feasible is not "
    "finitely checkable without inventing an absent definition. The bounded "
    "sweep exposes a concrete obstruction to the asserted packing implication, "
    "but it cannot certify that obstruction as a counterexample to the full claim."
)
SEARCH_SPACE = (
    "Exhaustively swept all 8,160 pairs (M,B) on U={0,1,2,3,4,5}, where M "
    "is an unordered pair of disjoint 3-subsets and B is a 3-element subfamily "
    "of the remaining 3-subsets; for each pair, all four X subsets of M and "
    "all 32 subfamilies of C=M∪B were checked."
)


def mask(elements):
    value = 0
    for element in elements:
        value |= 1 << element
    return value


def is_packing(family):
    for left, right in combinations(family, 2):
        if left & right:
            return False
    return True


def maximum_packing_size(family):
    best = 0
    size = len(family)
    for selection in range(1 << size):
        chosen = tuple(family[index] for index in range(size)
                       if selection & (1 << index))
        if is_packing(chosen) and len(chosen) > best:
            best = len(chosen)
    return best


universe = tuple(range(6))
triples = tuple(mask(parts) for parts in combinations(universe, 3))
known_m = frozenset((mask((0, 1, 2)), mask((3, 4, 5))))
known_b = frozenset((mask((0, 1, 3)), mask((0, 2, 3)), mask((0, 3, 4))))
examined = 0
structural_candidates = 0
known_found = False

for matching in combinations(triples, 2):
    if matching[0] & matching[1]:
        continue
    available = tuple(item for item in triples if item not in matching)
    for sources in combinations(available, 3):
        examined += 1
        collection = matching + sources
        maximum_size = maximum_packing_size(collection)
        eligible = tuple(
            sum(1 for member in matching if source & member) == 2
            for source in sources
        )
        excess_found = False
        for vertex_selection in range(4):
            induced_edges = 0
            if vertex_selection == 3:
                induced_edges = sum(1 for flag in eligible if flag)
            vertex_count = sum(
                1 for index in range(2)
                if vertex_selection & (1 << index)
            )
            if induced_edges > vertex_count:
                excess_found = True
        weights = tuple(Fraction(1, 3) for _ in sources)
        positive_support = all(weight > 0 for weight in weights)
        structural_failure = not is_packing(sources)
        globally_optimal = maximum_size <= len(matching)
        if (all(eligible) and excess_found and positive_support
                and structural_failure and globally_optimal):
            structural_candidates += 1
            if (frozenset(matching) == known_m
                    and frozenset(sources) == known_b):
                known_found = True

assert examined == 8160
assert structural_candidates > 0
assert known_found

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
