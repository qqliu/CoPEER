"""A bijection between the edge sets of two graphs with equally sized vertex sets implies that the graphs are isomorphic."""

import itertools
import json

REPORT = {
    "record_id": "reddit_learnmath_o65dcu",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: both graphs have four vertices and two edges, so the displayed edge correspondence is a bijection, while exhaustive checking of all vertex bijections finds no graph isomorphism; their degree multisets also differ. The refuted statement is substantive, not plainly a typo.",
}

vertices_g = (0, 1, 2, 3)
vertices_h = (0, 1, 2, 3)
edges_g = frozenset(((0, 1), (0, 2)))
edges_h = frozenset(((0, 3), (1, 2)))
edge_correspondence = (((0, 1), (0, 3)), ((0, 2), (1, 2)))

assert len(vertices_g) == len(vertices_h) == 4
assert all(left in vertices_g and right in vertices_g and left != right for left, right in edges_g)
assert all(left in vertices_h and right in vertices_h and left != right for left, right in edges_h)
assert frozenset(source for source, target in edge_correspondence) == edges_g
assert frozenset(target for source, target in edge_correspondence) == edges_h
assert len(edge_correspondence) == len(edges_g) == len(edges_h)

degrees_g = tuple(sorted(sum(vertex in edge for edge in edges_g) for vertex in vertices_g))
degrees_h = tuple(sorted(sum(vertex in edge for edge in edges_h) for vertex in vertices_h))
assert degrees_g == (0, 1, 1, 2)
assert degrees_h == (1, 1, 1, 1)
assert degrees_g != degrees_h

def image_edges(vertex_images):
    images = []
    for left, right in edges_g:
        mapped_left = vertex_images[left]
        mapped_right = vertex_images[right]
        if mapped_left < mapped_right:
            images.append((mapped_left, mapped_right))
        else:
            images.append((mapped_right, mapped_left))
    return frozenset(images)

vertex_bijections = tuple(itertools.permutations(vertices_h))
assert len(vertex_bijections) == 24
assert all(image_edges(vertex_images) != edges_h for vertex_images in vertex_bijections)

assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, separators=(",", ":")))
