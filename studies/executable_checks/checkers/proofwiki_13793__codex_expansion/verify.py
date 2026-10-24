r"""The substitution sec(theta)=x/|a| is valid and domain-preserving under the stated hypotheses without requiring a≠0."""

import json
from fractions import Fraction

record_id = "proofwiki_13793__codex_expansion"
a = 0
x = -1
magnitude = -a if a < 0 else a

zero_denominator_detected = False
try:
    Fraction(x, magnitude)
except ZeroDivisionError:
    zero_denominator_detected = True

if a == 0 and x == -1 and magnitude == 0 and zero_denominator_detected:
    verdict = "CONFIRMED"
    notes = "The refuted statement is substantive, not plainly a typo: for the reported witness a=0 and x=-1, |a|=0, so the exact ratio x/|a| has a zero denominator and the substitution is undefined."
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The refuted statement is substantive, not plainly a typo, but the reported witness could not be independently reproduced."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False, separators=(",", ":")))
