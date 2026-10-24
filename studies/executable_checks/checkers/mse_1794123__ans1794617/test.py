"""If the likelihood of having boys does depend on the family, men on average have more brothers, not fewer."""

import json


RECORD_ID = "mse_1794123__ans1794617"
CANDIDATE_MODELS = ()
WITNESS_DESCRIPTION = "No concrete witness can be evaluated from the supplied quote alone."
REFUTATION_EXPLANATION = (
    "The quote specifies no family model, family-size distribution, "
    "sex-probability distribution, sampling rule, or precise meaning of the "
    "average over men. Constructing a nonempty candidate space or deciding "
    "whether a candidate violates the claim would therefore require "
    "definitions or data absent from the quote."
)
SEARCH_SPACE = (
    "Exhaustively swept 0 candidate models: the empty tuple (), because the "
    "permitted quote supplies no concrete family model or averaging rule from "
    "which a candidate can be constructed without adding data."
)


def main():
    witness = None
    for candidate in CANDIDATE_MODELS:
        witness = candidate
        break
    if witness is not None:
        raise AssertionError("The declared empty search space was not empty")
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
