"""The refined recurrence for multiple machines correctly computes the feasible load vectors and supports the claimed multi-machine algorithm."""

import json
from itertools import product

RECORD_ID = "arxiv_2402.16847v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No witness can be certified from the supplied data."
REFUTATION_EXPLANATION = (
    "The quote specifies how S_j is generated but never defines the reference "
    "set of \"feasible load vectors\" or the multi-machine algorithm's promised "
    "property, so no enumerated instance can be classified as a counterexample "
    "without adding semantics."
)
SEARCH_SPACE = (
    "All 22,140 parameter instances with m in {1,2,3}, n in {1,2,3,4}, "
    "and each (p_j,d_j) in {1,2,3}^2, with the displayed recurrence "
    "evaluated exactly using integer tuple vectors; the sweep can test only "
    "recurrence-defined invariants, not correctness against an undefined "
    "feasible-set specification."
)


def evaluate_recurrence(machine_count, processing_times, deadlines):
    zero = (0,) * machine_count
    states = [{zero}]
    for processing_time, deadline in zip(processing_times, deadlines):
        previous = states[-1]
        limit = deadline - processing_time
        eligible = {
            vector
            for vector in previous
            if all(coordinate <= limit for coordinate in vector)
        }
        provisional = set(eligible)
        for vector in eligible:
            for index in range(machine_count):
                extended = list(vector)
                extended[index] += processing_time
                provisional.add(tuple(extended))
        states.append(provisional | previous)
    return states


def exhaustive_sweep():
    values = (1, 2, 3)
    instance_count = 0
    for machine_count in (1, 2, 3):
        for job_count in (1, 2, 3, 4):
            for encoded in product(values, repeat=2 * job_count):
                processing_times = encoded[0::2]
                deadlines = encoded[1::2]
                states = evaluate_recurrence(
                    machine_count, processing_times, deadlines
                )
                assert len(states) == job_count + 1
                assert states[0] == {(0,) * machine_count}
                assert all(
                    len(vector) == machine_count
                    and all(coordinate >= 0 for coordinate in vector)
                    for state in states
                    for vector in state
                )
                instance_count += 1
    assert instance_count == 22140


def main():
    exhaustive_sweep()
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
