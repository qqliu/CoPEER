"""Thus if we can reach a root of the tree from each of its vertices after going down at most $m$ moves, we should have the inequality $k[k(k-1)]^{m-1}\\ge P=(p,k)$."""

import json


def main():
    candidate_instances = ()
    witness = None
    for candidate in candidate_instances:
        witness = candidate
        break

    assert witness is None
    result = {
        "record_id": "mse_427652__ans429754",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be formed from the supplied quote because it gives no definitions or admissible instances.",
        "refutation_explanation": "The quote does not define the tree, its roots, what a downward move is, the domains of k, m, and p, or the meaning of P=(p,k). Assigning any of those meanings would invent absent data, so the inequality cannot be evaluated.",
        "search_space": "Exhaustively swept the empty finite tuple of fully specified candidate instances supplied by the quote: exactly 0 instances.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
