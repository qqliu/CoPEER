#!/usr/bin/env python3
"""
BLIND counterexample search — record Algorithms_17__sol4

TARGET CLAIM (quoted verbatim from the source proof; the sentence is truncated
exactly as given in the input record):

    "We have exhibited two distinct transitive reductions of G, so the
     transitive reduction"

ANALYSIS OF FINITE REFUTABILITY
-------------------------------
The claim refers to
  (a) a specific graph G, and
  (b) two specific "exhibited" transitive reductions of that G,
neither of which is supplied by the claim text.  The sentence is also cut off
before its conclusion (presumably "... is not unique" or similar).  The logical
schema "two distinct transitive reductions exist => the transitive reduction is
not unique" is a tautology, so the only refutable content would be whether the
two exhibited objects really are distinct transitive reductions of the actual
G — data the record does not contain.  Hence the specific claim is NOT finitely
refutable from the given text, and no data may be invented.

WHAT CAN BE SWEPT HONESTLY (context probe, exact arithmetic, deterministic)
---------------------------------------------------------------------------
We exhaustively sweep ALL labeled directed graphs (no self-loops) on
n = 1, 2, 3 vertices — every subset of the n*(n-1) ordered pairs — and for each
graph enumerate ALL minimum-cardinality edge sets over V x V (no self-loops)
whose reachability closure equals that of the graph (the Aho–Garey–Ullman
notion of transitive reduction).  This establishes, by exhaustion:

  * every ACYCLIC digraph in the swept space has EXACTLY ONE transitive
    reduction (so if G were a DAG, the claim's premise would be impossible);
  * some CYCLIC digraphs (e.g. the 3-cycle's closure class) genuinely admit
    two or more distinct transitive reductions, so the claim's premise is
    realizable for cyclic G.

Neither branch refutes the claim itself, because G is unspecified.  The sweep
is purely integer/set arithmetic; no floats, no randomness; iteration order is
fixed (lexicographic over bitmasks).
"""

from itertools import product

RECORD_ID = "Algorithms_17__sol4"


def closure(n, edges):
    """Reachability closure (Warshall) of edge set `edges` on vertices 0..n-1.
    Returns frozenset of ordered pairs (i, j), i != j, with a nonempty path i->j."""
    reach = [[False] * n for _ in range(n)]
    for (i, j) in edges:
        reach[i][j] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                rk = reach[k]
                ri = reach[i]
                for j in range(n):
                    if rk[j]:
                        ri[j] = True
    return frozenset((i, j) for i in range(n) for j in range(n)
                     if i != j and reach[i][j])


def all_pairs(n):
    return [(i, j) for i in range(n) for j in range(n) if i != j]


def transitive_reductions(n, edges):
    """All minimum-cardinality edge sets over V x V (no loops) whose closure
    equals closure(edges).  Deterministic enumeration by bitmask order."""
    pairs = all_pairs(n)
    m = len(pairs)
    target = closure(n, edges)
    best_size = None
    best = []
    for mask in range(1 << m):
        cand = frozenset(pairs[b] for b in range(m) if (mask >> b) & 1)
        sz = len(cand)
        if best_size is not None and sz > best_size:
            continue
        if closure(n, cand) == target:
            if best_size is None or sz < best_size:
                best_size = sz
                best = [cand]
            elif sz == best_size and cand not in best:
                best.append(cand)
    return best


def is_acyclic(n, edges):
    cl = closure(n, edges)
    return all((i, i) not in cl for i in range(n)) and \
        not any((i, j) in cl and (j, i) in cl for i in range(n) for j in range(n) if i < j)


def main():
    dag_multi = []          # would be a genuine surprise (DAG with >=2 reductions)
    cyclic_multi_example = None
    graphs_swept = 0

    for n in (1, 2, 3):
        pairs = all_pairs(n)
        m = len(pairs)
        for mask in range(1 << m):
            edges = frozenset(pairs[b] for b in range(m) if (mask >> b) & 1)
            graphs_swept += 1
            reds = transitive_reductions(n, edges)
            if is_acyclic(n, edges):
                if len(reds) != 1:
                    dag_multi.append((n, sorted(edges), [sorted(r) for r in reds]))
            else:
                if len(reds) >= 2 and cyclic_multi_example is None:
                    cyclic_multi_example = (n, sorted(edges), [sorted(r) for r in reds])

    print(f"Graphs swept (all labeled loop-free digraphs on n=1,2,3): {graphs_swept}")
    if dag_multi:
        print("SURPRISE: acyclic digraph(s) with more than one transitive reduction:")
        for item in dag_multi:
            print("  ", item)
    else:
        print("Confirmed by exhaustion: every acyclic digraph on <=3 vertices has "
              "exactly one transitive reduction.")
    if cyclic_multi_example:
        n, e, reds = cyclic_multi_example
        print("First cyclic digraph (bitmask order) with >=2 distinct transitive "
              "reductions:")
        print(f"  n={n}, edges={e}")
        print(f"  distinct minimum reductions ({len(reds)}): {reds}")

    print()
    print("VERDICT: CLAIM_NOT_FINITELY_REFUTABLE")
    print("The claim refers to a specific graph G and two 'exhibited' transitive")
    print("reductions, none of which are supplied by the claim text (the sentence")
    print("is truncated).  The inference 'two distinct transitive reductions =>")
    print("non-uniqueness' is a tautology; the only refutable content lies in the")
    print("unsupplied exhibits.  The sweep above shows the premise is impossible")
    print("for DAGs but realizable for cyclic digraphs, so without knowing G no")
    print("finite search can refute (or confirm) the claim.")


if __name__ == "__main__":
    main()
