"""If every minimal vertex separator of a connected noncomplete unichord-free graph is a singleton, then the graph is a tree and is 2-colorable."""

import json
from itertools import combinations

RECORD_ID = "arxiv_1311.1928v3__source_enriched_codex"
MAX_VERTICES = 6

WITNESS_DESCRIPTION = (
    "No certified counterexample was found; all 33,867 enumerated graph "
    "encodings remained semantically undecidable from the supplied text."
)
REFUTATION_EXPLANATION = (
    "The supplied quote does not define \"unichord-free\" or \"minimal vertex "
    "separator,\" so the antecedent cannot be evaluated without adding "
    "definitions. Consequently the finite enumeration cannot certify or "
    "refute the claim."
)
SEARCH_SPACE = (
    "All 33,867 labeled undirected loopless simple-graph edge encodings on "
    "vertex sets {0,...,n-1} for n=1,...,6 (equivalently, all masks from 0 "
    "through 2^(n choose 2)-1 for each n), in increasing n and mask order. "
    "The sweep is illustrative only because the quoted text supplies no "
    "predicate definitions."
)


def graph_encodings(max_vertices):
    """Yield every edge-mask encoding in a fixed, explicitly bounded order."""
    for vertex_count in range(1, max_vertices + 1):
        edge_slots = tuple(combinations(range(vertex_count), 2))
        for mask in range(1 << len(edge_slots)):
            edges = tuple(
                edge_slots[index]
                for index in range(len(edge_slots))
                if mask & (1 << index)
            )
            yield vertex_count, mask, edges


def status_from_supplied_text(vertex_count, mask, edges):
    """Return None because the supplied text gives no rules for key predicates."""
    del vertex_count, mask, edges
    return None


def main():
    scanned = 0
    unresolved = 0
    witness = None

    for vertex_count, mask, edges in graph_encodings(MAX_VERTICES):
        scanned += 1
        status = status_from_supplied_text(vertex_count, mask, edges)
        if status is None:
            unresolved += 1
        elif status:
            witness = (vertex_count, mask, edges)
            break

    expected = sum(
        1 << (vertex_count * (vertex_count - 1) // 2)
        for vertex_count in range(1, MAX_VERTICES + 1)
    )
    assert scanned == expected == 33867
    assert unresolved == scanned
    assert witness is None

    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
