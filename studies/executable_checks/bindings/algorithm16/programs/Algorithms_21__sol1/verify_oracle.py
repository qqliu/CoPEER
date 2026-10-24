#!/usr/bin/env python3
"""Independent exact operation-count oracle for the reported G_7 input."""

LEVELS = 7
BASE = 33


def make_instance():
    """Encode the vertices in the solution's displayed topological order."""
    labels = ["a0"]
    for level in range(1, LEVELS + 1):
        labels.extend(("b" + str(level), "a" + str(level)))
    labels.append("t")

    arcs = [[] for _ in labels]
    for level in range(1, LEVELS + 1):
        previous_a = 2 * (level - 1)
        b_vertex = 2 * level - 1
        next_a = 2 * level
        weight = BASE ** (LEVELS - level)
        arcs[previous_a].append((next_a, 0))
        arcs[previous_a].append((b_vertex, weight))
        arcs[b_vertex].append((next_a, -weight - 1))
    arcs[2 * LEVELS].append((len(labels) - 1, 0))
    return tuple(labels), tuple(tuple(row) for row in arcs)


def combine(old, new):
    """Join independently attainable extrema for two operation counters."""
    joined = (
        min(old[0], new[0]),
        max(old[1], new[1]),
        min(old[2], new[2]),
        max(old[3], new[3]),
    )
    return joined


def enumerate_min_key_runs(arcs):
    """Explore every legal choice among vertices tied for minimum current key.

    A state contains exact integer tentative labels and the set of queued
    vertices.  The four attached values are the minimum and maximum RELAX
    counts and a_7 extraction counts capable of reaching that state.
    """
    vertex_count = len(arcs)
    initial_distances = (0,) + (None,) * (vertex_count - 1)
    initial_state = (initial_distances, 1)
    extrema = {initial_state: (0, 0, 0, 0)}
    pending_states = [initial_state]
    queued_target_was_decreased = False

    while pending_states:
        state = pending_states.pop()
        distances, queue_mask = state
        if queue_mask == 0:
            continue

        queued_vertices = [
            vertex for vertex in range(vertex_count)
            if queue_mask & (1 << vertex)
        ]
        smallest_key = min(distances[vertex] for vertex in queued_vertices)
        legal_extractions = [
            vertex for vertex in queued_vertices
            if distances[vertex] == smallest_key
        ]

        prior = extrema[state]
        for extracted in legal_extractions:
            next_distances = list(distances)
            next_queue = queue_mask & ~(1 << extracted)

            for target, weight in arcs[extracted]:
                proposal = distances[extracted] + weight
                old_label = next_distances[target]
                if old_label is None or proposal < old_label:
                    if next_queue & (1 << target):
                        queued_target_was_decreased = True
                    next_distances[target] = proposal
                    next_queue |= 1 << target

            scanned = len(arcs[extracted])
            extracted_a7 = int(extracted == 2 * LEVELS)
            reached = (tuple(next_distances), next_queue)
            candidate = (
                prior[0] + scanned,
                prior[1] + scanned,
                prior[2] + extracted_a7,
                prior[3] + extracted_a7,
            )

            if reached not in extrema:
                extrema[reached] = candidate
                pending_states.append(reached)
            else:
                joined = combine(extrema[reached], candidate)
                if joined != extrema[reached]:
                    extrema[reached] = joined
                    pending_states.append(reached)

    terminal_states = [state for state in extrema if state[1] == 0]
    terminal_data = [extrema[state] for state in terminal_states]
    overall = (
        min(data[0] for data in terminal_data),
        max(data[1] for data in terminal_data),
        min(data[2] for data in terminal_data),
        max(data[3] for data in terminal_data),
    )
    final_labels = {state[0] for state in terminal_states}
    return overall, final_labels, len(extrema), queued_target_was_decreased


def expected_shortest_labels(vertex_count):
    expected = [None] * vertex_count
    expected[0] = 0
    for level in range(1, LEVELS + 1):
        b_vertex = 2 * level - 1
        a_vertex = 2 * level
        weight = BASE ** (LEVELS - level)
        expected[b_vertex] = weight - (level - 1)
        expected[a_vertex] = -level
    expected[-1] = -LEVELS
    return tuple(expected)


def main():
    names, arcs = make_instance()
    edge_count = sum(len(row) for row in arcs)
    negative_count = sum(
        int(weight < 0) for row in arcs for target, weight in row
    )
    forward = all(
        source < target
        for source, row in enumerate(arcs)
        for target, weight in row
    )

    assert len(names) == 2 * LEVELS + 2
    assert BASE > 2 * LEVELS + 2
    assert edge_count == 3 * LEVELS + 1
    assert negative_count == LEVELS
    assert forward

    counts, final_labels, state_count, collision = enumerate_min_key_runs(arcs)
    minimum_relax, maximum_relax, minimum_t7, maximum_t7 = counts
    expected = expected_shortest_labels(len(names))
    assert final_labels == {expected}
    assert not collision

    claimed = 1 << LEVELS
    confirmed = maximum_relax < claimed

    print("record_id: Algorithms_21__sol1")
    print("input: n=7, vertices=16, B=33, edges=" + str(edge_count))
    print("all edges forward: " + str(forward))
    print("negative edges: " + str(negative_count))
    print("reachable queue states checked: " + str(state_count))
    print("decrease of an already queued vertex: " + str(collision))
    print("RELAX calls over all minimum-key tie choices: min="
          + str(minimum_relax) + ", max=" + str(maximum_relax))
    print("a7 extractions over all minimum-key tie choices: min="
          + str(minimum_t7) + ", max=" + str(maximum_t7))
    print("claimed lower count 2^7: " + str(claimed))
    print("terminal a-labels: "
          + str(tuple(expected[2 * level] for level in range(LEVELS + 1))))
    if confirmed:
        print("CONCLUSION: CONFIRMED; even the maximum legal count is below 2^7.")
    else:
        print("CONCLUSION: CANNOT_REPRODUCE; a legal count reaches 2^7.")


if __name__ == "__main__":
    main()
