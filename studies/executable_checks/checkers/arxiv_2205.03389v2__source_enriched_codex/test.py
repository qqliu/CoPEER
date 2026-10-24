r"""For every prime p, work in the finite field \(\mathbb F_p\). Define \(\tau:\mathbb F_p\to\mathbb N\cup\{\infty\}\) by \(\tau(0)=0\); for \(b\ne0\), let \(\tau(b)\) be the smallest nonnegative integer \(r\) such that \(2^r\in\{-b,b\}\), and set \(\tau(b)=\infty\) if no such \(r\) exists. Let \(\Omega=\{b\in\mathbb F_p:\tau(b)<\infty\}\). Define the matrix \(P\), indexed by \(\Omega\times\Omega\), by \(P(x,0)=P(x,2x)=1/2\) for every \(x\in\Omega\setminus\{0\}\), \(P(0,1)=P(0,-1)=1/2\), and \(P(x,y)=0\) otherwise. Then \(P\) is aperiodic: for every \(x\in\Omega\), \(\gcd\{t\in\mathbb N^+:P^t(x,x)>0\}=1\), where \(P^t\) is the ordinary t-th matrix power. No input-size convention is required because this is a finite mathematical claim, not an asymptotic or algorithmic one."""

import json
from fractions import Fraction
from math import gcd

RECORD_ID = "arxiv_2205.03389v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "p=2 with x=0 (also x=1): Ω={0,1}, and the literal matrix assignments give P(0,1)=P(1,0)=1/2 with both diagonal entries zero."
REFUTATION_EXPLANATION = "At p=2 the positive-support graph is the directed 2-cycle 0→1→0. Hence every walk from 0 back to 0 has even length, and one exists at every positive even length. Therefore {t∈N+:P^t(0,0)>0}={2,4,6,...}, whose gcd is 2 rather than 1."
SEARCH_SPACE = "Exhaustively swept every prime p in the integer interval 2<=p<=257 (55 primes), every x in its computed Ω, and every positive-support edge of the literally defined finite matrix P; each period was computed exactly from the finite strongly connected component using integer gcd cycle constraints."


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def omega(p):
    values = {0}
    seen = set()
    value = 1 % p
    while value not in seen:
        seen.add(value)
        values.add(value)
        values.add((-value) % p)
        value = (2 * value) % p
    return tuple(sorted(values))


def positive_edges(p, states):
    half = Fraction(1, 2)
    zero = Fraction(0, 1)
    matrix = {(x, y): zero for x in states for y in states}
    for x in states:
        if x == 0:
            matrix[(x, 1 % p)] = half
            matrix[(x, (-1) % p)] = half
        else:
            matrix[(x, 0)] = half
            matrix[(x, (2 * x) % p)] = half
    return {
        x: tuple(y for y in states if matrix[(x, y)] > zero)
        for x in states
    }


def reachable(start, edges):
    reached = {start}
    queue = [start]
    index = 0
    while index < len(queue):
        node = queue[index]
        index += 1
        for neighbor in edges[node]:
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    return reached


def period_at(start, edges):
    reverse = {node: [] for node in edges}
    for node in sorted(edges):
        for neighbor in edges[node]:
            reverse[neighbor].append(node)
    reverse_edges = {node: tuple(sorted(reverse[node])) for node in reverse}
    component = reachable(start, edges) & reachable(start, reverse_edges)

    distance = {start: 0}
    queue = [start]
    index = 0
    while index < len(queue):
        node = queue[index]
        index += 1
        for neighbor in edges[node]:
            if neighbor in component and neighbor not in distance:
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)

    cycle_gcd = 0
    for node in sorted(component):
        for neighbor in edges[node]:
            if neighbor in component:
                constraint = abs(distance[node] + 1 - distance[neighbor])
                cycle_gcd = gcd(cycle_gcd, constraint)
    return cycle_gcd


def main():
    failures = []
    prime_count = 0
    for p in range(2, 258):
        if not is_prime(p):
            continue
        prime_count += 1
        states = omega(p)
        edges = positive_edges(p, states)
        for x in states:
            period = period_at(x, edges)
            if period != 1:
                failures.append((p, x, period))

    assert prime_count == 55
    assert (2, 0, 2) in failures
    assert (2, 1, 2) in failures

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
