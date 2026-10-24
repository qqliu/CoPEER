#!/usr/bin/env python3


def main():
    vertex_count = 4
    reported_edges = (
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 2),
        (1, 3),
        (2, 3),
    )

    # The proposed reduction makes no graph change.
    reduced_vertex_count = vertex_count
    reduced_edges = reported_edges
    assert reduced_vertex_count == vertex_count
    assert reduced_edges == reported_edges

    # Independently inspect every map from the four vertices to three colors.
    assignments_checked = 0
    proper_three_coloring = None
    for encoded_assignment in range(3 ** vertex_count):
        residue = encoded_assignment
        assignment = []
        for unused_vertex in range(vertex_count):
            residue, color = divmod(residue, 3)
            assignment.append(color)
        assignments_checked += 1

        has_conflict = False
        for endpoint_a, endpoint_b in reported_edges:
            if assignment[endpoint_a] == assignment[endpoint_b]:
                has_conflict = True
                break
        if not has_conflict:
            proper_three_coloring = tuple(assignment)
            break

    assert assignments_checked == 81
    assert proper_three_coloring is None

    # Four distinct palette entries give a proper coloring using at most 12.
    twelve_color_witness = (0, 1, 2, 3)
    assert len(twelve_color_witness) == reduced_vertex_count
    assert all(0 <= color < 12 for color in twelve_color_witness)
    witness_is_proper = all(
        twelve_color_witness[endpoint_a] != twelve_color_witness[endpoint_b]
        for endpoint_a, endpoint_b in reduced_edges
    )
    assert witness_is_proper

    # The solution maps each palette entry to its within-group index.
    recovered_colors = tuple(color % 3 for color in twelve_color_witness)
    recovery_conflicts = tuple(
        edge
        for edge in reported_edges
        if recovered_colors[edge[0]] == recovered_colors[edge[1]]
    )
    assert recovered_colors == (0, 1, 2, 0)
    assert recovery_conflicts == ((0, 3),)

    three_colorable = proper_three_coloring is not None
    reduced_graph_twelve_colorable = witness_is_proper
    assert three_colorable is False
    assert reduced_graph_twelve_colorable is True
    assert three_colorable != reduced_graph_twelve_colorable

    print("CONFIRMED: the identity reduction fails on the reported K4.")
    print("Exact 3-color assignments checked: 81; proper assignments found: 0.")
    print("Proper at-most-12-color witness for unchanged K4: (0, 1, 2, 3).")
    print("Claimed recovery gives (0, 1, 2, 0), conflicting on edge (0, 3).")


if __name__ == "__main__":
    main()
