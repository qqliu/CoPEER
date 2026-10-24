r"""The submitted calculation concludes that (t+1/t)(t-1/t) equals 0."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_askmath_1qujy46",
    "verdict": "REFUTED_WITNESS_INVALID",
    "notes": "Exact arithmetic gives 15/4 at t=2, so the equality is a substantive algebraic error, not a typo. However, the stated claim is that the submission concludes the value is 0, and the supplied quote does make that conclusion; the witness therefore does not refute the stated attribution.",
}

t = Fraction(2, 1)
reciprocal = Fraction(1, 2)
zero = Fraction(0, 1)
assert t * reciprocal == Fraction(1, 1)
value = (t + reciprocal) * (t - reciprocal)
assert value == Fraction(15, 4)
assert value != zero

submission = "So I did (t x 1/t = t/t = 1) and (t x -1/t =-t/t = -1)\n\n(1)+(-1) =0"
normalized_submission = "".join(submission.split())
submission_concludes_zero = normalized_submission.endswith("(1)+(-1)=0")
assert submission_concludes_zero
assert REPORT["verdict"] == "REFUTED_WITNESS_INVALID"
assert tuple(REPORT) == ("record_id", "verdict", "notes")
print(json.dumps(REPORT, separators=(",", ":")))
