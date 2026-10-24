r"""$\tan{\angle ABC}=\tan{\theta}=\frac{m_{BC}-m_{AB}}{1+m_{BC} m_{AB}}"""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "mse_4217205__ans4217514"
WITNESS_DESCRIPTION = "A=(0, 0), B=(1, 0), C=(2, 1), with m_AB=0 and m_BC=1."
REFUTATION_EXPLANATION = "For the ordinary angle ABC between BA=(-1, 0) and BC=(1, 1), tan(angle ABC)=abs(det(BA,BC))/(BA dot BC)=1/(-1)=-1, while (m_BC-m_AB)/(1+m_BC*m_AB)=1; hence -1 != 1."
SEARCH_SPACE = "All 15,625 ordered triples (A,B,C) from the 25 integer grid points {-2,-1,0,1,2}^2 were visited in lexicographic itertools.product order. Equality was tested for every pairwise-distinct, noncollinear triple for which m_AB, m_BC, tan(angle ABC), and the displayed rational expression are defined."

points = tuple(product(range(-2, 3), repeat=2))
named = ((0, 0), (1, 0), (2, 1))
swept = 0
eligible = 0
violation_count = 0
named_seen = False

for a, b, c in product(points, repeat=3):
    swept += 1
    if a == b or b == c or a == c:
        continue

    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    bc_x = c[0] - b[0]
    bc_y = c[1] - b[1]
    ba_x = a[0] - b[0]
    ba_y = a[1] - b[1]

    cross = ba_x * bc_y - ba_y * bc_x
    dot = ba_x * bc_x + ba_y * bc_y
    if cross == 0 or ab_x == 0 or bc_x == 0 or dot == 0:
        continue

    m_ab = Fraction(ab_y, ab_x)
    m_bc = Fraction(bc_y, bc_x)
    rhs_denominator = 1 + m_bc * m_ab
    if rhs_denominator == 0:
        continue

    eligible += 1
    lhs = Fraction(abs(cross), dot)
    rhs = Fraction(m_bc - m_ab, rhs_denominator)
    if lhs != rhs:
        violation_count += 1
        if (a, b, c) == named:
            assert lhs == -1
            assert rhs == 1
            named_seen = True

assert swept == 15625
assert eligible > 0
assert violation_count > 0
assert named_seen

output = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(output, separators=(",", ":")))
