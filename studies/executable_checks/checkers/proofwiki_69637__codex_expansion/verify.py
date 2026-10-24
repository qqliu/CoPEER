"""The stated subset P has a smallest element merely because the ambient set is well-ordered."""

import json

RECORD_ID = "proofwiki_69637__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = (
    "The empty-set witness is valid: the empty set is a subset of every ambient "
    "set and cannot have a smallest element because it has no elements. This is "
    "a substantive missing nonemptiness hypothesis, not merely a typographical error."
)


def is_subset(candidate, ambient_membership):
    for element in candidate:
        if not ambient_membership(element):
            return False
    return True


def arbitrary_ambient_membership(_element):
    raise AssertionError("membership must not be queried for the empty candidate")


def main():
    candidate_p = frozenset()

    inclusion_holds = is_subset(candidate_p, arbitrary_ambient_membership)
    has_an_element_that_could_be_smallest = any(True for _ in candidate_p)
    witness_valid = inclusion_holds and not has_an_element_that_could_be_smallest

    if not witness_valid:
        raise AssertionError("independent verification failed")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
