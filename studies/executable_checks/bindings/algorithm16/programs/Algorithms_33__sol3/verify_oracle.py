#!/usr/bin/env python3

RECORD = "Algorithms_33__sol3"
VERTICES = tuple(range(4))
EDGES = ((0, 1), (1, 2), (2, 3), (0, 3))
S_SIDE = frozenset((0, 2))


class DisjointSets:
    def __init__(self, items):
        self.parent = {item: item for item in items}

    def representative(self, item):
        trail = []
        while self.parent[item] != item:
            trail.append(item)
            item = self.parent[item]
        for old in trail:
            self.parent[old] = item
        return item

    def join(self, left, right):
        left_root = self.representative(left)
        right_root = self.representative(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def normalized_edge(left, right):
    if left < right:
        return (left, right)
    return (right, left)


def boundary(vertex_set):
    return frozenset(
        normalized_edge(left, right)
        for left, right in EDGES
        if (left in vertex_set) != (right in vertex_set)
    )


def induced_component_labels(side):
    labels = DisjointSets(side)
    for left, right in EDGES:
        if left in side and right in side:
            labels.join(left, right)
    return {vertex: labels.representative(vertex) for vertex in side}


def component_sets(labels):
    groups = {}
    for vertex, label in labels.items():
        groups.setdefault(label, set()).add(vertex)
    return tuple(sorted((tuple(sorted(group)) for group in groups.values())))


def solution_pieces():
    other_side = frozenset(VERTICES) - S_SIDE
    s_labels = induced_component_labels(S_SIDE)
    t_labels = induced_component_labels(other_side)
    pieces = {}
    for edge in boundary(S_SIDE):
        left, right = edge
        if left in S_SIDE:
            s_vertex, t_vertex = left, right
        else:
            s_vertex, t_vertex = right, left
        key = (s_labels[s_vertex], t_labels[t_vertex])
        pieces.setdefault(key, set()).add(edge)
    ordered_pieces = (frozenset(piece) for piece in pieces.values())
    return s_labels, t_labels, tuple(
        sorted(ordered_pieces, key=lambda piece: tuple(sorted(piece)))
    )


def every_nontrivial_cut():
    cuts = set()
    full_mask = (1 << len(VERTICES)) - 1
    for mask in range(1, full_mask):
        if mask & 1:
            chosen = frozenset(
                vertex for vertex in VERTICES if mask & (1 << vertex)
            )
            cuts.add(boundary(chosen))
    return cuts


def component_count(removed):
    labels = DisjointSets(VERTICES)
    for left, right in EDGES:
        if normalized_edge(left, right) not in removed:
            labels.join(left, right)
    return len({labels.representative(vertex) for vertex in VERTICES})


def edge_text(edge):
    return "%d-%d" % edge


def edges_text(edge_set):
    return "{" + ",".join(edge_text(edge) for edge in sorted(edge_set)) + "}"


def main():
    s_labels, t_labels, pieces = solution_pieces()
    original_cut = boundary(S_SIDE)
    cut_catalogue = every_nontrivial_cut()
    base_components = component_count(frozenset())

    assert component_sets(s_labels) == ((0,), (2,))
    assert component_sets(t_labels) == ((1,), (3,))
    assert original_cut == frozenset(EDGES)
    assert len(pieces) == 4
    assert all(len(piece) == 1 for piece in pieces)
    assert frozenset().union(*pieces) == original_cut

    results = []
    for piece in pieces:
        is_a_cut = piece in cut_catalogue
        after_removal = component_count(piece)
        results.append((piece, is_a_cut, after_removal))
        assert not is_a_cut
        assert after_removal == base_components

    example = frozenset(((0, 1),))
    assert example in pieces
    assert boundary(frozenset((0,))) == frozenset(((0, 1), (0, 3)))

    print("record_id: " + RECORD)
    print("delta({0,2}): " + edges_text(original_cut))
    print("components of G[S]: {0}, {2}")
    print("components of G[T]: {1}, {3}")
    print("solution Cij pieces: " + ", ".join(edges_text(piece) for piece in pieces))
    print("distinct cut-sets from all proper bipartitions: %d" % len(cut_catalogue))
    for piece, is_a_cut, after_removal in results:
        print(
            "%s: is delta(X)=%s; components before=%d after deletion=%d"
            % (edges_text(piece), is_a_cut, base_components, after_removal)
        )
    print("delta({0}) is " + edges_text(boundary(frozenset((0,)))))
    print("CONCLUSION: CONFIRMED - all four claimed Cij are not cut-sets.")


if __name__ == "__main__":
    main()
