r"""$\tan{\angle ABC}=\tan{\theta}=\frac{m_{BC}-m_{AB}}{1+m_{BC} m_{AB}}"""

import json
from fractions import Fraction

record_id = "mse_4217205__ans4217514"
notes = "Exact recomputation gives tan(angle ABC) = -1 and the displayed slope expression = 1 for the witness. The refuted statement has a substantive orientation/sign error, not plainly a typo."

A = (0, 0)
B = (1, 0)
C = (2, 1)

BA = (A[0] - B[0], A[1] - B[1])
BC = (C[0] - B[0], C[1] - B[1])
AB = (B[0] - A[0], B[1] - A[1])

determinant = BA[0] * BC[1] - BA[1] * BC[0]
dot_product = BA[0] * BC[0] + BA[1] * BC[1]

if determinant == 0 or dot_product == 0 or AB[0] == 0 or BC[0] == 0:
    raise ArithmeticError("The reported witness does not define both sides")

m_ab = Fraction(AB[1], AB[0])
m_bc = Fraction(BC[1], BC[0])
rhs_denominator = 1 + m_bc * m_ab
if rhs_denominator == 0:
    raise ArithmeticError("The displayed expression is undefined")

ordinary_angle_tangent = Fraction(abs(determinant), dot_product)
displayed_expression = Fraction(m_bc - m_ab, rhs_denominator)

if ordinary_angle_tangent != -1 or displayed_expression != 1:
    raise ArithmeticError("Independent exact values differ from the report")
if ordinary_angle_tangent == displayed_expression:
    raise ArithmeticError("The witness does not refute the claim")

print(json.dumps({
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}, separators=(",", ":")))
