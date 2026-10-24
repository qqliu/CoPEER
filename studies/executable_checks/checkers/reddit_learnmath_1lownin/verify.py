r"""If A has r independent columns and B has r independent rows, then AB is invertible for general dimensions A∈R^{m×r} and B∈R^{r×n}."""

import json

record_id = "reddit_learnmath_1lownin"
a = ((1,),)
b = ((0, 1),)


def matrix_product(left, right):
    row_count = len(left)
    shared_count = len(right)
    column_count = len(right[0])
    return tuple(
        tuple(
            sum(left[i][k] * right[k][j] for k in range(shared_count))
            for j in range(column_count)
        )
        for i in range(row_count)
    )


def apply_matrix(matrix, vector):
    return tuple(
        sum(row[j] * vector[j] for j in range(len(vector)))
        for row in matrix
    )


product = matrix_product(a, b)
a_column_independent = a[0][0] != 0
b_row_independent = any(entry != 0 for entry in b[0])
kernel_vector = (1, 0)
nonzero_kernel_witness = (
    any(entry != 0 for entry in kernel_vector)
    and apply_matrix(product, kernel_vector) == (0,)
)
witness_valid = (
    len(a) == 1
    and len(a[0]) == 1
    and len(b) == 1
    and len(b[0]) == 2
    and product == ((0, 1),)
    and a_column_independent
    and b_row_independent
    and nonzero_kernel_witness
)

verdict = "CONFIRMED" if witness_valid else "REFUTED_WITNESS_INVALID"
notes = (
    "Exact integer recomputation confirms the witness: A's sole column and B's sole row are nonzero and therefore independent, while AB=[[0,1]] has the nonzero kernel vector (1,0), so it is not invertible. The refuted statement is substantive, not plainly a typo: the hypotheses do not force AB to be square or bijective."
    if witness_valid
    else
    "The reported witness did not survive exact recomputation. The alleged issue would be substantive rather than plainly a typo."
)
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, ensure_ascii=False))
