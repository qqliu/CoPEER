# P15: the response's witness n=2, x=1, y=1 against line 25
#   x + y  =?=  sum_{i=0}^{1} C(n,i) x^i y^(n-i)
from math import comb
def rhs(n, x, y): return sum(comb(n, i) * x**i * y**(n - i) for i in range(0, 2))
for n, x, y in ((2, 1, 1), (1, 1, 1), (3, 1, 1), (2, 2, 3)):
    print("n,x,y =", (n, x, y), " x+y =", x + y, " sum_{i=0}^{1} C(n,i)x^i y^(n-i) =", rhs(n, x, y),
          " equal?", x + y == rhs(n, x, y))
n, x, y = 2, 1, 1
print("\nsupplied witness: terms are", [(i, comb(n, i) * x**i * y**(n - i)) for i in range(0, 2)],
      " total", rhs(n, x, y), " versus x+y =", x + y)
