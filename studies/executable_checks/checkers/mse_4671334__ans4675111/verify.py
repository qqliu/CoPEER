r"""Use the below inequality: For $a>0,b>0,c>0,d>0$,
$(a-b)/(c-d) \leq a/c \iff c(a-b) \leq a(c-d) \iff -bc \leq -ad \iff b/d \geq a/c$"""

import json


def rational_le(left_num, left_den, right_num, right_den):
    if left_den == 0 or right_den == 0:
        raise ZeroDivisionError("undefined rational comparison")
    if left_den < 0:
        left_num = -left_num
        left_den = -left_den
    if right_den < 0:
        right_num = -right_num
        right_den = -right_den
    return left_num * right_den <= right_num * left_den


a, b, c, d = 1, 1, 1, 2
assert a > 0 and b > 0 and c > 0 and d > 0
assert c != d

first = rational_le(a - b, c - d, a, c)
second = c * (a - b) <= a * (c - d)
third = -b * c <= -a * d
fourth = rational_le(a, c, b, d)

assert (first, second, third, fourth) == (True, False, False, False)
assert c - d < 0
assert first != second

result = {
    "record_id": "mse_4671334__ans4675111",
    "verdict": "CONFIRMED",
    "notes": "Exact integer arithmetic verifies that at (a,b,c,d)=(1,1,1,2), the four statements have truth values (true,false,false,false). The refuted statement is substantive, not plainly a typo: it omits the sign condition on c-d, so multiplying by c-d can reverse the inequality.",
}
print(json.dumps(result, separators=(",", ":")))
