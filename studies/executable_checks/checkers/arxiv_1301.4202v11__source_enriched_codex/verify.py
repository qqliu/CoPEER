r"""The inversion theorem recovers G from F without requiring the essential hypothesis α(1)≠0."""

import json

RECORD_ID = "arxiv_1301.4202v11__source_enriched_codex"
NOTES = (
    "Exact arithmetic confirms the substantive counterexample: with α(1)=0, "
    "G(1)=-1 and G(1)=0 are distinct but both yield F(1)=0, so F cannot "
    "uniquely determine G."
)


def value_at_one(alpha_one, g_one):
    total = 0
    for n in range(1, 2):
        if n != 1:
            raise AssertionError("unexpected summation index")
        total += alpha_one * g_one
    return total


def main():
    alpha_one = 0
    first_g_one = -1
    second_g_one = 0
    first_f_one = value_at_one(alpha_one, first_g_one)
    second_f_one = value_at_one(alpha_one, second_g_one)

    noninjective = (
        first_g_one != second_g_one
        and first_f_one == 0
        and second_f_one == 0
        and first_f_one == second_f_one
    )
    inverse_coefficient_impossible = all(
        alpha_one * candidate != 1 for candidate in range(-2, 3)
    ) and alpha_one * 0 != 1

    verdict = (
        "CONFIRMED"
        if noninjective and inverse_coefficient_impossible
        else "REFUTED_WITNESS_INVALID"
    )
    result = {
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
