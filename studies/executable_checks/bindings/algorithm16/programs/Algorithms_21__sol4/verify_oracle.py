N = 12

# Reconstruct the stated complete forward DAG using only integer weights.
delta = [0] * (N + 1)
for vertex in range(2, N):
    delta[vertex] = 1 << (vertex - 2)
W = sum(delta)

outgoing = [[] for _ in range(N + 1)]
for tail in range(1, N):
    for head in range(tail + 1, N + 1):
        if tail == 1:
            cost = W if head == N else 0
        else:
            cost = W - delta[tail] if head == N else -delta[tail]
        outgoing[tail].append((head, cost))

# This is a decrease-key worklist version of the algorithm described in the
# solution.  Removing a vertex from pending is not permanent: any later strict
# improvement adds it back.  Equal keys use the solution's v2, v3, ... order.
label = [None] * (N + 1)
label[1] = 0
pending = {1}
extraction_order = []
relax_invocations = 0
successful_relaxations = 0
sink_writes = []

while pending:
    chosen = None
    for candidate in pending:
        if chosen is None or (label[candidate], candidate) < (label[chosen], chosen):
            chosen = candidate
    pending.remove(chosen)
    extraction_order.append(chosen)

    for head, cost in outgoing[chosen]:
        relax_invocations += 1
        proposed = label[chosen] + cost
        if label[head] is None or proposed < label[head]:
            label[head] = proposed
            successful_relaxations += 1
            pending.add(head)
            if head == N:
                sink_writes.append(proposed)

# Independently enumerate the stated subset path weights for this one input.
# A bit set at position k means that v_(k+2) is on the path.
path_weights = []
for mask in range(1 << (N - 2)):
    reduction = 0
    for bit in range(N - 2):
        if mask & (1 << bit):
            reduction += delta[bit + 2]
    path_weights.append(W - reduction)

expected_edges = N * (N - 1) // 2
claimed_intermediate_sink_updates = (1 << (N - 2)) - 1
expected_sink_writes = [W]
prefix = 0
for vertex in range(2, N):
    prefix += delta[vertex]
    expected_sink_writes.append(W - prefix)

assert W == 1023
assert len(path_weights) == 1024
assert len(set(path_weights)) == 1024
assert min(path_weights) == 0
assert extraction_order == list(range(1, N + 1))
assert label[N] == 0
assert sink_writes == expected_sink_writes
assert relax_invocations == expected_edges == 66
assert successful_relaxations == 66
assert len(sink_writes) == 11
assert len(sink_writes) - 1 == 10
assert 10 < claimed_intermediate_sink_updates

print("CONFIRMED")
print("n=12, W=1023, edges=66, distinct_source_sink_paths=1024")
print("extraction_order=" + ",".join(str(v) for v in extraction_order))
print("relax_invocations=66, successful_relaxations=66")
print("sink_writes=11, intermediate_to_sink_updates=10, claimed=1023")
print("final_sink_distance=0")
print("The exponential Relax claim is substantive, not a typo, and is false on the stated trace.")
