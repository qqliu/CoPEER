#!/usr/bin/env python3
"""Independent exact checker for Algorithms_21__sol5, at reported n = 12."""


def process_current_entry(labels, ready, vertex, size):
    """Process one current queue entry and count its outgoing Relax calls."""
    changed = list(labels)
    next_ready = ready & ~(1 << vertex)
    offered = labels[vertex] - (1 << vertex)
    for head in range(vertex + 1, size):
        if offered < changed[head]:
            changed[head] = offered
            next_ready |= 1 << head
    return tuple(changed), next_ready, size - vertex - 1


def maximum_relax_count(size):
    """Enumerate all legal choices among equal minimum current labels.

    A bit in ``ready`` represents the unique queue entry carrying a vertex's
    current label.  Older entries made stale by a strict decrease are omitted:
    popping one invokes no Relax operation and changes no label, so deleting it
    cannot alter this operation-count maximum.
    """
    initial_labels = (0,) + (-1,) * (size - 1)
    initial_ready = ((1 << size) - 1) & ~1
    initial_calls = size - 1

    start = (initial_labels, initial_ready)
    best_prefix = {start: initial_calls}
    agenda = [start]
    terminal_maximum = -1

    while agenda:
        state = agenda.pop()
        labels, ready = state
        calls_so_far = best_prefix[state]
        if ready == 0:
            if calls_so_far > terminal_maximum:
                terminal_maximum = calls_so_far
            continue

        minimum = None
        scan = ready
        while scan:
            bit = scan & -scan
            vertex = bit.bit_length() - 1
            value = labels[vertex]
            if minimum is None or value < minimum:
                minimum = value
            scan -= bit

        choices = []
        scan = ready
        while scan:
            bit = scan & -scan
            vertex = bit.bit_length() - 1
            if labels[vertex] == minimum:
                choices.append(vertex)
            scan -= bit

        for vertex in choices:
            new_labels, new_ready, added = process_current_entry(
                labels, ready, vertex, size
            )
            successor = (new_labels, new_ready)
            candidate = calls_so_far + added
            previous = best_prefix.get(successor)
            if previous is None or candidate > previous:
                best_prefix[successor] = candidate
                agenda.append(successor)

    return terminal_maximum, len(best_prefix)


def fixed_tie_relax_count(size, prefer_larger):
    """Run the same model with a fixed index rule for equal labels."""
    labels = (0,) + (-1,) * (size - 1)
    ready = ((1 << size) - 1) & ~1
    calls = size - 1
    while ready:
        vertices = [v for v in range(size) if ready & (1 << v)]
        least = min(labels[v] for v in vertices)
        tied = [v for v in vertices if labels[v] == least]
        vertex = max(tied) if prefer_larger else min(tied)
        labels, ready, added = process_current_entry(
            labels, ready, vertex, size
        )
        calls += added
    return calls


def main():
    size = 12
    edge_count = size * (size - 1) // 2
    structure_ok = all(
        tail < head and -(1 << tail) < 0
        for tail in range(size)
        for head in range(tail + 1, size)
    )

    low_index_calls = fixed_tie_relax_count(size, False)
    high_index_calls = fixed_tie_relax_count(size, True)
    all_execution_maximum, states = maximum_relax_count(size)
    claimed_minimum = (1 << size) - 1

    assert structure_ok
    assert edge_count == 66
    assert low_index_calls == 66
    assert high_index_calls == all_execution_maximum
    assert all_execution_maximum < claimed_minimum

    print("record_id=Algorithms_21__sol5")
    print("input=n=12; vertices=12; edges=66; forward_DAG_and_negative=True")
    print("Relax calls, low-index ties={}".format(low_index_calls))
    print("Relax calls, high-index ties={}".format(high_index_calls))
    print("Relax calls, exact maximum over all legal tie choices={}".format(
        all_execution_maximum
    ))
    print("distinct reduced queue states checked={}".format(states))
    print("claimed required minimum={}".format(claimed_minimum))
    print("CONCLUSION: CONFIRMED; exact maximum is below claimed minimum")


if __name__ == "__main__":
    main()
