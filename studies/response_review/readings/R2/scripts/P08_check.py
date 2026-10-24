# P08: the response's witness, checked by finite enumeration.
# Witness: the tree with edges u-x and x-v; the walk u-x-u-x-v from u to v.
import itertools
V = ["u", "x", "v"]
E = [frozenset(("u", "x")), frozenset(("x", "v"))]
def adj(a, b): return frozenset((a, b)) in E

# 1. is the witness graph a tree? (connected + acyclic, checked by brute force)
seen, stack = {"u"}, ["u"]
while stack:
    a = stack.pop()
    for b in V:
        if b not in seen and adj(a, b):
            seen.add(b); stack.append(b)
print("connected?", seen == set(V), " |V| =", len(V), " |E| =", len(E), " |E| == |V|-1?", len(E) == len(V) - 1)

# cycles: every closed trail / cycle of length >= 3 on these vertices
cycles = []
for r in range(3, len(V) + 1):
    for seq in itertools.permutations(V, r):
        if seq[0] != min(seq): continue
        if all(adj(seq[i], seq[(i + 1) % r]) for i in range(r)):
            cycles.append(seq)
print("cycles of length >= 3:", cycles, " => graph is circuit-free?", not cycles)

# 2. the supplied walk
W = ["u", "x", "u", "x", "v"]
is_walk = all(adj(W[i], W[i + 1]) for i in range(len(W) - 1))
edges_used = [frozenset((W[i], W[i + 1])) for i in range(len(W) - 1)]
rep_v = len(set(W)) != len(W)
rep_e = len(set(edges_used)) != len(edges_used)
print("W =", "-".join(W), " endpoints u,v distinct?", W[0] == "u" and W[-1] == "v" and "u" != "v")
print("is a walk between u and v?", is_walk, " repeats a vertex?", rep_v, " repeats an edge?", rep_e)
print("is a path (no repeated vertices, no repeated edges)?", not rep_v and not rep_e)
