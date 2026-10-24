#!/usr/bin/env python3
from itertools import combinations


VERTICES = frozenset(("a", "b", "c", "d"))
GRAPH = frozenset((
    ("a", "b"),
    ("a", "c"),
    ("b", "d"),
    ("c", "d"),
))
REPORTED_CUT = GRAPH


def connected_parts(vertices, edges):
    waiting = set(vertices)
    answer = []
    while waiting:
        reached = {min(waiting)}
        border = set(reached)
        while border:
            following = set()
            for u, v in edges:
                if u in border and v not in reached:
                    following.add(v)
                if v in border and u not in reached:
                    following.add(u)
            reached.update(following)
            border = following
        answer.append(frozenset(reached))
        waiting.difference_update(reached)
    return tuple(answer)


def is_cut(vertices, edges, removed):
    before = len(connected_parts(vertices, edges))
    after = len(connected_parts(vertices, edges.difference(removed)))
    return after > before


def subsets(edge_set, include_full):
    ordered = tuple(sorted(edge_set))
    upper = len(ordered) + 1 if include_full else len(ordered)
    for size in range(upper):
        for choice in combinations(ordered, size):
            yield frozenset(choice)


def is_minimal_cut(vertices, edges, removed):
    if not removed or not is_cut(vertices, edges, removed):
        return False
    return not any(
        is_cut(vertices, edges, smaller)
        for smaller in subsets(removed, False)
    )


def show(edge_set):
    return "{" + ",".join(u + v for u, v in sorted(edge_set)) + "}"


def main():
    assert is_cut(VERTICES, GRAPH, REPORTED_CUT)

    first_choices = tuple(
        choice
        for choice in subsets(REPORTED_CUT, False)
        if is_minimal_cut(VERTICES, GRAPH, choice)
    )
    assert len(first_choices) == 6
    assert all(len(choice) == 2 for choice in first_choices)

    valid_procedure_outputs = 0
    example_blocks = None
    for first_bond in first_choices:
        sides = connected_parts(VERTICES, GRAPH.difference(first_bond))
        assert len(sides) == 2
        leftover = REPORTED_CUT.difference(first_bond)

        # On this input G-first_bond is a two-edge forest.  Consequently each
        # remaining edge is already a one-edge bond in the induced component
        # to which the proof recurses, so the proof emits the following blocks.
        local_singletons = []
        for edge in sorted(leftover):
            containing_side = next(
                side for side in sides if edge[0] in side and edge[1] in side
            )
            induced_edges = frozenset(
                candidate for candidate in GRAPH
                if candidate[0] in containing_side and candidate[1] in containing_side
            )
            singleton = frozenset((edge,))
            assert is_minimal_cut(containing_side, induced_edges, singleton)
            local_singletons.append(singleton)

        blocks = (first_bond,) + tuple(local_singletons)
        assert frozenset().union(*blocks) == REPORTED_CUT
        assert sum(len(block) for block in blocks) == len(REPORTED_CUT)
        if all(is_minimal_cut(VERTICES, GRAPH, block) for block in blocks):
            valid_procedure_outputs += 1
        if first_bond == frozenset((("b", "d"), ("c", "d"))):
            example_blocks = blocks

    assert valid_procedure_outputs == 0
    assert example_blocks is not None
    singleton_flags = tuple(
        is_cut(VERTICES, GRAPH, block) for block in example_blocks[1:]
    )
    assert singleton_flags == (False, False)

    correct_partition = (
        frozenset((("a", "b"), ("a", "c"))),
        frozenset((("b", "d"), ("c", "d"))),
    )
    assert frozenset().union(*correct_partition) == REPORTED_CUT
    assert sum(len(block) for block in correct_partition) == len(REPORTED_CUT)
    assert all(
        is_minimal_cut(VERTICES, GRAPH, block) for block in correct_partition
    )

    print("CONFIRMED: the solution procedure fails on the reported C4 input.")
    print("input_is_cut=True; admissible_first_bonds=6")
    print("valid_outputs_over_all_first_choices=0")
    print("example_output=" + " | ".join(show(block) for block in example_blocks))
    print("example_singletons_are_global_cuts=False,False")
    print("valid_global_partition=" + " | ".join(
        show(block) for block in correct_partition
    ))
    print("line_0051_lifting_claim=substantive_false_claim_not_typo")


if __name__ == "__main__":
    main()
