r"""For every prime p, work in the finite field \(\mathbb F_p\). Define \(\tau:\mathbb F_p\to\mathbb N\cup\{\infty\}\) by \(\tau(0)=0\); for \(b\ne0\), let \(\tau(b)\) be the smallest nonnegative integer \(r\) such that \(2^r\in\{-b,b\}\), and set \(\tau(b)=\infty\) if no such \(r\) exists. Let \(\Omega=\{b\in\mathbb F_p:\tau(b)<\infty\}\). Define the matrix \(P\), indexed by \(\Omega\times\Omega\), by \(P(x,0)=P(x,2x)=1/2\) for every \(x\in\Omega\setminus\{0\}\), \(P(0,1)=P(0,-1)=1/2\), and \(P(x,y)=0\) otherwise. Then \(P\) is aperiodic: for every \(x\in\Omega\), \(\gcd\{t\in\mathbb N^+:P^t(x,x)>0\}=1\), where \(P^t\) is the ordinary t-th matrix power. No input-size convention is required because this is a finite mathematical claim, not an asymptotic or algorithmic one."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_2205.03389v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Independent exact recomputation confirms the witness. In F_2, Omega={0,1}; because 1=-1 and 2·1=0, the literal entry assignments collide rather than add, leaving exactly the positive-support edges 0→1 and 1→0. The support walk is therefore a deterministic 2-cycle, so returns to 0 occur exactly at positive even lengths and their gcd is 2. This is a substantive counterexample to the universal claim as written, not plainly a typo, although it likely reflects an omitted odd-prime hypothesis."


def prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def tau_value(b, p):
    if b == 0:
        return 0
    value = 1 % p
    r = 0
    visited = set()
    while value not in visited:
        if value == b or value == (-b) % p:
            return r
        visited.add(value)
        value = (value * 2) % p
        r += 1
    return None


def multiply(left, right, size):
    zero = Fraction(0, 1)
    product = [[zero for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            total = zero
            for k in range(size):
                total += left[i][k] * right[k][j]
            product[i][j] = total
    return product


def main():
    p = 2
    assert prime(p)
    states = tuple(b for b in range(p) if tau_value(b, p) is not None)
    assert states == (0, 1)

    index = {state: position for position, state in enumerate(states)}
    zero = Fraction(0, 1)
    half = Fraction(1, 2)
    matrix = [[zero for _ in states] for _ in states]

    for x in states:
        if x != 0:
            matrix[index[x]][index[0]] = half
            matrix[index[x]][index[(2 * x) % p]] = half
    matrix[index[0]][index[1 % p]] = half
    matrix[index[0]][index[(-1) % p]] = half

    support = {}
    for x in states:
        support[x] = tuple(y for y in states if matrix[index[x]][index[y]] > zero)
    assert support == {0: (1,), 1: (0,)}

    squared = multiply(matrix, matrix, len(states))
    assert matrix[index[0]][index[0]] == zero
    assert squared[index[0]][index[0]] == Fraction(1, 4)

    start = 0
    first_seen = {start: 0}
    current = start
    steps = 0
    while True:
        successors = support[current]
        assert len(successors) == 1
        current = successors[0]
        steps += 1
        if current in first_seen:
            cycle_start = first_seen[current]
            cycle_length = steps - cycle_start
            break
        first_seen[current] = steps

    assert current == start
    assert cycle_start == 0
    assert cycle_length == 2
    assert cycle_length != 1

    result = {"record_id": RECORD_ID, "verdict": VERDICT, "notes": NOTES}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
