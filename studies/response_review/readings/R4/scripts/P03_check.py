# P03: exact check of the witness supplied by the critic's response, with von Neumann ordinals
# represented literally as sets.
# Witness: S a singleton. The construction of lines 15-24 then uses the single index alpha = 0,
# so line 28's beta = union over {alpha : s_alpha in S} of alpha = union{0} = 0 = empty set,
# and the map s_alpha |-> alpha sends S onto {0}, which is not a subset of beta.

def ordinal(n):                      # von Neumann: 0 = {}, n+1 = n u {n}
    o = frozenset()
    for k in range(n):
        o = o | {ordinal(k)}
    return o

def union_of(ords):                  # set-theoretic union of a set of ordinals = sup
    u = frozenset()
    for o in ords:
        u = u | o
    return u

def as_int(o):                       # rank of a von Neumann ordinal
    return len(o)

for n in range(1, 7):
    indices = [ordinal(i) for i in range(n)]          # alphas used for an n-element S: 0..n-1
    beta = union_of(indices)
    image_in_beta = all(a in beta for a in indices)
    print(f"|S| = {n}: indices used = {[as_int(a) for a in indices]}, "
          f"beta = union of them = {as_int(beta)}, image of s_alpha |-> alpha inside beta ? {image_in_beta}")
    assert not image_in_beta

print()
# the response's own instance, spelled out
indices = [ordinal(0)]
beta = union_of(indices)
print("singleton S: only index alpha = 0 ; beta =", set(beta), "= the empty set ; as_int(beta) =", as_int(beta))
print("is 0 an element of beta ?", ordinal(0) in beta)
print("S is non-empty but beta is empty, so no injection S -> beta exists:", as_int(beta) == 0)
assert ordinal(0) not in beta and as_int(beta) == 0
print("=> line 28 is FALSE for a singleton S: the map s_alpha |-> alpha does not land in beta.")

print()
print("for contrast, when the index set has no maximum the union does work, e.g. S countably")
print("infinite has indices 0,1,2,... and union = omega, which does contain every index;")
print("the failure is exactly when the set of indices used has a largest element.")
