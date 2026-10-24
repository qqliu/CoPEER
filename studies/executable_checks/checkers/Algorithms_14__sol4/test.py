#!/usr/bin/env python3
"""
Counterexample search for the claim (Algorithms_14__sol4), quoted verbatim:

    "By the time we reach x, the neighbor y is already visited, so the DFS
     will not take the edge {x, y} as a tree edge"

Formalization used here (the claim's checkable content, read literally):

    (IMPLICATION, reading A) For any undirected graph G, any DFS of G
    (deterministic: recursive DFS, roots and neighbors scanned in ascending
    vertex order), and any adjacent pair (x, y): if y receives its discovery
    time strictly before x does (i.e. "by the time we reach x, the neighbor
    y is already visited"), then the edge {x, y} is NOT a tree edge of the
    resulting DFS forest.

    (Reading B, stricter "future" reading) Under the same premise, the DFS
    does not take {x, y} as a tree edge AT ANY MOMENT AFTER x is discovered.
    (This excludes the parent edge, which is taken at the moment x is
    discovered, not after.)

Search space (exhaustive, deterministic, exact integer arithmetic only):
    - all labeled undirected simple graphs on n = 1..4 vertices
      (every subset of the C(n,2) possible edges),
    - one canonical DFS per graph: iterate roots 0..n-1 in order, recursive
      DFS visiting neighbors in ascending order,
    - every ordered adjacent pair (x, y) with disc[y] < disc[x].

For each such triple (graph, x, y) we test whether {x, y} is a tree edge
(reading A) and whether it became a tree edge after x's discovery
(reading B). The first violation in the fixed iteration order is printed
as the witness. No floats, no randomness.
"""

from itertools import combinations

def dfs_forest(n, adj):
    """Deterministic DFS. Returns (disc, tree_edges_ordered) where disc[v]
    is the discovery time of v and tree_edges_ordered is the list of tree
    edges (parent, child) in the order they are taken. All exact ints."""
    disc = [None] * n
    tree = []
    t = [0]

    def visit(u):
        disc[u] = t[0]
        t[0] += 1
        for w in adj[u]:          # ascending order: deterministic
            if disc[w] is None:
                tree.append((u, w))
                visit(w)

    for r in range(n):            # ascending roots: deterministic
        if disc[r] is None:
            visit(r)
    return disc, tree

def main():
    witness_A = None
    violations_B = 0
    graphs_swept = 0
    pairs_checked = 0

    for n in range(1, 5):
        all_edges = list(combinations(range(n), 2))
        for k in range(len(all_edges) + 1):
            for edge_set in combinations(all_edges, k):
                graphs_swept += 1
                adj = [[] for _ in range(n)]
                for (a, b) in edge_set:
                    adj[a].append(b)
                    adj[b].append(a)
                for row in adj:
                    row.sort()
                disc, tree = dfs_forest(n, adj)
                tree_set = {frozenset(e) for e in tree}
                # order in which tree edges were taken (index = step)
                step_of = {frozenset(e): i for i, e in enumerate(tree)}

                for (a, b) in edge_set:
                    for (x, y) in ((a, b), (b, a)):
                        # premise: y already visited by the time we reach x
                        if disc[y] < disc[x]:
                            pairs_checked += 1
                            e = frozenset((x, y))
                            # Reading A: edge must not be a tree edge at all
                            if e in tree_set and witness_A is None:
                                witness_A = (n, edge_set, x, y, disc,
                                             list(tree))
                            # Reading B: edge taken as tree edge strictly
                            # after x was discovered. A tree edge (p,c) is
                            # taken at the moment disc[c] is assigned; it is
                            # "after x is reached" iff disc[child] > disc[x].
                            if e in tree_set:
                                p, c = tree[step_of[e]]
                                if disc[c] > disc[x]:
                                    violations_B += 1

    print("Swept: all labeled simple undirected graphs on n = 1..4 vertices")
    print("(%d graphs), canonical deterministic DFS each," % graphs_swept)
    print("%d adjacent ordered pairs (x,y) with disc[y] < disc[x] checked."
          % pairs_checked)
    print()

    if witness_A is not None:
        n, edge_set, x, y, disc, tree = witness_A
        print("VERDICT: WITNESS_FOUND (literal reading A)")
        print("Witness graph: n = %d, edges = %s" % (n, list(edge_set)))
        print("DFS discovery times: %s" % ({v: disc[v] for v in range(n)},))
        print("DFS tree edges in order taken: %s" % (tree,))
        print("Take x = %d, y = %d: edge {%d,%d} is present, disc[y]=%d < "
              "disc[x]=%d, so y is already visited by the time we reach x,"
              % (x, y, x, y, disc[y], disc[x]))
        print("yet {%d,%d} IS a tree edge (it is exactly the tree edge by "
              "which DFS discovered x from its parent y)." % (x, y))
        print("This contradicts the claim's conclusion that the DFS will "
              "not take {x,y} as a tree edge.")
    else:
        print("VERDICT: NO_WITNESS_EXHAUSTIVE for reading A in this space.")

    print()
    if violations_B == 0:
        print("Reading B (edge taken as tree edge strictly AFTER x is "
              "discovered): 0 violations in the entire space -- under that "
              "stricter reading the claim holds on all swept graphs.")
    else:
        print("Reading B violations: %d" % violations_B)

if __name__ == "__main__":
    main()
