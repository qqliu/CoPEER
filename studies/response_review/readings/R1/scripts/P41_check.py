# P41: check exactly the supplied witness for line 7 ("tree is circuit-free, so P_1 is a path"):
# "In a tree with an edge between u and v, the walk u-v-u-v is not a path as it repeats vertices and
#  edges, despite the tree being circuit-free."
# Smallest instance of the family the response names: T = the tree on {u,v} with the single edge uv.
from itertools import combinations

V = ['u', 'v']
E = [frozenset({'u', 'v'})]

def is_walk(seq):
    return all(frozenset({seq[i], seq[i + 1]}) in E for i in range(len(seq) - 1))
def repeats_vertices(seq):
    return len(set(seq)) != len(seq)
def repeated_edges(seq):
    es = [frozenset({seq[i], seq[i + 1]}) for i in range(len(seq) - 1)]
    return len(set(es)) != len(es)
def connected():
    seen, stack = set(), [V[0]]
    while stack:
        x = stack.pop()
        if x in seen: continue
        seen.add(x)
        for e in E:
            if x in e: stack.extend(e - {x})
    return seen == set(V)
def has_circuit():
    # a circuit needs a closed walk with no repeated edge; in a simple graph that needs a cycle
    # on at least 3 distinct vertices, or two parallel edges
    for r in range(3, len(V) + 1):
        for S in combinations(V, r):
            deg = {x: sum(1 for e in E if x in e and e <= set(S)) for x in S}
            if all(d >= 2 for d in deg.values()): return True
    return len(E) != len(set(E))        # parallel edges
walk = ['u', 'v', 'u', 'v']
print("T: V =", V, " E =", [sorted(e) for e in E])
print("T is connected:", connected(), "  T is circuit-free:", not has_circuit(),
      "  so T is a tree, and u != v")
print("sequence", '-'.join(walk), "is a walk from u to v:", is_walk(walk),
      " (every consecutive pair is an edge)")
print("it repeats vertices:", repeats_vertices(walk), "  it repeats edges:", repeated_edges(walk))
print("so by line 7's own parenthetical ('path has no repeated edges and no repeated vertices'),")
print("   it is a path?", not repeats_vertices(walk) and not repeated_edges(walk))
print()
print("line 7 asserts that circuit-freeness makes the walk of line 6 a path; refuted here?",
      (not has_circuit()) and is_walk(walk) and repeats_vertices(walk))
