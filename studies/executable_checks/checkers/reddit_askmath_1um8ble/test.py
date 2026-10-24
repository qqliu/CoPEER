"""For every integer n ≥ ⌈R/a_m⌉, the expression 2a_m*n^m - n^{m-1}*(a_m*n - R) is at most its value at n = ⌈R/a_m⌉."""

import json


def main():
    concrete_instances = ()
    for _instance in concrete_instances:
        raise AssertionError("The supplied data determine no concrete instance")

    result = {
        "record_id": "reddit_askmath_1um8ble",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be determined because no values or domains are supplied for a_m, R, or m.",
        "refutation_explanation": "The claim quantifies n but leaves a_m, R, and m unspecified. Their domains and necessary side conditions, including when ⌈R/a_m⌉ and the integer powers are defined, are absent, so the supplied data do not determine a concrete proposition that can be numerically tested.",
        "search_space": "The empty set of concrete tuples (a_m, R, m, n), of cardinality 0; no such tuple is determined by the supplied claim and quote."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
