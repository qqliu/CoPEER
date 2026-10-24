source = (3, 3, 3, 1, 1, 1)
m = 2

assert len(source) == 3 * m
assert all(value > 0 for value in source)
assert sum(source) % m == 0
common_sum = sum(source) // m

# For two blocks, a valid source partition exists exactly when some three
# indexed elements have half the total sum.
source_yes = False
for mask in range(1 << len(source)):
    if mask.bit_count() != 3:
        continue
    selected_sum = 0
    for index in range(len(source)):
        if mask & (1 << index):
            selected_sum += source[index]
    if selected_sum == common_sum:
        source_yes = True

constructed = source + (0,) * (9 * m)
well_formed_target = (
    len(constructed) == 12 * m
    and all(value > 0 for value in constructed)
)

# These two blocks are an independently stated certificate for the reported
# constructed multiset when the positivity restriction is temporarily relaxed.
block_one = (3, 3) + (0,) * 10
block_two = (3, 1, 1, 1) + (0,) * 8
certificate_uses_all_items = sorted(block_one + block_two) == sorted(constructed)
certificate_has_right_sizes = len(block_one) == 12 and len(block_two) == 12
certificate_has_equal_sums = sum(block_one) == sum(block_two) == common_sum
relaxed_target_yes = (
    certificate_uses_all_items
    and certificate_has_right_sizes
    and certificate_has_equal_sums
)
nonzero_counts = (
    sum(value != 0 for value in block_one),
    sum(value != 0 for value in block_two),
)

assert common_sum == 6
assert not source_yes
assert not well_formed_target
assert relaxed_target_yes
assert nonzero_counts == (2, 4)

print("reported source instance: 3Partition = NO; target sum = 6")
print("written reduction output: malformed because it contains zero padding")
print("under the relaxed nonnegative interpretation: 12Partition = YES")
print("witness block nonzero counts: 2 and 4; both blocks have size 12 and sum 6")
print("CONCLUSION: CONFIRMED -- the claimed reduction and its forcing statement fail")
