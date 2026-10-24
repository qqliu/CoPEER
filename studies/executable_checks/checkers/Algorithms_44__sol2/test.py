r"""|hP(v) -hP(w)| = max x in P (v * x) - max z in P (w * z) <= max x in P |(v -w) * x| <= Mv -w."""

import json
from itertools import combinations

REPORT = {
    "record_id": "Algorithms_44__sol2",
    "outcome": "WITNESS_FOUND",
    "witness_description": "P = {1}, v = 0, and w = 1; the displayed left side is 1 and the displayed directed difference is -1.",
    "refutation_explanation": "With P = {1}, the displayed maxima give hP(t) = max(t*x for x in P) = t. Hence |hP(0) - hP(1)| = 1, but max(0*x for x in P) - max(1*z for z in P) = 0 - 1 = -1. The claimed equality would require 1 = -1.",
    "search_space": "All 12 cases with P ranging over the nonempty subsets of {0, 1} and v,w independently ranging over {0, 1}; every case was evaluated in fixed subset-size/lexicographic, then v, then w order.",
}

values = (0, 1)
subsets = []
for size in range(1, len(values) + 1):
    subsets.extend(combinations(values, size))

checked = []
violations = []
for p in subsets:
    for v in values:
        for w in values:
            checked.append((p, v, w))
            h_v = max(v * x for x in p)
            h_w = max(w * z for z in p)
            absolute_difference = abs(h_v - h_w)
            directed_difference = h_v - h_w
            if absolute_difference != directed_difference:
                violations.append(
                    (p, v, w, h_v, h_w, absolute_difference, directed_difference)
                )

assert len(checked) == len(subsets) * len(values) * len(values)
assert violations
assert violations[0] == ((1,), 0, 1, 0, 1, 1, -1)
assert violations[0][5] != violations[0][6]

print(json.dumps(REPORT, separators=(",", ":")))
