r"""Suppose it's the case when $f(m)=O(m^{\log_2 1-\epsilon})=O(m^{0-\epsilon})$. Let $\epsilon=0.5$ then:"""

import json
from fractions import Fraction

RECORD_ID = "SE_cs_77908__q"
TARGET_CLAIM = r"""Suppose it's the case when $f(m)=O(m^{\log_2 1-\epsilon})=O(m^{0-\epsilon})$. Let $\epsilon=0.5$ then:"""
SOURCE_QUOTE = r"""Suppose it's the case when $f(m)=O(m^{\log_2 1-\epsilon})=O(m^{0-\epsilon})$. Let $\epsilon=0.5$ then:"""
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No counterexample can be named because the supplied text contains no conclusion to violate."
REFUTATION_EXPLANATION = "The text ends at 'then:' and states no consequent, predicate, domain for m, or concrete f. Thus there is no truth-valued conclusion against which any candidate could be a counterexample; the finite structural sweep cannot resolve a mathematical claim."
SEARCH_SPACE = "Exactly the 2 labeled supplied strings {target_claim, source_quote}, each paired with the sole stated exact epsilon value {1/2}; all 2 pairs were checked for a nonempty consequent after the final 'then:'. No domain for m or class of f was supplied."


def has_nonempty_consequent(text):
    marker = "then:"
    marker_index = text.rfind(marker)
    if marker_index < 0:
        return False
    return bool(text[marker_index + len(marker):].strip())


def main():
    exact_epsilon = Fraction(1, 2)
    bounded_space = (
        ("target_claim", TARGET_CLAIM, exact_epsilon),
        ("source_quote", SOURCE_QUOTE, exact_epsilon),
    )
    checked = []
    for label, text, epsilon in bounded_space:
        checked.append((label, epsilon, has_nonempty_consequent(text)))

    assert len(checked) == 2
    assert all(item[1] == Fraction(5, 10) for item in checked)
    assert not any(item[2] for item in checked)

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), ensure_ascii=True))


if __name__ == "__main__":
    main()
