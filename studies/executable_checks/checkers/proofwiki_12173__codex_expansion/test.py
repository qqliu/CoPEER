"""For arbitrary classes A and B, the Axiom of Pairing yields a set x whose elements are exactly A and B."""

import json


RECORD_ID = "proofwiki_12173__codex_expansion"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No witness: the supplied data gives no finite class-theory structure or "
    "concrete classes A and B."
)
REFUTATION_EXPLANATION = (
    "The claim quantifies over arbitrary classes and invokes the Axiom of "
    "Pairing. The quote supplies only the formula, with no finite domain, "
    "membership relation, interpretation of set versus class, or bounded "
    "representation of arbitrary classes; therefore a finite exact "
    "counterexample check cannot be defined without inventing absent semantics."
)
SEARCH_SPACE = (
    "Exhaustively swept the explicitly bounded admissible-candidate space of "
    "size 0: (). The space is empty because the supplied quote specifies no "
    "concrete finite structures or class assignments."
)


def main():
    admissible_candidates = ()
    for _candidate in admissible_candidates:
        raise AssertionError("The explicitly empty search space was not empty")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
