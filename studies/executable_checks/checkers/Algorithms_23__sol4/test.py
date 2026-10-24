"""g(x, y) −f(x, y) = h(x, y) −h(y, x) ."""

import json

TARGET_CLAIM = "g(x, y) −f(x, y) = h(x, y) −h(y, x) ."
SOURCE_QUOTE = "g(x, y) −f(x, y) = h(x, y) −h(y, x) ."
SOURCES = (TARGET_CLAIM, SOURCE_QUOTE)
APPLICATIONS = ("g(x, y)", "f(x, y)", "h(x, y)", "h(y, x)")


def exhaustive_textual_sweep():
    seen_applications = set()
    numeric_positions = []
    substring_count = 0

    for source_index, text in enumerate(SOURCES):
        for position, character in enumerate(text):
            if character.isdecimal():
                numeric_positions.append((source_index, position, character))
        for start in range(len(text) + 1):
            for end in range(start, len(text) + 1):
                substring_count += 1
                substring = text[start:end]
                for application in APPLICATIONS:
                    if substring == application:
                        seen_applications.add(application)

    return (
        substring_count,
        tuple(sorted(seen_applications)),
        tuple(numeric_positions),
    )


def main():
    substring_count, seen_applications, numeric_positions = exhaustive_textual_sweep()
    if substring_count <= 0:
        raise AssertionError("The bounded textual sweep was not performed")
    if seen_applications != tuple(sorted(APPLICATIONS)):
        raise AssertionError("The supplied equation was not completely recognized")
    if numeric_positions:
        raise AssertionError("Unexpected concrete numeric data")

    result = {
        "record_id": "Algorithms_23__sol4",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness is determined: the quote supplies no domain, quantifier, definitions of f, g, or h, or values at any x and y.",
        "refutation_explanation": "The displayed equation alone does not say which objects x and y range over or how f, g, and h are defined. Assigning values or a finite domain would add data absent from the quote, so neither side can be evaluated and no counterexample can be certified.",
        "search_space": "Exhaustively inspected both supplied strings, at every character position and for every contiguous substring, plus the four displayed function applications g(x, y), f(x, y), h(x, y), and h(y, x). This finite textual space contains no admissible concrete valuations to test.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
