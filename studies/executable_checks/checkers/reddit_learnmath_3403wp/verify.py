r"""There are 6,555 ways to choose a cabinet containing exactly 8 men from 15 and 7 women from 10."""

import json


def binomial(n, k):
    counts = [1] + [0] * k
    for _ in range(n):
        for index in range(k, 0, -1):
            counts[index] += counts[index - 1]
    return counts[k]


def main():
    men_choices = binomial(15, 8)
    women_choices = binomial(10, 7)
    cabinet_choices = men_choices * women_choices

    if (men_choices != 6435 or women_choices != 120 or
            cabinet_choices != 772200 or cabinet_choices == 6555):
        raise RuntimeError("exact recomputation did not establish the refutation")

    result = {
        "record_id": "reddit_learnmath_3403wp",
        "verdict": "CONFIRMED",
        "notes": "Exact independent recomputation gives C(15,8)=6435 and C(10,7)=120, hence 772200 cabinets, not 6555. The refuted statement is substantive: 6555 is the erroneous sum 6435+120, not a plain typo."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
