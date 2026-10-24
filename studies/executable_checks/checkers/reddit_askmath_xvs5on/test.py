"""Contractibility requires the composites of maps between X and a point to equal the corresponding identity maps exactly."""

import json
from itertools import product


def main():
    pairs_checked = 0
    exact_identity_sizes = set()
    failed_identity_sizes = set()

    for n in range(9):
        domain = tuple(range(n))
        point = (0,)

        for f in product(point, repeat=n):
            for g in product(domain, repeat=1):
                pairs_checked += 1

                f_after_g = tuple(f[g[y]] for y in point)
                g_after_f = tuple(g[f[x]] for x in domain)

                if f_after_g == point and g_after_f == domain:
                    exact_identity_sizes.add(n)
                else:
                    failed_identity_sizes.add(n)

    assert pairs_checked == 36
    assert exact_identity_sizes == {1}
    assert failed_identity_sizes == set(range(2, 9))

    result = {
        "record_id": "reddit_askmath_xvs5on",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No counterexample witness is certified. For every checked labeled set X with 2 through 8 elements, every available pair (f,g) fails g o f = identity_X, but the supplied data does not determine whether any such X is contractible.",
        "refutation_explanation": "The source quote specifies functions and exact equality of composites, but supplies no definition or finite test for contractibility. The bounded sweep can decide the stated function equations: among nonempty checked sets, both composites are identities exactly when X has one element. It cannot decide the additional contractibility condition needed to turn an equality failure into a counterexample.",
        "search_space": "All 36 pairs (f,g) for labeled finite sets X={0,...,n-1} with 1<=n<=8, codomain {0}: the unique function f:X->{0} and each of the n functions g:{0}->X. The case n=0 was also checked and has no function g:{0}->X."
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
