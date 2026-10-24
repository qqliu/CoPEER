"""The proof claims that |min(f(s),g(s))| = |min(|f(s)|,|g(s)|)|."""

import json

record_id = "proofwiki_123739__codex_expansion"
confirmed_notes = (
    "Exact integer recomputation gives 2 on the left and 1 on the right for "
    "f(s) = -2 and g(s) = -1. The refuted statement is substantive, not "
    "plainly a typo."
)
invalid_notes = (
    "The reported witness did not produce unequal sides under exact integer "
    "recomputation. The alleged issue would therefore not be established."
)


def magnitude(value):
    if value < 0:
        return -value
    return value


def lesser(first, second):
    if first <= second:
        return first
    return second


f_at_s = -2
g_at_s = -1
left_side = magnitude(lesser(f_at_s, g_at_s))
right_side = magnitude(lesser(magnitude(f_at_s), magnitude(g_at_s)))

if left_side == 2 and right_side == 1 and left_side != right_side:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_notes

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
