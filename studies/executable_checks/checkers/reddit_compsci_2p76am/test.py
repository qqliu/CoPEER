"""If L1 polynomial-time many-one reduces to an NP-complete problem, then that NP-complete problem polynomial-time many-one reduces to L1."""

import itertools
import json

RECORD_ID = "reddit_compsci_2p76am"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take L1 to be the empty language. For the NP-complete language A in the "
    "premise, choose a no-instance n not in A and use the constant reduction "
    "f(x)=n."
)
REFUTATION_EXPLANATION = (
    "The forward map is polynomial-time and valid because both x in L1 and "
    "f(x) in A are false for every x. An NP-complete language A also has a "
    "yes-instance y. Any alleged reduction g from A to the empty language "
    "would require y in A if and only if g(y) is in the empty language, whose "
    "right side is false, a contradiction."
)
SEARCH_SPACE = (
    "Exhaustively enumerated all 4 Boolean membership signatures for "
    "distinguished inputs (n,y), both possible constant images for a forward "
    "map, and all 4 functions from the two-input carrier to itself for each "
    "signature/image pair. The witness uses the signature A(n)=false, "
    "A(y)=true and L1 empty; the finite sweep checks the "
    "membership-equivalence obstruction, while the explanation proves it for "
    "the full languages."
)

carrier = (0, 1)
l1_membership = (False, False)
certificates = []

for a_membership in itertools.product((False, True), repeat=2):
    for constant_image in carrier:
        forward_ok = all(
            l1_membership[x] == a_membership[constant_image]
            for x in carrier
        )
        reverse_exists = False
        for reverse_map in itertools.product(carrier, repeat=2):
            reverse_ok = all(
                a_membership[x] == l1_membership[reverse_map[x]]
                for x in carrier
            )
            if reverse_ok:
                reverse_exists = True
        if (
            a_membership == (False, True)
            and forward_ok
            and not reverse_exists
        ):
            certificates.append((a_membership, constant_image))

if certificates != [((False, True), 0)]:
    raise AssertionError("finite certificate sweep produced an unexpected result")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
