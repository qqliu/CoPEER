"""Every real semi-inner product space is, with the same given structure, a complex semi-inner product space."""

import json

SOURCE_QUOTE = """This follows immediately from:

* {{Defof|Real Semi-Inner Product Space}}

* {{Defof|Complex Semi-Inner Product Space}}

* [[Real Semi-Inner Product is Complex Semi-Inner Product]]"""

EXPECTED_LINES = (
    "This follows immediately from:",
    "",
    "* {{Defof|Real Semi-Inner Product Space}}",
    "",
    "* {{Defof|Complex Semi-Inner Product Space}}",
    "",
    "* [[Real Semi-Inner Product is Complex Semi-Inner Product]]",
)

lines = tuple(SOURCE_QUOTE.splitlines())
assert lines == EXPECTED_LINES

introductory_lines = []
blank_lines = []
reference_lines = []
explicit_mathematical_data = []

for index in range(7):
    line = lines[index]
    if line == "":
        blank_lines.append(index)
    elif index == 0 and line == "This follows immediately from:":
        introductory_lines.append(index)
    elif line.startswith("* "):
        reference_lines.append(index)
    else:
        explicit_mathematical_data.append((index, line))

assert introductory_lines == [0]
assert blank_lines == [1, 3, 5]
assert reference_lines == [2, 4, 6]
assert explicit_mathematical_data == []

result = {
    "record_id": "proofwiki_110169__codex_expansion",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No counterexample is reported because the supplied quote specifies no candidate semi-inner product space or defining axioms that can be checked.",
    "refutation_explanation": "The quote contains only an introductory sentence and cross-references to definitions and another result. Without the referenced definitions, the meanings and required compatibility of real and complex semi-inner product spaces are unavailable, so the target claim cannot be tested or refuted from the permitted data.",
    "search_space": "The program exhaustively scans the 7 source_quote lines at indices 0 through 6, in fixed order. They consist only of one introductory sentence, three blank lines, and three cross-reference bullets; consequently the quote specifies zero candidate semi-inner product spaces to test.",
}

print(json.dumps(result, separators=(",", ":")))
