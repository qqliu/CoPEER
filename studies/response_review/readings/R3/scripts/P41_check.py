# P41: check the supplied witness: a tree containing the edge uv, and the sequence u-v-u-v.
E = {frozenset(('u','v'))}          # the 2-vertex tree containing an edge between u and v
V = {'u','v'}
seq = ['u','v','u','v']
is_walk = all(frozenset((seq[i], seq[i+1])) in E for i in range(len(seq)-1))
rep_vertices = len(set(seq)) < len(seq)
edges_used = [frozenset((seq[i], seq[i+1])) for i in range(len(seq)-1)]
rep_edges = len({tuple(sorted(e)) for e in edges_used}) < len(edges_used)
print("graph: V =", sorted(V), " E =", [sorted(e) for e in E], " (a tree: connected, n-1 = 1 edge, acyclic)")
print("sequence", '-'.join(seq), ": consecutive vertices adjacent (so a walk from u to v)?", is_walk)
print("repeats a vertex?", rep_vertices, "  repeats an edge?", rep_edges,
      "-> is it a path (no repeated vertices, no repeated edges, per line 7)?", not (rep_vertices or rep_edges))
print("does the walk create a circuit in the graph? no new edges are added; the graph is still acyclic:",
      len(E) == len(V) - 1)
