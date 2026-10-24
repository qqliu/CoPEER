r"""In the displayed computation the proof asserts f^\to \circ (f^{-1})^\to = (f \circ f^{-1})^\to = (I_S)^\to = I_{\powerset S}, i.e. that f \circ f^{-1} = I_S (and symmetrically that (f^{-1})^\to \circ f^\to = I_{\powerset T}). Under the standard composition convention (g \circ f)(x) = g(f(x)) used by the source wiki, f \circ f^{-1} is the identity on T, not on S, so the two identity subscripts are swapped: the first composite is I_{\powerset T} and the second is I_{\powerset S}."""

import itertools
import json

RECORD_ID = "proofwiki_145181"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "S={0}, T={1}, and the bijection f:S→T given by f(0)=1 (so f^{-1}(1)=0)."
REFUTATION_EXPLANATION = "For this witness, f∘f^{-1} has domain T and graph {(1,1)}, whereas I_S has graph {(0,0)}; hence they are not equal. Its direct-image mapping is the identity on P(T)={∅,{1}}, not on P(S)={∅,{0}}. Symmetrically, f^{-1}∘f is the identity on S, not on T, so the displayed identity subscripts are swapped."
SEARCH_SPACE = "All 6 triples (S,T,f) where S and T are nonempty subsets of {0,1} with |S|=|T| and f ranges over every bijection S→T (4 singleton triples and 2 two-element bijections); the full space was swept in lexicographic combination/permutation order."


def power_set(values):
    return tuple(
        tuple(choice)
        for size in range(len(values) + 1)
        for choice in itertools.combinations(values, size)
    )


def direct_image_graph(domain, mapping):
    return tuple(
        (subset, tuple(sorted(mapping[item] for item in subset)))
        for subset in power_set(domain)
    )


universe = (0, 1)
violations = []
examined = 0

for size in (1, 2):
    for source in itertools.combinations(universe, size):
        for target in itertools.combinations(universe, size):
            for target_order in itertools.permutations(target):
                examined += 1
                function_graph = tuple(zip(source, target_order))
                function = dict(function_graph)
                inverse = {value: key for key, value in function_graph}

                first_composite = tuple(
                    (value, function[inverse[value]]) for value in target
                )
                second_composite = tuple(
                    (value, inverse[function[value]]) for value in source
                )
                identity_source = tuple((value, value) for value in source)
                identity_target = tuple((value, value) for value in target)

                first_direct = direct_image_graph(target, dict(first_composite))
                second_direct = direct_image_graph(source, dict(second_composite))
                direct_identity_source = tuple(
                    (subset, subset) for subset in power_set(source)
                )
                direct_identity_target = tuple(
                    (subset, subset) for subset in power_set(target)
                )

                if (
                    first_composite != identity_source
                    or second_composite != identity_target
                    or first_direct != direct_identity_source
                    or second_direct != direct_identity_target
                ):
                    violations.append(
                        (source, target, function_graph, first_composite,
                         identity_source, second_composite, identity_target)
                    )

assert examined == 6
assert violations
assert violations[0] == (
    (0,), (1,), ((0, 1),), ((1, 1),), ((0, 0),), ((0, 0),), ((1, 1),)
)

payload = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
