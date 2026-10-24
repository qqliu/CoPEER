"""Under the stated convention R^0 = R, the proof claims that R^(n+m) = R^n composed with R^m for natural numbers n and m."""

import json


def compose(relation_left, relation_right):
    return frozenset(
        (x, z)
        for x, y_left in relation_left
        for y_right, z in relation_right
        if y_left == y_right
    )


def main():
    points = (0, 1)
    ordered_pairs = tuple((x, y) for x in points for y in points)
    first_witness = None

    for mask in range(1 << len(ordered_pairs)):
        relation = frozenset(
            ordered_pairs[index]
            for index in range(len(ordered_pairs))
            if mask & (1 << index)
        )
        # For n=m=0, the supplied convention determines both sides:
        # R^(0+0) = R^0 = R and R^0 composed with R^0 = R composed with R.
        left_side = relation
        right_side = compose(relation, relation)
        if left_side != right_side and first_witness is None:
            first_witness = relation

    expected_witness = frozenset(((0, 1),))
    if first_witness != expected_witness:
        raise AssertionError("unexpected deterministic search result")

    result = {
        "record_id": "proofwiki_24804__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "On X={0,1}, take R={(0,1)} and n=m=0. Then R^(0+0)=R={(0,1)}, but R^0 composed with R^0=R composed with R=empty.",
        "refutation_explanation": "The stated convention makes R^0=R. For R={(0,1)}, there is no intermediate element y with (x,y) in R and (y,z) in R, so R composed with R is empty and therefore differs from R. Thus the claimed equality fails at n=m=0.",
        "search_space": "All 16 binary relations R contained in {0,1}x{0,1}, in increasing four-bit mask order with ordered pairs ((0,0),(0,1),(1,0),(1,1)), were swept for the fixed natural-number pair (n,m)=(0,0).",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
