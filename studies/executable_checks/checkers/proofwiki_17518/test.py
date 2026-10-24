"""Proof 2's injectivity step asserts, for arbitrary a in S, that for all x_1, x_2 in S, (x_1, a circ x_1) in lambda_a AND (x_2, a circ x_2) in lambda_a implies x_1 = x_2. Since (x, a circ x) belongs to lambda_a for EVERY x by the definition of lambda_a, the antecedent is universally satisfied, so the stated claim literally asserts that S has at most one element. The preceding chain x_1 = a * lambda_a(x_1) = a * lambda_a(x_2) = x_2 uses an unjustified middle equality (many-to-one-ness of lambda_a only gives single-valuedness at a fixed argument, not lambda_a(x_1) = lambda_a(x_2))."""

import itertools
import json

RECORD_ID = "proofwiki_17518"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "S={0,1}, a=0, circ is the constant-zero operation, "
    "lambda_0={(0,0),(1,0)}, x_1=0, and x_2=1."
)
REFUTATION_EXPLANATION = (
    "Both (0, 0 circ 0)=(0,0) and (1, 0 circ 1)=(1,0) belong to "
    "lambda_0, so the antecedent is true, while the conclusion x_1=x_2 "
    "is false because 0 != 1."
)
SEARCH_SPACE = (
    "Exhaustively swept carrier sizes n in {1,2}; for S={0,...,n-1}, "
    "every one of the n^(n^2) binary operation tables, every a in S, "
    "and every ordered pair (x_1,x_2) in S^2, with lambda_a defined as "
    "exactly {(x,a circ x): x in S}. This is 33 pointed algebras and 129 "
    "ordered-pair tests, in fixed lexicographic order."
)


def search():
    first_witness = None
    pointed_algebras = 0
    pair_tests = 0

    for n in (1, 2):
        carrier = tuple(range(n))
        table_positions = n * n
        for table in itertools.product(carrier, repeat=table_positions):
            def circ(left, right, operation=table, size=n):
                return operation[left * size + right]

            for a in carrier:
                pointed_algebras += 1
                lambda_a = frozenset((x, circ(a, x)) for x in carrier)
                for x_1 in carrier:
                    for x_2 in carrier:
                        pair_tests += 1
                        antecedent = (
                            (x_1, circ(a, x_1)) in lambda_a
                            and (x_2, circ(a, x_2)) in lambda_a
                        )
                        if antecedent and x_1 != x_2 and first_witness is None:
                            first_witness = (
                                n,
                                table,
                                a,
                                lambda_a,
                                x_1,
                                x_2,
                            )

    expected = (
        2,
        (0, 0, 0, 0),
        0,
        frozenset(((0, 0), (1, 0))),
        0,
        1,
    )
    if pointed_algebras != 33 or pair_tests != 129:
        raise RuntimeError("finite search was not completed")
    if first_witness != expected:
        raise RuntimeError("unexpected first counterexample")


search()
print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}))
