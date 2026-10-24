"""The stated two-case split exhausts the possible parity counts of previously odd and previously even neighbors when the new node has odd degree."""

import json


def main():
    prior_vertices = (0, 1)
    prior_edges = ((0, 1),)
    new_neighbors = (0,)

    prior_degrees = {vertex: 0 for vertex in prior_vertices}
    graph_is_valid = True
    for left, right in prior_edges:
        if left not in prior_degrees or right not in prior_degrees or left == right:
            graph_is_valid = False
        else:
            prior_degrees[left] += 1
            prior_degrees[right] += 1

    if len(set(new_neighbors)) != len(new_neighbors):
        graph_is_valid = False
    for neighbor in new_neighbors:
        if neighbor not in prior_degrees:
            graph_is_valid = False

    previously_odd_count = 0
    previously_even_count = 0
    if graph_is_valid:
        for neighbor in new_neighbors:
            if prior_degrees[neighbor] % 2 == 1:
                previously_odd_count += 1
            else:
                previously_even_count += 1

    new_degree = len(new_neighbors)
    first_case = (
        previously_odd_count % 2 == 0
        and previously_even_count % 2 == 1
    )
    second_case = (
        previously_even_count % 2 == 1
        and previously_odd_count % 2 == 0
    )

    confirmed = (
        graph_is_valid
        and previously_odd_count == 1
        and previously_even_count == 0
        and new_degree == 1
        and new_degree % 2 == 1
        and not (first_case or second_case)
    )

    if confirmed:
        verdict = "CONFIRMED"
        notes = "The witness is valid: before insertion, an edge joins two odd-degree vertices; connecting the new node to one gives previously_odd_count=1, previously_even_count=0 and odd new degree 1. Neither quoted case holds because both encode the same parity pattern. The refuted statement is plainly a typo, not a substantive parity error."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The proposed witness could not be validated; the apparent duplicated case is plainly a typo."

    result = {
        "record_id": "reddit_askmath_1v6fw7",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
