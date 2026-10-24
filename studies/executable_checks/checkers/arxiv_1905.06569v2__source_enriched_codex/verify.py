r"""Whenever the ratios $a_i b_i^{-1}$ agree on parts of $\pi\wedge\sigma$, the equations $u_i v_i=a_i b_i^{-1}$, with $u$ constant on parts of $\pi$ and $v$ constant on parts of $\sigma$, have exactly $|G|^{|\pi\vee\sigma|}$ solutions."""

import json


def multiply(x, y):
    assert x in (0, 1) and y in (0, 1)
    return x ^ y


def inverse(x):
    assert x in (0, 1)
    return x


def intersections(left, right):
    answer = []
    for left_block in left:
        for right_block in right:
            block = tuple(i for i in left_block if i in right_block)
            if block:
                answer.append(block)
    return tuple(answer)


def connected_components(left, right, size):
    adjacency = [set() for _ in range(size)]
    for partition in (left, right):
        for block in partition:
            for x in block:
                for y in block:
                    adjacency[x].add(y)

    unseen = set(range(size))
    components = []
    while unseen:
        start = min(unseen)
        pending = [start]
        reached = set()
        while pending:
            x = pending.pop()
            if x in reached:
                continue
            reached.add(x)
            pending.extend(y for y in adjacency[x] if y not in reached)
        unseen.difference_update(reached)
        components.append(tuple(sorted(reached)))
    return tuple(components)


def main():
    pi = ((0, 1), (2, 3))
    sigma = ((0, 2), (1, 3))
    a = (0, 0, 0, 0)
    b = (0, 0, 0, 1)
    size = 4

    ratios = tuple(multiply(a[i], inverse(b[i])) for i in range(size))
    meet = intersections(pi, sigma)
    hypothesis = all(
        all(ratios[i] == ratios[block[0]] for i in block)
        for block in meet
    )
    join = connected_components(pi, sigma, size)

    pi_number = {i: number for number, block in enumerate(pi) for i in block}
    sigma_number = {
        i: number for number, block in enumerate(sigma) for i in block
    }

    solutions = 0
    checked = 0
    for assignment in range(16):
        u = ((assignment >> 0) & 1, (assignment >> 1) & 1)
        v = ((assignment >> 2) & 1, (assignment >> 3) & 1)
        checked += 1
        if all(
            multiply(u[pi_number[i]], v[sigma_number[i]]) == ratios[i]
            for i in range(size)
        ):
            solutions += 1

    predicted = 2 ** len(join)
    assert ratios == (0, 0, 0, 1)
    assert meet == ((0,), (1,), (2,), (3,))
    assert hypothesis
    assert join == ((0, 1, 2, 3),)
    assert checked == 16
    assert solutions == 0
    assert predicted == 2
    assert solutions != predicted

    result = {
        "record_id": "arxiv_1905.06569v2__source_enriched_codex",
        "verdict": "CONFIRMED",
        "notes": "Substantive, not a typo: exact C2 arithmetic gives four singleton meet blocks and one join block, so the hypothesis holds and the formula predicts 2 solutions, but exhaustive enumeration of all 16 block-constant assignments gives 0.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
