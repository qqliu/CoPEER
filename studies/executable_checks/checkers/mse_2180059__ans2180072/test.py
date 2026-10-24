r"""Then $1=a^k=g^{km}$ so $km=p-1$ since $g$ is a generator."""

import json


def is_prime(n):
    if n < 2:
        return False
    for divisor in range(2, n):
        if n % divisor == 0:
            return False
    return True


def is_generator(g, p):
    generated = {g ** exponent % p for exponent in range(1, p)}
    return generated == set(range(1, p))


def multiplicative_order(a, p):
    for exponent in range(1, p):
        if a ** exponent % p == 1:
            return exponent
    raise AssertionError("No multiplicative order found")


counterexamples = []
triples_checked = 0
for p in range(3, 12):
    if not is_prime(p):
        continue
    for g in range(1, p):
        if not is_generator(g, p):
            continue
        for m in range(1, p):
            triples_checked += 1
            a = g ** m % p
            k = multiplicative_order(a, p)
            if (
                a ** k % p == 1
                and g ** (k * m) % p == 1
                and k * m != p - 1
            ):
                counterexamples.append((p, g, m, a, k))

assert triples_checked == 62
assert counterexamples
assert counterexamples[0] == (5, 2, 3, 3, 4)

result = {
    "record_id": "mse_2180059__ans2180072",
    "outcome": "WITNESS_FOUND",
    "witness_description": "In the multiplicative group modulo 5, take p=5, generator g=2, m=3, a=g^m=3, and k=4 (the multiplicative order of a). Then a^k=3^4=1 modulo 5 and g^(km)=2^12=1 modulo 5, but km=12 whereas p-1=4.",
    "refutation_explanation": "A generator g of a group of order p-1 satisfies g^n=1 exactly when p-1 divides n; this does not force n=p-1. Here p-1 divides km, but km is a larger multiple.",
    "search_space": "Exhaustively swept all 62 triples (p,g,m) with p in {3,5,7,11}, g every primitive generator modulo p, and 1 <= m <= p-1; a=g^m modulo p and k was computed as the least positive multiplicative order of a. The lexicographically first counterexample was retained."
}
print(json.dumps(result, separators=(",", ":")))
