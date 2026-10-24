# P21: check exactly the supplied witness for line 14 ("Functions, where g o f is injective but g is
# not injective do not exist"):
# "Take f(n)=2n and g(n)= n/2 if n is even, g(n)=0 if n is odd; then g o f(n)=n is injective while
#  g is not injective because g(1)=g(3)=0."
# The source (line 1) writes f, g : N -> N without saying whether 0 is in N, so both conventions
# are tested; membership is tested against N itself, not against the finite sample.
def f(n): return 2 * n
def g(n): return n // 2 if n % 2 == 0 else 0

for name, lo in (("N = {0,1,2,...}", 0), ("N = {1,2,3,...}", 1)):
    dom = list(range(lo, 400))
    in_N = lambda v: isinstance(v, int) and v >= lo
    f_vals = [f(n) for n in dom]
    gf_vals = [g(f(n)) for n in dom]
    print(name)
    print("   f injective on sample?", len(set(f_vals)) == len(f_vals),
          "  every f(n) in N?", all(in_N(v) for v in f_vals))
    print("   g o f (n) = n for all sampled n?", all(g(f(n)) == n for n in dom),
          "  g o f injective?", len(set(gf_vals)) == len(gf_vals))
    print("   g injective?", len(set(g(n) for n in dom)) == len(dom),
          "  response's pair: g(1) =", g(1), ", g(3) =", g(3), "-> equal?", g(1) == g(3))
    print("   every g(n) in N?", all(in_N(g(n)) for n in dom),
          " (the only values g takes are n/2 on evens and 0 on odds)")
    ok = (len(set(gf_vals)) == len(gf_vals) and g(1) == g(3)
          and all(in_N(v) for v in f_vals) and all(in_N(g(n)) for n in dom))
    print("   -> witness is a pair of functions N->N refuting line 14 under this convention?", ok)
    print()
