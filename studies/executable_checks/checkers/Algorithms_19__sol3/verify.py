"""Since T is a tree, e1 is a bridge in T, meaning that removing e1 disconnects T into exactly two components. These components must be precisely S and V \ S (as e1 connects these two sets)."""

import json

RECORD_ID = "Algorithms_19__sol3"
CONFIRMED_NOTES = "Exact recomputation confirms that T is a tree, e1 crosses the cut, and T minus e1 has components {0,2} and {1}, not S={0} and V\\S={1,2}. The refuted statement is a substantive logical error, not plainly a typo."
INVALID_NOTES = "Exact recomputation did not validate every required property of the reported witness. The alleged refutation is therefore invalid; the challenged statement would be substantive rather than plainly a typo if refuted."


def reachable(start, vertices, edges):
    found = {start}
    pending = [start]
    while pending:
        vertex = pending.pop()
        for left, right in edges:
            if left == vertex:
                neighbor = right
            elif right == vertex:
                neighbor = left
            else:
                continue
            if neighbor not in found:
                found.add(neighbor)
                pending.append(neighbor)
    return frozenset(found)


def partition(vertices, edges):
    remaining = set(vertices)
    result = set()
    while remaining:
        component = reachable(min(remaining), vertices, edges)
        result.add(component)
        remaining.difference_update(component)
    return frozenset(result)


def main():
    vertices = frozenset({0, 1, 2})
    tree_edges = frozenset({(0, 1), (0, 2)})
    subset = frozenset({0})
    complement = vertices - subset
    removed_edge = (0, 1)

    endpoints_valid = all(
        left in vertices and right in vertices and left != right
        for left, right in tree_edges
    )
    whole_components = partition(vertices, tree_edges)
    is_tree = (
        endpoints_valid
        and len(tree_edges) == len(vertices) - 1
        and whole_components == frozenset({vertices})
    )
    crosses_cut = (
        removed_edge in tree_edges
        and ((removed_edge[0] in subset) != (removed_edge[1] in subset))
    )

    remaining_edges = tree_edges - frozenset({removed_edge})
    actual_components = partition(vertices, remaining_edges)
    reported_components = frozenset({frozenset({0, 2}), frozenset({1})})
    claimed_components = frozenset({subset, complement})

    valid_refutation = (
        is_tree
        and subset
        and subset != vertices
        and crosses_cut
        and actual_components == reported_components
        and len(actual_components) == 2
        and actual_components != claimed_components
    )

    if valid_refutation:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = INVALID_NOTES

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
