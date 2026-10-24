"""We need to show that G is 3-colorable if and only if G′ is 12-colorable."""

import itertools
import json


def main():
    valuations = tuple(itertools.product((False, True), repeat=2))
    unequal = tuple(pair for pair in valuations if pair[0] != pair[1])

    assert valuations == (
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    )
    assert unequal == ((False, True), (True, False))

    result = {
        "record_id": "Algorithms_28__sol5",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be named because the quote provides neither graphs nor a definition relating G to G′.",
        "refutation_explanation": "The four possible Boolean truth-value pairs for “G is 3-colorable” and “G′ is 12-colorable” include unequal pairs, but the quote does not determine whether any such pair is admissible under the intended construction of G′. Thus the Boolean sweep cannot yield a mathematical counterexample.",
        "search_space": "Exhaustively swept all 4 ordered pairs in {False, True} × {False, True}; this is only the complete Boolean abstraction, not a graph-instance space.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
