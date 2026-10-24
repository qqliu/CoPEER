'''Assuming that there is an amount of men and women that does not equal $0$ in a family (not including the parents), let's say $3$ men and $3$ women, obviously a woman has $3$ brothers whereas one of her brothers only has $2$ brothers.'''

import itertools
import json


RECORD_ID = "mse_1794123__ans1794130"
WITNESS_DESCRIPTION = (
    "No counterexample exists in the swept labeled family model with exactly "
    "3 men and 3 women."
)
REFUTATION_EXPLANATION = (
    "Every woman has all 3 men as brothers, and each of those men has exactly "
    "the other 2 men as brothers. Thus every one of the 20 assignments "
    "satisfies the stated 3-men/3-women comparison."
)
SEARCH_SPACE = (
    "All 20 labeled sex assignments obtained by choosing exactly 3 men among "
    "6 non-parent family members; for every assignment, all 3 women and each "
    "of their 3 brothers were checked."
)

people = tuple(range(6))
violations = []
assignment_count = 0

for male_tuple in itertools.combinations(people, 3):
    assignment_count += 1
    men = frozenset(male_tuple)
    women = tuple(person for person in people if person not in men)

    for woman in women:
        brothers_of_woman = tuple(person for person in people if person in men)
        woman_has_three_brothers = len(brothers_of_woman) == 3
        some_brother_has_two_brothers = any(
            len(tuple(other for other in men if other != brother)) == 2
            for brother in brothers_of_woman
        )
        if not (woman_has_three_brothers and some_brother_has_two_brothers):
            violations.append((male_tuple, woman))

if assignment_count != 20 or violations:
    raise AssertionError("The exhaustive finite check did not have the expected result")

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
