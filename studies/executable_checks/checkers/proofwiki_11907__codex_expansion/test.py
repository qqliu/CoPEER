"""Every element τ of Gal(F/K) fixes F pointwise."""

import itertools
import json

RECORD_ID = "proofwiki_11907__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Let K=GF(2) and F=GF(4)=GF(2)[a]/(a^2+a+1). With elements encoded as 0, 1, a, 1+a, the function tau=(0,1,3,2) fixes 0 and 1 and is a field automorphism, but tau(a)=1+a != a."
REFUTATION_EXPLANATION = "The exhaustive sweep finds the nonidentity Frobenius automorphism tau(x)=x^2 in Gal(GF(4)/GF(2)). Since it does not fix a, it does not fix F pointwise, contradicting the universal claim."
SEARCH_SPACE = "All 4^4=256 functions GF(4)->GF(4), in lexicographic order of their four-value tables, tested for bijectivity, preservation of addition and multiplication, and pointwise fixation of the subfield GF(2)."


def add(x, y):
    return x ^ y


def multiply(x, y):
    # Elements are coefficient bit pairs for c0 + c1*a, where a^2=a+1.
    x0, x1 = x & 1, (x >> 1) & 1
    y0, y1 = y & 1, (y >> 1) & 1
    constant = (x0 * y0) ^ (x1 * y1)
    linear = (x0 * y1) ^ (x1 * y0) ^ (x1 * y1)
    return constant | (linear << 1)


def is_galois_element(table):
    if len(set(table)) != 4:
        return False
    if table[0] != 0 or table[1] != 1:
        return False
    for x in range(4):
        for y in range(4):
            if table[add(x, y)] != add(table[x], table[y]):
                return False
            if table[multiply(x, y)] != multiply(table[x], table[y]):
                return False
    return True


def main():
    witnesses = []
    functions_checked = 0
    for table in itertools.product(range(4), repeat=4):
        functions_checked += 1
        if is_galois_element(table) and any(table[x] != x for x in range(4)):
            witnesses.append(table)

    assert functions_checked == 256
    assert witnesses == [(0, 1, 3, 2)]

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
