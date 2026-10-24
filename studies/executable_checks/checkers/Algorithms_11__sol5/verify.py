"""Independent exact witness checker.

The ferry capacity k = c+1 implies at most c passengers can be transported at a time (excluding Charon). - Thus, the passengers can be partitioned into at most c independent sets, corresponding to a c-coloring of G.
"""

import itertools
import json

RECORD_ID = "Algorithms_11__sol5"
NOTES = (
    "Confirmed by exact recomputation: for G=K2 and c=1, the schedule "
    "carries passenger 0 across, returns empty, then carries passenger 1 "
    "across; every unattended bank is independent. K2 has no 1-coloring. "
    "The refuted statement is a substantive logical error, not a typo: "
    "a per-trip load bound does not imply a c-coloring."
)


def independent(passengers, edges):
    return all(not ({u, v} <= passengers) for u, v in edges)


def schedule_is_valid(vertices, edges, capacity, boat_capacity, schedule):
    if boat_capacity != capacity + 1:
        return False

    left = set(vertices)
    charon_side = "L"

    for origin, destination, carried in schedule:
        if charon_side != origin:
            return False
        if (origin, destination) not in (("L", "R"), ("R", "L")):
            return False
        if len(carried) != len(set(carried)) or len(carried) > capacity:
            return False

        load = set(carried)
        current_bank = left if origin == "L" else set(vertices) - left
        if not load <= current_bank:
            return False

        if origin == "L":
            left -= load
        else:
            left |= load
        charon_side = destination

        unattended = left if charon_side == "R" else set(vertices) - left
        if not independent(unattended, edges):
            return False

    return not left and charon_side == "R"


def has_proper_coloring(vertices, edges, color_count):
    ordered = tuple(sorted(vertices))
    for colors in itertools.product(range(color_count), repeat=len(ordered)):
        assigned = dict(zip(ordered, colors))
        if all(assigned[u] != assigned[v] for u, v in edges):
            return True
    return False


def main():
    vertices = frozenset((0, 1))
    edges = frozenset(((0, 1),))
    capacity = 1
    boat_capacity = 2
    schedule = (
        ("L", "R", (0,)),
        ("R", "L", ()),
        ("L", "R", (1,)),
    )

    feasible = schedule_is_valid(
        vertices, edges, capacity, boat_capacity, schedule
    )
    colorable = has_proper_coloring(vertices, edges, capacity)
    established = feasible and not colorable

    verdict = "CONFIRMED" if established else "REFUTED_WITNESS_INVALID"
    notes = NOTES if established else (
        "Independent exact recomputation did not validate the reported witness."
    )
    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
