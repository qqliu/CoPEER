"""There are 6,555 ways to choose a cabinet containing exactly 8 men from 15 and 7 women from 10."""

import json
from itertools import combinations


def main():
    men = tuple(range(1, 16))
    women = tuple(range(1, 11))

    men_choice_count = 0
    women_choice_count = 0
    cabinet_count = 0

    for _ in combinations(men, 8):
        men_choice_count += 1

    for _ in combinations(women, 7):
        women_choice_count += 1

    for chosen_men in combinations(men, 8):
        for chosen_women in combinations(women, 7):
            cabinet = (chosen_men, chosen_women)
            if len(cabinet[0]) == 8 and len(cabinet[1]) == 7:
                cabinet_count += 1

    assert men_choice_count == 6435
    assert women_choice_count == 120
    assert cabinet_count == 772200
    assert cabinet_count != 6555

    result = {
        "record_id": "reddit_learnmath_3403wp",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Exhaustive enumeration gives 6,435 choices of 8 men and 120 choices of 7 women, producing 6,435 × 120 = 772,200 distinct cabinets.",
        "refutation_explanation": "A cabinet is determined by both its chosen men and its chosen women, so the independent choice counts multiply. The exhaustive count is 772,200, which is not 6,555.",
        "search_space": "Every pair (M, W) where M is an 8-element subset of the labeled men {1, ..., 15} and W is a 7-element subset of the labeled women {1, ..., 10}; exactly C(15,8) × C(10,7) = 772,200 pairs were swept."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
