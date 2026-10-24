r'''The proof asserts that (1+2/(k-1))^(a-1) is at most 1+2(a-1)/(k-1), an inequality used to establish Part 1's upper bound in the Non-Intersection Bias Lemma.'''

import json

record_id = "arxiv_1304.1796v2__source_enriched_codex"
a = 3
k = 1000001

base_numerator = (k - 1) + 2
base_denominator = k - 1
left_numerator = base_numerator * base_numerator
left_denominator = base_denominator * base_denominator
right_numerator = (k - 1) + 2 * (a - 1)
right_denominator = k - 1

expected_left_numerator = 250001000001
expected_left_denominator = 250000000000
expected_right_numerator = 250001000000
expected_right_denominator = 250000000000

left_matches = (
    left_numerator * expected_left_denominator
    == expected_left_numerator * left_denominator
)
right_matches = (
    right_numerator * expected_right_denominator
    == expected_right_numerator * right_denominator
)
strictly_greater = (
    left_numerator * right_denominator
    > right_numerator * left_denominator
)
difference_matches = (
    left_numerator * right_denominator - right_numerator * left_denominator
    == (left_denominator * right_denominator) // 250000000000
)
confirmed = left_matches and right_matches and strictly_greater and difference_matches

if confirmed:
    verdict = "CONFIRMED"
    notes = "Exact integer arithmetic independently reproduces the witness: at a=3 and k=1000001, the left side is 250001000001/250000000000, exceeding 250001000000/250000000000 by 1/250000000000. The refuted statement is a substantive false inequality, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Independent exact arithmetic does not validate the reported witness. The challenged statement would be substantive rather than plainly a typo."

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
