"""Under the stated hypotheses, ‖f‖ attains both a minimum and a maximum on X, even though X is not assumed nonempty."""

import json

RECORD_ID = "proofwiki_10636__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = ("Exact recomputation confirms that the empty domain has a unique empty function, "
         "while minimum and maximum attainment each require an existentially chosen point "
         "of X; both therefore fail. The refuted statement has a substantive "
         "missing-nonemptiness flaw, not a plain typo.")


def is_total_function(domain, graph):
    inputs = tuple(pair[0] for pair in graph)
    return all(inputs.count(x) == 1 for x in domain) and all(x in domain for x in inputs)


def attains_minimum(domain, values):
    return any(all(values[x] <= values[y] for y in domain) for x in domain)


def attains_maximum(domain, values):
    return any(all(values[y] <= values[x] for y in domain) for x in domain)


def main():
    domain = frozenset()
    function_graph = tuple()
    norm_values = {}

    assert is_total_function(domain, function_graph)
    assert function_graph == tuple()
    assert set(norm_values) == set(domain)

    has_minimum = attains_minimum(domain, norm_values)
    has_maximum = attains_maximum(domain, norm_values)
    assert has_minimum is False
    assert has_maximum is False
    assert not (has_minimum and has_maximum)

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
