"""The claimed equivalence that a locale isomorphism is precisely the opposite of some frame homomorphism."""

import json
from itertools import product


RECORD_ID = "proofwiki_136810__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No mathematical witness is identified; the finite sweep only produces "
    "formal valuations of undefined symbols."
)
REFUTATION_EXPLANATION = (
    "The quote does not supply the domains, typing, or semantics of locale "
    "isomorphism, frame homomorphism, or the opposite operation. Consequently, "
    "disagreements in an uninterpreted finite abstraction cannot be certified "
    "as mathematical counterexamples, while imposing the displayed equivalence "
    "as a definition would make the claim tautological."
)
SEARCH_SPACE = (
    "All 4 interpretations on the one-element carrier {0}: LocaleIso and "
    "FrameHom independently range over both subsets of {0}, op ranges over "
    "the unique function {0}->{0}, and f is 0."
)


def member(mask, element):
    return bool(mask & (1 << element))


def main():
    carrier = (0,)
    interpretation_count = 0
    formal_disagreements = []

    for locale_mask in range(1 << len(carrier)):
        for frame_mask in range(1 << len(carrier)):
            for op_values in product(carrier, repeat=len(carrier)):
                interpretation_count += 1
                f = 0
                left = member(locale_mask, f)
                right = any(
                    member(frame_mask, h) and op_values[h] == f
                    for h in carrier
                )
                if left != right:
                    formal_disagreements.append(
                        (locale_mask, frame_mask, op_values, f)
                    )

    assert interpretation_count == 4
    assert len(formal_disagreements) == 2

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
