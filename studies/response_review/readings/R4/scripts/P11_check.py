# P11: exact check of the witness supplied in the critic's response.
# Witness: p = x1^2 x2 + x1 x2^2 in K[x1,x2] with the degree reverse lexicographic order.
# Response's assertions to check:
#   (i)  LM(p) = x1^2 x2, i.e. exponent vector (2,1);
#   (ii) the exponents then satisfy a_1 = 2 > a_2 = 1 with i=1 < j=2 (hypothesis of source line 24);
#   (iii) the swapped monomial x_1^{a_2} x_2^{a_1} = x1 x2^2 does appear in p;
#   (iv) that swapped monomial is SMALLER than LM(p), not larger  -> source line 29 fails on this instance.
# degrevlex (standard, Cox-Little-O'Shea): a > b iff deg a > deg b, or degs equal and the
# RIGHTMOST nonzero entry of a-b is negative.

def cmp_degrevlex(a, b):
    da, db = sum(a), sum(b)
    if da != db:
        return 1 if da > db else -1
    d = [x - y for x, y in zip(a, b)]
    for k in range(len(d) - 1, -1, -1):
        if d[k] != 0:
            return 1 if d[k] < 0 else -1
    return 0

def leading(mons):
    lm = mons[0]
    for m in mons[1:]:
        if cmp_degrevlex(m, lm) > 0:
            lm = m
    return lm

p = [(2, 1), (1, 2)]          # monomials of p, exactly as the response gives them
lm = leading(p)
print("monomials of p:", p)
print("LM(p) =", lm, "(x1^%d x2^%d)" % lm)
assert lm == (2, 1), "response's LM claim fails"

a1, a2 = lm
print("a1 > a2 ?", a1 > a2, "  (hypothesis of source line 24 with i=1<j=2)")
assert a1 > a2

swapped = (a2, a1)            # source line 27 with n=2, i=1, j=2
print("swapped monomial (line 27) =", swapped)
print("swapped appears in p ?", swapped in p)
assert swapped in p
c = cmp_degrevlex(swapped, lm)
print("cmp_degrevlex(swapped, LM(p)) =", c, "-> swapped is", "LARGER" if c > 0 else ("SMALLER" if c < 0 else "EQUAL"))
assert c < 0, "line 29 would hold"
print("=> source line 29 ('it would be larger than LM p') is FALSE on this instance.")

# sanity check on the order convention: within each degree the nonincreasing arrangement is
# the largest, so source line 22 (a_1 >= ... >= a_n) is consistent with this convention,
# i.e. the witness does not covertly assume the opposite convention.
from itertools import permutations
ok = True
for exps in [(2,1),(3,1),(2,2),(3,0)]:
    orbit = sorted(set(permutations(exps)))
    top = leading(orbit)
    if list(top) != sorted(exps, reverse=True):
        ok = False
        print("convention check FAILED for", exps, "top =", top)
for exps in [(2,1,0),(3,1,1),(2,2,1),(4,2,0)]:
    orbit = sorted(set(permutations(exps)))
    top = leading(orbit)
    if list(top) != sorted(exps, reverse=True):
        ok = False
        print("convention check FAILED for", exps, "top =", top)
print("convention check (LM of a full symmetric orbit is the nonincreasing arrangement):", ok)
