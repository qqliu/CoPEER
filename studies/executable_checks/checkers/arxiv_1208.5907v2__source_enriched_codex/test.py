"""Choose Outsiders First always outputs a valid cover.

The permitted quote supplies no concrete instance on which cover validity can
be evaluated, so the explicitly bounded candidate space is empty.
"""

import json


RECORD_ID = "arxiv_1208.5907v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness: the supplied quote contains no concrete universe U, IN/OUT "
    "classification, cover relation, or executable specification of Choose "
    "Outsiders First."
)
REFUTATION_EXPLANATION = (
    "The quote asserts that IN is a cover after classification, but it does "
    "not define cover validity, specify the algorithm, or supply any concrete "
    "instance. Therefore the universal claim cannot be tested or refuted from "
    "the permitted data."
)
SEARCH_SPACE = (
    "Exhaustively swept the empty finite set of concrete algorithm instances "
    "supplied by the quote (0 instances); no candidate universe, "
    "classification, or cover relation was provided."
)


def main():
    candidate_instances = ()
    witness = None
    for candidate in candidate_instances:
        witness = candidate
        break
    assert witness is None

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
