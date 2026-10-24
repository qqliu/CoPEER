"""If the linear composition F∘G is one-to-one, then both F and G are one-to-one."""

import json
from itertools import combinations, permutations, product


def determinant(matrix):
    n = len(matrix)
    total = 0
    for permutation in permutations(range(n)):
        inversions = sum(
            1
            for i in range(n)
            for j in range(i + 1, n)
            if permutation[i] > permutation[j]
        )
        term = 1
        for row in range(n):
            term *= matrix[row][permutation[row]]
        if inversions % 2:
            total -= term
        else:
            total += term
    return total


def matrix_rank(matrix):
    row_count = len(matrix)
    column_count = len(matrix[0])
    for size in range(min(row_count, column_count), 0, -1):
        for rows in combinations(range(row_count), size):
            for columns in combinations(range(column_count), size):
                minor = tuple(
                    tuple(matrix[row][column] for column in columns)
                    for row in rows
                )
                if determinant(minor) != 0:
                    return size
    return 0


def matrix_product(left, right):
    return tuple(
        tuple(
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        )
        for i in range(len(left))
    )


def main():
    entries = (0, 1)
    g_matrices = tuple(
        ((values[0],), (values[1],))
        for values in product(entries, repeat=2)
    )
    f_matrices = tuple(
        ((values[0], values[1]),)
        for values in product(entries, repeat=2)
    )

    witnesses = []
    for g_matrix in g_matrices:
        for f_matrix in f_matrices:
            composition = matrix_product(f_matrix, g_matrix)
            composition_is_injective = matrix_rank(composition) == 1
            g_is_injective = matrix_rank(g_matrix) == 1
            f_is_injective = matrix_rank(f_matrix) == 2
            if composition_is_injective and not (f_is_injective and g_is_injective):
                witnesses.append((g_matrix, f_matrix, composition))

    first_witness = witnesses[0]
    assert first_witness == (((0,), (1,)), ((0, 1),), ((1,),))

    result = {
        "record_id": "reddit_learnmath_7bk5gk",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Over Q, let U=Q, V=Q^2, W=Q, G(x)=(0,x), and F(y,z)=z. Then (F∘G)(x)=x, but F is not one-to-one since F(0,0)=F(1,0)=0.",
        "refutation_explanation": "The composition is the identity on Q and hence is one-to-one, while the distinct vectors (0,0) and (1,0) have the same image under F. Therefore the asserted conclusion that both F and G are one-to-one is false.",
        "search_space": "All 16 ordered pairs (G,F) with G a 2×1 and F a 1×2 matrix over Q, every entry in {0,1}; matrices are enumerated in itertools.product order with 0 before 1, and all 16 pairs are tested."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
