"""The asserted identity f(x) = f(-x) + (-f(x)) holds for an arbitrary function on a domain closed under negation."""

import itertools
import json


def main():
    domain = (0,)
    values = (0, 1, -1)
    first_witness = None
    functions_checked = 0

    assert all(-x in domain for x in domain)

    for output_tuple in itertools.product(values, repeat=len(domain)):
        function = dict(zip(domain, output_tuple))
        functions_checked += 1
        for x in domain:
            lhs = function[x]
            rhs = function[-x] + (-function[x])
            if lhs != rhs and first_witness is None:
                first_witness = (x, lhs, rhs, output_tuple)

    assert functions_checked == 3
    assert first_witness == (0, 1, 0, (1,))

    result = {
        "record_id": "reddit_learnmath_dm6itc",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Witness: domain D={0} (closed under negation), with integer-valued f(0)=1. At x=0, f(x)=1 but f(-x)+(-f(x))=f(0)-f(0)=0.",
        "refutation_explanation": "Since 1 is not equal to 0, this function violates the asserted identity; therefore it does not hold for an arbitrary function.",
        "search_space": "All 3 integer-valued functions on D={0} whose sole value is in the fixed ordered set (0, 1, -1), each checked at x=0. Every function in this finite space was examined."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
