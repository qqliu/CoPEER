r"""Over a real vector space, the existence of one real eigenvalue implies that the operator has an upper-triangular matrix in an orthonormal basis."""

import json

record_id = "reddit_learnmath_1co5gzk"
confirmed_notes = "Exact recomputation gives Ae3=e3 and det(tI-A)=(t-1)(t^2+1). The quadratic factor has discriminant -4, so the characteristic polynomial does not split over the reals; therefore A cannot be similar, orthogonally or otherwise, to a real upper-triangular matrix. The refuted statement is substantive, not a typo."
invalid_notes = "The reported witness failed independent exact verification. The alleged refutation would be substantive rather than a mere typo."

matrix = (
    (0, -1, 0),
    (1, 0, 0),
    (0, 0, 1),
)
eigenvector = (0, 0, 1)
eigenvalue = 1

image = tuple(
    sum(matrix[row][column] * eigenvector[column] for column in range(3))
    for row in range(3)
)
scaled_vector = tuple(eigenvalue * coordinate for coordinate in eigenvector)

trace = matrix[0][0] + matrix[1][1] + matrix[2][2]
principal_minors = (
    matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    + matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]
    + matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]
)
determinant = (
    matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
    - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
    + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
)
characteristic = (-determinant, principal_minors, -trace, 1)

quadratic = (1, 0, 1)
factored_coefficients = (
    -eigenvalue * quadratic[0],
    quadratic[0] - eigenvalue * quadratic[1],
    quadratic[1] - eigenvalue * quadratic[2],
    quadratic[2],
)
discriminant = quadratic[1] * quadratic[1] - 4 * quadratic[2] * quadratic[0]

verified = all((
    eigenvector != (0, 0, 0),
    image == scaled_vector,
    characteristic == (-1, 1, -1, 1),
    factored_coefficients == characteristic,
    discriminant == -4,
    discriminant < 0,
))

verdict = "CONFIRMED" if verified else "REFUTED_WITNESS_INVALID"
notes = confirmed_notes if verified else invalid_notes
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
