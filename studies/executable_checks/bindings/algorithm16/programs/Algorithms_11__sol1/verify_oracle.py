#!/usr/bin/env python3

# Independent exact check of the reported K_{1,3} instance.

VERTICES = (0, 1, 2, 3)
EDGES = ((0, 1), (0, 2), (0, 3))
ALL = (1 << len(VERTICES)) - 1
K = 1
BOAT_CAPACITY = K + 1
PASSENGER_CAPACITY = BOAT_CAPACITY - 1
LEFT = 0
RIGHT = 1


def has(mask, vertex):
    return (mask & (1 << vertex)) != 0


def independent(mask):
    for first, second in EDGES:
        if has(mask, first) and has(mask, second):
            return False
    return True


def covers_every_edge(mask):
    for first, second in EDGES:
        if not has(mask, first) and not has(mask, second):
            return False
    return True


def safe_state(left_mask, charon_side):
    if charon_side == LEFT:
        unattended = ALL ^ left_mask
    else:
        unattended = left_mask
    return independent(unattended)


def possible_payloads(source_mask):
    # On this reported input the ferry can carry zero or one passenger.
    assert PASSENGER_CAPACITY == 1
    payloads = [0]
    for vertex in VERTICES:
        singleton = 1 << vertex
        if source_mask & singleton:
            payloads.append(singleton)
    return tuple(payloads)


def successors(state):
    left_mask, charon_side = state
    if charon_side == LEFT:
        source = left_mask
    else:
        source = ALL ^ left_mask

    result = []
    for payload in possible_payloads(source):
        if charon_side == LEFT:
            next_state = (left_mask ^ payload, RIGHT)
        else:
            next_state = (left_mask | payload, LEFT)
        if safe_state(next_state[0], next_state[1]):
            result.append(next_state)
    return tuple(result)


def complete_reachable_set():
    initial = (ALL, LEFT)
    reached = {initial}
    pending = [initial]
    while pending:
        state = pending.pop()
        for next_state in successors(state):
            if next_state not in reached:
                reached.add(next_state)
                pending.append(next_state)
    return reached


def names(mask):
    labels = ("center", "leaf1", "leaf2", "leaf3")
    return "{" + ",".join(labels[v] for v in VERTICES if has(mask, v)) + "}"


def apply_prescribed_move(state, payload, expected_side):
    left_mask, charon_side = state
    assert charon_side == expected_side
    source = left_mask if charon_side == LEFT else ALL ^ left_mask
    assert payload & ~source == 0
    assert payload.bit_count() <= PASSENGER_CAPACITY
    if charon_side == LEFT:
        following = (left_mask ^ payload, RIGHT)
    else:
        following = (left_mask | payload, LEFT)
    return following, safe_state(following[0], following[1])


def audit_solution_cycle_prefix():
    center = 1 << 0
    leaf1 = 1 << 1
    prescribed = (
        (center, LEFT, "cycle 1 step 1"),
        (0, RIGHT, "cycle 1 step 2"),
        (leaf1, LEFT, "cycle 1 step 3"),
        (center, RIGHT, "cycle 1 step 4"),
        (center, LEFT, "cycle 2 step 1"),
        (0, RIGHT, "cycle 2 step 2"),
    )
    state = (ALL, LEFT)
    audit = []
    for payload, side, label in prescribed:
        state, safe = apply_prescribed_move(state, payload, side)
        unattended = state[0] if state[1] == RIGHT else ALL ^ state[0]
        audit.append((label, safe, unattended))
    return tuple(audit)


def main():
    cover_sizes = [mask.bit_count() for mask in range(ALL + 1)
                   if covers_every_edge(mask)]
    minimum_cover_size = min(cover_sizes)
    center_mask = 1 << 0
    assert minimum_cover_size == K
    assert covers_every_edge(center_mask)

    reached = complete_reachable_set()
    goal = (0, RIGHT)
    feasible = goal in reached
    assert not feasible

    audit = audit_solution_cycle_prefix()
    first_unsafe = next(item for item in audit if not item[1])
    label, safe, unattended = first_unsafe
    assert not safe
    assert label == "cycle 2 step 2"
    assert unattended == ((1 << 0) | (1 << 1))
    assert not independent(unattended)

    print("Independent exact verification on G=K_{1,3}, K=1, k=2")
    print("minimum vertex-cover size:", minimum_cover_size)
    print("center alone is a size-1 vertex cover:", covers_every_edge(center_mask))
    print("reachable safe states from the initial state:", len(reached))
    print("all passengers can reach the right bank:", feasible)
    print("prescribed schedule first becomes unsafe at:", label)
    print("unattended bank then contains:", names(unattended))
    print("CONCLUSION: CONFIRMED -- a Vertex-Cover YES instance maps to a river-crossing NO instance.")


if __name__ == "__main__":
    main()
