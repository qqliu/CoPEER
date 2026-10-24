#!/usr/bin/env python3

# Independently check the reported forward-direction counterexample.
original = (5, 5, 6, 5, 5, 6)
target = 16
source_blocks = ((0, 1, 2), (3, 4, 5))

group_count = len(original) // 3
assert group_count == 2
assert sum(original) == group_count * target
assert all(4 * value > target and 2 * value < target for value in original)
assert all(len(block) == 3 for block in source_blocks)
assert all(sum(original[index] for index in block) == target
           for block in source_blocks)
assert sorted(index for block in source_blocks for index in block) == list(range(len(original)))

scale = 1 + sum(original)
elements = {}
for zero_based_index, value in enumerate(original):
    positional_weight = 4 ** (3 * group_count - zero_based_index)
    for coefficient in range(1, 5):
        tag = (zero_based_index, coefficient)
        elements[tag] = value + coefficient * scale * positional_weight

forward_groups = []
for block in source_blocks:
    tags = tuple((index, coefficient)
                 for index in block
                 for coefficient in range(1, 5))
    forward_groups.append(tags)

assert len(elements) == 24
assert all(len(group) == 12 for group in forward_groups)
assert set(forward_groups[0]).isdisjoint(set(forward_groups[1]))
assert set(forward_groups[0]) | set(forward_groups[1]) == set(elements)

forward_sums = tuple(sum(elements[tag] for tag in group)
                     for group in forward_groups)
assert forward_sums == (1774144, 27784)
assert forward_sums[0] != forward_sums[1]

print("source promise: valid")
print("source 3-partition witness: valid")
print("constructed element count:", len(elements))
print("forward subset sizes:", tuple(len(group) for group in forward_groups))
print("forward subset sums:", forward_sums)
print("equal forward sums:", forward_sums[0] == forward_sums[1])
print("CONCLUSION: CONFIRMED - the solution's stated forward construction does not produce equal-sum subsets")
