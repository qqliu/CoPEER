# P21: check the response's supplied witness f(n)=2n, g(n)=n/2 if n even else 0.
def f(n): return 2*n
def g(n): return n//2 if n % 2 == 0 else 0
N = 100000
comp = [g(f(n)) for n in range(N)]
print("g(f(n)) == n for 0 <= n <", N, ":", all(comp[n] == n for n in range(N)))
print("so g o f is injective on the checked range (and g(f(n)) = g(2n) = n identically by definition)")
print("g not injective: g(1) =", g(1), ", g(3) =", g(3), "-> equal:", g(1) == g(3), "with 1 != 3")
print("values g takes on odd inputs:", sorted({g(n) for n in range(1, 50, 2)}),
      "  <- 0 is in the codomain only if 0 in N")
print("min of g over 0..100:", min(g(n) for n in range(101)))
