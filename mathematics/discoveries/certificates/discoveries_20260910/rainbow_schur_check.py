#!/usr/bin/env python3
"""Independent exact enumeration for rainbow-schur-density-counterexample.

Run from any directory with Python 3; no dependencies, network, or file writes.
This new checker directly generates triples by their sum, independently of the
closed-form proof. Finite checks supplement the entry's all-m hand proof; they
are not a proof assistant certificate or a claim of extremal optimality.
"""

import argparse
from collections import Counter
from fractions import Fraction
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def coloring(m):
    require(m >= 1, "m must be positive")
    return [0] + [
        1 if k % 2 == 0 else (2 if k <= 8 * m or k > 20 * m else 3)
        for k in range(1, 22 * m + 1)
    ]


def check(m):
    colors = coloring(m)
    n = len(colors) - 1
    require(Counter(colors[1:]) == {1: 11 * m, 2: 5 * m, 3: 6 * m},
            f"population mismatch at m={m}")
    total = 0
    parities = Counter()
    mixed_pairs = Counter()
    for z in range(2, n + 1):
        for x in range(1, z):
            y = z - x
            total += 1
            if colors[x] == colors[y] or colors[x] == colors[z] or colors[y] == colors[z]:
                continue
            parities[(x % 2, y % 2)] += 1
            if (x + y) % 2:
                odd_addend = x if x % 2 else y
                mixed_pairs[(odd_addend, z)] += 1

    expected_pairs = {
        tuple(sorted((u, v)))
        for u in range(1, n + 1, 2) if colors[u] == 2
        for v in range(1, n + 1, 2) if colors[v] == 3
    }
    require(set(mixed_pairs) == expected_pairs, f"mixed bijection mismatch at m={m}")
    require(all(v == 2 for v in mixed_pairs.values()), f"orientation mismatch at m={m}")
    require(parities == {(0, 1): 30 * m * m, (1, 0): 30 * m * m,
                         (1, 1): 39 * m * m + 3 * m},
            f"parity counts mismatch at m={m}")
    rainbow = sum(parities.values())
    require(total == n * (n - 1) // 2 == 242 * m * m - 11 * m,
            f"normalization mismatch at m={m}")
    require(rainbow == 99 * m * m + 3 * m, f"rainbow count mismatch at m={m}")
    density = Fraction(rainbow, total)
    require(density > Fraction(9, 22) > Fraction(2, 5) + Fraction(1, 220),
            f"density gap mismatch at m={m}")
    return {"m": m, "n": n, "rainbow": rainbow, "ordered_schur": total,
            "density": str(density)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-m", type=int, default=80)
    args = parser.parse_args()
    if args.max_m < 1:
        parser.error("--max-m must be positive")
    endpoints = []
    for m in range(1, args.max_m + 1):
        result = check(m)
        if m in {1, args.max_m}:
            endpoints.append(result)
    require(Fraction(99, 242) == Fraction(9, 22), "limiting coefficient ratio")
    # Polynomial coefficient identities, not interpolation from finite samples:
    require(22 * 99 - 9 * 242 == 0 and 22 * 3 + 9 * 11 == 165,
            "all-m numerator of density minus 9/22")
    print(json.dumps({"status": "PASS", "checked_m": [1, args.max_m],
                      "endpoints": endpoints, "limiting_density": "9/22",
                      "epsilon": "1/220", "method": "exact ordered enumeration",
                      "scope": "finite enumeration; all-m proof in entry"}, indent=2))


if __name__ == "__main__":
    main()
