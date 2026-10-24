# P17: the response's witness G = S_3 against line 13's assertion G/G' isomorphic to Z(G)
from itertools import permutations
G = list(permutations(range(3)))
def mul(a, b): return tuple(a[b[i]] for i in range(3))
def inv(a):
    r = [0] * 3
    for i, v in enumerate(a): r[v] = i
    return tuple(r)
e = (0, 1, 2)

# derived subgroup G' = <[a,b]>
comms = {mul(mul(a, b), mul(inv(a), inv(b))) for a in G for b in G}
Gp = {e}
while True:
    new = {mul(x, y) for x in Gp | comms for y in Gp | comms} | Gp | comms
    if new == Gp: break
    Gp = new
Z = {a for a in G if all(mul(a, b) == mul(b, a) for b in G)}
print("|G| =", len(G), " |G'| =", len(Gp), " G' =", sorted(Gp))
print("|Z(G)| =", len(Z), " Z(G) =", sorted(Z))
print("|G/G'| =", len(G) // len(Gp))
print("G/G' isomorphic to Z(G)?  (orders", len(G) // len(Gp), "vs", len(Z), ") ->",
      (len(G) // len(Gp)) == len(Z))
print("G' = A_3 (the even permutations)?", Gp == {a for a in G if
      sum(1 for i in range(3) for j in range(i + 1, 3) if a[i] > a[j]) % 2 == 0})
# the proof's context is instantiable at this G: N normal in G with G' <= N
print("N = A_3 is normal in S_3 and contains G'?", True, Gp <= {a for a in G if
      sum(1 for i in range(3) for j in range(i + 1, 3) if a[i] > a[j]) % 2 == 0})
