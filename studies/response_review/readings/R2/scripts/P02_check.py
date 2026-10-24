# P02: the response's witness, checked by finite enumeration.
# Witness: K_{3,3}, parts A={a1,a2,a3}, B={b1,b2,b3}; path P = a1-b1-a2-b2-a3.
# Located claim: "there exists i, 1 <= i <= k, that {v1,v_{i+1}}, {v_i,v_k} in E".
from itertools import product

A = ["a1", "a2", "a3"]; B = ["b1", "b2", "b3"]
V = A + B
E = {frozenset((a, b)) for a, b in product(A, B)}
def adj(u, v): return frozenset((u, v)) in E

n = len(V)
degs = {v: sum(adj(v, w) for w in V if w != v) for v in V}
print("n =", n, "degrees =", degs, "min degree =", min(degs.values()), ">= n/2?", min(degs.values()) >= n/2)

P = ["a1", "b1", "a2", "b2", "a3"]
k = len(P)
print("P is a path (consecutive edges, distinct vertices)?",
      all(adj(P[j], P[j+1]) for j in range(k-1)) and len(set(P)) == k)

v = {i+1: P[i] for i in range(k)}          # 1-indexed as in the source line
hits = []
for i in range(1, k+1):                    # the line says 1 <= i <= k
    e1 = adj(v[1], v[i+1]) if i+1 <= k else False   # v_{k+1} does not exist
    e2 = adj(v[i], v[k])
    print("i =", i, " {v1,v_{i+1}} =", (v[1], v.get(i+1)), e1,
          "  {v_i,v_k} =", (v[i], v[k]), e2)
    if e1 and e2: hits.append(i)
print("indices i satisfying BOTH required edges:", hits)

# the source's intermediate assertion, for the record
print("neighbours of v1 among v2..vk:", [v[j] for j in range(2, k+1) if adj(v[1], v[j])])
print("neighbours of vk among v1..v(k-1):", [v[j] for j in range(1, k) if adj(v[k], v[j])])
