"""The asserted antiderivative identity has a plus sign before the residual integral."""

import json

RECORD_ID = "proofwiki_128227__codex_expansion"
SOURCE_QUOTES = (
    r"r = \frac {x^{n + 1} } {n + 1} \arctan a x + \frac a {n + 1} \int \frac {x^{n + 1} \rd x} {a^2 x^2 + 1}",
)
RESIDUAL_PREFIX = r"\frac a {n + 1} \int"

counterexamples = []
for source_quote in SOURCE_QUOTES:
    start = source_quote.find(RESIDUAL_PREFIX)
    preceding_text = source_quote[:start].rstrip() if start >= 0 else ""
    has_required_plus = start >= 0 and bool(preceding_text) and preceding_text[-1] == "+"
    if not has_required_plus:
        counterexamples.append(source_quote)

if counterexamples:
    raise AssertionError("The fixed singleton search unexpectedly found a counterexample")

result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_EXHAUSTIVE",
    "witness_description": "No counterexample exists in the singleton textual search space: the supplied identity has the character `+` immediately before the residual term.",
    "refutation_explanation": "The claim is syntactic rather than a claim that the displayed expression is a correct antiderivative. In the supplied source_quote, the residual term beginning `\\frac a {n + 1} \\int` is literally preceded by `+`. No unstated integrand, parameter domain, or semantic definition of r was introduced.",
    "search_space": "Exactly the singleton set containing the supplied source_quote. The program locates the unique literal residual-term prefix `\\frac a {n + 1} \\int` and checks the last non-whitespace character preceding it.",
}
print(json.dumps(result, separators=(",", ":")))
