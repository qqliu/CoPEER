r"""Whenever the ratios $a_i b_i^{-1}$ agree on parts of $\pi\wedge\sigma$, the equations $u_i v_i=a_i b_i^{-1}$, with $u$ constant on parts of $\pi$ and $v$ constant on parts of $\sigma$, have exactly $|G|^{|\pi\vee\sigma|}$ solutions."""

import itertools
import json


def all_partitions(n):
    result = []
    for labels in itertools.product(range(n), repeat=n):
        if labels[0] != 0:
            continue
        valid = True
        for i in range(1, n):
            if labels[i] > max(labels[:i]) + 1:
                valid = False
                break
        if not valid:
            continue
        blocks = tuple(
            tuple(i for i, label in enumerate(labels) if label == block_label)
            for block_label in range(max(labels) + 1)
        )
        result.append(blocks)
    return tuple(result)


def block_map(partition, n):
    result = [0] * n
    for block_number, block in enumerate(partition):
        for i in block:
            result[i] = block_number
    return tuple(result)


def meet_blocks(pi, sigma):
    blocks = []
    for p_block in pi:
        p_set = set(p_block)
        for s_block in sigma:
            intersection = tuple(i for i in s_block if i in p_set)
            if intersection:
                blocks.append(intersection)
    return tuple(blocks)


def agrees_on_meet(ratios, pi, sigma):
    for block in meet_blocks(pi, sigma):
        if any(ratios[i] != ratios[block[0]] for i in block[1:]):
            return False
    return True


def join_block_count(pi, sigma, n):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            parent[root_y] = root_x

    for partition in (pi, sigma):
        for block in partition:
            for i in block[1:]:
                union(block[0], i)
    return len({find(i) for i in range(n)})


def solution_count(pi, sigma, ratios, n):
    pi_of = block_map(pi, n)
    sigma_of = block_map(sigma, n)
    count = 0
    for u_values in itertools.product((0, 1), repeat=len(pi)):
        for v_values in itertools.product((0, 1), repeat=len(sigma)):
            if all(
                (u_values[pi_of[i]] ^ v_values[sigma_of[i]]) == ratios[i]
                for i in range(n)
            ):
                count += 1
    return count


def main():
    n = 4
    partitions = all_partitions(n)
    vectors = tuple(itertools.product((0, 1), repeat=n))
    first = None

    for pi in partitions:
        for sigma in partitions:
            expected = 2 ** join_block_count(pi, sigma, n)
            for a in vectors:
                for b in vectors:
                    ratios = tuple(a[i] ^ b[i] for i in range(n))
                    if not agrees_on_meet(ratios, pi, sigma):
                        continue
                    actual = solution_count(pi, sigma, ratios, n)
                    if actual != expected and first is None:
                        first = (pi, sigma, a, b, ratios, actual, expected)

    assert len(partitions) == 15
    assert first == (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        (0, 0, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 0, 1),
        0,
        2,
    )

    result = {
        "record_id": "arxiv_1905.06569v2__source_enriched_codex",
        "outcome": "WITNESS_FOUND",
        "witness_description": "In C2={0,1} with multiplication x*y=x XOR y (so every element is its own inverse), take indices {0,1,2,3}, pi={{0,1},{2,3}}, sigma={{0,2},{1,3}}, a=(0,0,0,0), and b=(0,0,0,1). Then a_i b_i^{-1}=(0,0,0,1).",
        "refutation_explanation": "The meet consists of four singleton parts, so the hypothesis holds. The join has one part, so the claim predicts 2 solutions. The four equations are u_A XOR v_C=0, u_A XOR v_D=0, u_B XOR v_C=0, and u_B XOR v_D=1. The first three force u_B=v_D, making the last left-hand side 0, a contradiction. Thus there are 0 solutions, not 2.",
        "search_space": "All 15 set partitions pi and all 15 set partitions sigma of {0,1,2,3}, and all 16^2 ordered pairs (a,b) in C2^4 x C2^4 (57,600 cases total); for every qualifying case, all 2^(|pi|+|sigma|) assignments to block-constant u and v were enumerated.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
