r"""Let \(\lambda\in\mathbb Q\) satisfy \(0\neq |1+\lambda|\neq1\), let \(k\in\mathbb N\), and suppose \(\mathcal A\) is a randomized \(2^{N^k}\)-approximation algorithm for \(I(\lambda)\): on every input graph \(H\) having \(N\) nodes, it runs in time polynomial in \(N\) and returns \(\mathcal I(H;\lambda)\in\mathbb Q\) such that \(\Pr[2^{-N^k}I(H;\lambda)\leq\mathcal I(H;\lambda)\leq2^{N^k}I(H;\lambda)]\geq3/4\). Let \(G=(V,E)\) have \(|V|=n\), and choose a positive integer \(l\) as follows. If \(|1+\lambda|>1\), put \(x=(1+\lambda)^l-1\), require \(|x|\geq2^{n^{k+1}}\), and let \(G_l\) be obtained by cloning every vertex of \(G\) exactly \(l-1\) times; hence \(|V(G_l)|=nl\) and \(I(G;x)=I(G_l;\lambda)\). If \(0<|1+\lambda|<1\), put \(x=\lambda/(1+\lambda)^l\), require \(|x|\geq2^{n^{k+1}}\), and let \(G_l\) be obtained by performing an \(l\)-comb at every original vertex, where an \(l\)-comb adds \(l\) new degree-one neighbors to that vertex; hence \(|V(G_l)|=n(l+1)\) and \(I(G;x)=(1+\lambda)^{-l|V|}I(G_l;\lambda)\). Define \(\mathcal I(G;x)=\mathcal I(G_l;\lambda)\) in the cloning case and \(\mathcal I(G;x)=\mathcal I(G_l;\lambda)/(1+\lambda)^{l|V|}\) in the comb case. The claim is that applying \(\mathcal A\) to the enlarged input \(G_l\) yields \(\Pr[2^{-n^k}I(G;x)\leq\mathcal I(G;x)\leq2^{n^k}I(G;x)]\geq3/4\), with the approximation exponent computed from \(n=|V(G)|\), rather than from the number of nodes \(|V(G_l)|\) in the graph actually supplied to \(\mathcal A\). Here \(I(G;x)\) is the independent-set polynomial used in the source, whose degree \(c\) is the maximum independent-set size and which is written as \(I(G;x)=Nx^c+\sum_{0\leq j\leq c-1}i(G;j)x^j\), with \(N\) the number of independent sets of maximum size."""

import json
from fractions import Fraction


def exact_independent_set_value(vertex_count, edges, activity):
    value = 0
    for subset in range(2 ** vertex_count):
        valid = all(
            not ((subset & (2 ** left)) and (subset & (2 ** right)))
            for left, right in edges
        )
        if valid:
            size = subset.bit_count()
            value += activity ** size
    return value


lam = 1
k = 1
n = 1
ell = 2
original_edges = ()

assert abs(1 + lam) > 1
assert ell > 0
x = (1 + lam) ** ell - 1
threshold_exponent = n ** (k + 1)
assert threshold_exponent >= 0
threshold = 2 ** threshold_exponent
assert abs(x) >= threshold

original_value = exact_independent_set_value(n, original_edges, x)

# Cloning the sole isolated vertex produces two isolated vertices.
enlarged_n = n * ell
enlarged_edges = ()
enlarged_value = exact_independent_set_value(enlarged_n, enlarged_edges, lam)
assert (x, enlarged_n, original_value, enlarged_value) == (3, 2, 4, 4)

# The constant-output algorithm A(H)=1 is globally valid here: at activity
# one, every graph has between 1 and 2^N independent sets.
output = Fraction(1, 1)
broad_exponent = enlarged_n ** k
assert broad_exponent >= 0
broad_factor = 2 ** broad_exponent
broad_lower = Fraction(enlarged_value, broad_factor)
broad_upper = Fraction(enlarged_value * broad_factor, 1)
assert (broad_lower, broad_upper) == (Fraction(1, 1), Fraction(16, 1))
assert broad_lower <= output <= broad_upper

claimed_exponent = n ** k
assert claimed_exponent >= 0
claimed_factor = 2 ** claimed_exponent
claimed_lower = Fraction(original_value, claimed_factor)
claimed_upper = Fraction(original_value * claimed_factor, 1)
assert (claimed_lower, claimed_upper) == (Fraction(2, 1), Fraction(8, 1))
assert not (claimed_lower <= output <= claimed_upper)
assert Fraction(0, 1) < Fraction(3, 4)

notes = "Independent exact recomputation confirms the witness. For λ=1 and k=1, the deterministic polynomial-time algorithm that always returns 1 satisfies the premise on every N-node graph because 1≤I(H;1)≤2^N. For the one-vertex edgeless G with l=2, x=3 meets the threshold, G_l has two isolated vertices, and both polynomial values are 4. The premise permits output 1 (interval [1,16]), while the claimed n-based interval is [2,8], so its event has probability 0. This is a substantive exponent/input-size error, not plainly a typo."
result = {
    "record_id": "arxiv_0707.4565v3__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
