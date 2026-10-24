# P37: the two arrays the response supplies, tested against the source's active assumption
# (line 24: "My initial array is A = {x_0,...,x_n} and i have x_0 < x_n") and against the
# challenged inequality x_m < x_0.
for A, m, n, tag in ((( 10, 5, 12, 2), 1, 3, "first array"),
                     (( 10, 11, 20, 2), 1, 3, "second array (offered as the counterexample)")):
    x0, xm, xn = A[0], A[m], A[n]
    print(tag, " A =", A, " m =", m, " n =", n)
    print("   x_0 =", x0, " x_m =", xm, " x_n =", xn)
    print("   source's standing assumption x_0 < x_n holds?", x0 < xn)
    print("   challenged inequality x_m < x_0 holds in this array?", xm < x0)
