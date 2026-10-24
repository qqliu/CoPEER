# P37: check of the two instances supplied by the critic's response against the assumptions
# in force at lines 24-25 of the source.
# Source line 24: "My initial array is A = {x_0, ..., x_n} and i have x_0 < x_n. Say that after
#   first pass x_0 switches place with x_m, ... Thus, x_m < x_0."
# Line 25 (the first choice): "Sum it up: x_m < x_0 < x_n < x_k."
# Assumptions in force for the challenged inequality x_m < x_0:
#   (H1) x_0 < x_n ;  (H2) x_0 and x_m are switched during the m-pass.
instances = [("A = [10, 5, 12, 2], m = 1, n = 3", [10, 5, 12, 2], 1, 3),
             ("A = [10, 11, 20, 2], m = 1, n = 3", [10, 11, 20, 2], 1, 3)]

for label, A, m, n in instances:
    x0, xm, xn = A[0], A[m], A[n]
    H1 = x0 < xn
    # an insertion-sort style pass swaps positions 0 and m only if they are out of order
    H2 = xm < x0
    claim = xm < x0
    print(label)
    print(f"   x_0 = {x0}, x_m = {xm}, x_n = {xn}")
    print(f"   (H1) x_0 < x_n : {H1}      <- the source's standing assumption at line 24")
    print(f"   (H2) x_0 and x_m would actually be switched (i.e. x_m < x_0) : {H2}")
    print(f"   challenged claim x_m < x_0 : {claim}")
    if not H1:
        print("   -> this instance VIOLATES the assumption in force, so it cannot refute the line")
    elif H2 and claim:
        print("   -> assumptions hold and the claim holds: supports the line, does not refute it")
    print()

# summary of what the supplied evidence does
print("instance 1: assumptions violated (x_0 = 10 is not < x_n = 2) and the claim x_m < x_0 holds anyway;")
print("            the response itself says 'and indeed x_m < x_0'.")
print("instance 2: assumptions violated twice over (x_0 = 10 is not < x_n = 2, and x_0 < x_m so no")
print("            switch occurs, which is the case the source excludes by hypothesis and treats")
print("            separately at line 28).")
print("=> neither supplied instance refutes the inequality asserted at line 25.")
