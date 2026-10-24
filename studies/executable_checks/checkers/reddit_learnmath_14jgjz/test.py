"""The condition |A| < |G| suffices to apply strong induction on |G| to G/A."""

import json


def subgroup(n, d):
    step = n // d
    return frozenset((k * step) % n for k in range(d))


def quotient_cosets(n, a):
    return frozenset(
        frozenset((x + element) % n for element in a)
        for x in range(n)
    )


def main():
    witnesses = []
    for n in range(2, 33):
        for d in range(1, n + 1):
            if n % d != 0:
                continue
            a = subgroup(n, d)
            cosets = quotient_cosets(n, a)
            if len(a) < n and len(cosets) >= n:
                witnesses.append((n, d, len(cosets)))

    assert witnesses
    n, d, quotient_order = witnesses[0]
    assert (n, d, quotient_order) == (2, 1, 2)

    result = {
        "record_id": "reddit_learnmath_14jgjz",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Let G=C_2 and let A={0}, the trivial subgroup. Then |A|=1<2=|G|, while G/A has 2 cosets and hence |G/A|=2=|G|.",
        "refutation_explanation": "Strong induction on |G| applies the inductive hypothesis only to strictly smaller sizes. In this witness the stated condition holds, but |G/A| is not strictly smaller than |G|, so that condition alone does not suffice to apply the inductive hypothesis to G/A.",
        "search_space": "All pairs (C_n,A_d) with 2<=n<=32 and d a positive divisor of n, where C_n is represented by residues modulo n and A_d={k(n/d) mod n: 0<=k<d}; every such pair was tested in increasing (n,d) order by explicitly constructing A_d and all of its cosets."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
