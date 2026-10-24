# P20: check the supplied witness for line 29, exactly as given:
# "For n=2, the monomial x_1^2 x_2 has exponents a_1 = 2 > 1 = a_2, but swapping them yields
#  x_1 x_2^2, which is strictly smaller than x_1^2 x_2 in the degree reverse lexicographic order."
from itertools import combinations

def grevlex_cmp(a, b):
    """standard degree reverse lexicographic: higher total degree wins; on a tie, a > b iff the
       RIGHTMOST nonzero entry of a-b is negative."""
    if sum(a) != sum(b):
        return 1 if sum(a) > sum(b) else -1
    d = [x - y for x, y in zip(a, b)]
    for v in reversed(d):
        if v != 0:
            return 1 if v < 0 else -1
    return 0

def elementary_symmetric_monomials(n, k):
    return [tuple(1 if i in S else 0 for i in range(n)) for S in combinations(range(n), k)]

def leading(mons):
    best = mons[0]
    for m in mons[1:]:
        if grevlex_cmp(m, best) > 0:
            best = m
    return best

def show(e):
    return "*".join("x_%d^%d" % (i + 1, v) for i, v in enumerate(e) if v) or "1"

# 1. pin the order convention using the source's own line 9: LM(sigma_k) = x_1...x_k
print("line 9 check under this convention: LM(sigma_k) for n=4")
for k in range(1, 5):
    lm = leading(elementary_symmetric_monomials(4, k))
    print("   k=%d  LM = %s   equals x_1..x_%d ? %s"
          % (k, show(lm), k, lm == tuple(1 if i < k else 0 for i in range(4))))

# 2. the supplied witness
u = (2, 1)          # x_1^2 x_2 = LM(p) in the response's instance, a_1 = 2 > a_2 = 1, i=1 < j=2
v = (1, 2)          # the line-27 monomial: exponents a_i, a_j swapped
print()
print("witness: u =", show(u), " v (swapped) =", show(v))
c = grevlex_cmp(v, u)
print("grevlex compare v vs u:", {1: "v > u", -1: "v < u", 0: "equal"}[c])
print("line 29 asserts v would be LARGER than LM(p) = u; is it? ", c > 0)
print("response asserts v is strictly SMALLER; is it?           ", c < 0)

# 3. the setting is instantiable: a symmetric p with LM(p) = u
print()
print("symmetric p = x_1^2 x_2 + x_1 x_2^2 has monomials", [show(u), show(v)],
      "and LM(p) =", show(leading([u, v])), "== u ?", leading([u, v]) == u)

# 4. how often does the swap in line 27 go the wrong way for line 29?
print()
print("all pairs a=(a_1,a_2,a_3) with a_i > a_j (i<j), entries 0..3: does the swapped monomial")
print("come out larger, as line 29 claims?")
bad = tot = 0
for a1 in range(4):
    for a2 in range(4):
        for a3 in range(4):
            a = (a1, a2, a3)
            for i, j in combinations(range(3), 2):
                if a[i] > a[j]:
                    s = list(a); s[i], s[j] = a[j], a[i]
                    tot += 1
                    if grevlex_cmp(tuple(s), a) <= 0:
                        bad += 1
print("   instances:", tot, "  swapped monomial NOT larger:", bad,
      "  -> line 29's claim holds in", tot - bad, "of them")
