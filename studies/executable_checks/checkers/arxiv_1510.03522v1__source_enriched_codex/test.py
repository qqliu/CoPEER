"""For the stated H-valued evolution on the mean-zero Hilbert space H, the nonlinear drift N(u)=u-u^3 is H-valued for u in H."""

import itertools
import json


def drift(x):
    return x - x ** 3


def main():
    values = range(-2, 3)
    visited = 0
    proxy_failures = []

    for triple in itertools.product(values, repeat=3):
        visited += 1
        if sum(triple) == 0:
            image = tuple(drift(x) for x in triple)
            if sum(image) != 0:
                proxy_failures.append((triple, image))

    assert visited == 125
    assert proxy_failures[0] == ((-2, 1, 1), (6, 0, 0))

    result = {
        "record_id": "arxiv_1510.03522v1__source_enriched_codex",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No claim-level witness can be certified. The finite proxy sweep finds (-2, 1, 1), whose entries sum to zero while their componentwise drift values (6, 0, 0) sum to 6, but the supplied data do not establish that this proxy represents an element of H.",
        "refutation_explanation": "The quote defines N(u)=u-u^3 but does not define H, its elements, or its membership criterion. Consequently, a finite-vector failure of mean preservation is illustrative only and cannot establish that some u belongs to the stated H while N(u) does not.",
        "search_space": "All 125 ordered integer triples in {-2,-1,0,1,2}^3 were visited in lexicographic product order; for every triple with coordinate sum zero, the componentwise integer drift x-x^3 was tested for coordinate sum zero."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
