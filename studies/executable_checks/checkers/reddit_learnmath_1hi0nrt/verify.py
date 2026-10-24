r"""For every n >= 2, F_n < F_{n+1} < 2F_n."""

import json

record_id = "reddit_learnmath_1hi0nrt"
expected_verdict = "CONFIRMED"
expected_notes = "With standard indexing F_0 = 0 and F_1 = 1, exact recurrence gives F_2 = 1 and F_3 = 2, so the strict upper inequality requires 2 < 2 and fails. This is a genuine refutation of the stated universal claim, but plainly a boundary-case typo (the strict inequality holds from n >= 3)."

n = 2
current = 0
following = 1
for _ in range(n):
    current, following = following, current + following

witness_is_valid = (
    n >= 2
    and current == 1
    and following == 2
    and not (current < following < 2 * current)
)

if witness_is_valid:
    verdict = expected_verdict
    notes = expected_notes
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "Independent exact recurrence did not reproduce the reported witness."

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
