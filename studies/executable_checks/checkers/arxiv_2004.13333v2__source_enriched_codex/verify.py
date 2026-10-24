r'''For every finite family of square-integrable one-dimensional martingale-difference sequences on a common discrete-time stochastic basis, there exists a martingale M with M_0=0 satisfying the displayed stochastic maximal inequality for every n≥1.'''

import json
from fractions import Fraction

REPORT = {
    "record_id": "arxiv_2004.13333v2__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic verifies that both sequences are square-integrable martingale differences. The time-1 obstacle is 0, while the time-2 obstacle is 2 on every atom; martingality therefore forces M_1≥2 on both time-1 nodes, contradicting E[M_1]=0. The refuted statement is substantive, not plainly a typo.",
}

ATOMS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
F0 = (ATOMS,)
F1 = (
    tuple(atom for atom in ATOMS if atom[0] == -1),
    tuple(atom for atom in ATOMS if atom[0] == 1),
)
F2 = tuple((atom,) for atom in ATOMS)


def xi(index, time, atom):
    r, s = atom
    if time == 1:
        return r
    if time == 2:
        return s if index == 0 else -s
    return 0


def conditional_mean(values, partition):
    result = {}
    for block in partition:
        mean = Fraction(sum(values[atom] for atom in block), len(block))
        for atom in block:
            result[atom] = mean
    return result


def is_measurable(values, partition):
    return all(
        all(values[atom] == values[block[0]] for atom in block)
        for block in partition
    )


assert len(set(ATOMS)) == 4
assert all(len(block) > 0 for partition in (F0, F1, F2) for block in partition)
assert all(
    sorted(atom for block in partition for atom in block) == sorted(ATOMS)
    for partition in (F0, F1, F2)
)

for index in (0, 1):
    first = {atom: xi(index, 1, atom) for atom in ATOMS}
    second = {atom: xi(index, 2, atom) for atom in ATOMS}
    assert is_measurable(first, F1)
    assert is_measurable(second, F2)
    assert all(value == 0 for value in conditional_mean(first, F0).values())
    assert all(value == 0 for value in conditional_mean(second, F1).values())
    assert all(value * value <= 1 for value in first.values())
    assert all(value * value <= 1 for value in second.values())
    assert all(xi(index, 3, atom) == 0 for atom in ATOMS)

pointwise_energy_1 = {
    atom: max(xi(index, 1, atom) * xi(index, 1, atom) for index in (0, 1))
    for atom in ATOMS
}
pointwise_energy_2 = {
    atom: max(xi(index, 2, atom) * xi(index, 2, atom) for index in (0, 1))
    for atom in ATOMS
}
energy_1 = conditional_mean(pointwise_energy_1, F0)
energy_2 = conditional_mean(pointwise_energy_2, F1)
assert all(value == 1 for value in energy_1.values())
assert all(value == 1 for value in energy_2.values())

largest_sum_square_1 = {
    atom: max(xi(index, 1, atom) * xi(index, 1, atom) for index in (0, 1))
    for atom in ATOMS
}
largest_sum_square_2 = {}
for atom in ATOMS:
    squares = []
    for index in (0, 1):
        total = xi(index, 1, atom) + xi(index, 2, atom)
        squares.append(total * total)
    largest_sum_square_2[atom] = max(squares)

obstacle_1 = {
    atom: Fraction(largest_sum_square_1[atom], 1) - energy_1[atom]
    for atom in ATOMS
}
obstacle_2 = {
    atom: Fraction(largest_sum_square_2[atom], 1)
    - energy_1[atom]
    - energy_2[atom]
    for atom in ATOMS
}
assert all(value == 0 for value in obstacle_1.values())
assert all(value == 2 for value in obstacle_2.values())

future_lower_bound = conditional_mean(obstacle_2, F1)
required_m1 = {
    atom: max(obstacle_1[atom], future_lower_bound[atom])
    for atom in ATOMS
}
assert is_measurable(required_m1, F1)
assert all(value == 2 for value in required_m1.values())

# Any admissible martingale would have M_1 at least this bound, because
# M_2 dominates obstacle_2 and E[M_2 | F_1] = M_1. But M_0 = 0 requires
# the unconditional mean of M_1 to be zero.
minimum_possible_mean_m1 = Fraction(
    sum(required_m1[atom] for atom in ATOMS), len(ATOMS)
)
assert minimum_possible_mean_m1 == 2
assert minimum_possible_mean_m1 > 0

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
