# P44: check exactly the supplied witness for line 25 ("x+y = sum_{i=0}^{1} (n choose i) x^i y^{n-i}"):
# "For n=2, x=1, y=1, the left side is 2 while the right side equals 3."
from math import comb
def rhs(n, x, y): return sum(comb(n, i) * x ** i * y ** (n - i) for i in range(0, 2))
n, x, y = 2, 1, 1
print("n, x, y =", n, x, y)
print("LHS x+y =", x + y)
print("RHS sum_{i=0}^{1} C(n,i) x^i y^{n-i} =",
      " + ".join("%d*%d^%d*%d^%d" % (comb(n, i), x, i, y, n - i) for i in range(2)),
      "=", rhs(n, x, y))
print("response's numbers reproduce (2 and 3)?", x + y == 2 and rhs(n, x, y) == 3)
print("line 25 holds at this instance?", x + y == rhs(n, x, y))
print()
print("for which (n,x,y) with small values does line 25 hold?  (x,y integers as line 3 requires)")
hold = fail = 0
for n in range(0, 6):
    for x in range(-3, 4):
        for y in range(-3, 4):
            if n - 1 < 0: continue
            try:
                ok = (x + y == rhs(n, x, y))
            except ZeroDivisionError:
                continue
            hold += ok; fail += (not ok)
print("   holds in", hold, "cases, fails in", fail, "cases (n = 0..5, x,y = -3..3)")
