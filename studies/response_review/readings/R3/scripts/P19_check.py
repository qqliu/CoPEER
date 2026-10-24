# P19: check the supplied witness A = [0,100,1] with n=2, m=2 against source line 24.
def gap_sort(a, g):          # sort each gap-g subsequence, i.e. a g-sort
    b = list(a)
    for s in range(g):
        idx = list(range(s, len(b), g))
        vals = sorted(b[i] for i in idx)
        for i, v in zip(idx, vals): b[i] = v
    return b
def is_gap_sorted(a, g):
    return all(a[i] <= a[i+g] for i in range(len(a)-g))
A = [0, 100, 1]; n = 2; m = 2
print("witness A =", A, " n =", n, " m =", m)
print("source assumption x_0 < x_n :", A[0] < A[n])
print("A is n-sorted (gap", n, ")?", is_gap_sorted(A, n))
print("after the m-sort (gap", m, "):", gap_sort(A, m), " unchanged?", gap_sort(A, m) == A,
      "-> x_0 does not swap with x_m, as the response says")
print()
print("but the source's setting requires the second gap to be SMALLER: m < n ?", m < n,
      "  (m =", m, ", n =", n, ") -> with m = n the 'm-sort' IS the n-sort, a degenerate case")
print("with a genuinely smaller gap, e.g. m=1 on the same array:", gap_sort(A, 1),
      " still n-sorted?", is_gap_sorted(gap_sort(A, 1), n))
print()
print("line 24 supposes the swap ('Say that after first pass x_0 switches place with x_m');")
print("under that supposition the gap subsequence at offset 0 ends sorted, so the entry landing at")
print("position 0 is <= the entry landing at position m, which is what line 24 records as x_m < x_0:")
B = [100, 0, 1]   # an array where the offset-0 subsequence (positions 0,2 for gap 2) does swap
print("  example of the supposed case: A' =", B, " -> 2-sort:", gap_sort(B, 2),
      " entry at 0 <= entry at 2 :", gap_sort(B, 2)[0] <= gap_sort(B, 2)[2])
