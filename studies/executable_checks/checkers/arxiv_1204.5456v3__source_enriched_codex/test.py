"""Lemma 2.4(iv) claims that its probability bound holds for any two paths, including the case P_1=P_2."""

import itertools
import json


def main():
    equality_patterns = tuple(itertools.product((False, True), repeat=1))
    visited = []
    for (paths_equal,) in equality_patterns:
        visited.append("P_1=P_2" if paths_equal else "P_1!=P_2")

    assert visited == ["P_1!=P_2", "P_1=P_2"]

    result = {
        "record_id": "arxiv_1204.5456v3__source_enriched_codex",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be evaluated from the supplied quote.",
        "refutation_explanation": "The quote states the bound for any two paths but does not define B_P, H_{P_1,P_2}, dim, l, p, the path domain, or the probability model. The equal-path case is one of the two equality patterns swept, but the bound cannot be numerically or symbolically checked without inventing absent definitions.",
        "search_space": "Exactly the two possible equality patterns for an ordered pair of path labels: P_1=P_2 and P_1!=P_2. Both were visited once; no semantic path or probability instances were supplied to enumerate."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
