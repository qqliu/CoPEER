r"""For an arbitrary ring homomorphism φ:R→S, if V is an ideal of R containing ker φ, then φ(V) is an ideal of the full codomain S."""

import json

RECORD_ID = "proofwiki_9004__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = "The witness is valid: the diagonal unital homomorphism has zero kernel, V=R, and (1,0)·(1,1)=(1,0) lies outside φ(V). The refuted statement is substantive rather than plainly a typo; it is missing a surjectivity/epimorphism hypothesis (or should concern an ideal of φ(R))."

R = (0, 1)
S = ((0, 0), (0, 1), (1, 0), (1, 1))


def r_add(x, y):
    return (x + y) % 2


def r_mul(x, y):
    return (x * y) % 2


def s_add(x, y):
    return ((x[0] + y[0]) % 2, (x[1] + y[1]) % 2)


def s_mul(x, y):
    return ((x[0] * y[0]) % 2, (x[1] * y[1]) % 2)


def phi(x):
    return (x, x)


def satisfies_ring_laws(carrier, add, mul, zero, one):
    members = set(carrier)
    for x in carrier:
        if add(x, zero) != x or add(zero, x) != x:
            return False
        if mul(x, one) != x or mul(one, x) != x:
            return False
        if not any(add(x, y) == zero and add(y, x) == zero for y in carrier):
            return False
        for y in carrier:
            if add(x, y) not in members or mul(x, y) not in members:
                return False
            if add(x, y) != add(y, x):
                return False
            for z in carrier:
                if add(add(x, y), z) != add(x, add(y, z)):
                    return False
                if mul(mul(x, y), z) != mul(x, mul(y, z)):
                    return False
                if mul(x, add(y, z)) != add(mul(x, y), mul(x, z)):
                    return False
                if mul(add(x, y), z) != add(mul(x, z), mul(y, z)):
                    return False
    return True


def is_two_sided_ideal(subset, carrier, add, mul, zero):
    part = set(subset)
    if zero not in part or not part.issubset(set(carrier)):
        return False
    for x in part:
        if not any(add(x, y) == zero and add(y, x) == zero for y in part):
            return False
        for y in part:
            if add(x, y) not in part:
                return False
        for scalar in carrier:
            if mul(scalar, x) not in part or mul(x, scalar) not in part:
                return False
    return True


def is_unital_homomorphism():
    if phi(0) != (0, 0) or phi(1) != (1, 1):
        return False
    for x in R:
        if phi(x) not in set(S):
            return False
        for y in R:
            if phi(r_add(x, y)) != s_add(phi(x), phi(y)):
                return False
            if phi(r_mul(x, y)) != s_mul(phi(x), phi(y)):
                return False
    return True


def main():
    v = set(R)
    kernel = {x for x in R if phi(x) == (0, 0)}
    image = {phi(x) for x in v}
    scalar = (1, 0)
    image_one = phi(1)
    product = s_mul(scalar, image_one)

    established = all((
        satisfies_ring_laws(R, r_add, r_mul, 0, 1),
        satisfies_ring_laws(S, s_add, s_mul, (0, 0), (1, 1)),
        is_unital_homomorphism(),
        is_two_sided_ideal(v, R, r_add, r_mul, 0),
        kernel == {0},
        kernel.issubset(v),
        image == {(0, 0), (1, 1)},
        scalar in set(S),
        image_one in image,
        product == (1, 0),
        product not in image,
        not is_two_sided_ideal(image, S, s_add, s_mul, (0, 0)),
    ))

    verdict = VERDICT if established else "REFUTED_WITNESS_INVALID"
    notes = NOTES if established else "The independent exact recomputation did not validate the proposed witness; the substantive claim was therefore not refuted by it."
    print(json.dumps({"record_id": RECORD_ID, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
