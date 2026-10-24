"""If G has a simple path visiting exactly n vertices, then none of the additional 17 isolated vertices can be on this path (as they have no edges)."""

import json

REPORT = {
    "record_id": "Algorithms_29__sol5",
    "verdict": "CONFIRMED",
    "notes": "Independent exact recomputation confirms the witness: with n=1, the singleton sequence containing isolated_00 is a simple path because it requires no edge, so it violates the conclusion. The refuted statement has a substantive boundary-condition error, not a plain typo; it needs an assumption such as n >= 2.",
}

additional_isolated = tuple(f"isolated_{index:02d}" for index in range(17))
vertices = frozenset(("ordinary_00",) + additional_isolated)
edges = frozenset()
n = 1
witness = ("isolated_00",)


def is_simple_path(sequence):
    if not sequence or any(vertex not in vertices for vertex in sequence):
        return False
    if len(frozenset(sequence)) != len(sequence):
        return False
    return all(
        (sequence[index], sequence[index + 1]) in edges
        or (sequence[index + 1], sequence[index]) in edges
        for index in range(len(sequence) - 1)
    )


def is_isolated(vertex):
    return all(vertex != left and vertex != right for left, right in edges)


assert len(additional_isolated) == 17
assert len(frozenset(additional_isolated)) == 17
assert all(vertex in vertices and is_isolated(vertex) for vertex in additional_isolated)
assert len(witness) == n
assert is_simple_path(witness)
assert witness[0] in additional_isolated

premise = is_simple_path(witness) and len(witness) == n
conclusion = all(vertex not in additional_isolated for vertex in witness)
assert premise
assert not conclusion

print(json.dumps(REPORT, sort_keys=True, separators=(",", ":")))
