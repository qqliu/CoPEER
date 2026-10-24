"""Equation (3) at line 218 incorrectly uses G(f,id_D), rather than F(f,id_D), on its right-hand side and can therefore fail even when the stated separate naturality assumptions hold."""

import json

SOURCE_QUOTE = r"::$(3)\quad \map G {f, \operatorname{id}_D} \circ \alpha_{\tuple{C, D} } = \alpha_{\tuple{C', D} } \circ \map G {f, \operatorname{id}_D}$"
CANDIDATE_INTERPRETATIONS = ()

# Exhaust the only semantic candidate space licensed by the supplied quote.
for interpretation in CANDIDATE_INTERPRETATIONS:
    raise AssertionError(interpretation)

# Exhaustively inspect the bounded syntactic space: every source position
# paired, in fixed order, with each symbol relevant to the alleged typo.
SYMBOLS = ("F", "G")
occurrences = tuple(
    (position, symbol)
    for position in range(len(SOURCE_QUOTE))
    for symbol in SYMBOLS
    if SOURCE_QUOTE.startswith(symbol, position)
)
assert tuple(symbol for _, symbol in occurrences) == ("G", "G")

result = {
    "record_id": "proofwiki_149255__codex_expansion",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness can be formed from the supplied equation alone.",
    "refutation_explanation": "The quote supplies only a formal equation containing G and gives no definitions of F, G, alpha, their domains, composition, or the stated separate naturality assumptions. Consequently there are no supplied semantic interpretations in which the assumptions and failure of the equation can both be checked.",
    "search_space": "Exhaustive sweep of the empty tuple of semantic interpretations supplied by the quote, plus a fixed syntactic scan of every character position in the single supplied equation for occurrences of the symbols F and G. The syntactic scan cannot decide semantic failure.",
}
print(json.dumps(result, separators=(",", ":")))
