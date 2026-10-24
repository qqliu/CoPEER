"""Under the stated hypotheses, ‖f‖ attains both a minimum and a maximum on X, even though X is not assumed nonempty."""

import json

RECORD_ID = "proofwiki_10636__codex_expansion"
WITNESS_DESCRIPTION = (
    "Take X = ∅ and f to be the unique empty function on X; then ‖f‖ also has empty domain."
)
REFUTATION_EXPLANATION = (
    "Attaining either a minimum or a maximum requires some x in X at which the relevant value is attained. "
    "Since X = ∅ has no element, ‖f‖ attains neither, contradicting the claim that it attains both when "
    "nonemptiness is not assumed."
)
SEARCH_SPACE = (
    "The singleton candidate space consisting of X = ∅ and the unique empty function f on X. "
    "The program sweeps that entire one-candidate space and checks both existential attainment conditions."
)


def main():
    candidates = (((), ()),)
    witnesses = []
    swept = 0

    for domain, graph in candidates:
        swept += 1
        assert len(graph) == 0
        attains_minimum = any(True for _x in domain)
        attains_maximum = any(True for _x in domain)
        if not (attains_minimum and attains_maximum):
            witnesses.append((domain, graph))

    assert swept == len(candidates) == 1
    assert witnesses == [((), ())]

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
