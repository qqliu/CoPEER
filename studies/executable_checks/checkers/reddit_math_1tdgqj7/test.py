"""When t=0, the proof claims that (2π_E−t)^2=D=−q, thereby identifying 2π_E−t with √(−q)."""

import json


def main():
    t = 0
    q_values = tuple(range(-16, 17))
    comparisons = []

    for q in q_values:
        discriminant = t ** 2 - 4 * q
        claimed_value = -q
        comparisons.append((q, discriminant, claimed_value,
                            discriminant == claimed_value))

    disagreements = tuple(item for item in comparisons if not item[3])
    agreements = tuple(item for item in comparisons if item[3])

    if len(comparisons) != 33 or len(disagreements) != 32 or agreements != ((0, 0, 0, True),):
        raise AssertionError("bounded exact search produced an unexpected result")

    result = {
        "record_id": "reddit_math_1tdgqj7",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No certified witness: q=1 would make D=-4 and -q=-1, but the quote does not state that q=1 is admissible or define π_E.",
        "refutation_explanation": "For every tested nonzero integer q, substituting t=0 makes t^2-4q differ from -q, while q=0 makes them equal. However, the supplied text gives neither the admissible domain or value of q nor any definition or constraints for π_E, so the tested integer assignments cannot be certified as counterexamples to the full claim.",
        "search_space": "All 33 assignments with t=0 and integer q from -16 through 16 inclusive; D=t^2-4q and -q were compared using exact integer arithmetic in increasing q order."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
