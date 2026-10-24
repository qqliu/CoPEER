r"""If adding/coloring the remaining vertex u creates no cycle, then the resulting connected graph G is a tree and therefore 2-colorable."""

import json

record_id = "reddit_askmath_pe1euu"
confirmed_notes = (
    "Exact recomputation confirms that the added leaf u lies on no cycle, "
    "while the connected resulting graph retains the base triangle, is not "
    "a tree, and has no proper 2-coloring. The refuted statement has a "
    "substantive omitted premise (that the pre-existing graph is acyclic), "
    "not a plain typo."
)

vertices = (0, 1, 2, 3)
u = 3
base_edges = frozenset({(0, 1), (0, 2), (1, 2)})
added_edges = frozenset({(0, 3)})
edges = base_edges | added_edges


def adjacent(vertex):
    result = set()
    for left, right in edges:
        if left == vertex:
            result.add(right)
        elif right == vertex:
            result.add(left)
    return result


def is_connected():
    reached = {vertices[0]}
    pending = [vertices[0]]
    while pending:
        current = pending.pop()
        for neighbor in adjacent(current):
            if neighbor not in reached:
                reached.add(neighbor)
                pending.append(neighbor)
    return reached == set(vertices)


def lies_on_cycle(target):
    pending = [(target, (target,))]
    while pending:
        current, path = pending.pop()
        for neighbor in adjacent(current):
            if neighbor == target:
                if len(path) >= 3:
                    return True
            elif neighbor not in path:
                pending.append((neighbor, path + (neighbor,)))
    return False


def has_proper_two_coloring():
    for assignment in range(1 << len(vertices)):
        proper = True
        for left, right in edges:
            left_color = (assignment >> left) & 1
            right_color = (assignment >> right) & 1
            if left_color == right_color:
                proper = False
                break
        if proper:
            return True
    return False


simple_edges = all(
    left in vertices and right in vertices and left < right
    for left, right in edges
)
reported_witness_exact = (
    base_edges == frozenset({(0, 1), (0, 2), (1, 2)})
    and added_edges == frozenset({(0, 3)})
)
addition_creates_no_cycle = not lies_on_cycle(u)
connected = is_connected()
is_tree = connected and len(edges) == len(vertices) - 1
two_colorable = has_proper_two_coloring()
triangle_remains = all(
    edge in edges for edge in ((0, 1), (0, 2), (1, 2))
)

verified = all((
    simple_edges,
    reported_witness_exact,
    addition_creates_no_cycle,
    connected,
    triangle_remains,
    not is_tree,
    not two_colorable,
))

if verified:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = (
        "Independent exact recomputation did not validate all required "
        "properties of the reported witness; the alleged refutation would "
        "therefore not be established."
    )

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
