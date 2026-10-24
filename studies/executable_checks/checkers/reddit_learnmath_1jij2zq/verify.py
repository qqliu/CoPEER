r"""For general n, x+y equals the displayed sum from i=0 to 1 with binomial coefficients depending on n."""

import json


def choose(total, selected):
    if selected < 0 or selected > total:
        return 0
    selected = min(selected, total - selected)
    value = 1
    for step in range(1, selected + 1):
        value = (value * (total - selected + step)) // step
    return value


def integer_power(base, exponent):
    if exponent < 0:
        raise ValueError("negative exponent")
    value = 1
    for _ in range(exponent):
        value *= base
    return value


n, x, y = 2, 1, 1
left = x + y
right = 0
for index in (0, 1):
    right += choose(n, index) * integer_power(x, index) * integer_power(y, n - index)

if left != 2 or right != 3 or left == right:
    raise RuntimeError("independent witness verification failed")

result = {
    "record_id": "reddit_learnmath_1jij2zq",
    "verdict": "CONFIRMED",
    "notes": "Independent exact arithmetic gives left=2 and displayed sum=3 at (n,x,y)=(2,1,1), so the witness refutes the general claim. The statement is plainly a typo: the usual binomial identity has (x+y)^n and sums through i=n."
}
print(json.dumps(result, separators=(",", ":")))
