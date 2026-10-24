# P32: exact check of the witness G = S_3 against source line 13 ("G/G' ~ Z(G)").
from itertools import permutations
G = [tuple(p) for p in permutations(range(3))]
def mul(p,q): return tuple(p[q[i]] for i in range(3))
def inv(p):
    r=[0]*3
    for i,x in enumerate(p): r[x]=i
    return tuple(r)
e=(0,1,2)
def gen(gs):
    S={e}
    while True:
        n={mul(a,b) for a in S for b in gs}|S
        if n==S: return S
        S=n
comms = {mul(mul(a,b), inv(mul(b,a))) for a in G for b in G}   # [a,b] = a b (b a)^{-1}
Gprime = gen(comms)
Z = {z for z in G if all(mul(z,g)==mul(g,z) for g in G)}
print("|S_3| =", len(G))
print("G' = [G,G] has order", len(Gprime), "(the 3-cycles and e: A_3)")
print("|G/G'| =", len(G)//len(Gprime))
print("Z(S_3) =", sorted(Z), " order", len(Z))
print("G/G' and Z(G) isomorphic? orders", len(G)//len(Gprime), "vs", len(Z),
      "->", (len(G)//len(Gprime)) == len(Z))
print("line 13 fails at G = S_3:", (len(G)//len(Gprime)) != len(Z))
