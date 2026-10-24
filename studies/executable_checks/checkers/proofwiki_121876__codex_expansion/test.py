"""The assumed commutative topological semigroup has an identity element 0_G."""

import itertools
import json

RECORD_ID = "proofwiki_121876__codex_expansion"
WITNESS_DESCRIPTION = (
    "Let G={0,1} have the discrete topology and define x+y=0 for every x,y "
    "in G. This operation is associative and commutative, and it is continuous "
    "because the topology is discrete. Neither 0 nor 1 is an identity: "
    "0+1=0 != 1 and 1+1=0 != 1."
)
REFUTATION_EXPLANATION = (
    "This is a commutative topological semigroup with no identity element, so "
    "being a commutative topological semigroup does not imply the existence of "
    "0_G. The source quote introduces 0_G as an identity but does not derive "
    "its existence from the semigroup assumptions."
)
SEARCH_SPACE = (
    "All 16 binary operations G x G -> G on the labeled two-element carrier "
    "G={0,1}, in lexicographic table order; every operation was tested for "
    "associativity, commutativity, continuity for the discrete topology, and "
    "existence of a two-sided identity."
)

G = (0, 1)
PAIRS = tuple(itertools.product(G, repeat=2))
DISCRETE_PRODUCT_TOPOLOGY = frozenset(range(1 << len(PAIRS)))


def add(table, x, y):
    return table[2 * x + y]


def is_associative(table):
    return all(
        add(table, add(table, x, y), z) == add(table, x, add(table, y, z))
        for x, y, z in itertools.product(G, repeat=3)
    )


def is_commutative(table):
    return all(add(table, x, y) == add(table, y, x) for x, y in PAIRS)


def is_continuous_for_discrete_topology(table):
    for open_mask in range(1 << len(G)):
        preimage_mask = 0
        for index, (x, y) in enumerate(PAIRS):
            if open_mask & (1 << add(table, x, y)):
                preimage_mask |= 1 << index
        if preimage_mask not in DISCRETE_PRODUCT_TOPOLOGY:
            return False
    return True


def identities(table):
    return tuple(
        e
        for e in G
        if all(add(table, e, x) == x and add(table, x, e) == x for x in G)
    )


def main():
    counterexamples = []
    operations_tested = 0
    for table in itertools.product(G, repeat=len(PAIRS)):
        operations_tested += 1
        if (
            is_associative(table)
            and is_commutative(table)
            and is_continuous_for_discrete_topology(table)
            and not identities(table)
        ):
            counterexamples.append(table)

    assert operations_tested == 16
    assert counterexamples
    assert counterexamples[0] == (0, 0, 0, 0)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
