# P43: check the response's witness (|G| = 2, n = 3) against the source's own formula and theorem.
def valency_complement(gsize):        # source line 223-224: valency of the complement is (|G|-1)(|G|-2)
    return (gsize-1)*(gsize-2)
def partitions_at_most_k_parts(n, k): # source line 217-219: rank = number of partitions of n into at most |G| parts
    def rec(n, mx, parts):
        if n == 0: return 1 if parts <= k else 0
        return sum(rec(n-i, i, parts+1) for i in range(min(n, mx), 0, -1))
    return rec(n, n, 0)
print("witness: G of order 2, n = 3")
print("  valency of the complement = (2-1)*(2-2) =", valency_complement(2), "-> complement empty")
print("  but n = 3 > 2, so the source's 'non-empty if and only if n>2' fails at this witness:",
      valency_complement(2) == 0 and 3 > 2)
print()
print("valency by |G|:", {g: valency_complement(g) for g in range(1, 7)},
      " -> zero exactly for |G| <= 2, independent of n")
print("rank of the scheme for n=3 (partitions of 3 into at most |G| parts):",
      {g: partitions_at_most_k_parts(3, g) for g in range(1, 7)},
      " -> rank 2 (trivial) at |G|=2, matching an empty complement")
