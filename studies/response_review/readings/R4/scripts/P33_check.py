# P33: exact enumeration of the witness supplied in the critic's response.
# Witness: n = 4, pi = {{1,2},{3,4}}, sigma = {{1,4},{2,3}}, z_i = a_i b_i^{-1}.
# Source line 157 claims: given that the z_i agree on parts of tau = pi /\ sigma,
# the number of ways to choose u (constant on parts of pi) and v (constant on parts of sigma)
# with u_i v_i = z_i is exactly |G|^{|pi \/ sigma|}.
# Response: the system forces z_1^{-1} z_2 = z_4^{-1} z_3, so there are 0 choices otherwise.
from itertools import product

pi    = [[0, 1], [2, 3]]      # {1,2},{3,4}   (0-indexed)
sigma = [[0, 3], [1, 2]]      # {1,4},{2,3}
n = 4

def meet(p, q):               # common refinement = meet (finer below coarser, source line 141)
    out = []
    for A in p:
        for B in q:
            C = sorted(set(A) & set(B))
            if C:
                out.append(C)
    return sorted(out)

def join(p, q):               # least upper bound = connected components of p U q
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def uni(x, y):
        parent[find(x)] = find(y)
    for blocks in (p, q):
        for B in blocks:
            for t in B[1:]:
                uni(B[0], t)
    comp = {}
    for i in range(n):
        comp.setdefault(find(i), []).append(i)
    return sorted(sorted(v) for v in comp.values())

print("pi /\\ sigma =", meet(pi, sigma), " -> parts:", len(meet(pi, sigma)))
print("pi \\/ sigma =", join(pi, sigma), " -> parts:", len(join(pi, sigma)))
J = len(join(pi, sigma))

# --- two concrete groups -------------------------------------------------
# Z_2 (additive) and S_3 (permutation composition)
def group_Z(m):
    els = list(range(m))
    return els, (lambda x, y: (x + y) % m), 0, (lambda x: (-x) % m)

def group_S3():
    els = list(product(range(3), repeat=3))
    els = [e for e in els if sorted(e) == [0, 1, 2]]
    mul = lambda p, q: tuple(p[q[i]] for i in range(3))
    e = (0, 1, 2)
    def inv(p):
        r = [0, 0, 0]
        for i, pi_ in enumerate(p):
            r[pi_] = i
        return tuple(r)
    return els, mul, e, inv

def count_uv(els, mul, z):
    """number of (u,v) with u constant on parts of pi, v constant on parts of sigma, u_i v_i = z_i"""
    cnt = 0
    for uvals in product(els, repeat=len(pi)):
        u = [None] * n
        for k, B in enumerate(pi):
            for i in B:
                u[i] = uvals[k]
        for vvals in product(els, repeat=len(sigma)):
            v = [None] * n
            for k, B in enumerate(sigma):
                for i in B:
                    v[i] = vvals[k]
            if all(mul(u[i], v[i]) == z[i] for i in range(n)):
                cnt += 1
    return cnt

def count_c(els, mul, inv, a, b):
    """direct count of c with a S_pi c and c S_sigma b (the (a,b) entry of B_pi B_sigma)"""
    cnt = 0
    for c in product(els, repeat=n):
        ok = True
        for B in pi:
            r = [mul(a[i], inv(c[i])) for i in B]
            if len(set(r)) != 1:
                ok = False; break
        if ok:
            for B in sigma:
                r = [mul(c[i], inv(b[i])) for i in B]
                if len(set(r)) != 1:
                    ok = False; break
        if ok:
            cnt += 1
    return cnt

for name, (els, mul, e, inv) in [("Z_2", group_Z(2)), ("Z_3", group_Z(3)), ("S_3", group_S3())]:
    G = len(els)
    claimed = G ** J
    bad = good = None
    for z in product(els, repeat=n):
        # tau = pi /\ sigma is all singletons here, so the line-152 hypothesis is vacuous: every z qualifies
        consistent = mul(inv(z[0]), z[1]) == mul(inv(z[3]), z[2])   # z_1^{-1} z_2 == z_4^{-1} z_3
        c = count_uv(els, mul, z)
        if not consistent and bad is None:
            bad = (z, c)
        if consistent and good is None:
            good = (z, c)
        assert (c == 0) == (not consistent), ("consistency criterion wrong", z, c)
    b = [e] * n
    a_bad = [mul(bad[0][i], b[i]) for i in range(n)]      # a_i = z_i * b_i, so a_i b_i^{-1} = z_i
    direct = count_c(els, mul, inv, a_bad, b)
    print(f"{name}: |G|={G}  claimed |G|^|pi\\/sigma| = {claimed}")
    print(f"   z violating z_1^-1 z_2 = z_4^-1 z_3 : z={bad[0]}  -> number of (u,v) choices = {bad[1]}"
          f"   [direct count of c: {direct}]")
    print(f"   z satisfying it                      : z={good[0]}  -> number of (u,v) choices = {good[1]}")
    assert bad[1] == 0 and direct == 0 and good[1] == claimed
print()
print("=> line 157 (count = |G|^{|pi \\/ sigma|} whenever the ratios agree on parts of pi /\\ sigma)")
print("   is FALSE: for this pi, sigma the hypothesis is vacuous but the count is 0 for some z.")
