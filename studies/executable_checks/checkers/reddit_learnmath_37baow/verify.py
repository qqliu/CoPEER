r"""No function f: P(A) --> P(A) can be surjective."""

import json


def power_set(items):
    subsets = {frozenset()}
    for item in items:
        subsets |= {subset | {item} for subset in tuple(subsets)}
    return frozenset(subsets)


def main():
    base_set = frozenset()
    domain = power_set(base_set)
    codomain = power_set(base_set)
    function = {element: element for element in domain}

    is_total = frozenset(function) == domain
    maps_into_codomain = all(value in codomain for value in function.values())
    image = frozenset(function.values())
    is_surjective = is_total and maps_into_codomain and image == codomain
    witness_valid = (
        base_set == frozenset()
        and domain == frozenset({frozenset()})
        and is_surjective
    )

    if witness_valid:
        verdict = "CONFIRMED"
        notes = "Exact recomputation confirms the witness: for A = ∅, P(A) has the single element ∅, and its identity function is surjective. The refuted statement is plainly a typo or theorem-direction mistake, since the identity on P(A) is surjective for every A."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "Exact recomputation does not establish that the reported function is surjective. The statement nevertheless appears plainly mistyped because an identity map from a set to itself is surjective."

    result = {
        "record_id": "reddit_learnmath_37baow",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
