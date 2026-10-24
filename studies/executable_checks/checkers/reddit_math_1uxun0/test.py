"""The logarithm law used to replace 2 ln(-1) by ln(1) is valid for the chosen complex logarithm."""

import json

RECORD_ID = "reddit_math_1uxun0"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No claim-specific witness can be named. The candidate n=0 gives "
    "2L_0(-1)=2πi while L_0(1)=0, but the supplied data do not identify "
    "n=0 as the chosen logarithm."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep finds failures (including n=0) and also n=-1, where "
    "both sides equal -2πi. Thus validity depends on the unspecified logarithm "
    "choice, so the supplied claim does not decide which result applies."
)
SEARCH_SPACE = (
    "All 17 integer shifts n from -8 through 8, in increasing order, for the "
    "symbolic logarithm values L_n(-1)=(2n+1)πi and L_n(1)=2nπi; the exact "
    "integer test was 2(2n+1)=2n."
)

satisfying = []
failing = []
for n in range(-8, 9):
    twice_log_minus_one_coefficient = 2 * (2 * n + 1)
    log_one_coefficient = 2 * n
    if twice_log_minus_one_coefficient == log_one_coefficient:
        satisfying.append(n)
    else:
        failing.append(n)

assert satisfying == [-1]
assert len(failing) == 16
assert 0 in failing

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
