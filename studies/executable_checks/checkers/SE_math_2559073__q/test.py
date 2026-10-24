r'''and $v_1$ is connected to at least $\frac{n}{2}$ vertices from $v_2$ to $v_k$, and $v_k$ is connected to at least $\frac{n}{2}$ vertices from $v_1$ to $v_{k-1}$'''

import json

RECORD_ID = "SE_math_2559073__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No witness is asserted: the quote is only a conjunctive sentence fragment and supplies no concrete graph, values of n and k, quantifiers, hypotheses, or definition of \"connected.\""
REFUTATION_EXPLANATION = "A counterexample cannot be validated from the supplied data alone. The fragment states two lower bounds but does not specify the class of objects over which they are claimed or the preceding assumptions; choosing a graph model would invent absent data."
SEARCH_SPACE = "The program exhaustively sweeps the explicitly bounded set of concrete instances supplied by the quote, which is empty (0 instances); it introduces no graph interpretations."


def main():
    concrete_instances = ()
    witness = None
    for instance in concrete_instances:
        witness = instance
        break
    assert witness is None
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
