# P02: exact check of the witness supplied by the critic's response.
# Witness: G = K_{3,3} (n = 6, every degree 3 >= n/2), P = a1-b1-a2-b2-a3.
# Line 11 asserts: "there exists i, 1 <= i <= k, that {v_1, v_{i+1}}, {v_i, v_k} in E".
from itertools import combinations

A = ["a1", "a2", "a3"]
B = ["b1", "b2", "b3"]
V = A + B
E = {frozenset({a, b}) for a in A for b in B}
n = len(V)
deg = {v: sum(1 for e in E if v in e) for v in V}
print("K_{3,3}: n =", n, " degrees =", deg, " min degree >= n/2 :", min(deg.values()) >= n / 2)

P = ["a1", "b1", "a2", "b2", "a3"]        # the response's path
k = len(P)
print("P =", P, " k =", k)
print("P is a path (consecutive pairs are edges, vertices distinct):",
      all(frozenset({P[t], P[t+1]}) in E for t in range(k - 1)) and len(set(P)) == k)

v1, vk = P[0], P[k - 1]
found = []
for i in range(1, k + 1):                  # 1 <= i <= k as written in line 11
    if i + 1 > k:                          # v_{i+1} does not exist on the path
        print(f"   i={i}: v_{{i+1}} = v_{i+1} is outside the path (k={k}) -> no such edge")
        continue
    e1 = frozenset({v1, P[i]})             # {v_1, v_{i+1}}  (P is 0-indexed: v_{i+1} = P[i])
    e2 = frozenset({P[i - 1], vk})         # {v_i, v_k}
    ok1, ok2 = e1 in E, e2 in E
    print(f"   i={i}: {{v1,v{i+1}}} = {sorted(e1)} in E: {ok1} ;  {{v{i},vk}} = {sorted(e2)} in E: {ok2}")
    if ok1 and ok2:
        found.append(i)
print("indices i satisfying BOTH conditions:", found)
assert found == []
print("=> line 11's 'therefore there exists i ...' FAILS for this G and this path P.")

# for the record: the same line also asserts that v_1 is joined to at least n/2 vertices among
# v_2..v_k; on this witness that fails too (a1's neighbours on P are b1 and b2 only).
onP = [w for w in P[1:] if frozenset({v1, w}) in E]
print("neighbours of v1 among v_2..v_k:", onP, " count", len(onP), "< n/2 =", n / 2)

# K_{3,3} is nevertheless Hamiltonian, so the defect is in the argument, not in Dirac's theorem:
ham = ["a1", "b1", "a2", "b2", "a3", "b3", "a1"]
print("a Hamiltonian cycle of K_{3,3} exists, e.g.", ham, ":",
      all(frozenset({ham[t], ham[t+1]}) in E for t in range(len(ham) - 1)))
