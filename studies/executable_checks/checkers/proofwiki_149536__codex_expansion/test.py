"""Equation (3) is asserted as the first-variable naturality equation, but incorrectly uses G(f,id_D) rather than F(f,id_D) on its right-hand side."""

import json

SOURCE_QUOTE = r"""::$(3)\quad \map G {f, \operatorname{id}_D} \circ \alpha_{\tuple{C, D} } = \alpha_{\tuple{C', D} } \circ \map G {f, \operatorname{id}_D}$"""
G_TERM = r"\map G {f, \operatorname{id}_D}"
F_TERM = r"\map F {f, \operatorname{id}_D}"


def occurrence_positions(text, needle):
    return tuple(
        index
        for index in range(len(text))
        if text.startswith(needle, index)
    )


def main():
    whole_g = occurrence_positions(SOURCE_QUOTE, G_TERM)
    whole_f = occurrence_positions(SOURCE_QUOTE, F_TERM)
    equals_positions = occurrence_positions(SOURCE_QUOTE, "=")
    if len(equals_positions) != 1:
        raise AssertionError("The bounded syntactic analysis requires one equals sign")
    right_hand_side = SOURCE_QUOTE[equals_positions[0] + 1:]
    rhs_g = occurrence_positions(right_hand_side, G_TERM)
    rhs_f = occurrence_positions(right_hand_side, F_TERM)
    if not (len(whole_g) == 2 and len(whole_f) == 0 and len(rhs_g) == 1 and len(rhs_f) == 0):
        raise AssertionError("Unexpected literal-occurrence result")

    result = {
        "record_id": "proofwiki_149536__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete counterexample is determined by the supplied quote.",
        "refutation_explanation": "An exhaustive literal scan confirms that the displayed right-hand side contains G(f,id_D) and does not contain F(f,id_D). However, the quote provides no definitions, types, or naturality convention for F, G, and alpha, and it does not independently establish how equation (3) was asserted. Thus the supplied data cannot decide whether that occurrence of G is mathematically incorrect.",
        "search_space": "Every character start position i with 0 <= i < len(source_quote), checked in fixed order for the literal G(f,id_D) and F(f,id_D) map expressions, both in the whole quote and in the substring strictly following its sole equals sign.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
