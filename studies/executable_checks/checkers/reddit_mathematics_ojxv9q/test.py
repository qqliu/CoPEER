"""All runners with pairwise distinct velocities will occupy the same position at some positive time t'."""

import json


RECORD_ID = "reddit_mathematics_ojxv9q"

# This singleton is the entire permitted input space. None records that the
# corresponding component is absent; it does not supply a mathematical value.
supplied_records = (
    {
        "runner_count": None,
        "initial_positions": None,
        "velocities": None,
        "circumference": None,
        "position_law": None,
    },
)

complete_configurations = []
required_fields = (
    "runner_count",
    "initial_positions",
    "velocities",
    "circumference",
    "position_law",
)

for supplied_record in supplied_records:
    if all(supplied_record[field] is not None for field in required_fields):
        complete_configurations.append(supplied_record)

assert len(supplied_records) == 1
assert len(complete_configurations) == 0

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be named from the supplied data.",
    "refutation_explanation": "The claim and quote supply no runner count, initial positions, velocity values, circumference value, or mathematical position law. Therefore simultaneous occupancy at a positive time cannot be evaluated without adding definitions or data absent from the supplied quote.",
    "search_space": "The singleton supplied record was exhaustively checked for a fully specified numerical runner configuration; it contains zero such configurations because every required configuration component (runner count, initial positions, velocities, circumference, and position law) is unspecified.",
}

print(json.dumps(result, separators=(",", ":")))
