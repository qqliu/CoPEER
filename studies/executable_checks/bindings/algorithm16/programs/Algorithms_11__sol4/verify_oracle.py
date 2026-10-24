#!/usr/bin/env python3

# Independent check of the reported P4 execution of the schedule in the solution.
vertices = frozenset((0, 1, 2, 3))
edges = frozenset(((0, 1), (1, 2), (2, 3)))
cover = frozenset((1, 2))
K = 2
capacity = K + 1
noncover = vertices - cover


def internal_edges(bank):
    return tuple(sorted(edge for edge in edges if edge[0] in bank and edge[1] in bank))


assert len(cover) == K
assert all(u in cover or v in cover for u, v in edges)
assert not internal_edges(noncover)

# The solution labels c1 = 1 and c2 = 2.  These are its initial trip,
# two stated cover rounds, and its stated empty return and final load.
trips = (
    ("L", "R", cover),
    ("R", "L", cover - frozenset((1,))),
    ("L", "R", cover - frozenset((1,))),
    ("R", "L", cover - frozenset((2,))),
    ("L", "R", cover - frozenset((2,))),
    ("R", "L", frozenset()),
    ("L", "R", noncover),
)

banks = {"L": set(vertices), "R": set()}
charon = "L"
first_failure = None

print("P4 edges:", sorted(edges))
print("C:", sorted(cover), "is_vertex_cover:",
      all(u in cover or v in cover for u, v in edges))
print("V-C:", sorted(noncover), "internal_edges:", internal_edges(noncover))
print("capacity including Charon:", capacity, "passenger_limit:", capacity - 1)

for number, (source, destination, load) in enumerate(trips, 1):
    assert charon == source
    assert destination != source
    assert load <= banks[source]
    assert len(load) + 1 <= capacity

    banks[source].difference_update(load)
    banks[destination].update(load)
    charon = destination

    unattended = banks[source]
    conflicts = internal_edges(unattended)
    print("trip", number, source + "->" + destination, "load", sorted(load),
          "unattended", source, sorted(unattended), "internal_edges", conflicts)
    if conflicts and first_failure is None:
        first_failure = (number, source, tuple(sorted(unattended)), conflicts)

assert first_failure == (6, "R", (1, 2), ((1, 2),))
print("CONFIRMED: after completed trip 6, Charon is on L while unattended R contains edge (1, 2).")
