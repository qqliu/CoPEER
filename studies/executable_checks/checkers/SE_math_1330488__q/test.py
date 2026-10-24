"""So now there are $k$ vertices with a degree of at least $k-1$ and from the induction hypothesis we'll have a path of length $k$."""

import json

RECORD_ID = "SE_math_1330488__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No witness can be evaluated from the supplied quote alone."
REFUTATION_EXPLANATION = (
    "The quote does not specify the graph class, the range of k, whether path "
    "length counts edges or vertices, or the induction hypothesis. Assigning "
    "any of these would add definitions or data absent from the quote, so no "
    "candidate can be judged an exact counterexample."
)
SEARCH_SPACE = (
    "The empty finite set of fully specified graph instances derivable from "
    "the supplied quote without adding definitions; exactly 0 instances were swept."
)


def main():
    admissible_instances = ()
    for _instance in admissible_instances:
        raise AssertionError("The source supplies no fully specified instance")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
