# P33: the response's witness, n = 4, pi = {{1,2},{3,4}}, sigma = {{1,4},{2,3}}.
# Count the (u,v) with u constant on parts of pi, v constant on parts of sigma, u_i v_i = z_i
# (lines 153-155), and compare with line 157's claimed |G|^{|pi v sigma|}.
from itertools import product, permutations

pi    = [{1, 2}, {3, 4}]
sigma = [{1, 4}, {2, 3}]

def meet(p, q):    # pi ^ sigma : intersections of parts
    return [A & B for A in p for B in q if A & B]
def join(p, q):    # pi v sigma : transitive closure of the two partitions
    blocks = [set(A) for A in p + q]
    merged = True
    while merged:
        merged = False
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                if blocks[i] & blocks[j]:
                    blocks[i] |= blocks.pop(j); merged = True; break
            if merged: break
    return blocks

print("pi ^ sigma =", meet(pi, sigma), " (all singletons -> line 152's condition is vacuous)")
J = join(pi, sigma); print("pi v sigma =", J, " |pi v sigma| =", len(J))

def count(G, mul, z):
    """z indexed 1..4; u constant on pi-parts, v constant on sigma-parts."""
    n = 0
    for u1, u3 in product(G, repeat=2):          # u on {1,2} and on {3,4}
        u = {1: u1, 2: u1, 3: u3, 4: u3}
        for v1, v2 in product(G, repeat=2):      # v on {1,4} and on {2,3}
            v = {1: v1, 4: v1, 2: v2, 3: v2}
            if all(mul(u[i], v[i]) == z[i] for i in (1, 2, 3, 4)):
                n += 1
    return n

# (i) G = Z/2
G2 = [0, 1]; add = lambda a, b: (a + b) % 2
for z in ({1: 0, 2: 1, 3: 0, 4: 0}, {1: 0, 2: 0, 3: 0, 4: 0}, {1: 1, 2: 0, 3: 1, 4: 0}):
    rel = add(-z[1] % 2, z[2]) == add(-z[4] % 2, z[3])
    print("G = Z/2  z =", [z[i] for i in (1,2,3,4)],
          " z1^-1 z2 == z4^-1 z3 ?", rel,
          " solutions =", count(G2, add, z), " line 157 claims |G|^1 =", 2)

# (ii) G = S_3 (non-abelian)
S3 = list(permutations(range(3)))
mul = lambda a, b: tuple(a[b[i]] for i in range(3))
inv = lambda a: tuple(sorted(range(3), key=lambda i: a[i]))
e, t, c = (0,1,2), (1,0,2), (1,2,0)
for z in ({1: e, 2: t, 3: e, 4: e}, {1: e, 2: e, 3: e, 4: e}, {1: c, 2: t, 3: t, 4: c}):
    rel = mul(inv(z[1]), z[2]) == mul(inv(z[4]), z[3])
    print("G = S_3  z =", [z[i] for i in (1,2,3,4)],
          " z1^-1 z2 == z4^-1 z3 ?", rel,
          " solutions =", count(S3, mul, z), " line 157 claims |G|^1 =", 6)
