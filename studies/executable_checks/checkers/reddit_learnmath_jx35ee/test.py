"""Method 1 claims that the derivative of e^[(-x)^(2)] is -2e^(-2x)."""

import json

RECORD_ID = "reddit_learnmath_jx35ee"
WITNESS_DESCRIPTION = "x = 0: the exact derivative of e^[(-x)^(2)] is 0, while the claimed value -2e^(-2x) is -2."
REFUTATION_EXPLANATION = "At x = 0, (-x)^2 has derivative 2x = 0 and e^0 = 1, so the chain rule gives 0; the claimed formula gives -2e^0 = -2. Since 0 != -2, this is a counterexample."
SEARCH_SPACE = "All integer x in range(0, 1), i.e. the singleton {0}; evaluated in fixed increasing order using exact integer arithmetic and e^0 = 1."


def exp_of_zero(exponent):
    if exponent != 0:
        raise ValueError("This exact bounded search only evaluates e at exponent zero.")
    return 1


def actual_derivative(x):
    exponent = (-x) ** 2
    exponent_derivative = 2 * x
    return exp_of_zero(exponent) * exponent_derivative


def claimed_derivative(x):
    exponent = -2 * x
    return -2 * exp_of_zero(exponent)


def main():
    witness = None
    for x in range(0, 1):
        if actual_derivative(x) != claimed_derivative(x):
            witness = x
            break

    if witness != 0:
        raise AssertionError("The exhaustive singleton search must find x = 0.")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
