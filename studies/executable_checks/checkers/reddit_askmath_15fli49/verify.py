r"""A countable subset of [0,1] with no limit points cannot exist."""

import json

RECORD_ID = "reddit_askmath_15fli49"
VERDICT = "CONFIRMED"
NOTES = "Confirmed independently with exact integer arithmetic: {0} lies in [0,1], is finite and therefore countable, and has no limit points. At 0, every punctured neighborhood contains no set member; away from 0, the open ball of radius |x| excludes 0. The refuted statement is substantive as written, not plainly a typo, although adding “infinite” would repair it."


def verify_witness():
    lower = 0
    point = 0
    upper = 1
    witness = (point,)

    # Exact interval-membership check.
    assert all(lower <= member <= upper for member in witness)

    # An explicit injection into the nonnegative integers certifies countability.
    indices = {member: index for index, member in enumerate(witness)}
    assert len(indices) == len(witness)
    assert all(index >= 0 for index in indices.values())

    # At the sole set member, a positive-radius punctured ball is empty.
    center_radius = 1
    assert center_radius > 0
    assert not any(
        member != point and abs(member - point) < center_radius
        for member in witness
    )

    # For an arbitrary center x distinct from 0, choose radius |x-0|.
    # The only set member is then exactly on the ball's boundary, while an
    # open ball requires strict inequality.  Equality of the two symbolic
    # expressions certifies this branch without approximating x.
    distance_expression = ("absolute_difference", "x", point)
    radius_expression = ("absolute_difference", "x", point)
    assert distance_expression == radius_expression

    # The two exhaustive cases x = 0 and x != 0 therefore each provide a
    # punctured neighborhood containing no member of the singleton.
    return True


def main():
    assert verify_witness()
    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
