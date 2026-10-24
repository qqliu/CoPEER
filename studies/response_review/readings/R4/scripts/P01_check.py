# P01: exact check of the witness supplied by the critic's response.
# Witness: k = 1, P_1 = 2.  Response: floor(2 + 2*sqrt(2)) + 1 = 5, an odd prime,
# contradicting line 144 ("cannot be a prime since it is an even number for any k").
from math import isqrt

def floor_val(p):
    # floor(p + 2*sqrt(p)) = p + floor(sqrt(4p)) computed with exact integer arithmetic:
    # 2*sqrt(p) = sqrt(4p), and floor(p + sqrt(4p)) = p + isqrt(4p) since p is an integer
    return p + isqrt(4 * p)

def is_prime(n):
    if n < 2: return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0: return False
    return True

p = 2                                   # P_1 = 2, the first prime (the source uses P_1 = 2 at line 135)
# certify isqrt(8) = 2 exactly: 2^2 = 4 <= 8 < 9 = 3^2
print("4*P_1 =", 4 * p, " isqrt =", isqrt(4 * p), " certificate: 2^2=4 <= 8 < 9=3^2:", 2**2 <= 8 < 3**2)
v = floor_val(p) + 1
print("floor(P_1 + 2*sqrt(P_1)) + 1 =", v)
print("v even ?", v % 2 == 0, "  v prime ?", is_prime(v))
assert v == 5 and v % 2 == 1 and is_prime(v)
print("=> line 144 is FALSE at k = 1: the value is 5, odd AND prime.")

print()
print("for context, the first primes (the claim is asserted 'for any k'):")
primes = [n for n in range(2, 60) if is_prime(n)]
for i, q in enumerate(primes[:12], start=1):
    v = floor_val(q) + 1
    print(f"   k={i:2d}  P_k={q:3d}  floor(P_k+2*sqrt(P_k))+1 = {v:3d}  even={v%2==0}  prime={is_prime(v)}")
