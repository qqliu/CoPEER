r'''So write $(23$, then notice $3$ is sent to $2$ by the rightmost cycle and the $2$ is sent to $1$ by the other cycle, so write $(321$. Notice $1$ must go to $3$ to finish the cycle as $(321)$.'''

import json

record_id = "mse_1091361__ans1091441"
notes = ("Exact recomputation gives 3→2→1 for the stated rightmost-first "
         "composition, hence 3→1, whereas the standard cycle (321) sends "
         "3→2. The refuted statement is plainly a cycle-order typo, not a "
         "substantive mathematical failure.")

first_arrow = (3, 2)
second_arrow = (2, 1)
cycle = (3, 2, 1)

if first_arrow[1] != second_arrow[0]:
    raise AssertionError("the stated arrows do not compose")
composed_image = second_arrow[1]

cycle_image = {}
for position in range(len(cycle)):
    following = position + 1
    if following == len(cycle):
        following = 0
    cycle_image[cycle[position]] = cycle[following]

if composed_image != 1 or cycle_image[3] != 2:
    raise AssertionError("independent recomputation failed")
if composed_image == cycle_image[3]:
    raise AssertionError("reported discrepancy is absent")

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
