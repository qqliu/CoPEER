r"""If f:X→Y is injective, then there exists g:Y→X such that g∘f=id_X."""

import json

RECORD_ID = "reddit_learnmath_13vpgw3"
VERDICT = "CONFIRMED"
NOTES = (
    "The witness is valid: the empty function from X=∅ to Y={0} is "
    "injective, while no total function Y→X exists. The refutation exposes "
    "a substantive missing nonemptiness condition, not a plain typo."
)


def all_graphs(domain, codomain):
    pairs = tuple((source, target) for source in domain for target in codomain)
    graphs = [frozenset()]
    for pair in pairs:
        additions = [graph.union((pair,)) for graph in graphs]
        graphs = graphs + additions
    return tuple(graphs)


def is_total_function(graph, domain, codomain):
    allowed = frozenset(
        (source, target) for source in domain for target in codomain
    )
    if not graph.issubset(allowed):
        return False
    for source in domain:
        images = tuple(
            target for candidate, target in graph if candidate == source
        )
        if len(images) != 1:
            return False
    return True


def function_value(graph, source):
    images = tuple(
        target for candidate, target in graph if candidate == source
    )
    if len(images) != 1:
        raise ValueError("graph is not single-valued at the requested input")
    return images[0]


def is_injective(graph, domain, codomain):
    if not is_total_function(graph, domain, codomain):
        return False
    images = tuple(function_value(graph, source) for source in domain)
    return len(frozenset(images)) == len(images)


def is_left_inverse(f_graph, g_graph, domain, codomain):
    if not is_total_function(f_graph, domain, codomain):
        return False
    if not is_total_function(g_graph, codomain, domain):
        return False
    return all(
        function_value(g_graph, function_value(f_graph, source)) == source
        for source in domain
    )


def main():
    domain = frozenset()
    codomain = frozenset((0,))
    f_graph = frozenset()

    possible_f_graphs = all_graphs(domain, codomain)
    assert possible_f_graphs == (f_graph,)
    assert is_injective(f_graph, domain, codomain)

    possible_g_graphs = all_graphs(codomain, domain)
    total_g_graphs = tuple(
        graph
        for graph in possible_g_graphs
        if is_total_function(graph, codomain, domain)
    )
    assert total_g_graphs == ()
    assert not any(
        is_left_inverse(f_graph, graph, domain, codomain)
        for graph in possible_g_graphs
    )

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
