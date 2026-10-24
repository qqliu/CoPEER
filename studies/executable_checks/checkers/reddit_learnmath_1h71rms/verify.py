r"""If a^2 is divisible by n, then a is divisible by n."""

import json

record_id = "reddit_learnmath_1h71rms"
a = 2
n = 4
square = a * a
premise_holds = square % n == 0
conclusion_fails = a % n != 0

if premise_holds and conclusion_fails:
    verdict = "CONFIRMED"
    notes = (
        "The refuted statement is substantive, not plainly a typo. "
        "Exact recomputation gives 2 × 2 = 4, whose remainder modulo 4 is 0, "
        "while 2 has remainder 2 modulo 4."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The proposed witness does not refute the substantive statement."

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
