r"""Defined $h: \{0\} \to \{1\}$ as $h(1)=0$.
It follows that $h(P) =  $\{1^p : p \text{ is a primes}\}$ and therefore is irregular."""

import itertools
import json


def main():
    domain = (0,)
    codomain = (1,)
    functions = []
    for outputs in itertools.product(codomain, repeat=len(domain)):
        functions.append(dict(zip(domain, outputs)))

    assert len(functions) == 1
    assert functions[0] == {0: 1}
    assert all(1 not in function for function in functions)
    assert 0 not in codomain

    result = {
        "record_id": "SE_cs_42947__q",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The unique function h:{0}->{1}, namely h(0)=1, is a witness: h(1) is undefined, so it cannot satisfy h(1)=0.",
        "refutation_explanation": "The asserted definition is impossible. Since 1 is not in the domain {0}, h(1) is undefined; moreover, 0 is not in the codomain {1}. Thus no function of the stated type can obey h(1)=0, so the subsequent conclusion about h(P) cannot follow from that definition.",
        "search_space": "Exhaustively enumerated all functions from the one-element domain {0} to the one-element codomain {1}: exactly 1 function, h(0)=1."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
