"""For all real a,b and all z>0, if a<=b+z, then a<=b."""

import itertools
import json


def main():
    a_values = (-1, 0, 1)
    b_values = (-1, 0, 1)
    z_values = (1, 2)
    first_witness = None

    for a, b, z in itertools.product(a_values, b_values, z_values):
        if z > 0 and a <= b + z and not a <= b:
            if first_witness is None:
                first_witness = (a, b, z)

    assert first_witness == (0, -1, 1)
    result = {
        "record_id": "reddit_math_1flfslo",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a=0, b=-1, z=1.",
        "refutation_explanation": "Here z>0 and a<=b+z because 0<=-1+1=0, but a<=b is false because 0<=-1 is false.",
        "search_space": "All 18 ordered triples (a,b,z) in {-1,0,1} x {-1,0,1} x {1,2}, evaluated in lexicographic product order using exact integer arithmetic."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
