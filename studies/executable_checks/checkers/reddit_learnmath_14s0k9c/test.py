"""Under an embedding into a symmetric group, every element of order 2 must map to a single transposition."""

import itertools
import json


def compose(permutation, permutation_again):
    return tuple(permutation[permutation_again[index]] for index in range(len(permutation)))


def is_embedding_image_of_c2(permutation):
    identity = tuple(range(len(permutation)))
    return permutation != identity and compose(permutation, permutation) == identity


def is_single_transposition(permutation):
    moved = tuple(index for index, image in enumerate(permutation) if index != image)
    return (
        len(moved) == 2
        and permutation[moved[0]] == moved[1]
        and permutation[moved[1]] == moved[0]
    )


def cycle_notation(permutation):
    visited = [False] * len(permutation)
    cycles = []
    for start in range(len(permutation)):
        if not visited[start] and permutation[start] != start:
            cycle = []
            current = start
            while not visited[current]:
                visited[current] = True
                cycle.append(current + 1)
                current = permutation[current]
            cycles.append("(" + " ".join(str(value) for value in cycle) + ")")
    return "".join(cycles) if cycles else "()"


def main():
    witnesses = []
    permutation_count = 0
    for degree in range(1, 5):
        for permutation in itertools.permutations(range(degree)):
            permutation_count += 1
            if is_embedding_image_of_c2(permutation) and not is_single_transposition(permutation):
                witnesses.append((degree, permutation))

    if permutation_count != 33:
        raise AssertionError("unexpected search-space size")
    if not witnesses:
        raise AssertionError("the bounded exhaustive search found no witness")

    degree, witness = witnesses[0]
    notation = cycle_notation(witness)
    if degree != 4 or notation != "(1 2)(3 4)":
        raise AssertionError("unexpected first witness")

    result = {
        "record_id": "reddit_learnmath_14s0k9c",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Embed C2 into S4 by sending its nonidentity element to (1 2)(3 4).",
        "refutation_explanation": "The permutation (1 2)(3 4) is nonidentity and its square is the identity, so it has order 2 and defines an injective homomorphism C2 -> S4. Its image is a product of two disjoint transpositions, not a single transposition, contradicting the claim.",
        "search_space": "All 33 permutations in S_n for n=1,2,3,4, in lexicographic tuple order; every nonidentity involution was treated as the possible image of the generator under an embedding C2 -> S_n, and the lexicographically first image that was not a single transposition was selected."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
