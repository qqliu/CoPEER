#!/usr/bin/env python3
"""Independent exact operation counter for the reported G_20 witness."""

from heapq import heappop, heappush


PARAMETER = 20
SOURCE = (-1, 0)


def arcs_from(vertex, parameter):
    """Generate precisely the outgoing arcs in the solution's layered graph."""
    level, bit = vertex
    target = (parameter, 0)
    if vertex == SOURCE:
        return (((1, 0), 0), ((1, 1), 0))
    if 1 <= level < parameter - 1:
        magnitude = 1 << level
        weight = magnitude if bit == 0 else 1 - magnitude
        return (((level + 1, 0), weight), ((level + 1, 1), weight))
    if level == parameter - 1:
        return ((target, 0),)
    return ()


def count_execution(parameter):
    """Count a lazy re-insertion execution, breaking sibling ties by bit 0 first."""
    labels = {SOURCE: 0}
    pending = [(0, SOURCE)]
    relax_invocations = 0
    successful = 0
    successful_at_target = 0
    processed = 0
    successes_by_head_level = {}
    target = (parameter, 0)

    while pending:
        key, vertex = heappop(pending)
        if labels.get(vertex) != key:
            continue
        processed += 1
        for head, weight in arcs_from(vertex, parameter):
            relax_invocations += 1
            candidate = key + weight
            previous = labels.get(head)
            if previous is None or candidate < previous:
                labels[head] = candidate
                heappush(pending, (candidate, head))
                successful += 1
                head_level = head[0]
                successes_by_head_level[head_level] = (
                    successes_by_head_level.get(head_level, 0) + 1
                )
                if head == target:
                    successful_at_target += 1

    return (
        relax_invocations,
        successful,
        successful_at_target,
        processed,
        successes_by_head_level,
        labels,
    )


def main():
    n = PARAMETER
    (
        calls,
        successes,
        target_successes,
        processed,
        by_level,
        labels,
    ) = count_execution(n)

    expected_levels = {1: 2, n: 1}
    for level in range(2, n):
        expected_levels[level] = 4

    vertex_count = 2 * n
    linear_success_bound = 4 * n - 5
    linear_call_count = 4 * n - 4
    claimed_target_count = 1 << (n - 1)

    assert vertex_count == 40
    assert by_level == expected_levels
    assert processed == vertex_count
    assert successes == linear_success_bound == 75
    assert calls == linear_call_count == 76
    assert target_successes == 1
    assert claimed_target_count == 524288
    assert len(labels) == vertex_count

    print("CONFIRMED: the reported G_20 execution is linear, not exponential.")
    print("vertices=40")
    print("Relax invocations=76")
    print("successful Relax operations=75")
    print("successful Relax operations at t=1")
    print("solution's claimed target-path count=" + str(claimed_target_count))
    print("per-level successful counts: level 1 -> 2, levels 2..19 -> 4, t -> 1")
    print("universal structural upper bound for this family: 4*n-5 successful")
    print("Reason: equal-tail arcs give each sibling pair equal labels; the cheaper")
    print("bit-1 predecessor is queued before either worse child can be processed.")


if __name__ == "__main__":
    main()
