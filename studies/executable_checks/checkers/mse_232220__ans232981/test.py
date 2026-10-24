"""Once the phone rings, sending the closest car is in fact globally optimal."""

import json


def main():
    candidate_instances = ()
    witness = None

    for instance in candidate_instances:
        raise AssertionError("The source quote specified no candidate instances")

    assert witness is None
    result = {
        "record_id": "mse_232220__ans232981",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No counterexample was found because the permitted source supplies zero formally specified dispatch instances.",
        "refutation_explanation": "The quote provides no definitions of distance, system state, admissible dispatch policies, future calls, costs, or the objective meant by globally optimal, so the claim cannot be evaluated without inventing absent data.",
        "search_space": "Exactly 0 candidate dispatch instances: the empty tuple (), which exhausts all instances formally specified by the source quote.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
