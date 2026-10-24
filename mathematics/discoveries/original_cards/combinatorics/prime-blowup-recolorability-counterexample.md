---
id: prime-blowup-recolorability-counterexample
title: A prime nine-cycle with a non-recolorable clique blowup
type: counterexample
domain: combinatorics
subdomain: graph-recoloring
tags: [graph-coloring, recoloring, modular-decomposition, prime-graphs, clique-blowups, frozen-coloring, original-conjecture-refutation]
refutes: >
  For every finite simple prime graph G, all clique blowups of G are
  recolorable if and only if every induced subgraph of G is recolorable.
statement: >
  The cycle C9 is prime and every induced subgraph of C9 is recolorable.
  Its uniform clique blowup H=C9[K2] has 18 vertices, 45 edges, independence
  number 4, and chromatic number 5, but admits a frozen proper 6-coloring.
  Therefore R_6(H) is disconnected and H is not recolorable, refuting the
  induced-subgraph-to-blowup implication in the original Conjecture 1.
true_theorem: >
  If X is d-degenerate, then R_k(X) is connected for every k >= d+2.
  This proves recolorability of all induced subgraphs of C9, but does not
  imply recolorability of its clique blowups at chi+1 colors.
hypothesis_violated: null
source:
  book: discovery-prime-blowup-2026
  chapter: "Section 6, Conclusion"
  item: null
  pages: null
difficulty: 3
status: draft
related: []
formalized: []
---

## Object

Let $G=C_9$, with indices in $\mathbb Z/9\mathbb Z$. Replace vertex $i$ by
the clique $B_i=\{(i,0),(i,1)\}$. Join all vertices of $B_i$ to all vertices
of $B_{i-1}$ and $B_{i+1}$, and add no other edges. The resulting graph
$H=C_9[K_2]$ has 18 vertices, 45 edges, and degree 5 at every vertex.

For a finite simple graph $X$, $R_k(X)$ has all proper maps
$V(X)\to\{1,\ldots,k\}$ as vertices; two maps are adjacent when they differ
at one vertex. The map need not use all $k$ colors. The graph $X$ is
*recolorable* when $R_k(X)$ is connected for every $k\geq\chi(X)+1$.
A module is a nonempty vertex set whose outside vertices are each adjacent
to either all or none of it. A graph is prime when its only modules are
singletons and its full vertex set.

The frozen coloring assigns the palettes

$$
(\{1,2\},\{3,4\},\{5,6\},\{1,2\},\{3,4\},\{5,6\},
  \{1,2\},\{3,4\},\{5,6\})
$$

to the nine bags in order, using each listed color once in its bag.

## What it kills

Conjecture 1 of Belavadi, Cameron, and Sintiari asserts, for a prime graph
$G$, the equivalence of recolorability of every clique blowup and
recolorability of every induced subgraph. Here the latter condition holds
and the former fails. The counterexample satisfies the original hypotheses,
including primality and the quantifier over all induced subgraphs.
The graph substitution uses nonempty cliques, as required by the paper's
definition. It refutes the conjecture itself, not just an attempted proof.

The published title is *Recoloring via Modular Decomposition*. The historical
benchmark input's title “Recoloring modular graphs” is inaccurate; its DOI,
definitions, and conjecture identify the correct source. The publisher's
Section 6 and definitions were checked on 2026-09-10.

## Why it works

**Degeneracy lemma, covering every required number of colors.** If $X$ is
$d$-degenerate, $R_k(X)$ is connected whenever $k\geq d+2$. Induct on the
number of vertices. Choose $v$ of degree at most $d$ and connect the
restrictions of two colorings on $X-v$ by induction. Lift each step to $X$.
If a neighbor is about to receive the current color of $v$, first recolor
$v$ to another color absent from its neighborhood. At least two colors are
absent there, so such a different color exists. The neighbor's intended move
is then valid. After lifting the entire path, give $v$ its target color,
which is absent from its now target-colored neighborhood. This constructs
a recoloring path between arbitrary endpoints.

**The original graph is prime.** Suppose $S$ were a proper module with at
least two vertices. Connectivity gives an outside vertex $v$ adjacent to
some member of $S$. Modularity makes $v$ adjacent to all of $S$, so its degree
2 forces $S$ to be exactly the two neighbors of $v$. In $C_9$, the other
neighbor of either member of $S$ lies outside $S$ and distinguishes its two
members, a contradiction.

**Every induced subgraph is recolorable.** The full $C_9$ has chromatic
number 3 and degeneracy 2, so the lemma applies for every $k\geq4$.
Every proper induced subgraph is a disjoint union of paths. When it contains
an edge, its chromatic number is 2 and degeneracy is 1, so the lemma applies
for every $k\geq3$. Nonempty edgeless subgraphs have chromatic number 1 and
can be recolored one coordinate at a time for every $k\geq2$. The empty
graph has a unique coloring. This argument covers all $k$ in the definition,
not merely the first value $k=\chi+1$.

**The blowup has chromatic number 5.** An independent set in $H$ uses at
most one vertex per bag, and its bag indices form an independent set of
$C_9$. Conversely, every independent set of $C_9$ lifts to $H$. Since
$\alpha(C_9)=4$, we have $\alpha(H)=4$ and
$\chi(H)\geq\lceil18/4\rceil=5$. For the matching upper bound, assign
the following palettes in order:

$$
(\{1,2\},\{3,4\},\{1,2\},\{3,4\},\{1,2\},\{3,4\},
  \{1,5\},\{2,3\},\{4,5\}).
$$

Consecutive palettes, including the last and first, are disjoint. Each bag
uses two different colors, giving a proper 5-coloring.

**The blowup is not recolorable.** In the displayed periodic 6-coloring,
each vertex sees all five other colors on its bagmate and the four vertices
in the neighboring bags. Thus no vertex can change color: the coloring is
isolated in $R_6(H)$. The proper 5-coloring above is also a distinct vertex
of $R_6(H)$, proving disconnection. Since $6=\chi(H)+1$, $H$ fails
recolorability at the first required number of colors.

## Debugging uses

- Check that a blowup argument preserves available colors for single-vertex
  recoloring; three consecutive bags here exhaust the entire palette.
- Separate recolorability of a prime graph and all its induced subgraphs
  from the stronger assertion concerning all clique blowups.
- Include a second coloring when using a frozen coloring to prove that a
  reconfiguration graph is disconnected.

## Remarks

The counterexample occurs in the neutral baseline of the historical
`open_frontier_paired_extension_v5r1_20260904` run, record
`ext5_prime_blowup_recolorability`. That baseline completed on 2026-09-04
using `gpt-5.6-sol` with `max` reasoning, before the plain/BugBank revision
split. Its independent baseline audit reported `FULLY_RESOLVES_TARGET`.
This entry was added on 2026-09-10 after source and certificate review;
the discovery is not attributed to Astra or to BugBank retrieval. No claim
of priority over the mathematical literature is made.

The standard-library checker
[`prime_blowup_check.py`](../../certificates/discoveries_20260910/prime_blowup_check.py)
runs as `python3 BugBank/certificates/discoveries_20260910/prime_blowup_check.py`.
It checks all 501 nontrivial proper module candidates, all 512 induced
subgraphs with exact chromatic number and degeneracy, and full connectivity
of each induced graph's $R_{\chi+1}$. It visits all $2^{18}$ vertex subsets
to compute the blowup's independence number and verifies both explicit
colorings and all 18 frozen-vertex conditions. It returns `PASS`.
The all-$k$ conclusion uses the hand proof above; the finite boundary checks
alone do not establish it. The independent historical audit checker was
also retained and rerun during this review.

This is a draft entry supported by a complete hand argument and exact
computational checks. There is no claim-bound Lean or external formal
certification, so `formalized` remains empty. The provenance record
[`prime_blowup_provenance.json`](../../certificates/discoveries_20260910/prime_blowup_provenance.json)
binds the historical input, baseline, audit, run state, and audit checker
by SHA-256. Existing entries were searched for recoloring and blowup
duplicates; no entry for this counterexample was found. The live benchmark
database was not rebuilt or modified by this addition.

## References

- Manoj Belavadi, Kathie Cameron, and Ni Luh Dewi Sintiari,
  [*Recoloring via Modular Decomposition*](https://onlinelibrary.wiley.com/doi/10.1002/jgt.70005),
  *Journal of Graph Theory* 111(4) (2026), 113–123, Section 6, Conjecture 1;
  first published 16 February 2026.
- [arXiv:2405.06446](https://arxiv.org/abs/2405.06446), author preprint.
- Historical run artifacts and exact hashes are recorded in the linked
  provenance JSON; the archived baseline and audit remain unchanged.
