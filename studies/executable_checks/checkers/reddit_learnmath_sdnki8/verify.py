r"""For every clock c, (touch(c) → ¬stop(c)) → (start(c) → ¬touch(c))."""

import json

REPORT = {
    "record_id": "reddit_learnmath_sdnki8",
    "verdict": "CONFIRMED",
    "notes": "Independent exact Boolean recomputation confirms the one-clock witness makes the outer implication false. The refuted statement has a substantive logical failure; the source's “cloak” versus “clock” wording is merely an unrelated typo.",
}


def implication(left, right):
    assert left in (0, 1)
    assert right in (0, 1)
    return 1 - left + left * right


touch_c0 = 1
stop_c0 = 0
start_c0 = 1

not_stop_c0 = 1 - stop_c0
not_touch_c0 = 1 - touch_c0
premise = implication(touch_c0, not_stop_c0)
conclusion = implication(start_c0, not_touch_c0)
whole_instance = implication(premise, conclusion)

assert not_stop_c0 == 1
assert not_touch_c0 == 0
assert premise == 1
assert conclusion == 0
assert whole_instance == 0
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
