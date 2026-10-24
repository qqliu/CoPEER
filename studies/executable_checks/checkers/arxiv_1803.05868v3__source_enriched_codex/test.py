"""Every finite-covolume Kleinian group Γ < PSL_2(C) admits a discrete faithful representation into SL_2(C)."""

import json

RECORD_ID = "arxiv_1803.05868v3__source_enriched_codex"
OUTCOME = "CLAIM_NOT_FINITELY_REFUTABLE"
WITNESS_DESCRIPTION = (
    "No concrete witness is available: the source quote specifies no concrete "
    "Kleinian group or representation to test."
)
REFUTATION_EXPLANATION = (
    "The claim quantifies over all finite-covolume Kleinian groups and requires "
    "deciding whether each admits a discrete faithful representation into SL_2(C). "
    "The quote only asserts the general result and supplies neither a finite "
    "candidate domain nor finite criteria for checking discreteness, faithfulness, "
    "and nonexistence of such a representation. Therefore the claim is not "
    "finitely refutable from the permitted data."
)
SEARCH_SPACE = (
    "The exact finite space swept is the empty set of concrete candidate Kleinian "
    "groups explicitly specified by the source quote (cardinality 0); this empty "
    "sweep is not evidence for the universal claim."
)


def main():
    supplied_concrete_groups = ()
    for _candidate in supplied_concrete_groups:
        raise AssertionError("The permitted source supplied no concrete candidate")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
