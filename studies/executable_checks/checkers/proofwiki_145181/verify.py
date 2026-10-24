r"""In the displayed computation the proof asserts f^\to \circ (f^{-1})^\to = (f \circ f^{-1})^\to = (I_S)^\to = I_{\powerset S}, i.e. that f \circ f^{-1} = I_S (and symmetrically that (f^{-1})^\to \circ f^\to = I_{\powerset T}). Under the standard composition convention (g \circ f)(x) = g(f(x)) used by the source wiki, f \circ f^{-1} is the identity on T, not on S, so the two identity subscripts are swapped: the first composite is I_{\powerset T} and the second is I_{\powerset S}."""

import json

record_id = "proofwiki_145181"
verdict = "CONFIRMED"
notes = "Exact recomputation confirms the singleton witness: f∘f^{-1} is I_T and (f^{-1})∘f is I_S, with the corresponding direct-image identities on P(T) and P(S). The refuted displayed statement is plainly a subscript-swapping typo, though it is literally false when S and T differ."

S = frozenset((0,))
T = frozenset((1,))
f = {0: 1}

assert set(f) == set(S)
assert frozenset(f.values()) == T
assert len(f.values()) == len(set(f.values()))
f_inverse = {image: preimage for preimage, image in f.items()}


def identity(domain):
    return (domain, frozenset((x, x) for x in domain))


def composite(outer, inner, domain):
    return (domain, frozenset((x, outer[inner[x]]) for x in domain))


def subsets(domain):
    items = tuple(sorted(domain))
    answer = set()
    for mask in range(1 << len(items)):
        answer.add(frozenset(items[index] for index in range(len(items))
                             if mask & (1 << index)))
    return frozenset(answer)


def direct_image(mapping, domain):
    domain_subsets = subsets(domain)
    graph = frozenset(
        (part, frozenset(mapping[x] for x in part))
        for part in domain_subsets
    )
    return (domain_subsets, graph)


def compose_direct(outer, inner):
    inner_domain, inner_graph = inner
    outer_domain, outer_graph = outer
    inner_map = dict(inner_graph)
    outer_map = dict(outer_graph)
    assert frozenset(inner_map.values()).issubset(outer_domain)
    return (
        inner_domain,
        frozenset((part, outer_map[inner_map[part]]) for part in inner_domain),
    )

first = composite(f, f_inverse, T)
second = composite(f_inverse, f, S)
I_S = identity(S)
I_T = identity(T)

f_direct = direct_image(f, S)
inverse_direct = direct_image(f_inverse, T)
first_direct = compose_direct(f_direct, inverse_direct)
second_direct = compose_direct(inverse_direct, f_direct)
I_power_S = identity(subsets(S))
I_power_T = identity(subsets(T))

assert first == I_T
assert second == I_S
assert first != I_S
assert second != I_T
assert first_direct == I_power_T
assert second_direct == I_power_S
assert first_direct != I_power_S
assert second_direct != I_power_T

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, ensure_ascii=False, separators=(",", ":")))
