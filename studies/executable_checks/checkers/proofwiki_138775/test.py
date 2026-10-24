r"""The proof asserts that the dual of the meet-prime condition is the displayed formula on line 0007, and then that this displayed formula is exactly the definition of 'z is a join prime element'. As written, the displayed formula has 'z \preceq z' as its first disjunct (instead of 'z \preceq x'), so it is vacuously true by reflexivity for every element z of every ordered set, and therefore is NOT equivalent to join primeness."""

import itertools
import json


def main():
    counterexamples = []
    checked = 0
    first_disjunct = True

    for antecedent, second_disjunct in itertools.product(
        (False, True), repeat=2
    ):
        checked += 1
        implication = (not antecedent) or (
            first_disjunct or second_disjunct
        )
        if not implication:
            counterexamples.append((antecedent, second_disjunct))

    assert checked == 4
    assert counterexamples == []

    result = {
        "record_id": "proofwiki_138775",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No counterexample is reported; the bounded sweep only verifies the propositional vacuity of the displayed implication.",
        "refutation_explanation": "The finite sweep finds no valuation falsifying the displayed implication because its first consequent disjunct is fixed True. However, the quote supplies no definition of 'join prime element' and no class of ordered structures to enumerate, so the claimed non-equivalence cannot be tested without inventing absent data.",
        "search_space": "All 4 Boolean valuations (antecedent, second_disjunct) in {False, True}^2, in itertools.product order, with first_disjunct fixed to True by the claim's stated reflexivity premise. This exhausts only the displayed formula's propositional vacuity, not ordered sets or join primeness."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
