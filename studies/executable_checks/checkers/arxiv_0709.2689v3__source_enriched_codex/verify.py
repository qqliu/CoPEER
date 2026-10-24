r"""For a graph G on n vertices whose maximum independent-set size is k, the strictly upper-triangular part UA of its adjacency matrix satisfies (UA)^(n-k+1)=θ, and conversely."""

import json
from itertools import combinations

RECORD_ID = "arxiv_0709.2689v3__source_enriched_codex"
CONFIRMED_NOTES = "Exact integer recomputation gives α(G)=2 and (UA)^2[0][2]=1, so the claimed equivalence is refuted; this is a substantive mathematical error, not a plain typo."


def is_independent(vertices, edges):
    for left, right in combinations(vertices, 2):
        if (left, right) in edges or (right, left) in edges:
            return False
    return True


def independence_number(vertex_count, edges):
    vertices = tuple(range(vertex_count))
    for size in range(vertex_count, -1, -1):
        for selected in combinations(vertices, size):
            if is_independent(selected, edges):
                return size
    raise ArithmeticError("finite graph has no independent set")


def product(left, right):
    row_count = len(left)
    column_count = len(right[0])
    shared_count = len(right)
    result = [[0 for _ in range(column_count)] for _ in range(row_count)]
    for row in range(row_count):
        for column in range(column_count):
            value = 0
            for shared in range(shared_count):
                value += left[row][shared] * right[shared][column]
            result[row][column] = value
    return result


def nonnegative_matrix_power(matrix, exponent):
    if exponent < 0:
        raise ValueError("negative exponent")
    dimension = len(matrix)
    result = [
        [int(row == column) for column in range(dimension)]
        for row in range(dimension)
    ]
    for _ in range(exponent):
        result = product(result, matrix)
    return result


def main():
    vertex_count = 3
    edges = {(0, 1), (1, 2)}
    k = independence_number(vertex_count, edges)

    adjacency = [[0 for _ in range(vertex_count)] for _ in range(vertex_count)]
    for left, right in edges:
        adjacency[left][right] = 1
        adjacency[right][left] = 1

    upper = [
        [adjacency[row][column] if row < column else 0
         for column in range(vertex_count)]
        for row in range(vertex_count)
    ]
    exponent = vertex_count - k + 1
    powered = nonnegative_matrix_power(upper, exponent)

    witness_valid = (
        k == 2
        and is_independent((0, 2), edges)
        and not is_independent((0, 1, 2), edges)
        and exponent == 2
        and powered[0][2] == 1
        and any(entry != 0 for row in powered for entry in row)
    )

    if witness_valid:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "Independent exact recomputation did not validate the reported witness."

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes
    }, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
