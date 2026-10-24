# P47: ILLUSTRATION of the construction in the response's witness (its own witness, the frame
# O(R) of opens of the real line, is infinite and was checked analytically, not here).
# The construction: h : {0,1} -> F with 0 |-> bottom, 1 |-> top, for a frame F with |F| > 2.
# Checked here on two finite frames: a 3-chain, and the topology of the Sierpinski space.
from itertools import combinations

def check(name, F, leq, meet, join, bot, top):
    dom = [0, 1]
    h = {0: bot, 1: top}
    pres_meet = meet(h[0], h[1]) == h[0]                 # 0 ^ 1 = 0 in {0,1}
    pres_join = join(h[0], h[1]) == h[1]                 # 0 v 1 = 1
    pres_bot, pres_top = h[0] == bot, h[1] == top
    inj = h[0] != h[1]
    surj = set(h.values()) == set(F)
    print(name, " |F| =", len(F),
          " h preserves meet/join/bottom/top:", (pres_meet, pres_join, pres_bot, pres_top),
          " injective:", inj, " surjective:", surj,
          " => frame homomorphism but NOT an isomorphism:", all([pres_meet, pres_join, pres_bot, pres_top]) and not surj)

# 3-chain 0 < a < 1
F1 = [0, 1, 2]
check("3-chain      ", F1, lambda x, y: x <= y, min, max, 0, 2)

# topology of the Sierpinski space {x,y} with opens {}, {x}, {x,y}
F2 = [frozenset(), frozenset({"x"}), frozenset({"x", "y"})]
check("Sierpinski   ", F2, lambda A, B: A <= B, lambda A, B: A & B, lambda A, B: A | B,
      frozenset(), frozenset({"x", "y"}))
print("\nThe same two-element image sits inside O(R): h(0) = empty set, h(1) = R;")
print("O(R) contains e.g. the open interval (0,1), so h is not surjective and not an isomorphism.")
