r"""No woman would prefer a man who didnt propose to her over her current partner (since men propose in order of preference)."""

import json
from itertools import permutations, product

REPORT = {
    "record_id": "Algorithms_12__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "With men m0, m1 and women w0, w1: m0 ranks w0>w1 and proposes only to w0; m1 ranks w1>w0 and proposes only to w1. Both top-choice proposals are accepted, so w0's current partner is m0 and w1's is m1. Woman w0 ranks m0>m1, and woman w1 ranks m0>m1.",
    "refutation_explanation": "Man m0 did not propose to w1, yet w1 prefers m0 to her current partner m1. Each man made only his top-choice proposal, so the stated condition that men propose in preference order is satisfied; this directly contradicts the universal claim.",
    "search_space": "All 16 strict preference profiles for 2 labeled men and 2 labeled women, in lexicographic permutation-product order. The counterexample predicate was evaluated on the 8 profiles whose two first-choice proposals had distinct recipients, with both proposals accepted as the current partnerships. All 16 profiles were swept, and the first violation was retained.",
}

MEN = (0, 1)
WOMEN = (0, 1)
MAN_ORDERS = tuple(permutations(WOMEN))
WOMAN_ORDERS = tuple(permutations(MEN))

first_violation = None
examined_profiles = 0
eligible_profiles = 0

for men_preferences in product(MAN_ORDERS, repeat=2):
    for women_preferences in product(WOMAN_ORDERS, repeat=2):
        examined_profiles += 1
        proposals = tuple(preference[0] for preference in men_preferences)

        # Distinct recipients can accept both top-choice proposals, producing
        # an unambiguous current partnership for each woman.
        if proposals[0] == proposals[1]:
            continue
        eligible_profiles += 1

        current_partners = [None, None]
        for man in MEN:
            current_partners[proposals[man]] = man

        for woman in WOMEN:
            partner = current_partners[woman]
            ranking = women_preferences[woman]
            partner_position = ranking.index(partner)
            for man in MEN:
                did_not_propose = proposals[man] != woman
                prefers_man = ranking.index(man) < partner_position
                if did_not_propose and prefers_man and first_violation is None:
                    first_violation = (
                        men_preferences,
                        women_preferences,
                        proposals,
                        tuple(current_partners),
                        woman,
                        man,
                        partner,
                    )

computed_outcome = (
    "WITNESS_FOUND" if first_violation is not None
    else "NO_WITNESS_EXHAUSTIVE"
)
assert REPORT["outcome"] == computed_outcome
assert first_violation is not None

(
    found_men_preferences,
    found_women_preferences,
    found_proposals,
    found_partners,
    found_woman,
    found_man,
    found_partner,
) = first_violation

computed_witness_description = (
    "With men m0, m1 and women w0, w1: "
    f"m0 ranks w{found_men_preferences[0][0]}>w{found_men_preferences[0][1]} "
    f"and proposes only to w{found_proposals[0]}; "
    f"m1 ranks w{found_men_preferences[1][0]}>w{found_men_preferences[1][1]} "
    f"and proposes only to w{found_proposals[1]}. "
    "Both top-choice proposals are accepted, so "
    f"w0's current partner is m{found_partners[0]} and "
    f"w1's is m{found_partners[1]}. "
    f"Woman w0 ranks m{found_women_preferences[0][0]}>m{found_women_preferences[0][1]}, "
    f"and woman w1 ranks m{found_women_preferences[1][0]}>m{found_women_preferences[1][1]}."
)
computed_refutation_explanation = (
    f"Man m{found_man} did not propose to w{found_woman}, yet "
    f"w{found_woman} prefers m{found_man} to her current partner "
    f"m{found_partner}. Each man made only his top-choice proposal, so "
    "the stated condition that men propose in preference order is satisfied; "
    "this directly contradicts the universal claim."
)
computed_search_space = (
    f"All {examined_profiles} strict preference profiles for 2 labeled men "
    "and 2 labeled women, in lexicographic permutation-product order. "
    f"The counterexample predicate was evaluated on the {eligible_profiles} "
    "profiles whose two first-choice proposals had distinct recipients, with "
    "both proposals accepted as the current partnerships. "
    f"All {examined_profiles} profiles were swept, and the first violation "
    "was retained."
)

assert REPORT["witness_description"] == computed_witness_description
assert REPORT["refutation_explanation"] == computed_refutation_explanation
assert REPORT["search_space"] == computed_search_space
assert tuple(REPORT) == (
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
)

print(json.dumps(REPORT, separators=(",", ":")))
