r"""Furthermore, note that all the regions outside of $T$ are unbounded."""

import json


def main():
    admissible_instances = ()
    for instance in admissible_instances:
        raise AssertionError(instance)

    result = {
        "record_id": "mse_1344117__ans1344370",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be formed because neither T nor a region outside T is defined in the supplied source data.",
        "refutation_explanation": "The source quote merely repeats the claim and supplies no definition or instance of T, no ambient space, and no meaning of region or unbounded. Therefore the empty admissible-instance space is exhaustively searched, but this cannot decide or refute the claim.",
        "search_space": "Exactly the empty tuple of admissible instances, containing 0 elements.",
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
