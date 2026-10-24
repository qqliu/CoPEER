"""The identity E[aX+b] = aE[X]+b is asserted for every continuous random variable X without assuming that X has a finite expectation."""

import json


def main():
    candidate_space = ()
    for _candidate in candidate_space:
        pass

    result = {
        "record_id": "proofwiki_85350__codex_expansion",
        "outcome": "CLAIM_NOT_FINITELY_REFUTABLE",
        "witness_description": "None; no concrete random variable or probability law is present in the permitted data.",
        "refutation_explanation": "No refutation is claimed. The target quantifies over every continuous random variable and depends on whether its expectations exist, but the quote supplies no distribution, definition, finite encoding, or bounded family on which that analytic condition can be checked.",
        "search_space": "Exhaustive bounded sweep of the empty tuple: exactly 0 concrete random-variable specifications, since the permitted quote supplies only a formal expectation expression and no probability law or finite candidate family."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
