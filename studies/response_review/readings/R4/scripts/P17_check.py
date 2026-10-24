# P17: exact finite check of the witness supplied in the critic's response.
# Witness: G = S_3.  Response asserts G' = A_3, G/G' = C_2, Z(S_3) = {e},
# hence G/G' is NOT isomorphic to Z(G), refuting line 13 ("Since G/G' ~ Z(G)").
from itertools import permutations

n = 3
G = list(permutations(range(n)))           # S_3 as tuples: p[i] = image of i

def mul(p, q):                             # (p*q)(i) = p(q(i))
    return tuple(p[q[i]] for i in range(n))

def inv(p):
    r = [0] * n
    for i, pi in enumerate(p):
        r[pi] = i
    return tuple(r)

def closure(gens):
    S = {tuple(range(n))}
    frontier = list(S)
    while frontier:
        new = []
        for a in frontier:
            for g in gens:
                b = mul(a, g)
                if b not in S:
                    S.add(b); new.append(b)
        frontier = new
    return S

# derived subgroup G' = <[a,b] : a,b in G>
comms = {mul(mul(inv(a), inv(b)), mul(a, b)) for a in G for b in G}
Gprime = closure(list(comms))
# center Z(G)
Z = {a for a in G if all(mul(a, b) == mul(b, a) for b in G)}

print("|G|      =", len(G))
print("|G'|     =", len(Gprime), " (A_3 has order 3)")
print("|G/G'|   =", len(G) // len(Gprime))
print("|Z(G)|   =", len(Z), " Z(G) =", sorted(Z))

# G' is exactly the alternating group A_3 (even permutations)?
def sign(p):
    s = 1
    for i in range(n):
        for j in range(i + 1, n):
            if p[i] > p[j]:
                s = -s
    return s
A3 = {p for p in G if sign(p) == 1}
print("G' == A_3 ?", Gprime == A3)

# G' is normal in G (so G/G' is a group) and contains no non-trivial issue
normal = all(mul(mul(g, h), inv(g)) in Gprime for g in G for h in Gprime)
print("G' normal in G ?", normal)

print("|G/G'| == |Z(G)| ?", len(G) // len(Gprime) == len(Z))
assert len(G) // len(Gprime) == 2 and len(Z) == 1
print("=> G/G' (order 2, so C_2) is NOT isomorphic to Z(G) (order 1): line 13 is FALSE at G = S_3.")

# the witness is admissible for the source's standing hypothesis G' <= N <= G with N normal:
# e.g. N = G' itself, or N = A_3; list the normal subgroups containing G'.
subsets_ok = []
for N in [Gprime, set(G)]:
    isnorm = all(mul(mul(g, h), inv(g)) in N for g in G for h in N)
    subsets_ok.append((len(N), isnorm, Gprime <= N))
print("candidate N (|N|, normal in G, contains G'):", subsets_ok)
