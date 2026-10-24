r"""The displayed unweighted ℓ² formula defines a metric d₂ on all of the Hilbert cube I^ω."""

import json

RECORD_ID = "proofwiki_113885__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = (
    "The witness is valid: both constant endpoint sequences belong to I^ω, "
    "while their exact N-term squared-distance sum is N and hence unbounded. "
    "The displayed formula therefore is not real-valued on all pairs and "
    "cannot be a metric on all of I^ω. This is a substantive mathematical "
    "error as written, not plainly a typo."
)


def x(coordinate):
    assert isinstance(coordinate, int) and coordinate > 0
    return 0


def y(coordinate):
    assert isinstance(coordinate, int) and coordinate > 0
    return 1


def in_unit_interval(value):
    return 0 <= value <= 1


def squared_term(coordinate):
    difference = x(coordinate) - y(coordinate)
    return difference * difference


def partial_sum(length):
    assert isinstance(length, int) and length > 0
    total = 0
    for coordinate in range(1, length + 1):
        total += squared_term(coordinate)
    return total


def main():
    # The defining coordinate rules show that both sequences are in [0,1]^N.
    for coordinate in range(1, 33):
        assert in_unit_interval(x(coordinate))
        assert in_unit_interval(y(coordinate))
        assert squared_term(coordinate) == 1

    # Independently derive and check the exact finite-sum identity S_N = N.
    for length in range(1, 65):
        assert partial_sum(length) == length

    # For every nonnegative integer bound B, the constructive choice N=B+1
    # gives S_N=N>B. This exact identity certifies unboundedness of the series.
    def exceeds_bound(bound):
        assert isinstance(bound, int) and bound >= 0
        length = bound + 1
        return partial_sum(length) == length and length > bound

    for bound in (0, 1, 2, 7, 31, 128):
        assert exceeds_bound(bound)

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
