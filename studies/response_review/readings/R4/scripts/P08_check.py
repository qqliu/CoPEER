# P08: exact check of the witness supplied by the critic's response.
# Witness: the tree with edges u-x and x-v, and the walk u-x-u-x-v from u to v.
# Line 7 asserts: because the tree is circuit-free, the walk P_1 of line 6 IS a path
# ("path has no repeated edges and no repeated vertices" -- the source's own definition).
from itertools import combinations

V = ["u", "x", "v"]
E = [frozenset({"u", "x"}), frozenset({"x", "v"})]
Eset = set(E)

def neighbours(a):
    return [w for e in E for w in e if a in e and w != a]

# (1) the witness graph is a tree: connected and acyclic
seen, stack = {V[0]}, [V[0]]
while stack:
    a = stack.pop()
    for w in neighbours(a):
        if w not in seen:
            seen.add(w); stack.append(w)
connected = seen == set(V)
print("V =", V, " E =", [sorted(e) for e in E])
print("connected:", connected, " |E| = |V|-1 :", len(E) == len(V) - 1, " -> tree:", connected and len(E) == len(V) - 1)

# (2) circuit-free in the closed-trail sense: no closed walk of positive length without a repeated edge
def closed_trails(maxlen=6):
    out = []
    def rec(start, at, used, seq):
        if len(seq) > 1 and at == start:
            out.append(list(seq)); return
        if len(used) >= maxlen:
            return
        for w in neighbours(at):
            e = frozenset({at, w})
            if e not in used:
                rec(start, w, used | {e}, seq + [w])
    for s in V:
        rec(s, s, frozenset(), [s])
    return out
ct = closed_trails()
print("closed trails of positive length with no repeated edge (length <= 6):", ct, "-> circuit-free:", ct == [])

# (3) the witness walk
W = ["u", "x", "u", "x", "v"]
is_walk = all(frozenset({W[t], W[t+1]}) in Eset for t in range(len(W) - 1))
rep_v = len(set(W)) != len(W)
edges_used = [frozenset({W[t], W[t+1]}) for t in range(len(W) - 1)]
rep_e = len(set(edges_used)) != len(edges_used)
print("walk W =", W, " endpoints:", W[0], "->", W[-1])
print("every consecutive pair is an edge (so W is a walk between u and v):", is_walk)
print("W repeats a vertex:", rep_v, " W repeats an edge:", rep_e,
      " -> W is NOT a path in the source's sense:", rep_v or rep_e)
assert connected and len(E) == len(V) - 1 and ct == [] and is_walk and rep_v and rep_e
print("=> a circuit-free connected graph can carry a u-v walk that is not a path:")
print("   line 7's inference ('tree is circuit-free, so P_1 is a path') fails for this P_1.")

# (4) and the theorem being proved is still true here: exactly one u-v path exists
def simple_paths(a, b):
    res = []
    def rec(at, seq):
        if at == b:
            res.append(list(seq)); return
        for w in neighbours(at):
            if w not in seq:
                rec(w, seq + [w])
    rec(a, [a])
    return res
print("simple u-v paths in the witness tree:", simple_paths("u", "v"), "-> unique, so the theorem is untouched")
