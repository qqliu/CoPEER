r"""Since f lies on the path P from u to v in T2:
 The subpath of P from u to x does not use edge f, so this path exists in T2 \ {f}. Therefore u in D1.
 The subpath of P from y to v does not use edge f, so this path exists in T2 \ {f}. Therefore v in D2."""

import itertools
import json

REPORT = {
    "record_id": "Algorithms_36__sol3",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete graph witness is claimed: the quote does not define D1 or D2 or state how x and y are related to edge f.",
    "refutation_explanation": "The bounded Boolean sweep finds both a completion in which all four asserted atomic conclusions hold and a completion in which at least one fails. Because the quote supplies no definitions constraining those atoms, this demonstrates underdetermination, not a mathematical counterexample.",
    "search_space": "All 16 Boolean assignments, in itertools.product((False, True), repeat=4) order, to the four conclusions about the two subpaths and membership in D1 and D2, with only 'f lies on P' held fixed as true. This is an exhaustive diagnostic sweep of those assignments, not of graphs or of the target claim.",
}

premise_f_lies_on_p = True
swept = 0
found_supporting_completion = False
found_challenging_completion = False

for valuation in itertools.product((False, True), repeat=4):
    swept += 1
    asserted_conclusions_hold = all(valuation)
    if premise_f_lies_on_p and asserted_conclusions_hold:
        found_supporting_completion = True
    if premise_f_lies_on_p and not asserted_conclusions_hold:
        found_challenging_completion = True

if swept != 16:
    raise AssertionError("the stated finite diagnostic space was not swept")
if not found_supporting_completion:
    raise AssertionError("the sweep did not establish the claimed underdetermination")
if not found_challenging_completion:
    raise AssertionError("the sweep did not establish the claimed underdetermination")

print(json.dumps(REPORT, separators=(",", ":")))
