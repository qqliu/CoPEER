# ADJ check for P43: the critic's witness is G of order 2 with n = 3, tested against
# the source's OWN valency formula for the complement (line 224: "(|G|-1)(|G|-2)").
for gsize in range(1, 7):
    val = (gsize - 1) * (gsize - 2)
    print("|G| =", gsize, " valency of complement = (|G|-1)(|G|-2) =", val,
          " non-empty:", val > 0)
n = 3
gsize = 2
val = (gsize - 1) * (gsize - 2)
print("\nwitness: |G| = %d, n = %d -> valency = %d, complement empty: %s, while n > 2: %s"
      % (gsize, n, val, val == 0, n > 2))
print("source's biconditional 'non-empty iff n>2' at the witness:",
      "LHS(non-empty) =", val > 0, " RHS(n>2) =", n > 2,
      " -> biconditional holds:", (val > 0) == (n > 2))
print("the condition that the source's own formula actually gives: non-empty iff |G| > 2 ->",
      all(((gs - 1) * (gs - 2) > 0) == (gs > 2) for gs in range(1, 200)))
