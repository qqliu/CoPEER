r"""Since the induced subgraph $H := G[G \setminus \{v\}]$ has size less than $n$, it verifies the inductive hypotheses."""

import json

RECORD_ID = "SE_math_2793846__q"
TARGET_CLAIM = r"Since the induced subgraph $H := G[G \setminus \{v\}]$ has size less than $n$, it verifies the inductive hypotheses."
SOURCE_QUOTE = r"Since the induced subgraph $H := G[G \setminus \{v\}]$ has size less than $n$, it verifies the inductive hypotheses."

WITNESS_DESCRIPTION = (
    "No concrete witness can be formed from the supplied sentence because it "
    "supplies no concrete graph G, integer n, vertex v, size convention, or "
    "statement of the inductive hypotheses."
)
REFUTATION_EXPLANATION = (
    "The claim says that H has size less than n and therefore verifies "
    "unspecified inductive hypotheses. Whether that inference is valid cannot "
    "be evaluated without the content and scope of those hypotheses, so the "
    "supplied data does not determine a counterexample predicate."
)
SEARCH_SPACE = (
    "Exactly the singleton supplied (target_claim, source_quote) pair was "
    "inspected in fixed order. It specifies zero fully determined mathematical "
    "instances over which the asserted inductive inference can be tested."
)


def main():
    supplied_pairs = ((TARGET_CLAIM, SOURCE_QUOTE),)
    inspected = 0
    specified_instances = ()

    for target_claim, source_quote in supplied_pairs:
        inspected += 1
        assert target_claim == source_quote
        for _instance in specified_instances:
            raise AssertionError("No specified instance should exist")

    assert inspected == 1

    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
