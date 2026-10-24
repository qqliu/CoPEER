r"""S = \binom 02 + 19 \cdot \binom 62 + \binom 52 + 99 \cdot \binom 02 = 310."""

import json

RECORD_ID = "mse_4124583__ans4124608"
CONFIRMED_NOTES = "Independent exact recomputation gives C(0,2)=0, C(6,2)=15, C(5,2)=10, hence S=0+19*15+10+99*0=295, not 310. The refuted statement is substantive as a false closed arithmetic equality; the permitted evidence does not establish it as plainly a typo."


def binomial(n, k):
    if n < 0 or k < 0:
        raise ValueError("arguments must be nonnegative")
    if k > n:
        return 0
    selected = k if k <= n - k else n - k
    value = 1
    index = 1
    while index <= selected:
        product = value * (n - selected + index)
        if product % index != 0:
            raise ArithmeticError("nonintegral recurrence")
        value = product // index
        index += 1
    return value


def main():
    c_zero_two = binomial(0, 2)
    c_six_two = binomial(6, 2)
    c_five_two = binomial(5, 2)
    c_zero_two_repeat = binomial(0, 2)
    total = c_zero_two + 19 * c_six_two + c_five_two + 99 * c_zero_two_repeat
    established = (
        (c_zero_two, c_six_two, c_five_two, c_zero_two_repeat) == (0, 15, 10, 0)
        and total == 295
        and total != 310
    )
    if established:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "Independent exact recomputation did not establish the reported refutation; the typo classification is therefore unresolved."
    print(json.dumps({"record_id": RECORD_ID, "verdict": verdict, "notes": notes}, separators=(",", ":")))


if __name__ == "__main__":
    main()
