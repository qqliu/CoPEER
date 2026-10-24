# P04: the response's witness f(x)=x+1, g(x)=max(0,x-1) on N (0 included), against line 14
f = lambda x: x + 1
g = lambda x: max(0, x - 1)
N = range(0, 2001)
print("g maps N into N?", all(g(x) >= 0 and isinstance(g(x), int) for x in N))
vals = [(x, g(f(x))) for x in N]
print("g(f(x)) = x on the tested range?", all(gf == x for x, gf in vals))
print("g o f injective on the tested range?", len({gf for _, gf in vals}) == len(vals))
print("g(0), g(1) =", g(0), g(1), " -> g injective?", g(0) != g(1))
print("with the other convention N = {1,2,...}: g(1) =", g(1), "which is NOT in {1,2,...}")
