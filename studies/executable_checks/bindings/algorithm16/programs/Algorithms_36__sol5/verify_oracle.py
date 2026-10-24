#!/usr/bin/env python3

VERTICES = (1, 2, 3, 4)
T1 = frozenset(((1, 2), (1, 3), (1, 4)))
T2 = frozenset(((1, 2), (2, 3), (3, 4)))
e = (1, 3)
f = (3, 4)


def reachable(start, edges):
    reached = {start}
    pending = [start]
    while pending:
        current = pending.pop()
        for left, right in edges:
            if left == current:
                other = right
            elif right == current:
                other = left
            else:
                continue
            if other not in reached:
                reached.add(other)
                pending.append(other)
    return reached


def tree_status(edges):
    valid_edges = all(
        left in VERTICES and right in VERTICES and left < right
        for left, right in edges
    )
    connected = valid_edges and reachable(VERTICES[0], edges) == set(VERTICES)
    right_size = len(edges) == len(VERTICES) - 1
    return valid_edges and connected and right_size


assert tree_status(T1)
assert tree_status(T2)
assert e in T1

T1_without_e = T1 - {e}
A = reachable(e[0], T1_without_e)
B = set(VERTICES) - A
assert A == {1, 2, 4}
assert B == {3}
assert f in T2
assert (f[0] in A and f[1] in B) or (f[1] in A and f[0] in B)

first_exchange = T1_without_e | {f}
second_exchange = (T2 - {f}) | {e}
first_is_tree = tree_status(first_exchange)
second_is_tree = tree_status(second_exchange)

assert first_exchange == frozenset(((1, 2), (1, 4), (3, 4)))
assert second_exchange == frozenset(((1, 2), (1, 3), (2, 3)))
assert first_is_tree
assert not second_is_tree
assert reachable(1, second_exchange) == {1, 2, 3}

print("A={1,2,4}; B={3}; f=3-4 is a permitted crossing edge")
print("(T1-e)+f edges=1-2,1-4,3-4; tree=True")
print("(T2-f)+e edges=1-2,1-3,2-3; reachable_from_1={1,2,3}; tree=False")
print("CONFIRMED: the solution's 'choose any crossing edge' claim fails")
