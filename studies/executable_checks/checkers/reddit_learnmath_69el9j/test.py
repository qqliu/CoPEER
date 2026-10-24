"""The stated two cases—having an angle greater than 90 degrees or having all angles less than 90 degrees—exhaust all triangles."""

import json

RECORD_ID = "reddit_learnmath_69el9j"
WITNESS_DESCRIPTION = (
    "The integer angle triple (1, 89, 90) degrees is a triangle: all angles "
    "are positive and their sum is 180 degrees."
)
REFUTATION_EXPLANATION = (
    "This triangle has no angle greater than 90 degrees, and not all of its "
    "angles are less than 90 degrees because one angle equals 90 degrees. "
    "Thus it belongs to neither stated case."
)
SEARCH_SPACE = (
    "All nondecreasing integer triples (a, b, c) with 1 <= a <= b <= c <= "
    "179 and a + b + c = 180, checked in lexicographic order; the first "
    "counterexample is (1, 89, 90)."
)

witness = None
for a in range(1, 180):
    for b in range(a, 180):
        for c in range(b, 180):
            if a + b + c != 180:
                continue
            has_angle_greater_than_90 = any(x > 90 for x in (a, b, c))
            has_all_angles_less_than_90 = all(x < 90 for x in (a, b, c))
            if not has_angle_greater_than_90 and not has_all_angles_less_than_90:
                witness = (a, b, c)
                break
        if witness is not None:
            break
    if witness is not None:
        break

if witness != (1, 89, 90):
    raise AssertionError("deterministic search produced an unexpected result")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))
