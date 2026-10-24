# P19: run exactly the witness the response supplies -- "n=2, m=2, and A = [0, 100, 1] (so x0 < x2),
# a 2-sort leaves the array unchanged" -- and then test it against what line 24 actually asserts.
def gap_sort(a, g):                      # m-sort: sort each gap-g subsequence
    a = list(a)
    for s in range(g):
        idx = list(range(s, len(a), g))
        vals = sorted(a[i] for i in idx)
        for i, v in zip(idx, vals):
            a[i] = v
    return a

def is_h_sorted(a, h):
    return all(a[i] <= a[i + h] for i in range(len(a) - h))

A = [0, 100, 1]           # x0=0, x1=100, x2=1
m, n = 2, 2
B = gap_sort(A, m)
print("A      =", A, "  x0 < xn ?", A[0] < A[n])
print("after %d-sort B =" % m, B, "  unchanged ?", B == A)
print("did x0 (value %d) swap with xm (value %d)?" % (A[0], A[m]), B[0] != A[0])
print("is 'x_m < x_0' (i.e. %d < %d) true?" % (A[m], A[0]), A[m] < A[0])
print()
print("So the response's arithmetic is right: no swap occurs and x_m < x_0 fails.")
print("But line 24 asserts 'x_m < x_0' only inside its case hypothesis")
print("  'Say that after first pass x_0 switches place with x_m'.")
print("This witness makes that hypothesis FALSE (no swap), so it instantiates the")
print("complementary case, which line 28 handles explicitly:")
print("  'If we assumed the switchings of x_0 and x_n didn't happen during m-sorting,")
print("   we are trivially done ... since x_0 < x_n, B is n-sorted.'")
print("Check line 28's own conclusion on this very witness: B[0]=%d < B[n]=%d, B is n-sorted? %s"
      % (B[0], B[n], is_h_sorted(B, n)))
print()
print("Second defect of the witness: it takes m = n = 2, i.e. the second gap is not SMALLER")
print("than the first, while the passage is about m-sorting after n-sorting with m < n.")
print()
print("Control: when the case hypothesis of line 24 DOES hold, is its conclusion x_m < x_0 true?")
for A2 in ([5, 100, 1], [7, 0, 2], [9, 3, 4]):
    B2 = gap_sort(A2, 2)
    swapped = B2[0] != A2[0]
    print("  A =", A2, "-> B =", B2, " swap happened:", swapped,
          " x_m < x_0 :", A2[2] < A2[0], " (subsequence sorted: B[0] <= B[2] =", B2[0] <= B2[2], ")")
