r"""The given right adjoint functor \otimes is strictly equal to the independently chosen product functor \times, rather than merely naturally isomorphic to it."""

import json


def main():
    candidates = ()
    witness = None

    for candidate in candidates:
        witness = candidate
        break

    assert witness is None
    result = {
        "record_id": "proofwiki_150886__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness is available: the supplied quote contains no category, objects, morphisms, functor definitions, or component values to test.",
        "refutation_explanation": "Strict equality of two functors cannot be checked or refuted from the quoted assertion alone. The source data does not specify either functor or any input on which their object or morphism assignments could differ.",
        "search_space": "Exactly the empty tuple of candidate counterexamples, because the supplied source quote provides zero concrete categories, functor assignments, objects, or morphisms from which a candidate can be formed."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
