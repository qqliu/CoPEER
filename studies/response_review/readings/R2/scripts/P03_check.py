# P03: the response's witness -- S a singleton -- evaluated on von Neumann ordinals.
# Line 28 embeds S via s_alpha -> alpha into beta = union over {alpha : s_alpha in S} of alpha.
# Ordinal n is the SET of smaller ordinals; union of a set of ordinals is its supremum,
# which for a set with a largest element is that largest element.
def vn(n):                      # von Neumann n as a frozenset
    return frozenset(vn(i) for i in range(n))

def union_of(indices):          # \bigcup_{alpha in indices} alpha, as a set
    out = set()
    for a in indices:
        out |= set(vn(a))
    return frozenset(out)

for size in (1, 2, 3, 5):
    used = list(range(size))            # the construction of lines 15-24 uses s_0..s_{size-1}
    beta = union_of(used)
    beta_as_int = len(beta)             # a finite von Neumann ordinal is its own cardinality
    inside = [a for a in used if vn(a) in beta]
    print("|S| =", size, " indices used =", used, " beta =", beta_as_int,
          " indices actually lying in beta =", inside,
          " map s_alpha->alpha lands in beta for all alpha?", len(inside) == size)

print()
print("witness |S| = 1: beta =", len(union_of([0])), "(the empty set); is 0 an element of beta?", vn(0) in union_of([0]))
print("an injection from a 1-element set into the empty set exists?", False)
