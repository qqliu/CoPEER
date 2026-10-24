# P43: check exactly the supplied witness: "For G of order 2 and n=3, the complement has valency 0,
# hence is empty even though n>2", against the assertion "The valency of the complement is
# (|G|-1)(|G|-2), so it is non-empty if and only if n>2" (source line 224).
def partitions_at_most(n, k):
    # number of partitions of n into at most k parts, computed directly
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def p(n, k, mx):
        if n == 0: return 1
        if k == 0: return 0
        return sum(p(n - part, k - 1, part) for part in range(1, min(n, mx) + 1))
    return p(n, k, n)

n = 3
print(" |G|  valency (|G|-1)(|G|-2)  complement non-empty?   n>2 ?   claim of line 224 holds?")
for q in (1, 2, 3, 4, 5):
    val = (q - 1) * (q - 2)
    print("  %2d          %4d                 %-6s          %-5s   %s"
          % (q, val, val > 0, n > 2, (val > 0) == (n > 2)))
print()
q = 2
print("the supplied witness: |G| = 2, n = 3 -> valency =", (q - 1) * (q - 2),
      ", so the complement relation is empty, while n = 3 > 2")
print("the correct condition is |G| > 2, not n > 2")
print()
print("cross-check against the source's own rank formula (line 217-219: rank = number of")
print("partitions of n into at most |G| parts):")
for q in (2, 3, 4):
    print("   |G| =", q, " n = 3 -> rank =", partitions_at_most(3, q),
          "  (rank 2 means only 'equal' and one other relation, i.e. the complement is absent)")
