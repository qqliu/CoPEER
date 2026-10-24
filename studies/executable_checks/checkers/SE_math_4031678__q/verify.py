r"""$${100\choose 50}\cdot 1\leq 100\cdot {99\choose 49}\implies 51\leq 50,$$"""

import json


def binomial(n, k):
    if n < 0 or k < 0 or k > n:
        raise ValueError("invalid binomial arguments")
    reduced_k = min(k, n - k)
    result = 1
    for index in range(1, reduced_k + 1):
        product = result * (n - reduced_k + index)
        if product % index != 0:
            raise ArithmeticError("nonintegral intermediate result")
        result = product // index
    return result


left = binomial(100, 50)
right = 100 * binomial(99, 49)
reported_left = 100891344545564193334812497256
reported_right = 5044567227278209666740624862800
valid = (
    left == reported_left
    and right == reported_right
    and left <= right
    and not (51 <= 50)
)

if valid:
    verdict = "CONFIRMED"
    notes = ("Exact recomputation confirms the reported witness: C(100,50) = "
             "100891344545564193334812497256 and 100*C(99,49) = "
             "5044567227278209666740624862800, so the antecedent is true while "
             "51 <= 50 is false. The refuted implication is substantive as "
             "written; the permitted evidence gives no basis to classify it "
             "as a plain typo.")
else:
    verdict = "CANNOT_REPRODUCE"
    notes = ("Exact recomputation did not validate the reported witness. The "
             "refuted implication is substantive as written; the permitted "
             "evidence gives no basis to classify it as a plain typo.")

output = {
    "record_id": "SE_math_4031678__q",
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(output, separators=(",", ":")))
