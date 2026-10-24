"""After choosing merely another subgroup H of order p, the proof may treat G/H as a quotient group and apply the induction hypothesis to it."""

import itertools
import json

ELEMENTS = tuple((i, j) for i in range(4) for j in range(2))
IDENTITY = (0, 0)


def mul(left, right):
    i, j = left
    k, ell = right
    signed_k = k if j == 0 else -k
    return ((i + signed_k) % 4, (j + ell) % 2)


def inverse(element):
    candidates = tuple(
        candidate
        for candidate in ELEMENTS
        if mul(element, candidate) == IDENTITY
        and mul(candidate, element) == IDENTITY
    )
    if len(candidates) != 1:
        raise AssertionError("inverse is not unique")
    return candidates[0]


def is_subgroup(subset):
    if IDENTITY not in subset:
        return False
    for a in subset:
        if inverse(a) not in subset:
            return False
        for b in subset:
            if mul(a, b) not in subset:
                return False
    return True


def is_normal(subgroup):
    for g in ELEMENTS:
        g_inverse = inverse(g)
        for h in subgroup:
            if mul(mul(g, h), g_inverse) not in subgroup:
                return False
    return True


def left_coset(representative, subgroup):
    return frozenset(mul(representative, h) for h in subgroup)


# Exhaustively certify that the displayed operation is a group operation.
for g in ELEMENTS:
    if mul(IDENTITY, g) != g or mul(g, IDENTITY) != g:
        raise AssertionError("identity law failed")
    inverse(g)
for a, b, c in itertools.product(ELEMENTS, repeat=3):
    if mul(mul(a, b), c) != mul(a, mul(b, c)):
        raise AssertionError("associativity failed")

# Exhaustively enumerate every subset in increasing bit-mask order.
subgroups = []
for mask in range(1 << len(ELEMENTS)):
    subset = frozenset(
        ELEMENTS[index]
        for index in range(len(ELEMENTS))
        if mask & (1 << index)
    )
    if is_subgroup(subset):
        subgroups.append(subset)

order_two_subgroups = tuple(
    subgroup for subgroup in subgroups if len(subgroup) == 2
)
if len(order_two_subgroups) != 5:
    raise AssertionError("unexpected order-2 subgroup count")

# Check every ordered pair, and for every qualifying pair sweep all 8^4
# choices of representatives to test whether coset multiplication is well-defined.
qualifying_pair_count = 0
counterexample_pairs = []
for n_subgroup in order_two_subgroups:
    for h_subgroup in order_two_subgroups:
        qualifies = (
            is_normal(n_subgroup)
            and n_subgroup.intersection(h_subgroup) == frozenset((IDENTITY,))
            and not is_normal(h_subgroup)
        )
        if not qualifies:
            continue
        qualifying_pair_count += 1
        first_ambiguity = None
        for a, a_prime, b, b_prime in itertools.product(ELEMENTS, repeat=4):
            same_inputs = (
                left_coset(a, h_subgroup) == left_coset(a_prime, h_subgroup)
                and left_coset(b, h_subgroup) == left_coset(b_prime, h_subgroup)
            )
            different_outputs = (
                left_coset(mul(a, b), h_subgroup)
                != left_coset(mul(a_prime, b_prime), h_subgroup)
            )
            if same_inputs and different_outputs and first_ambiguity is None:
                first_ambiguity = (a, a_prime, b, b_prime)
        if first_ambiguity is not None:
            counterexample_pairs.append(
                (n_subgroup, h_subgroup, first_ambiguity)
            )

if qualifying_pair_count != 4 or len(counterexample_pairs) != 4:
    raise AssertionError("the exhaustive search did not find the expected pairs")

expected_n = frozenset(((0, 0), (2, 0)))
expected_h = frozenset(((0, 0), (0, 1)))
if not any(
    n_subgroup == expected_n and h_subgroup == expected_h
    for n_subgroup, h_subgroup, ambiguity in counterexample_pairs
):
    raise AssertionError("the stated witness was not found")

# Explicitly verify the stated conjugation and representative ambiguity.
r = (1, 0)
s = (0, 1)
r_squared_s = (2, 1)
if mul(mul(r, s), inverse(r)) != r_squared_s or r_squared_s in expected_h:
    raise AssertionError("the stated failure of normality was not verified")
if left_coset(IDENTITY, expected_h) != left_coset(s, expected_h):
    raise AssertionError("e and s should represent the same coset")
if left_coset(mul(IDENTITY, r), expected_h) == left_coset(mul(s, r), expected_h):
    raise AssertionError("the stated coset-product ambiguity was not verified")

result = {
    "record_id": "arxiv_2107.00735v2__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": "G=D8={r^i s^j: 0<=i<4, 0<=j<2}, p=2, N=<r^2>, and H=<s>. Both N and H have order 2, N is normal, and N intersection H={e}, but H is not normal.",
    "refutation_explanation": "Conjugation by r sends s to r^2 s, which is not in H. Consequently multiplication of left cosets is not well-defined: eH=sH=H and rH=rH, but (er)H=rH={r,rs} whereas (sr)H={r^3s,r^3}. Hence G/H is not a quotient group under induced coset multiplication, so merely choosing H does not justify induction on G/H as a group.",
    "search_space": "The program exhaustively checks the group laws on the explicitly defined 8-element D8 (including all 8^3=512 associativity triples), tests all 2^8=256 subsets for the subgroup axioms, tests all 5^2=25 ordered pairs (N,H) of its order-2 subgroups, and tests all 8^4=4096 ordered representative quadruples for each of the four pairs satisfying N normal, N intersection H={e}, and H nonnormal (16384 quadruples total).",
}
print(json.dumps(result, separators=(",", ":")))
