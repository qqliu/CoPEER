# P27: check the supplied witness: the unique map from the two-element frame to the one-element frame.
from itertools import combinations
# frames as finite lattices given by their element sets with meet/join on a linear order
two = [0, 1]      # 0 < 1 : the two-element frame
one = [0]         # the one-element frame (top = bottom)
h = {0: 0, 1: 0}  # the unique function 2 -> 1
def meet(a, b, L): return min(a, b)
def join(S, L):    return max(S) if S else min(L)
ok_meet = all(h[meet(a,b,two)] == meet(h[a],h[b],one) for a in two for b in two)
ok_join = all(h[join(list(S),two)] == join([h[x] for x in S], one)
              for k in range(len(two)+1) for S in combinations(two, k))
ok_top  = h[max(two)] == max(one)
ok_bot  = h[min(two)] == min(one)
print("h preserves finite meets:", ok_meet, " arbitrary joins (incl. empty join = bottom):", ok_join)
print("h preserves top:", ok_top, " bottom:", ok_bot, " -> h is a frame homomorphism:",
      ok_meet and ok_join and ok_top and ok_bot)
print("h is the unique function 2 -> 1 (the target has one element):", True)
print("h injective?", len(set(h.values())) == len(two), "  surjective?", set(h.values()) == set(one))
print("so h is NOT a frame isomorphism; the two frames have", len(two), "and", len(one),
      "elements, so they are not isomorphic as lattices, and no invertible map between the")
print("corresponding locales exists -> f = h^op satisfies line 17's right-hand side but is not")
print("an isomorphism of locales:", (ok_meet and ok_join and ok_top and ok_bot) and len(two) != len(one))
