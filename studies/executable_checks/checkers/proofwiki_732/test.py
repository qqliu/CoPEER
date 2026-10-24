"""In case (2) (some x is related by R to two distinct y_1 != y_2), the proof asserts that neither {y_1} nor {y_2} can lie in the range of R^-> , and concludes from this that R^-> cannot be a surjection."""

import itertools
import json


def main():
    powerset = tuple(range(4))
    singleton_0 = 1
    singleton_1 = 2
    counterexamples = []

    for outputs in itertools.product(powerset, repeat=len(powerset)):
        image = frozenset(outputs)
        both_absent = singleton_0 not in image and singleton_1 not in image
        surjective = image == frozenset(powerset)
        if both_absent and surjective:
            counterexamples.append(outputs)

    if counterexamples:
        raise AssertionError("Unexpected counterexample to the finite logical implication")

    result = {
        "record_id": "proofwiki_732",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No counterexample was found in the bounded function sweep, but the target claim cannot be decided from the supplied data.",
        "refutation_explanation": "The source quote does not define R^->, explain how it is constructed from R, or state its codomain. Thus the central assertion about which singletons can occur in its range cannot be tested without inventing missing definitions. The finite sweep verifies only the abstract implication when the codomain is explicitly P({0,1}); it does not decide the target claim.",
        "search_space": "All 4^4 = 256 total functions f:P({0,1})->P({0,1}), enumerated in lexicographic output-tuple order; each was tested for having both {0} and {1} absent from its range while still being surjective. No relations R were swept because the supplied quote does not define R^-> or its connection to R."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
