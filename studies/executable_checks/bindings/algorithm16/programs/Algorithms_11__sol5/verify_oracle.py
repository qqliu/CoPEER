#!/usr/bin/env python3

"""Independent exact check of the reported K2, c=1 counterexample."""

N = 2
C = 1
K = C + 1
EDGES = ((0, 1),)
ALL_LEFT = (1 << N) - 1


def member(mask, vertex):
    return (mask & (1 << vertex)) != 0


def independent(mask):
    for first, second in EDGES:
        if member(mask, first) and member(mask, second):
            return False
    return True


def safe(left_mask, charon_on_right):
    if charon_on_right:
        unattended = left_mask
    else:
        unattended = ALL_LEFT ^ left_mask
    return independent(unattended)


def passenger_count(mask):
    count = 0
    for vertex in range(N):
        if member(mask, vertex):
            count += 1
    return count


def next_states(state):
    left_mask, charon_on_right = state
    if charon_on_right:
        available = ALL_LEFT ^ left_mask
    else:
        available = left_mask

    results = []
    for carried in range(1 << N):
        if carried & (ALL_LEFT ^ available):
            continue
        if passenger_count(carried) > K - 1:
            continue
        if charon_on_right:
            new_left = left_mask | carried
        else:
            new_left = left_mask & (ALL_LEFT ^ carried)
        candidate = (new_left, not charon_on_right)
        if safe(candidate[0], candidate[1]):
            results.append(candidate)
    return results


def crossing_reachable():
    start = (ALL_LEFT, False)
    goal = (0, True)
    reached = {start}
    changed = True
    while changed:
        changed = False
        snapshot = tuple(sorted(reached))
        for state in snapshot:
            for candidate in next_states(state):
                if candidate not in reached:
                    reached.add(candidate)
                    changed = True
    return goal in reached, reached


def one_colorable():
    colors = (0,) * N
    for first, second in EDGES:
        if colors[first] == colors[second]:
            return False
    return True


def validate_reported_witness():
    state = (ALL_LEFT, False)
    moves = (1 << 0, 0, 1 << 1)
    expected_sides = (False, True, False)
    for carried, expected_side in zip(moves, expected_sides):
        if state[1] != expected_side:
            return False
        successors = next_states(state)
        if state[1]:
            new_left = state[0] | carried
        else:
            new_left = state[0] & (ALL_LEFT ^ carried)
        state = (new_left, not state[1])
        if state not in successors:
            return False
    return state == (0, True)


def main():
    colorable = one_colorable()
    feasible, reached = crossing_reachable()
    witness_valid = validate_reported_witness()

    assert K == 2
    assert not colorable
    assert feasible
    assert witness_valid

    print("input: G=K2, c=1, solution reduction gives k=2")
    print("exact 1-colorability: False")
    print("exact crossing reachability: True")
    print("validated crossing: take 0 L->R; return alone; take 1 L->R")
    print("reachable legal states:", len(reached))
    print("conclusion: the claimed equivalence fails on the reported input")


if __name__ == "__main__":
    main()
