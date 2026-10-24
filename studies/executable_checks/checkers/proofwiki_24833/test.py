r"""In the converse direction of the characterization, the proof splits into the two cases 'p \preceq q' and 'p \preceq a and a \preceq q'. The second case hypothesis is not the theorem's second disjunct (which is 'p \preceq a and b \preceq q'), so (i) the case analysis does not cover all instances the theorem requires, and (ii) the lines immediately derived from it ('b \preceq' q', hence 'b \preceq'^+ q') do not follow from the stated hypothesis."""

import itertools
import json

RECORD_ID = "proofwiki_24833"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample is certified. The finite propositional sweep finds one "
    "valuation exhibiting the reported case-coverage gap and two valuations "
    "exhibiting failure of the reported implication, but those valuations cannot "
    "represent the unspecified mathematical context without inventing assumptions."
)
REFUTATION_EXPLANATION = (
    "The source quote supplies only the hypothesis p \\preceq a and a \\preceq q. "
    "It does not supply the theorem, the surrounding proof, the meaning or axioms "
    "of \\preceq and \\preceq', or the allegedly derived lines. Consequently, an "
    "exhaustive truth-table diagnostic cannot determine whether omitted context "
    "repairs either alleged defect, so the counterexample search is inconclusive."
)
SEARCH_SPACE = (
    "All 16 Boolean valuations, in itertools.product((False, True), repeat=4) "
    "order, of the four quoted or reported atomic statements p \\preceq q, "
    "p \\preceq a, a \\preceq q, and b \\preceq q; this is exhaustive only for "
    "the independent-proposition diagnostic, not for possible mathematical proof "
    "contexts."
)

coverage_gaps = 0
implication_failures = 0
for p_le_q, p_le_a, a_le_q, b_le_q in itertools.product(
    (False, True), repeat=4
):
    theorem_condition = p_le_q or (p_le_a and b_le_q)
    reported_cases = p_le_q or (p_le_a and a_le_q)
    if theorem_condition and not reported_cases:
        coverage_gaps += 1
    stated_hypothesis = p_le_a and a_le_q
    if stated_hypothesis and not b_le_q:
        implication_failures += 1

assert coverage_gaps == 1
assert implication_failures == 2

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False))
