r"""For Fibonacci numbers, f_i divides f_n if and only if i divides n, without excluding the exceptional repeated initial value."""

import json

REPORT = {
    "record_id": "reddit_math_3m6fzz",
    "verdict": "CONFIRMED",
    "notes": "Exact integer recomputation gives f_1 = f_2 = 1, so f_2 divides f_1 while 2 does not divide 1. The refuted statement is substantive, not plainly a typo, because it explicitly includes the exceptional repeated initial value.",
}


def fibonacci(index):
    assert isinstance(index, int)
    assert index >= 1
    previous, current = 1, 1
    if index == 1:
        return previous
    for _ in range(2, index):
        previous, current = current, previous + current
    return current


i, n = 2, 1
f_i = fibonacci(i)
f_n = fibonacci(n)
assert f_i == 1
assert f_n == 1
assert f_i != 0
fibonacci_divisibility = f_n % f_i == 0
index_divisibility = n % i == 0
assert fibonacci_divisibility
assert not index_divisibility
assert fibonacci_divisibility != index_divisibility

print(json.dumps(REPORT, separators=(",", ":")))
