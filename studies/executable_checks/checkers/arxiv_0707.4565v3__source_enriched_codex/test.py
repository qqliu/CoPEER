r"""Let \(\lambda\in\mathbb Q\) satisfy \(0\neq |1+\lambda|\neq1\), let \(k\in\mathbb N\), and suppose \(\mathcal A\) is a randomized \(2^{N^k}\)-approximation algorithm for \(I(\lambda)\): on every input graph \(H\) having \(N\) nodes, it runs in time polynomial in \(N\) and returns \(\mathcal I(H;\lambda)\in\mathbb Q\) such that \(\Pr[2^{-N^k}I(H;\lambda)\leq\mathcal I(H;\lambda)\leq2^{N^k}I(H;\lambda)]\geq3/4\). Let \(G=(V,E)\) have \(|V|=n\), and choose a positive integer \(l\) as follows. If \(|1+\lambda|>1\), put \(x=(1+\lambda)^l-1\), require \(|x|\geq2^{n^{k+1}}\), and let \(G_l\) be obtained by cloning every vertex of \(G\) exactly \(l-1\) times; hence \(|V(G_l)|=nl\) and \(I(G;x)=I(G_l;\lambda)\). If \(0<|1+\lambda|<1\), put \(x=\lambda/(1+\lambda)^l\), require \(|x|\geq2^{n^{k+1}}\), and let \(G_l\) be obtained by performing an \(l\)-comb at every original vertex, where an \(l\)-comb adds \(l\) new degree-one neighbors to that vertex; hence \(|V(G_l)|=n(l+1)\) and \(I(G;x)=(1+\lambda)^{-l|V|}I(G_l;\lambda)\). Define \(\mathcal I(G;x)=\mathcal I(G_l;\lambda)\) in the cloning case and \(\mathcal I(G;x)=\mathcal I(G_l;\lambda)/(1+\lambda)^{l|V|}\) in the comb case. The claim is that applying \(\mathcal A\) to the enlarged input \(G_l\) yields \(\Pr[2^{-n^k}I(G;x)\leq\mathcal I(G;x)\leq2^{n^k}I(G;x)]\geq3/4\), with the approximation exponent computed from \(n=|V(G)|\), rather than from the number of nodes \(|V(G_l)|\) in the graph actually supplied to \(\mathcal A\). Here \(I(G;x)\) is the independent-set polynomial used in the source, whose degree \(c\) is the maximum independent-set size and which is written as \(I(G;x)=Nx^c+\sum_{0\leq j\leq c-1}i(G;j)x^j\), with \(N\) the number of independent sets of maximum size."""

import json
from fractions import Fraction
from itertools import combinations, product


def labeled_graphs(vertex_count):
    possible_edges = tuple(combinations(range(vertex_count), 2))
    for choices in product((0, 1), repeat=len(possible_edges)):
        yield frozenset(
            edge for edge, included in zip(possible_edges, choices) if included
        )


def independent_set_polynomial(vertex_count, edges, activity):
    total = Fraction(0, 1)
    for mask in range(1 << vertex_count):
        independent = True
        for u, v in edges:
            if (mask & (1 << u)) and (mask & (1 << v)):
                independent = False
                break
        if independent:
            total += activity ** mask.bit_count()
    return total


def clone_graph(vertex_count, edges, clone_count):
    cloned_edges = set()
    for u, v in edges:
        for u_copy in range(clone_count):
            for v_copy in range(clone_count):
                cloned_edges.add(
                    (u * clone_count + u_copy, v * clone_count + v_copy)
                )
    return vertex_count * clone_count, frozenset(cloned_edges)


def search():
    for lam in (Fraction(1, 1),):
        for k in (1,):
            for n in (1,):
                for edges in labeled_graphs(n):
                    for ell in (1, 2):
                        x = (Fraction(1, 1) + lam) ** ell - 1
                        threshold = 2 ** (n ** (k + 1))
                        if abs(x) < threshold:
                            continue
                        enlarged_n, enlarged_edges = clone_graph(n, edges, ell)
                        original_value = independent_set_polynomial(n, edges, x)
                        enlarged_value = independent_set_polynomial(
                            enlarged_n, enlarged_edges, lam
                        )
                        assert original_value == enlarged_value
                        broad_factor = 2 ** (enlarged_n ** k)
                        tight_factor = 2 ** (n ** k)
                        broad_lower = enlarged_value * Fraction(1, broad_factor)
                        broad_upper = enlarged_value * broad_factor
                        tight_lower = original_value * Fraction(1, tight_factor)
                        tight_upper = original_value * tight_factor
                        candidates = (
                            ("lower", broad_lower),
                            ("upper", broad_upper),
                        )
                        for endpoint, output in candidates:
                            broad_ok = broad_lower <= output <= broad_upper
                            tight_ok = tight_lower <= output <= tight_upper
                            if broad_ok and not tight_ok:
                                return (
                                    lam,
                                    k,
                                    n,
                                    edges,
                                    ell,
                                    x,
                                    enlarged_n,
                                    enlarged_value,
                                    endpoint,
                                    output,
                                )
    return None


witness = search()
assert witness == (
    Fraction(1, 1),
    1,
    1,
    frozenset(),
    2,
    Fraction(3, 1),
    2,
    Fraction(4, 1),
    "lower",
    Fraction(1, 1),
)

result = {
    "record_id": "arxiv_0707.4565v3__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": "λ=1, k=1, G is the one-vertex edgeless graph (n=1), l=2, x=3, and G_l is the two-vertex edgeless graph (M=2). Its exact value is I(G;x)=I(G_l;1)=4. A deterministic output of 1 is allowed by the stated guarantee on G_l.",
    "refutation_explanation": "For M=2 the assumed guarantee permits 2^(-2)·4=1≤𝓘(G_l;1)≤16, so output 1 succeeds with probability 1. The claimed n-based lower bound is 2^(-1)·4=2, so the claimed event has probability 0. Given any baseline algorithm satisfying the premise, overriding it only on the fixed two-isolated-vertex input to return 1 preserves polynomial time and the stated M-based guarantee, while refuting the asserted 3/4 conclusion.",
    "search_space": "Exhaustive sweep of λ={1}, k={1}, n={1}, all labeled simple graphs on vertex set {0} (one edgeless graph), l∈{1,2}, retaining exactly the l satisfying |(1+λ)^l-1|≥2^(n^(k+1)), and both deterministic endpoint outputs {2^(-M^k)I(G_l;λ), 2^(M^k)I(G_l;λ)} with M=nl.",
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
