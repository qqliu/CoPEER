#!/usr/bin/env python3
"""
Counterexample search for record Algorithms_19__sol2.

TARGET CLAIM (quoted verbatim from the record):
    "Thus, if Condition (2) fails, the MST is not unique."

STATUS OF THE CLAIM TEXT
------------------------
The claim is a conditional whose antecedent is "Condition (2) fails", but the
record supplies ONLY the sentence above.  "Condition (2)" is a dangling
reference: its definition is NOT contained in the record.  Therefore the claim,
as given, is NOT decidable from the record alone, and the top-level verdict of
this program is INCONCLUSIVE.  We do not invent the missing definition.

WHAT THIS PROGRAM NEVERTHELESS CHECKS (clearly labeled, interpretation-
conditional, purely for transparency)
-------------------------------------
In standard treatments of MST uniqueness, a numbered "Condition (2)" is almost
always one of the two classical local-tie conditions:

  Reading A (cycle condition): every simple cycle of G has a UNIQUE
      maximum-weight edge.
  Reading B (cut condition): for every nonempty proper vertex subset S,
      the minimum-weight edge crossing the cut (S, V-S) is UNIQUE.

Under a given reading, the claim "Condition fails ==> MST not unique" is
refuted by any connected weighted graph in which the condition FAILS while the
MST IS unique.  This program exhaustively sweeps a bounded space of small
graphs with exact integer weights and reports, for each reading, the first
(deterministically ordered) such witness if one exists in the space.

SEARCH SPACE (exhaustive, deterministic, exact integer arithmetic)
------------------------------------------------------------------
  * n in {3, 4} vertices (labeled 0..n-1);
  * every connected spanning edge subset of K_n (edges in fixed sorted order);
  * every weight assignment mapping each edge to {1, 2, 3};
  * all spanning trees enumerated by brute force over (n-1)-edge subsets;
  * all simple cycles enumerated as edge subsets that are connected and
    2-regular on their support;
  * all cuts enumerated over nonempty proper vertex subsets.
No floats, no randomness, fixed iteration order throughout.

VERDICT: printed at the end.  The interpretation-conditional witnesses do NOT
upgrade the top-level verdict, because the actual "Condition (2)" of the source
proof is unknown and could differ from both readings (e.g. it could be a
condition under which the implication is a true theorem).
"""

from itertools import combinations, product


def connected(vertices, edges):
    """Exact connectivity check of the graph (vertices, edges) via BFS."""
    verts = sorted(vertices)
    if not verts:
        return True
    adj = {v: [] for v in verts}
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {verts[0]}
    stack = [verts[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == len(verts)


def spanning_trees(n, edges):
    """All spanning trees as sorted tuples of edges (deterministic order)."""
    out = []
    for sub in combinations(edges, n - 1):
        verts = set()
        for (u, v) in sub:
            verts.add(u)
            verts.add(v)
        if len(verts) == n and connected(range(n), sub):
            out.append(sub)
    return out


def simple_cycles_as_edge_sets(edges):
    """All simple cycles, each as a frozenset of edges: a subset whose support
    is connected and 2-regular (every vertex of the support has degree 2)."""
    cycles = []
    for k in range(3, len(edges) + 1):
        for sub in combinations(edges, k):
            deg = {}
            for (u, v) in sub:
                deg[u] = deg.get(u, 0) + 1
                deg[v] = deg.get(v, 0) + 1
            if all(d == 2 for d in deg.values()) and connected(deg.keys(), sub):
                cycles.append(sub)
    return cycles


def cycle_condition_holds(edges, w):
    """Reading A: every simple cycle has a unique maximum-weight edge."""
    for cyc in simple_cycles_as_edge_sets(edges):
        mx = max(w[e] for e in cyc)
        if sum(1 for e in cyc if w[e] == mx) > 1:
            return False
    return True


def cut_condition_holds(n, edges, w):
    """Reading B: every cut has a unique minimum-weight crossing edge."""
    verts = list(range(n))
    for r in range(1, n):
        for S in combinations(verts, r):
            Sset = set(S)
            crossing = [e for e in edges if (e[0] in Sset) != (e[1] in Sset)]
            if not crossing:
                continue
            mn = min(w[e] for e in crossing)
            if sum(1 for e in crossing if w[e] == mn) > 1:
                return False
    return True


def main():
    WEIGHTS = (1, 2, 3)
    witness = {"A": None, "B": None}
    graphs_swept = 0

    for n in (3, 4):
        all_edges = list(combinations(range(n), 2))  # fixed sorted order
        for m in range(n - 1, len(all_edges) + 1):
            for esub in combinations(all_edges, m):
                verts = set()
                for (u, v) in esub:
                    verts.add(u)
                    verts.add(v)
                if len(verts) != n or not connected(range(n), esub):
                    continue
                trees = spanning_trees(n, esub)
                for wvec in product(WEIGHTS, repeat=m):
                    graphs_swept += 1
                    w = dict(zip(esub, wvec))
                    costs = [sum(w[e] for e in t) for t in trees]
                    best = min(costs)
                    n_mst = sum(1 for c in costs if c == best)
                    if n_mst != 1:
                        continue  # MST not unique: cannot refute either reading
                    if witness["A"] is None and not cycle_condition_holds(esub, w):
                        witness["A"] = (n, esub, wvec)
                    if witness["B"] is None and not cut_condition_holds(n, esub, w):
                        witness["B"] = (n, esub, wvec)
        if witness["A"] and witness["B"]:
            break

    print("Record: Algorithms_19__sol2")
    print('Claim: "Thus, if Condition (2) fails, the MST is not unique."')
    print()
    print("The record does not define 'Condition (2)'.  The claim as quoted is")
    print("therefore not decidable from the record alone.")
    print()
    print("Interpretation-conditional exhaustive sweep "
          "(n in {3,4}, weights in {1,2,3}; %d weighted graphs):" % graphs_swept)
    for key, name in (("A", "cycle condition (unique max edge on every cycle)"),
                      ("B", "cut condition (unique min edge across every cut)")):
        if witness[key] is None:
            print("  Reading %s [%s]: NO witness in the swept space." % (key, name))
        else:
            n, esub, wvec = witness[key]
            desc = ", ".join("w(%d,%d)=%d" % (u, v, wt)
                             for (u, v), wt in zip(esub, wvec))
            print("  Reading %s [%s]:" % (key, name))
            print("    WITNESS (conditional on this reading): n=%d, %s" % (n, desc))
            print("    Here the condition FAILS yet the MST IS unique, refuting")
            print("    'condition fails ==> MST not unique' UNDER THIS READING.")

    print()
    print("VERDICT: NO_WITNESS_INCONCLUSIVE")
    print("Reason: 'Condition (2)' is undefined in the record; the antecedent of")
    print("the conditional cannot be evaluated without inventing data the claim")
    print("does not supply.  The witnesses above are conditional on standard")
    print("textbook readings and do not adjudicate the source proof's actual")
    print("Condition (2).")


if __name__ == "__main__":
    main()
