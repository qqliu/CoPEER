r"""No woman would prefer a man who didnt propose to her over her current partner (since men propose in order of preference)."""

import json

REPORT = {
    "record_id": "Algorithms_12__sol5",
    "verdict": "CONFIRMED",
    "notes": "Independent exact simulation reaches the terminal matching w0-m0, w1-m1; m0 never proposes to w1, although w1 ranks m0 above m1. Thus the literal universal claim fails. The refuted statement is substantive, not plainly a typo: it omits the essential mutual-preference condition.",
}

men_preferences = ((0, 1), (1, 0))
women_preferences = ((0, 1), (0, 1))
number_of_men = 2
number_of_women = 2

assert len(men_preferences) == number_of_men
assert len(women_preferences) == number_of_women
assert all(tuple(sorted(order)) == (0, 1) for order in men_preferences)
assert all(tuple(sorted(order)) == (0, 1) for order in women_preferences)

next_choice = [0, 0]
woman_partner = [-1, -1]
man_partner = [-1, -1]
free_men = [0, 1]
proposals = []

while free_men:
    man = free_men.pop(0)
    assert man_partner[man] == -1
    assert next_choice[man] < number_of_women
    woman = men_preferences[man][next_choice[man]]
    next_choice[man] += 1
    proposals.append((man, woman))
    incumbent = woman_partner[woman]

    if incumbent == -1:
        woman_partner[woman] = man
        man_partner[man] = woman
    else:
        ranking = women_preferences[woman]
        if ranking.index(man) < ranking.index(incumbent):
            woman_partner[woman] = man
            man_partner[man] = woman
            man_partner[incumbent] = -1
            free_men.append(incumbent)
        else:
            free_men.append(man)

assert tuple(woman_partner) == (0, 1)
assert tuple(man_partner) == (0, 1)
assert all(partner != -1 for partner in woman_partner)
assert all(partner != -1 for partner in man_partner)

for man in range(number_of_men):
    actual = tuple(woman for proposer, woman in proposals if proposer == man)
    expected = men_preferences[man][:len(actual)]
    assert actual == expected

woman = 1
nonproposer = 0
current_partner = woman_partner[woman]
assert current_partner == 1
assert (nonproposer, woman) not in proposals
assert women_preferences[woman].index(nonproposer) < women_preferences[woman].index(current_partner)

literal_claim_is_violated = (
    (nonproposer, woman) not in proposals
    and women_preferences[woman].index(nonproposer)
    < women_preferences[woman].index(current_partner)
)
assert literal_claim_is_violated

nonproposer_partner = man_partner[nonproposer]
assert nonproposer_partner == 0
assert men_preferences[nonproposer].index(nonproposer_partner) < men_preferences[nonproposer].index(woman)

assert tuple(REPORT) == ("record_id", "verdict", "notes")
assert REPORT["record_id"] == "Algorithms_12__sol5"
assert REPORT["verdict"] == ("CONFIRMED" if literal_claim_is_violated else "REFUTED_WITNESS_INVALID")
print(json.dumps(REPORT, separators=(",", ":")))
