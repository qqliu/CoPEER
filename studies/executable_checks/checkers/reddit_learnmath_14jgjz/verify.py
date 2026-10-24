r"""The condition |A| < |G| suffices to apply strong induction on |G| to G/A."""

import json

RECORD_ID = "reddit_learnmath_14jgjz"
CONFIRMED_NOTES = "Exact reconstruction confirms the substantive counterexample, not a plain typo: for C_2 with the trivial subgroup A={0}, |A|=1<2=|G|, but G/A has two cosets, so |G/A|=|G| and strong induction on |G| cannot be applied to G/A."
INVALID_NOTES = "The reported witness could not be validated exactly; the alleged refutation is therefore invalid."


def add_mod_two(left, right):
    total = left + right
    if total >= 2:
        total -= 2
    return total


def main():
    group = (0, 1)
    subgroup = frozenset((0,))

    identity_valid = all(add_mod_two(0, element) == element for element in group)
    closure_valid = all(
        add_mod_two(left, right) in subgroup
        for left in subgroup
        for right in subgroup
    )
    inverse_valid = all(
        any(add_mod_two(element, candidate) == 0 for candidate in subgroup)
        for element in subgroup
    )

    quotient = frozenset(
        frozenset(add_mod_two(representative, element) for element in subgroup)
        for representative in group
    )

    premise = len(subgroup) < len(group)
    induction_applies_to_quotient = len(quotient) < len(group)
    witness_valid = (
        len(group) == 2
        and subgroup == frozenset((0,))
        and identity_valid
        and closure_valid
        and inverse_valid
        and premise
        and quotient == frozenset((frozenset((0,)), frozenset((1,))))
        and len(quotient) == len(group)
        and not induction_applies_to_quotient
    )

    result = {
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED" if witness_valid else "REFUTED_WITNESS_INVALID",
        "notes": CONFIRMED_NOTES if witness_valid else INVALID_NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
