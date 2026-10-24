"""Dividing a = (a * c1) * c2 by a validly yields 1 = c1 * c2 for all integers satisfying the hypotheses."""

import json

record_id = "reddit_askmath_19b1r7e"
a, c1, c2 = 0, 0, 0
premise = a == (a * c1) * c2
conclusion = 1 == c1 * c2
cancellation_is_valid = a != 0

if premise and not conclusion and not cancellation_is_valid:
    verdict = "CONFIRMED"
    notes = "Exact recomputation confirms that (a, c1, c2) = (0, 0, 0) satisfies a = (a * c1) * c2, while c1 * c2 = 0, not 1; cancellation by a is invalid because a = 0. The refuted statement contains a substantive missing nonzero hypothesis, not a plain typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The proposed witness does not independently refute the claim. The alleged issue would be substantive rather than a plain typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
