r"""The stated assumptions that X is nonempty and bounded above and a > 0 suffice for the real suprema sup f(x) and sup(af(x)) to exist and satisfy sup(af(x)) = a sup f(x)."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_15g4y45"
VERDICT = "CONFIRMED"
NOTES = "Confirmed exactly: for every positive integer n, x_n=-1/n belongs to X, x_n<=0, and x_n f(x_n)=-1 gives f(x_n)=n. Thus X is nonempty and bounded above, while both f(X) and a f(X) contain every positive integer and are unbounded above, so neither real supremum exists. This is a substantive missing-hypothesis error, not plainly a typo."


def point_and_value(n):
    if type(n) is not int or n <= 0:
        raise AssertionError("n must be a positive integer")
    x_n = Fraction(-1, n)
    value = Fraction(n, 1)
    # Since x_n is nonzero and x_n*value=-1, value is exactly -1/x_n.
    if x_n >= 0 or x_n * value != Fraction(-1, 1):
        raise AssertionError("witness identity failed")
    return x_n, value


def value_above_integer(k):
    if type(k) is not int:
        raise AssertionError("integer bound required")
    n = 1 if k < 0 else k + 1
    x_n, value = point_and_value(n)
    if value <= Fraction(k, 1):
        raise AssertionError("unboundedness certificate failed")
    return x_n, value


def main():
    a = Fraction(1, 1)
    if a <= 0:
        raise AssertionError("a is not positive")

    x_one, value_one = point_and_value(1)
    if x_one != Fraction(-1, 1) or value_one != Fraction(1, 1):
        raise AssertionError("X is not witnessed as nonempty")

    # point_and_value proves the formula for an arbitrary positive integer n:
    # every point -1/n is at most 0, so 0 bounds X above, and f(-1/n)=n.
    # value_above_integer is a uniform certificate above any integer k.
    # By the Archimedean property of the reals, this makes f(X) unbounded above.
    # Multiplication by a=1 leaves every certified value unchanged.
    for k in (-9, 0, 1, 23, 104):
        _, value = value_above_integer(k)
        if a * value != value:
            raise AssertionError("scaled-value identity failed")

    payload = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
