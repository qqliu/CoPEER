r"""The rank of any matrix with at least two prime-valued entries per row and per column is at least 2."""

import json

record_id = "reddit_learnmath_1ll9v6l"
expected_notes = "Exact recomputation confirms that every entry of [[2, 2], [2, 2]] is prime, so each row and column contains two prime-valued entries. The matrix is nonzero and has determinant 0, hence its rank over the rationals is exactly 1. The refuted statement is substantively false as written, not plainly a typo."


def prime_integer(number):
    if not isinstance(number, int) or isinstance(number, bool) or number < 2:
        return False
    candidate = 2
    while candidate * candidate <= number:
        if number % candidate == 0:
            return False
        candidate += 1
    return True


matrix = ((2, 2), (2, 2))
row_condition = all(sum(1 for entry in row if prime_integer(entry)) >= 2 for row in matrix)
column_condition = all(
    sum(1 for row_index in range(len(matrix)) if prime_integer(matrix[row_index][column_index])) >= 2
    for column_index in range(len(matrix[0]))
)

a = matrix[0][0]
b = matrix[0][1]
c = matrix[1][0]
d = matrix[1][1]
determinant = a * d - b * c
nonzero_entry_exists = any(entry != 0 for row in matrix for entry in row)
rank = 1 if nonzero_entry_exists and determinant == 0 else (2 if determinant != 0 else 0)

verified = row_condition and column_condition and rank < 2
verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"
notes = expected_notes if verified else "The reported witness did not pass independent exact verification; the statement therefore was not refuted by this witness. The alleged issue cannot be classified as a substantive error or a plain typo from this witness."
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
